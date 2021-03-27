from tkinter import *
from math import floor
import json
import pip

def pinstall(package):
    pip.main(['install', package])

try:
    from fixedint import Int64, Int32
except:
    pinstall("fixedint")
    from fixedint import Int64, Int32

def convBinary(x, bits):
    x = bin(x)[2:]
    if x[0] == "b":
        return getComplement(x[1:], bits)
    else:
        return x

def getComplement(x, bits):
    xLen = len(x)
    for i in range(bits - xLen):
        x = "0" + x
    x = list(x)
    for i in range(bits):
        if x[bits - i - 1] == "1":
            x[bits - i - 1] = "0"
        else:
            x[bits - i - 1] = "1"
    for i in range(bits):
        if x[bits - i - 1] == "1":
            x[bits - i - 1] = "0"
        else:
            x[bits - i - 1] = "1"
            break
    rtnstr = ""
    for i in x:
        rtnstr = rtnstr + i
    return rtnstr

def rUShift32(x):
    if x >= 0:
        return x >> 32
    else:
        e = convBinary(x, 64)
        if len(e) > 32:
            return int(e[:32], 2)
        else:
            return x

def isRandom(worldSeed):
    a = Int64(worldSeed)
    b = Int64(18218081)
    c = Int64(1) << 48
    d = Int64(7847617)
    e = ((((d * ((rUShift32(a) * 24667315 + b * Int32(a) + 67552711) >> 32) - b * ((-4824621 * rUShift32(a) + d * Int32(a) + d) >> 32)) - 11) * Int64(0xdfe05bcb1365)) % c)
    return ((((Int64(0x5deece66d) * e + 11) % c) >> 16) << 32) + Int32(((Int64(0xbb20b4600a69) * e + Int64(0x40942de6ba)) % c) >> 16) == a

# thanks to DuncanRuns for isRandom and its dependencies

def str_time(seconds, milliseconds = 0):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours != 0:
        return "{0}:{1:0>2}:{2:0>2}.{3:0>3}".format(hours, minutes, seconds, milliseconds)
    elif minutes != 0:
        return "{0}:{1:0>2}.{2:0>3}".format(minutes, seconds, milliseconds)
    elif seconds != 0:
        return "{0}.{1:0>3}".format(seconds, milliseconds)
    else:
        return "0.{0:0>3}".format(milliseconds)

