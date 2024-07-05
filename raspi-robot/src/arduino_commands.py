# Immutable command variables
"""
Commands for the robot
"""
RESET = 0
BUCKET_ONE = 1
BUCKET_TWO = 2
GET_PACKAGE = 3

"""
Error messages
"""
MALLOC = 'm'    # malloc error: malloc for boxes_array failed
SCALE = 's'     # scale error: “Timeout, check MCU>HX711 wiring and pin designations”
WEIGHT = 'w'    # weighting error: package weights too little or too much
LIGHT = 'l'     # light barrier error: the light barrier was triggered
WIFI = 'i'      # internet error: “Communication with WiFi module failed”
TCP = 't'       # server error: “Failed to connect to TCP server”