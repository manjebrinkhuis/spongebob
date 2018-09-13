import Tkinter as tk
import serial, time
from serial import SerialException
import SPM as SPM


def main():

	# ----- Serial Port Settings -----
	#COMPort = int(raw_input("Enter COM Port: "))    # Choose serial port
	#COMPort = 4

	#test = sov.SerialSelectWindow()
	#test.mainloop()

	ser = SPM.SerialSelect()

	patterns = [SPM.Pattern() for i in range(400)]
	root = tk.Tk()
	app = SPM.PatternMakerGUI(root,patterns,ser)
	app.PressPattern(0,0)
	root.mainloop()

if __name__ == "__main__":
	main()