class VerifClient:
    def __init__(self, log_func = print):
        self.log_func = log_func
        
        self.window = Tk()
        self.window.title("VerifClient v2.2")
        self.window.wm_attributes("-topmost", 1)

        Label(self.window, text = "Rejection Messages").grid(row = 0, column = 0, columnspan = 7)
        Label(self.window, text = " ").grid(row = 1,column = 0)
        Button(self.window, text = "Seed", command = self.copy_seed, width = 7).grid(row = 1, column = 1)
        Button(self.window, text = "Optifine", command = self.copy_optifine).grid(row = 1, column = 2)
        Button(self.window, text = "NaLiP", command = self.copy_nalip).grid(row = 1, column = 3)
        Button(self.window, text = "F3/Title", command = self.copy_f3).grid(row = 1, column = 4)
        Button(self.window, text = "Create", command = self.copy_create).grid(row = 1, column = 5)
        Label(self.window, text = "  ").grid(row = 1, column = 6)
        Button(self.window, text = "Sub 20", command = self.copy_files).grid(row = 2, column = 2, sticky = 'news')
        Button(self.window, text = "VOD", command = self.copy_vod).grid(row = 2, column = 3, sticky = 'news')
        Button(self.window, text = "Dupe", command = self.copy_duplicate).grid(row = 2, column = 4, sticky = 'news')

        Label(self.window, text = "").grid(row = 3,column = 0)

        Label(self.window, text = "Retiming").grid(row = 4, column = 0, columnspan = 7)

        Label(self.window, text = "Framerate").grid(row = 5, column = 2, columnspan = 2)
        self.fps_field = Entry(self.window, width = 5, justify = CENTER)
        self.fps_field.grid(row = 5, column = 4)

        Label(self.window, text = "Start").grid(row = 6, column = 1)
        self.start_field = Entry(self.window, width = 20)
        self.start_field.grid(row = 6, column = 2, columnspan = 3)
        self.start_time = Label(self.window, text = "0.000")
        self.start_time.grid(row = 6, column = 5)

        Label(self.window, text = "End").grid(row = 7, column = 1)
        self.end_field = Entry(self.window, width = 20)
        self.end_field.grid(row = 7, column = 2, columnspan = 3)
        self.end_time = Label(self.window, text = "0.000")
        self.end_time.grid(row = 7,column = 5)

        Button(self.window, text = "Calculate", command = self.calculate_time).grid(row = 8, column = 1)
        self.final_time = Label(self.window, text = "0.000")
        self.final_time.grid(row = 8, column = 2, columnspan = 3)
        Button(self.window, text = "Clear", command = self.reset_time_fields).grid(row = 8, column = 5)

        Label(self.window, text = "").grid(row = 9, column = 0)
        Label(self.window, text = "Seed Tester").grid(row = 10, column = 0, columnspan = 7)
        self.seed_field = Entry(self.window, width = 25)
        self.seed_field.grid(row = 11, column = 1, columnspan = 5)
        Button(self.window, text = "Test", command = self.seed_field_test, width = 7).grid(row = 12, column = 1)
        self.seed_result = Label(self.window, width = 15, text = "-")
        self.seed_result.grid(row = 12, column = 2, columnspan = 3)
        Button(self.window, text = "Clear", command = self.reset_seed_field).grid(row = 12, column = 5)

        self.window.mainloop()

    def copy(self, text):
        self.window.clipboard_clear()
        self.window.clipboard_append(text)

    def copy_seed(self):
        self.copy("The world seed is required in the run description. " \
                  "Please resubmit with the seed in the run description.")

    def copy_optifine(self):
        self.copy("Optifine is not allowed for versions 1.16 and up.")

    def copy_nalip(self):
        self.copy("Run was submitted as Vanilla but title screen indicates mods were used. " \
                  'If allowed mods (full list in the rules) were used, resubmit as "CaffeineMC"; ' \
                  "mods not in the list are not allowed.")

    def copy_f3(self):
        self.copy("F3/title screen not shown.")

    def copy_create(self):
        self.copy("You must show the world being created from the world selection screen.")

    def copy_vod(self):
        self.copy("VODs are not permanent. Please resubmit with a permanent video.")

    def copy_files(self):
        self.copy("Sub 20 runs require a download link for the world file in the run description. " \
                  "Please resubmit with such a link in the run description.")

    def copy_duplicate(self):
        self.copy("Duplicate submission. Your run is still in the queue.")

    def calculate_time(self):
        try:
            fps = int(self.fps_field.get())
            
            startframe = floor(float(json.loads(self.start_field.get())['cmt']) * fps)
            endframe = floor(float(json.loads(self.end_field.get())['cmt']) * fps)
            
            self.start_time.configure(text = str(round(startframe / fps, 3)))
            self.end_time.configure(text = str(round(endframe / fps, 3)))
            
            duration = endframe - startframe
            seconds, frames = divmod(duration, fps)
            milliseconds = round(frames / fps * 1000)

            self.final_time.configure(text = str_time(seconds, milliseconds))
            self.final_time.configure(bg = 'SystemButtonFace')
        except Exception as e:
            self.final_time.configure(text = "Error, check console")
            self.final_time.configure(bg = 'yellow2')
            self.log_func(f"Error: {e}")

    def reset_time_fields(self):
        self.end_field.delete(0, END)
        self.start_field.delete(0, END)

    def seed_field_test(self):
        try:
            if isRandom(int(self.seed_field.get())):
                self.seed_result.configure(text = "Valid")
                self.seed_result.configure(bg = 'SpringGreen3')
            else:
                self.seed_result.configure(text = "Invalid")
                self.seed_result.configure(bg = 'IndianRed1')
        except Exception as e:
            self.seed_result.configure(text = "Error, check console")
            self.seed_result.configure(bg = 'yellow2')
            self.log_func(f"Error: {e}")

    def reset_seed_field(self):
        self.seed_field.delete(0, END)
        self.seed_result.configure(text = "-")
        self.seed_result.configure(bg = 'SystemButtonFace')

if __name__ == '__main__':
    client = VerifClient()
