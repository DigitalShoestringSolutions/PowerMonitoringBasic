//from django example https://docs.djangoproject.com/en/3.2/ref/csrf/
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function mergeSettings(A, B) {
  return { ...A, ...B, headers: { ...A.headers, ...B.headers } }
}

//todo: could move csrf token to a context

async function api_post(url, data) {
  return await api_call(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
}

async function api_delete(url) {
  return await api_call(url, { method: 'DELETE' })
}

async function api_put(url, data) {
  return await api_call(url, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
}

async function api_get(url) {
  return await api_call(url)
}

async function api_call(url, settings = {}) {
  const csrf_token = getCookie('csrftoken');
  let defaults = {
    method: 'GET',
    mode: 'cors',
    // credentials: 'include',
    cache: 'no-cache',
    headers: {
      'Accept': 'application/json',
      'X-CSRFToken': csrf_token,
    },
  }
  var response = await fetch(url, mergeSettings(defaults, settings))
  const contentType = response.headers.get("content-type");
  var output = ''
  if (contentType && contentType.indexOf("application/json") !== -1) {
    output = await response.json()
    return { status: response.status, payload: output }
  } else {
    output = await response.text()
    console.log(output)
    return { status: response.status, payload: output}
  }
}

const Ex = {api_get, api_post, api_put, api_delete}
export default Ex