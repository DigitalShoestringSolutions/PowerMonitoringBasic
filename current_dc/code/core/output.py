import logging
import json

import jsonpath_rw
from enum import Enum, auto

logger = logging.getLogger(__name__)


# if append is true - changes dictated by the spec are added to the original message
# if append is false - only the items contained in the spec are sent
#
# spec:
# The spec can either be defined in json as spec_json or in toml as spec
# The spec is made up of a set of 'keys' and 'values'.
#
# Each spec key defines the key in the output and the spec value defines the corresponding value from the input
#
#  Example:
# | spec                   | Output                              |
# |========================|=====================================|
# | key:<value>            | { "key":<value> }                   |
# | lvl1.lvl2.key: <value> | { "lvl1":{"lvl2":{"key":<value>"}}} |
#
# in a json spec, hierarchy can be expressed directly or using dot delimiters
# e.g. {"a":{"b":{"c":"<spec_value>"}}} and {"a.b.c":"<spec_value>"} are equivalent
# in toml this would be:
# [spec]
# a.b.c = "<spec_value>"
#
# Spec values are assumed to be jsonpath mappings to values in the original message unless prefixed:
# more details on jsonpath can be found here: https://goessner.net/articles/JsonPath/
# spec values with a '#' prefix are treated as json strings
# An '=' prefix is used for json numbers and special values
#
#  Example:
# | spec value  | message value |
# |=============|===============|
# | "#abc"      | "key":"abc"   |
# | "=true"     | "key": true   !
# | "=false"    | "key": false  |
# | "=null"     | "key": null   |
# | "=1.123"    | "key": 1.123  |
# | "=1"        | "key": 1      |
#
#  JsonPath Example:
#  original:
# {
#  	"a": {
#     "b": {
#	 	"c": "123",
#       "d": "abc",
#     },
# 	},
#   "e": true,
# }
#
# | spec                    | output (append=false)       |
# |=========================|=============================|
# | "x":"$.a.b"             | {"x":{"c":"123","d":"abc"}} |
# | "x":"$.a.b.c","y":"$.e" | {"x":"123","y":true}        |

class LEAF(Enum):
    JSONPATH = auto()
    STRING = auto()
    NUMBER = auto()
    BOOLEAN = auto()
    NULL = auto()


def generate_json_path_message(input_dataset, spec, append=False):
    logger.debug(f"Transform: {'append' if append else 'new'};{spec};{input_dataset};")
    output = {} if not append else to_flat_tree(input_dataset)
    for leaf_path, leaf_value in to_flat_tree(spec).items():
        leaf_type, true_value = get_leaf_type(leaf_value)
        if leaf_type == LEAF.JSONPATH:
            res = jsonpath_rw.parse(true_value).find(input_dataset)
            if len(res) == 0:
                # not found
                logger.warning(f"json_path {leaf_value} return no data and was ignored")
                continue

            if len(res) > 1:
                logger.warning("json_path {leaf_value} returned more than one result - using first entry")
            leaf = res[0]
            value = leaf.value
            output[leaf_path] = value

            if append and str(leaf.full_path) != leaf_path:
                output.pop(str(leaf.full_path), None)
        else:
            output[leaf_path] = true_value
    return from_flat_tree(output)


def get_leaf_type(leaf_value):
    if leaf_value[0] == '#':
        return LEAF.STRING, leaf_value[1:]
    if leaf_value[0] == '=':
        rem = leaf_value[1:]
        if rem.casefold() == 'true':
            return LEAF.BOOLEAN, True
        if rem.casefold() == 'false':
            return LEAF.BOOLEAN, False
        if rem.casefold() == 'null':
            return LEAF.NULL, None
        else:
            try:
                return LEAF.NUMBER, int(rem)
            except ValueError:
                try:
                    return LEAF.NUMBER, float(rem)
                except ValueError:
                    logger.warning(f"Unable to parse {leaf_value} treating as string")
                    return LEAF.STRING, rem
    else:
        return LEAF.JSONPATH, leaf_value


def to_flat_tree(dataset):
    return flatten_by_type(dataset)


def flat_loop_dict(nested_dict, path=""):
    acc = {}
    for key, value in nested_dict.items():
        path_string = f"{path}{'.' if path else ''}{key}"
        acc.update(flatten_by_type(value, path_string))
    return acc


def flat_loop_list(list, path=""):
    acc = {}
    for index, value in enumerate(list):
        path_string = f"{path}{'.' if path else ''}[{index}]"
        acc.update(flatten_by_type(value, path_string))
    return acc


def flatten_by_type(value, path=""):
    if isinstance(value, dict):
        return flat_loop_dict(value, path)
    elif isinstance(value, list):  # check if list of objects
        return flat_loop_list(value, path)
    else:  # should be an int or a string
        return {path: value}


def from_flat_tree(path_leave_dict):
    tree = None

    for path_string, leaf_value in path_leave_dict.items():
        path_element_list = path_string.split('.')
        branch = recursive_build_branch(path_element_list, leaf_value)
        if tree is None:
            tree = clean_branch(branch)
        else:
            merge_branch(tree, branch)

    return tree

# bottom up build
# a.b.[0].c => {a:{b:[{c:value}]}}
def recursive_build_branch(path_list, value):
    if len(path_list) == 0:
        return value

    current_element = path_list.pop(0)
    array_element = current_element[0] == '[' and current_element[-1] == ']'

    child_obj = recursive_build_branch(path_list, value)

    if array_element:
        array_index = int(current_element[1:-1])
        return [(array_index, child_obj)]
    else:
        return {current_element: child_obj}

# top down merge
def merge_branch(tree, branch):
    tree_is_dict = isinstance(tree, dict)
    tree_is_list = isinstance(tree, list)
    branch_is_dict = isinstance(branch, dict)
    branch_is_list = isinstance(branch, list)

    if tree_is_dict and branch_is_dict:
        branch_key, branch_value = list(branch.items())[0]
        if branch_key in tree:
            merge_branch(tree[branch_key], branch_value)
        else:
            tree[branch_key] = clean_branch(branch_value)
    elif tree_is_list and branch_is_list:
        branch_index, branch_value = branch[0]
        if branch_index < len(tree):
            merge_branch(tree[branch_index], branch_value)
        elif branch_index == len(tree):
            tree.append(clean_branch(branch_value))
        else:
            raise Exception("Something went Badly wrong")
    else:
        raise Exception("Something went Badly wrong")


def clean_branch(branch):
    if isinstance(branch, dict):
        branch_key, branch_value = list(branch.items())[0]
        return {branch_key: clean_branch(branch_value)}
    elif isinstance(branch, list):
        branch_index, branch_value = branch.pop()
        branch.append(branch_value)
        return [clean_branch(branch_value)]
    else:
        return branch

def generate_basic_output(input_dataset, output_spec):
    payload = {}
    if 'constants' in output_spec:
        payload = output_spec['constants']

    if 'variables' in output_spec:
        for variable in output_spec['variables']:
            payload[output_spec['variables'][variable]] = input_dataset.get(variable, None)

    return payload
