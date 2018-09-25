from sponge.serialconnector import SerialConnector
from sponge.pattern import parse_file, choose_file, get_difference_motor_position
from sponge.logger import Logger
from sponge.sponge import Sponge
from psychopy import visual, core, event
import csv
import pandas as pd
import numpy as np
import os
from collections import OrderedDict

# Constants
use_keys = ["up", "down", "left", "right"]
# use_keys = ["up", "down"]

# Arrow characters
# left_arrow_char = u"\u2190"
# up_arrow_char = u"\u2191"
# right_arrow_char = u"\u2192"
# down_arrow_char = u"\u2193"

# ----
# Logging the data to a file
# ----

logger = Logger(location="./data")

# ----
# Setup Sponge
# ----

sponge = Sponge(ncols=4, nrows=4, device='/dev/ttyACM0')
sponge.connect()

# ----
# Setup Psychopy
# ----

win = visual.Window(winType="pyglet")
txt_base = """
Current trial {trial_number}.
Respond with {first_keys}, or {last_key}.
"""

# Create text stimulus
t = visual.TextStim(win, "", height=.04)

# ----
# Load sequence
# ----

# Create the path to the file that contains the trials
source = "./source"
fname = choose_file(source)
path = os.path.join(source, fname)

# And parse that file, using the parse_file
# function in the "pattern" module.
parsed = parse_file(path, delimiter=",")

# Convert the parsed file, which is a
# "list" of "dictionaries" that contain
# trial information per pattern,
# to a pandas dataframe.
trials = pd.DataFrame(parsed)
trials.rename(columns={
    "col0": "block",
    "col1": "trial"
}, inplace=True)

# Convert strings to integers
trials.block = trials.block.astype(int)
trials.trial = trials.trial.astype(int)

# Leave out the first block
block0 = trials[trials.block==0]
trials = trials[trials.block!=0]

# ----
# Go through sequence of patterns
# ----

# Empty keyboard presses
event.clearEvents()

# We can group the pandas DataFrame instance
# by block and by trial (within that block).
# In that way we go through the trials,
# which are groups of patterns, one by one,
# one block at a time, and this allows us to
# define easily what to do on each trial and
# on each block (e.g. introduce a break)
for block_num, block in trials.groupby("block"):
    # Update the text with current pattern and the used keys.
    # And put things on the display
    t.text = "Press a key when ready."
    t.draw()
    win.flip()

    # Randomize trial order
    idx = block.groupby("trial").first().index
    block = block.set_index("trial").loc[np.random.permutation(idx)].reset_index()

    # Then wait for a user response
    # to start experiment
    event.waitKeys()

    # Then wait for the duration given in block 0
    core.wait(block0.iloc[0]["duration"] / 1000.0)

    for real_trial_num, (trial_num, trial) in enumerate(block.groupby("trial", sort=False)):

        print("--------")
        print(trial)

        # Extract the correct response
        # from the motor direction.
        if int(block_num) > 0:
            m0 = trial.iloc[0].motors[0]
            m1 = trial.iloc[2].motors[0]
            move_x, move_y = get_difference_motor_position(m0, m1)

        # Update the text with current pattern and the used keys.
        t.text = txt_base.format(
            trial_number=real_trial_num,
            first_keys=", ".join(use_keys[:-1]),
            last_key=use_keys[-1])

        # Put things on the display
        t.draw()
        win.flip()

        # Now go through all patterns in the
        # current trial.
        for idx in trial.index:
            pattern = trial.loc[idx]
            onset = core.getTime()

            # Turn the motor(s) on
            sponge.start()
            for motor in sponge.motors:
                if motor in pattern["motors"]:
                    idx = pattern["motors"].index(motor)
                    intensity = pattern["intensities"][idx]
                    sponge.motor_on(motor, intensity)
            sponge.end()

            # Convert pattern milliseconds to seconds.
            secs = pattern["duration"] / 1000.0

            # Wait seconds, hog CPU to acquire accurate response times.
            core.wait(secs, hogCPUperiod=secs)

            # Turn the motor off
            sponge.start()
            for motor in sponge.motors:
                if motor in pattern["motors"]:
                    sponge.motor_off(motor)
            sponge.end()

            offset = core.getTime()

            # Collect keys pressed during patterns
            keys_pressed = event.getKeys(use_keys + ["escape"], timeStamped=True)

            # If not response was pressed. Log pattern,
            # anyway, with keys_pressed = [(None, None)]
            if not keys_pressed:
                keys_pressed = [(None, None)]

            # Log each key pressed with the pattern info.
            for key, ts in keys_pressed:
                output = OrderedDict({
                    "block"     : block_num,
                    "real_trial": real_trial_num,
                    "trial"     : trial_num,
                    "move_x"    : move_x,
                    "move_y"    : move_y, # 1 means down, -1 means up
                    "pattern"   : [pattern["number"]],
                    "duration"  : [pattern["duration"]],
                    "motors"    : [",".join([str(v) for v in pattern["motors"]])],
                    "intensities": [",".join([str(v) for v in pattern["intensities"]])],
                    "onset"     : [round(onset*1000, 2)],
                    "offset"    : [round(offset*1000, 2)],
                    "key"       : [key],
                    "timestamp" : [None if ts is None else round(ts*1000, 2)],
                })

                # The logger takes care of logging to file.
                logger.log(output)

                # Show what's happened
                print("Key pressed: %s" % str(key))

        # If someone pressed escape, we should break the loop.
        if "escape" in zip(*keys_pressed)[0]:
            break

    # If someone pressed escape, we should break the loop.
    if "escape" in zip(*keys_pressed)[0]:
        break

# Clean up
sponge.close()
win.close()
