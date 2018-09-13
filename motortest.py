from sponge import Sponge
import time

sponge = Sponge(ncols=4, nrows=4)

try:
    for i in range(100):
        sponge.start()
        sponge.motor_on(intensity=100, motor=5)
        time.sleep(1)
        sponge.motor_off(motor=5)
        time.sleep(.5)
        sponge.motor_on(intensity=100, motor=10)
        time.sleep(1)
        sponge.motor_off(motor=10)
        time.sleep(.5)
        sponge.end()
except Exeption as e:
    sponge.motor_off(motor=5)
    sponge.motor_off(motor=10)
    sponge.end()
