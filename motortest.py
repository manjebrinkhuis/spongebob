from sponge.sponge import Sponge
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
except KeyboardInterrupt as e:
    print("Stopped by user.")
except Exception as e:
    print("Unknown error:")
    print(e)
finally:
    print("Closing down.")
    sponge.motor_off(motor=5)
    sponge.motor_off(motor=10)
    sponge.end()
    print("All closed.")
