from sponge.pattern import create_motor_layout
import numpy as np

LAYOUT = create_motor_layout(5, 5)
CENTER = np.array([2, 2])

moves_down = np.array([[1, 0], [2, 0]])
moves_up = moves_down * -1
moves_right = np.array([[0, 1], [0, 2]])
moves_left = moves_right * -1
moves_right_down = np.array([[1, 1], [1, 2], [2, 1], [2, 2]])
moves_right_up = moves_right_down.copy()
moves_right_up[:, 0] *= -1
moves_left_up = moves_right_up.copy()
moves_left_up[:, 1] *= -1
moves_left_down = moves_left_up.copy()
moves_left_down[:, 0] *= -1

MOVES = np.concatenate((
    moves_down, moves_up, moves_left, moves_right,
    moves_right_down, moves_right_up,
    moves_left_down, moves_left_up, [[0, 0]]
))

# Change this to None to ask to attach COM port
DEVICE = "test"

# There are 25 directions * 2 conditions = 50 trial types
# 12 trials per trial type gives 12 * 50 = 600 trials
TRIALS_PER_CONDITION = 12
TRIALS_BEFORE_BREAK = 100
INTER_INTERVAL_MIN = 1.1
INTER_INTERVAL_MAX = 1.7

MOTOR1_DURATION = .2
MOTOR2_DURATION = .2
INTER_MOTOR_INTERVAL_MIN = .05
INTER_MOTOR_INTERVAL_MAX = .05
WEAK = 30
STRONG = 100

STIMULUS_RESPONSE_INTERVAL_MIN = .1
STIMULUS_RESPONSE_INTERVAL_MAX = .1

# Display options: These only change how the motors are displayed
MIRROR_X = False
MIRROR_Y = False
REVERSE_AXES = False
DISPLAY = False
