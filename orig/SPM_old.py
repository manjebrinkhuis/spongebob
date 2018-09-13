import Tkinter as tk
import serial, time
from serial import SerialException
import sys
import glob

def ListSerialPorts():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def SerialSelect():


	def PressCancel():
		root.destroy()

	def DoubleClick(event):
		port.set(SerialList.get(SerialList.curselection()))
		is_serial.set(True)
		root.destroy()

	ports = ListSerialPorts()

	if ports == []:
		return None

	root = tk.Tk()
	root.title("Select Serial Port")
	root.configure(padx=5, pady=5)
	container = tk.Frame(root)
	container.pack()


	port = tk.StringVar()
	is_serial = tk.BooleanVar()

	SerialList = tk.Listbox(root)
	SerialList.bind("<Double-Button-1>", DoubleClick)

	for item in ports:
		SerialList.insert(0,item)

	SerialList.pack()

	CancelBtn = tk.Button(root, text="Cancel", command=PressCancel)

	CancelBtn.pack()

	root.mainloop()

	if is_serial.get() == True:
		ser = serial.Serial(port.get(),115200)
		time.sleep(2)  # at least 2 sec delay
		return ser
	else:
		return None

def LoadPattern(FileName):
	print "TODO"


class Pattern:
	def __init__(self):
		self.status = ["OFF" for i in range(64)]
		self.intensity = [0 for i in range(64)]
		self.duration = 0
		self.count = 0

	def WriteStatus(self,number,value):
		self.status[number] = value

	def WriteIntensity(self,number,value):
		self.intensity[number] = value

	def WriteDuration(self,value):
		self.duration = value

	def WriteCount(self,value):
		self.count = value

	def IncreaseCount(self):
		self.count += 1

	def DecreaseCount(self):
		self.count -= 1

	def GetStatus(self, select):
		if self.status[select] == "ON":
			return 1
		else: 
			return 0

	def GetIntensity(self, select):
		return self.intensity[select]

	def GetDuration(self):
		return self.duration

	def GetCount(self):
		return self.count

	def ZeroCount(self):
		self.count = 0

	def Reset(self):
		self.status = ["OFF" for i in range(64)]
		self.intensity = [0 for i in range(64)]
		self.duration = 0
		self.count = 0

	def PrintPattern(self):
		print self.status
		print self.intensity
		print self.duration
		print self.count

