from psychopy import event, core, visual, monitors

mon = monitors.Monitor('sponge', width=40, distance=57)
mon.setSizePix((1920, 1080))
win = visual.Window(
    winType="pyglet",
    size=(800, 600),
    monitor=mon,
    color=(-1,-1,-1),
    units='deg',
)

mouse = event.Mouse()
mouse.clickReset()

while True:
    buttons, times = mouse.getPressed(getTime=True)
    win.flip()
    core.wait(.01)
