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
    moves_left_down, moves_left_up
))

DEVICE = None

TRIALS_BEFORE_BREAK = 80
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

MIRROR_X = False
MIRROT_Y = False