class PatternMakerGUI():

	def __init__(self, master, patterns, ser=None):

		self.master = master
		self.patterns = patterns

		if ser:
			self.ser = ser
			self.is_serial = True
		else:
			self.is_serial = False

		self.current_erm = 0
		self.current_pattern = 0
		self.previous_pattern = -1
		self.current_button = [0,0]
		copy_pattern = patterns[0]

		# ----- Master Configuration -----
		self.master.title("Haptic Vest Pattern Maker")
		self.master.configure(padx=5, pady=5)

		# ----- Defined colors -----
		self.button_default_color = "turquoise"
		self.button_selected_color = "White"
		self.pattern_button_default_color = "light sky blue"
		self.pattern_button_selected_color = "yellow"

		# ----- Positioning variables -----
		self.upadx = 2
		self.upady = 2
		self.btn_h = 1
		self.btn_w = 15

		# ----- Number of patterns -----
		self.patterns_x = 22		
		self.patterns_y = 4

		# ----- Number of buttons -----
		self.erms_x = 4
		self.erms_y = 4

		# ----- Main Frame -----
		self.frame = tk.Frame(master)
		self.frame.pack()

		menubar = tk.Menu(self.master)

		# create a pulldown menu, and add it to the menu bar
		filemenu = tk.Menu(menubar, tearoff=0)
		filemenu.add_command(label="Set Default Directory", command=self.hello)
		#filemenu.add_command(label="Save", command=self.hello)
		filemenu.add_separator()
		filemenu.add_command(label="Exit", command=self.master.quit)
		menubar.add_cascade(label="File", menu=filemenu)

		# create more pulldown menus
		editmenu = tk.Menu(menubar, tearoff=0)
		editmenu.add_command(label="Cut", command=self.hello)
		editmenu.add_command(label="Copy", command=self.hello)
		editmenu.add_command(label="Paste", command=self.hello)
		menubar.add_cascade(label="Edit", menu=editmenu)

		helpmenu = tk.Menu(menubar, tearoff=0)
		helpmenu.add_command(label="About", command=self.hello)
		menubar.add_cascade(label="Help", menu=helpmenu)
		

		# display the menu
		self.master.config(menu=menubar)

		# ----- Power Entry Option -----
		self.PowerFrame = tk.LabelFrame(self.frame, text="Power [0-255]")
		self.PowerFrame.grid(column=8, row=0, padx=self.upadx, pady=self.upady)
		self.PowerEntry = tk.Entry(self.PowerFrame, text="Power", width=self.btn_w)
		self.PowerEntry.bind("<Return>",lambda event: self.ReturnKey("intensity"))
		self.PowerEntry.grid(column=9,sticky="N",padx=self.upadx, pady=self.upady)
		self.PowerEntry.insert(0,"0")

		# ----- Pattern Duration Option -----
		self.DurationFrame = tk.LabelFrame(self.frame, text="Pattern Duration [ms]")
		self.DurationFrame.grid(column=8, row=1, padx=self.upadx, pady=self.upady)
		self.DurationEntry = tk.Entry(self.DurationFrame, text="Duration", width=self.btn_w)
		self.DurationEntry.bind("<Return>",lambda event: self.ReturnKey("duration"))
		self.DurationEntry.grid(sticky="N",padx=self.upadx, pady=self.upady)	
		self.DurationEntry.insert(0,"0")

		# ----- Command Frame -----
		self.CommandFrame = tk.LabelFrame(self.frame, text="Commands")
		self.CommandFrame.grid(column=8, row=3, rowspan=5, padx=self.upadx, pady=self.upady)

		# ----- Clear All Button -----
		self.ClearAllerm_btn = tk.Button(self.CommandFrame, text="Clear All", height=self.btn_h, width=self.btn_w, command=self.PressClearAll)
		self.ClearAllerm_btn.grid(row=3, column=9, sticky="S", padx=self.upadx, pady=self.upady)

		# ----- Next Pattern Button
		self.NextPatternerm_btn = tk.Button(self.CommandFrame, text="Next Pattern", height=self.btn_h, width=self.btn_w, command=self.PressNextPattern)
		self.NextPatternerm_btn.grid(row=4, column=9, sticky="S", padx=self.upadx, pady=self.upady)
		self.master.bind("<Left>", self.LeftKey)

		# ----- Previous Pattern Button -----
		self.PreviousPatternerm_btn = tk.Button(self.CommandFrame, text="Previous Pattern", height=self.btn_h, width=self.btn_w, command=self.PressPreviousPattern)
		self.PreviousPatternerm_btn.grid(row=5, column=9, sticky="S", padx=self.upadx, pady=self.upady)
		self.master.bind("<Right>",self.RightKey)

		# ----- Load Pattern Button -----
		self.LoadPatternerm_btn = tk.Button(self.CommandFrame, text="Load Pattern File", height=self.btn_h, width=self.btn_w, command=self.PressLoadPatternFile)
		self.LoadPatternerm_btn.grid(row=6, column=9, sticky="S",padx=self.upadx, pady=self.upady)

		# ----- New Pattern File Button -----
		self.NewPatternFile_btn = tk.Button(self.CommandFrame, text="New Pattern File", height=self.btn_h, width=self.btn_w, command=self.PressNewPatternFile)
		self.NewPatternFile_btn.grid(row=7, column=9, sticky="S", padx=self.upadx, pady=self.upady)

		# Save Pattern File Button -----
		self.SavePatternFile_btn = tk.Button(self.CommandFrame, text="Save Pattern File", height=self.btn_h, width=self.btn_w, command=self.PressSavePatternFile)
		self.SavePatternFile_btn.grid(row=8, column=9, sticky="S", padx=self.upadx, pady=self.upady)

		# ----- Copy Pattern Button -----
		self.CopyPattern_btn = tk.Button(self.CommandFrame, text="Copy Pattern", height=self.btn_h, width=self.btn_w, command=self.PressCopyPattern)
		self.CopyPattern_btn.grid(row=9, column=9, sticky="S", padx=self.upadx, pady=self.upady)

		# ----- Paste Pattern Button -----
		self.PastePattern_btn = tk.Button(self.CommandFrame, text="Paste Pattern", height=self.btn_h, width=self.btn_w, command=self.PressPastePattern)
		self.PastePattern_btn.grid(row=10, column=9, sticky="S", padx=self.upadx, pady=self.upady)

		# ----- Matrix Frame -----
		self.MatrixFrame = tk.LabelFrame(self.frame, text="ERM Write Matrix")
		self.MatrixFrame.grid(column=0, row=0, columnspan=8, rowspan=8, padx=self.upadx, pady=self.upady)

		# ---- Matrix of buttons each representing corresponing ERM
		self.erm_btn =  [[0 for i in xrange(self.erms_x)] for j in xrange(self.erms_y)] 
		for y in range(self.erms_y):
			for x in range(self.erms_x):
				self.erm_btn[y][x] = tk.Button(self.MatrixFrame, text="%d \n %d" %(x+y*self.erms_x, 0), bg=self.button_default_color, height=5, width=10, command=lambda x=x, y=y: self.MatrixButtonPress(x,y))
				self.erm_btn[y][x].grid(column=x, row=y, padx=self.upadx, pady=self.upady)

		# ----- Playback Frame -----
		self.PlayBackFrame = tk.LabelFrame(self.frame, text="Playback")
		self.PlayBackFrame.grid(column=0, row=8, columnspan=10, rowspan=1, padx=self.upadx, pady=self.upady)

		# ----- Play Button -----
		self.Playbtn = tk.Button(self.PlayBackFrame, text="Play", height=self.btn_h, width=self.btn_w, command=lambda master=self.master: self.PlayPattern(master))
		self.Playbtn.grid(row=0, column=0, sticky="S", padx=self.upadx, pady=self.upady)

		# ----- Stop Button -----
		self.Stopbtn = tk.Button(self.PlayBackFrame, text="Stop", height=self.btn_h, width=self.btn_w, command=self.StopPattern)
		self.Stopbtn.grid(row=0, column=1, sticky="S", padx=self.upadx, pady=self.upady)

		# ----- Pattern Frame -----
		self.PatternFrame = tk.LabelFrame(self.frame, text="Patterns")
		self.PatternFrame.grid(column=0, row=9, columnspan=10, rowspan=2, padx=self.upadx, pady=self.upady)

		# ----- Pattern Matrix -----
		self.pattern_btn =  [0 for x in xrange(self.patterns_y*self.patterns_x)]
		for y in range(self.patterns_y):
		     for x in range(self.patterns_x):
		        self.pattern_btn[x+y*self.patterns_x] = tk.Button(self.PatternFrame, text="", bg="light sky blue", height=1, width=1, state="normal", relief="flat", command=lambda x=x, y=y: self.PressPattern(x,y))
		        self.pattern_btn[x+y*self.patterns_x].grid(column=x, row=y, padx=self.upadx, pady=self.upady)
			
	def hello(self):
	    print "hello!"

	# ----- TODO -----	        
	def ReturnKey(self,function):

		if function == "intensity":
			x = self.current_button[0]
			y = self.current_button[1]
			temp_intensity = int(self.PowerEntry.get())
			self.patterns[self.current_pattern].WriteIntensity(self.current_erm, temp_intensity)
			self.erm_btn[y][x].configure(text="%d \n %d" %(x+y*self.erms_x, temp_intensity))

		elif function == "duration":
			x = self.current_button[0]
			y = self.current_button[1]
			temp_duration = int(self.DurationEntry.get())
			self.patterns[self.current_pattern].WriteDuration(temp_duration)
			self.pattern_btn[self.current_pattern].configure(text="%d" % temp_duration)

	# ----- TODO -----
	def PressClearAll(self):
		x = self.current_button[0]
		y = self.current_button[1]

		for y in range(self.erms_y):
			for x in range(self.erms_x):
				self.patterns[self.current_pattern].WriteStatus(x+y*self.erms_x,"OFF")
				self.patterns[self.current_pattern].WriteIntensity(x+y*self.erms_x,0)
				self.erm_btn[y][x].configure(bg=self.button_default_color, text="%d \n %s" % (x+y*self.erms_x, ""))
				self.patterns[self.current_pattern].ZeroCount()
		self.pattern_btn[self.current_pattern].configure(text="", bg=self.pattern_button_default_color)
		self.patterns[self.current_pattern].WriteDuration(0)

	# ----- TODO -----
	def PressNextPattern(self):
		self.pattern_btn[self.current_pattern].configure(bg=self.pattern_button_default_color) 

		if self.current_pattern < self.patterns_x*self.patterns_y-1:
			self.previous_pattern = self.current_pattern
			self.current_pattern += 1

		self.pattern_btn[self.current_pattern].configure(bg=self.pattern_button_selected_color)
		self.RecallPattern()

	# ----- TODO -----
	def PressPreviousPattern(self):
		self.pattern_btn[self.current_pattern].configure(bg=self.pattern_button_default_color) 

		if self.current_pattern > 0:
			self.previous_pattern = self.current_pattern
			self.current_pattern -= 1

		self.pattern_btn[self.current_pattern].configure(bg=self.pattern_button_selected_color)
		self.RecallPattern()

	# ----- TODO -----
	def PressLoadPatternFile(self):
		def LoadFile():
			FileName = LoadEntry.get()
			text_file = open("%s.txt" % FileName)
			string_file = text_file.read()

			self.PressNewPatternFile()

			i = 0
			j = 0
			k = 0
			l = 0
			temp_duration = ""
			temp_count = ""
			temp_select = ""
			temp_intensity = ""

			while string_file[i] != "x":
				if string_file[i] == "P":

					i = i + 6
					while string_file[i] != " ":
						temp_duration += string_file[i]
						i += 1
					#print temp_duration
					self.patterns[j].WriteDuration(int(temp_duration))
					temp_duration = ""

					i = i + 4
					while string_file[i] != " ":
						temp_count += string_file[i]
						i += 1
					#print temp_count
					self.patterns[j].WriteCount(int(temp_count))
					temp_count = ""

					i = i + 4
					while string_file[i] != "I":
						while string_file[i] != " ":
							temp_select += string_file[i] 
							i += 1
						#print temp_select
						self.patterns[j].WriteStatus(int(temp_select), "ON")
						temp_select = ""
						i += 1

					i = i + 3
					while string_file[i] != "\n":
						while string_file[i] != " ":
							temp_intensity += string_file[i] 
							i += 1
						print temp_intensity


						while self.patterns[j].GetStatus(k) == 0:
							k += 1
							if k == 64:
								print "break"
								break
						self.patterns[j].WriteIntensity(k, int(temp_intensity))
						print k
						k += 1


						temp_intensity = ""
						i += 1
				self.patterns[j].PrintPattern()
				print "\n"

				i += 1
				j += 1
				k = 0

			for i in range(self.patterns_x*self.patterns_y):
				self.current_pattern = i
				print self.patterns[self.current_pattern].GetDuration()
				self.pattern_btn[self.current_pattern].configure(text="%d" % self.patterns[self.current_pattern].GetDuration())
				self.RecallPattern()

			self.current_pattern = 0
			self.PressPattern(0,0)
			text_file.close()
			LoadEntry.delete(0,"end")
			LoadWindow.destroy()

		def PressReturn(event):
			LoadFile()

		LoadWindow = tk.Toplevel()
		LoadWindow.title("Load Pattern File")
		LoadWindow.bind("<Return>", PressReturn)
		LoadEntry = tk.Entry(LoadWindow, text="Enter file name")
		LoadEntry.insert(0,"")
		LoadEntry.grid(row=0, column=0)
		LoadButton = tk.Button(LoadWindow, text="Load", height=self.btn_h, width=self.btn_w, command=LoadFile)
		LoadButton.grid(row=0, column=1)

	# ----- TODO -----
	def PressNewPatternFile(self):
		for i in range(self.patterns_x*self.patterns_y):
			self.current_pattern = i
			self.PressClearAll()
		self.current_pattern = 0


	# ----- TODO -----
	def PressSavePatternFile(self):
		def SaveFile():
			FileName = SaveEntry.get()
			text_file = open("%s.txt" % FileName, "w")

			for i in range (self.patterns_x*self.patterns_y):
				if self.patterns[i].GetCount() > 0 or self.patterns[i].GetDuration() > 0:
					text_file.write("P%d D%d %d E%d %d " % (i, i, self.patterns[i].GetDuration(), i, self.patterns[i].GetCount()))
					text_file.write("S%d " % i)
					for j in range(64):
						if self.patterns[i].GetStatus(j) == 1:
							text_file.write("%d " % j)
					text_file.write("I%d " % i)
					for j in range(64):
						if self.patterns[i].GetStatus(j) == 1:
							text_file.write("%d " % self.patterns[i].GetIntensity(j))
					text_file.write("\n")
			text_file.write("x")				
			text_file.close()
			SaveEntry.delete(0,"end")
			SaveWindow.destroy()

		def PressReturn(event):
			SaveFile()

		SaveWindow = tk.Toplevel()
		SaveWindow.title("Save Pattern File")
		SaveWindow.bind("<Return>", PressReturn)
		SaveEntry = tk.Entry(SaveWindow, text="Enter file name")
		SaveEntry.insert(0,"")
		SaveEntry.grid(row=0, column=0)
		SaveButton = tk.Button(SaveWindow, text="Save", height=self.btn_h, width=self.btn_w, command=SaveFile)
		SaveButton.grid(row=0, column=1)

	# ----- TODO -----
	def PressCopyPattern(self):
		self.copy_pattern = self.patterns[self.current_pattern] 

	# ----- TODO -----
	def PressPastePattern(self):
		self.patterns[self.current_pattern] = self.copy_pattern
		temp_duration = self.patterns[self.current_pattern].GetDuration()
		self.patterns[self.current_pattern].WriteDuration(temp_duration)

		self.pattern_btn[self.current_pattern].configure(text="%d" % temp_duration)
		self.RecallPattern()

	# ----- TODO -----
	def RightKey(self,event):
		self.PressNextPattern()

	# ----- TODO -----
	def LeftKey(self,event):
		self.PressPreviousPattern()

	# ----- TODO -----
	def MatrixButtonPress(self,x,y):

		self.current_erm = x+y*self.erms_x
		self.current_button = [x,y]

		if self.erm_btn[y][x].cget("bg") == self.button_default_color:
			self.erm_btn[y][x].configure(bg=self.button_selected_color)

			self.patterns[self.current_pattern].WriteStatus(self.current_erm,"ON")
			self.patterns[self.current_pattern].IncreaseCount()
		else:
			self.erm_btn[y][x].configure(bg=self.button_default_color)
			self.patterns[self.current_pattern].WriteStatus(self.current_erm,"OFF")
			self.patterns[self.current_pattern].DecreaseCount()

	# ----- TODO -----
	def PlayPattern(self,master):
		if self.is_serial == True:
			for i in range(self.current_pattern,self.patterns_x*self.patterns_y):
				if(self.patterns[i].GetDuration() > 0):		
					self.ser.write(chr(200))
					print "START"
					#self.ser.write(chr(self.patterns[i].GetCount()*2))		
					for j in range(0,self.erms_x*self.erms_y):
						if self.patterns[i].GetStatus(j) == 1:
							self.ser.write(chr(j))
							print j
							self.ser.write(chr(self.patterns[i].GetIntensity(j)))
							print self.patterns[i].GetIntensity(j)	
					self.ser.write(chr(255))
					print "STOP"		
					time.sleep(float(self.patterns[i].GetDuration())/1000.0)	
					self.PressNextPattern()
					master.update()
					self.ResetERM()
			time.sleep(0.5)		
			self.PressPattern(0,0)
		else:
			for i in range(self.current_pattern,self.patterns_x*self.patterns_y):
				if(self.patterns[i].GetDuration() > 0):		
					time.sleep(float(self.patterns[i].GetDuration())/1000.0)	
					self.PressNextPattern()
					master.update()
			time.sleep(0.5)		
			self.PressPattern(0,0)

	# ----- TODO -----
	def StopPattern(self):
		print "TODO"

	# ----- TODO -----
	def PressPattern(self,x,y):
		self.pattern_btn[self.current_pattern].configure(bg=self.pattern_button_default_color) 

		self.current_pattern = x+y*self.patterns_x
		self.pattern_btn[self.current_pattern].configure(bg=self.pattern_button_selected_color)
		self.RecallPattern()

	# ----- TODO -----
	def RecallPattern(self):
		for y in range(self.erms_y):
			for x in range(self.erms_x):
				if self.patterns[self.current_pattern].GetStatus(x+y*self.erms_x) == 1:
					self.erm_btn[y][x].configure(bg=self.button_selected_color)
					self.erm_btn[y][x].configure(text="%d \n %d" % (x+y*self.erms_x, self.patterns[self.current_pattern].GetIntensity(x+y*self.erms_x)))
				else:
					self.erm_btn[y][x].configure(bg=self.button_default_color)
					self.erm_btn[y][x].configure(text="%d \n %s" %(x+y*self.erms_x, ""))

	def ResetERM(self):
		self.ser.write(chr(200))
		for i in range(self.erms_x*self.erms_y):
			self.ser.write(chr(i))
			self.ser.write(chr(0))
		self.ser.write(chr(255))

