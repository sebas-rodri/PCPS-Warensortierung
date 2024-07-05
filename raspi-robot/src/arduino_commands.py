# Immutable command variables
"""
Commands for the robot
"""
RESET = 0
BUCKET_ONE = 1
BUCKET_TWO = 2

"""
Error messages
"""
SCALE = 's'     # scale error: “Timeout, check MCU>HX711 wiring and pin designations”
WEIGHT = 'w'    # weighting error: package weights too little or too much
LIGHT1 = 'l'    # light barrier error: the light barrier for box 1 was triggered
LIGHT2 = 'L'    # light barrier error: the light barrier for box 2 was triggered
