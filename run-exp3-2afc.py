from psychopy import visual, core, event, monitors
import numpy as np
np.seterr(divide='ignore')

import pandas as pd
from sponge.sponge import Sponge
from sponge.logger import Logger
from sponge.serialconnector import SerialConnector
from sponge.pattern import (
    parse_file, choose_file, get_difference_motor_position, create_motor_layout)

from config import (
    CENTER, MOVES, LAYOUT, TRIALS_BEFORE_BREAK,
    INTER_INTERVAL_MIN, INTER_INTERVAL_MAX,
    MOTOR1_DURATION, MOTOR2_DURATION,
    WEAK, STRONG,
    INTER_MOTOR_INTERVAL_MIN, INTER_MOTOR_INTERVAL_MAX,
    STIMULUS_RESPONSE_INTERVAL_MIN, STIMULUS_RESPONSE_INTERVAL_MAX,
    DEVICE,
    )

class Experiment():

    def __init__(
        self, win, trials,
        participant=0, condition=0, session=0,
        ntrials_to_break=TRIALS_BEFORE_BREAK
        ):

        self.win = win
        self.logger = Logger(
            prefix="exp3_",
            participant=participant,
            condition=condition,
            session=session,
        )

        self.trials = trials
        self.response = Response(win)
        self.break_stim = Break(win)
        self.ntrials_to_break = ntrials_to_break

    def close(self):
        self.win.close()

    def blank_interval(self, min, max):
        interval = (min, max)
        duration = np.random.rand() * np.diff(interval) + interval[0]
        self.win.flip()
        core.wait(duration)

    def run(self):
        while not self.trials.is_finished:

            output = self.trials.run()
            self.win.flip()

            self.blank_interval(
                STIMULUS_RESPONSE_INTERVAL_MIN, STIMULUS_RESPONSE_INTERVAL_MAX)

            resp = self.response.run()
            output = output.join(resp)

            self.logger.log(output)

            print(output)

            self.blank_interval(
                INTER_INTERVAL_MIN, INTER_INTERVAL_MAX)

            need_break = self.trials.trial_nr & ((self.trials.trial_nr % self.ntrials_to_break) == 0)
            if need_break:
                self.break_stim.run()


class Trial(object):

    def __init__(self, win, layout=LAYOUT, center=CENTER, moves=MOVES):
        self.win = win

        y, x = layout.shape
        self.sponge = Sponge(ncols=y, nrows=x, device=DEVICE)

        try:
            self.sponge.connect()
        except KeyboardInterrupt:
            print("Cancelled by user. No sponge used.")

        self.text_stim = visual.TextStim( win, text="Running sponge" )
        self.center = center
        self.layout = layout
        self.moves = MOVES
        self.motors_visual = [None, ] * (len(MOVES) + 1)

        # Create display
        for move in np.vstack((MOVES, (0,0))):
            x, y = move
            x, y = center + np.array([x, -y])
            motor = layout[y, x]
            circle = visual.Circle(win, fillColor=(0,0,0), pos=move, radius=.5)
            num = visual.TextStim(win, text=motor, pos=move, height=.5)
            self.motors_visual[motor] = {
                "circle": circle,
                "num": num
            }

    def set_move(self, move):
        self.move = move

    def set_intensity(self, first, second):
        self.intensity = (first, second)

    def draw_motors(self):
        for el in self.motors_visual:
            el["circle"].fillColor = (0,0,0)
            el["circle"].draw()
            el["num"].draw()

    def run(self):
        # First motor (central)
        x, y = self.center
        motor = self.layout[y, x]
        first, second = self.intensity

        self.sponge.start()
        self.sponge.motor_on(intensity=first, motor=motor)

        self.draw_motors()
        self.motors_visual[motor]["circle"].fillColor = (1,1,1)
        self.motors_visual[motor]["circle"].draw()
        self.win.flip()
        core.wait(MOTOR1_DURATION)

        self.sponge.motor_off(motor=motor)

        # Inter motor interval
        self.draw_motors()
        self.win.flip()

        interval = (INTER_MOTOR_INTERVAL_MIN, INTER_MOTOR_INTERVAL_MAX)
        duration = np.random.rand() * np.diff(interval) + interval[0]
        core.wait(duration)

        # Second motor
        x, y = self.move
        x, y = self.center + np.array([x, -y])
        motor = self.layout[y, x]

        self.sponge.motor_on(intensity=second, motor=motor)

        self.draw_motors()
        self.motors_visual[motor]["circle"].fillColor = (1,1,1)
        self.motors_visual[motor]["circle"].draw()
        self.win.flip()
        core.wait(MOTOR2_DURATION)

        self.sponge.motor_off(motor=motor)
        self.sponge.end()

        return motor

