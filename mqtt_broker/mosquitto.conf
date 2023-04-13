# Config file for mosquitto
#
# See mosquitto.conf(5) for more information.

# =================================================================
# Standard MQTT listener
# =================================================================

listener 1883
protocol mqtt

# =================================================================
#  Websocket MQTT Listener
# =================================================================

listener 9001
protocol websockets

# =================================================================
# Logging
# =================================================================

log_dest stdout

log_type error
log_type warning
log_type notice
log_type information
log_type subscribe
log_type unsubscribe

connection_messages true

log_timestamp true

# ISO 8601 datetime:
log_timestamp_format %Y-%m-%dT%H:%M:%S

# =================================================================
# Access control
# =================================================================
allow_anonymous true