class Trials(Trial):
    """"""
    def __init__(self, win, trials_per_move=9, conditions=2, **kwargs):
        super(Trials, self).__init__(win, **kwargs)

        x, y = np.tile(MOVES.T, trials_per_move)

        self.trials = pd.DataFrame({
            "move_x": np.tile(x, 2),
            "move_y": np.tile(y, 2),
            "condition": [1] * len(x) + [2] * len(x)
        })
        self.trials = self.trials.loc[np.random.permutation(self.trials.index.values)]
        self.trial_nr = 0
        self.is_finished = False

    def __next__(self):
        if self.trial_nr >= len(self.trials):
            self.is_finished = True
        self.trial_nr += 1

    def run(self):
        self.set_move((
            self.trials.iloc[self.trial_nr].move_x,
            self.trials.iloc[self.trial_nr].move_y
        ))

        if self.trials.iloc[self.trial_nr].condition == 1:
            self.set_intensity(WEAK, STRONG)
        else:
            self.set_intensity(STRONG, WEAK)

        motor = super(Trials, self).run()

        output = pd.DataFrame(
            self.trials.iloc[self.trial_nr]).T
        output = (
            output
            .reset_index()
            .assign(trial_nr=self.trial_nr)
            .assign(motor=motor)
        )

        self.__next__()
        return output


class Break():
    def __init__(self, win):
        self.win = win
        self.text = visual.TextStim(win, text="Press a key to continue...")

    def run(self):
        self.text.draw()
        self.win.flip()
        event.waitKeys()
        for i in [3,2,1]:
            self.text.text = "Continue in %d..." % i
            self.text.draw()
            self.win.flip()
            core.wait(1)


class Response():

    def __init__(self, win, width=.7, length=5, wait_for_next_trial=1, color=(1,1,1)):

        self.win = win
        self.length = length
        self.width = width
        self.color = color
        self.wait_for_next_trial = wait_for_next_trial

        # Create stimulus
        self.vertices = [
            (0, -width/2),
            (0, width/2),
            (length, width/2),
            (length+width/2, 0),
            (length, -width/2)
        ]


    def run(self):

        self.win.flip()
        mouse = MouseHandler()
        mouse.setPos((0, 0))

        first_click = False
        second_click = False
        trial_has_finished = False

        self.arrow = visual.ShapeStim(
            self.win, vertices=self.vertices, lineColor=self.color, fillColor=self.color)
        self.circle = visual.Circle(
            self.win, radius=self.width/2, lineColor=self.color, fillColor=self.color)

        output = pd.DataFrame({})

        mouse.clickReset()
        while not trial_has_finished:

            x, y = mouse.getPos()

            if (x >= 0) and (y >= 0):
                a = np.arctan( y / x )
            elif (x < 0) and (y >= 0):
                a = np.pi * .5 + np.arctan( np.abs(x) / np.abs(y) )
            elif (x < 0) and (y < 0):
                a = np.pi * 1 + np.arctan( np.abs(y) / np.abs(x) )
            elif (x >= 0) and (y < 0):
                a = np.pi * 1.5 + np.arctan( np.abs(x) / np.abs(y) )

            mouse_clicked = mouse.on_click()

            if mouse_clicked:
                buttons, times = mouse_clicked

                button = buttons.index(1)
                time = times[button]

                if not first_click:
                    first_click = True
                    output = output.assign(**{
                        "first_click_button": [button],
                        "first_click_time": [time]
                    })
                else:
                    first_click = False
                    second_click = True
                    output = output.assign(**{
                        "second_click_button": [button],
                        "second_click_time": [time]
                    })

            # Show arrow after first mouse click
            # and change orientation
            if first_click:
                self.arrow.ori = -a / (2*np.pi) * 360
                self.arrow.draw()
                self.circle.draw()
                self.win.flip()

            # Stop rotating arrow after second click
            # and wait second before breaking loop
            if second_click:
                self.arrow.fillColor = (0,0,0)
                self.arrow.lineColor = (0,0,0)
                self.circle.fillColor = (0,0,0)
                self.circle.lineColor = (0,0,0)
                self.arrow.draw()
                self.circle.draw()
                self.win.flip()
                core.wait(self.wait_for_next_trial)

                return output.assign(**{
                    "arrow_ori": [self.arrow.ori]
                })

            keys = event.getKeys( keyList=["escape"] )
            if "escape" in keys:
                break

            core.wait(0.04)

        return output


class MouseHandler(event.Mouse):
    """"""
    def __init__(self, *args, **kwargs):
        super(MouseHandler, self).__init__(*args, **kwargs)
        self.state = np.array(self.getPressed())

    def on_release(self):
        pressed, times = self.getPressed(getTime=True)
        diff = np.array(pressed) - self.state
        if (diff < 0).any():
            self.state = pressed[:]
            return pressed, times
        elif (diff > 0).any():
            self.state = pressed[:]

    def on_click(self):
        pressed, times = self.getPressed(getTime=True)
        diff = np.array(pressed) - self.state
        if (diff > 0).any():
            self.state = pressed[:]
            return pressed, times
        elif (diff < 0).any():
            self.state = pressed[:]


def main():
    mon = monitors.Monitor('sponge', width=40, distance=57)
    mon.setSizePix((1920, 1080))

    win = visual.Window(
        winType="pyglet",
        size=(800, 600),
        monitor=mon,
        color=(-1,-1,-1),
        units='deg',
    )

    trials = Trials(win, layout=LAYOUT, center=CENTER, moves=MOVES)
    exp = Experiment(win, trials)

    exp.run()

if __name__ == "__main__":
    main()
