#!/usr/bin/env python3

# Modbus things
import sys
import serial
import minimalmodbus
import time 

# debug
import random

# Gui and calculations things
# import queue
# import threading
import numpy
from numpy import nan
import tkinter
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib import style
import matplotlib.dates as mdates
# from psutil import cpu_percent
from datetime import datetime, timedelta




LARGE_FONT = ("Verdana", 12)
style.use("ggplot")

pressureList = [0]
Debug = None


if sys.argv[1:]:   # test if there are atleast 1 argument (beyond [0])
    arg = sys.argv[1]
else:
    arg = "None"

class Pressureapp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        #tk.Tk.iconbitmap(self, default="iconimage_kmeans.ico") #Icon for program
        tk.Tk.wm_title(self, "Измерение давлениия v0.2")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, GraphPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(GraphPage)


        # self.protocol("WM_DELETE_WINDOW", self.on_closing())

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    # def on_closing(self):
    #     if messagebox.askokcancel("Выход", "Закрыть программу?"):
    #         self.destroy()

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)


        self.labelCurP_var=tk.StringVar()
        self.labelMaxP_var=tk.StringVar()

        label = tk.Label(self, text="Давление разрушения", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        self.labelCurP = tk.Label(self, textvariable=self.labelCurP_var)
        self.labelCurP.pack()
        self.labelCurP_var.set("Нажмите кнопку для начала измерений")

        self.labelMaxP = tk.Label(self, text="Нажмите кнопку для начала измерений")
        self.labelMaxP.pack()

        # button = tk.Button(self, text="Начать измерения", command=buttonClick)
        # button.pack()

        button3 = ttk.Button(self, text="Показать график",
                             command=lambda: controller.show_frame(GraphPage))
        button3.pack(fill='x')

        def new_text(self, message):
                    self.labelCurP_var.set(message)

class GraphPage(tk.Frame):

    def __init__(self, parent, controller, nb_points=360):
        tk.Frame.__init__(self, parent)

        self.Start = False

        label = tk.Label(self, text="Давление разрушения", font=LARGE_FONT)
        label.pack(pady=10, padx=10, side='top')

        self.labelCurP = tk.Label(self, text="Нажмите кнопку для начала измерений")
        self.labelCurP.pack()

        self.labelMaxP = tk.Label(self, text="Нажмите кнопку для начала измерений")
        self.labelMaxP.pack()

        # matplotlib figure
        self.figure = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        # format the x-axis to show the time
        myFmt = mdates.DateFormatter("%H:%M:%S")
        self.ax.xaxis.set_major_formatter(myFmt)
        # initial x and y data
        dateTimeObj = datetime.now() + timedelta(seconds=-nb_points)
        self.x_data = [dateTimeObj + timedelta(seconds=i) for i in range(nb_points)]
        self.y_data = [0 for i in range(nb_points)]
        # create the plot
        self.plot = self.ax.plot(self.x_data, self.y_data, label='Press')[0]
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(self.x_data[0], self.x_data[-1])

        self.canvas = FigureCanvasTkAgg(self.figure, self)

        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()

        button1 = ttk.Button(self, text="Сброс",
                             command=self.back)
        button1.pack(side='bottom')
        self.button2 = ttk.Button(self, text="Старт",
                             command=lambda : self.buttonClick())
        self.button2.pack(side='bottom')
        self.canvas.get_tk_widget().pack(side='top', fill=tk.BOTH, expand=True)
        # self.animate()

    def back(self, nb_points=360):
        global pressureList
        self.y_data = [0 for i in range(nb_points)]
        pressureList = [0]
        lambda: controller.show_frame(StartPage)

    def buttonClick(self):
        # global Start
        if not self.Start:
            self.Start = True 
            self.button2.config(text="Стоп")
            self.animate()
        else:
            self.Start = False 
            self.button2.config(text="Старт")
            self.cancel()

    def animate(self):
        global pressureList

        # append new data point to the x and y data
        self.x_data.append(datetime.now())
        pressureCur = GetPressure()

        print(pressureCur)

        if str(pressureCur) == "nan":
            # print(pressureList[-1])
            pressureCur = pressureList[-1]
        pressureList.append(float(pressureCur))

        self.y_data.append(float(pressureCur))
        # remove oldest data point
        self.x_data = self.x_data[1:]
        self.y_data = self.y_data[1:]
        #  update plot data
        self.plot.set_xdata(self.x_data)
        self.plot.set_ydata(self.y_data)
        self.ax.set_ylim(0, (max(self.y_data))+10)
        self.ax.set_xlim(self.x_data[0], self.x_data[-1])
        self.canvas.draw_idle()  # redraw plot
        self.labelCurP.config(text = ' '.join(["Текущее значение:", str(pressureCur), "Бар"])) 
        self.labelMaxP.config(text = ' '.join(["Максимальное значение", str(max(pressureList)), "Бар"])) 

        # StartPage.new_text(' '.join(["Текущее значение:", str(pressureCur), "Бар"])) 
        # StartPage.labelMaxP.config(text = ' '.join(["Максимальное значение", str(max(pressureList)), "Бар"])) 

        self._job = self.after(1000, self.animate)  # repeat after 1s

    def cancel(self):
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None


class Device( minimalmodbus.Instrument ):
    def __init__(self, portname, slaveaddress ):
        minimalmodbus.Instrument.__init__(self, portname, slaveaddress)

        # self = minimalmodbus.Instrument.__init__(self,port='/dev/ttyUSB0', slaveaddress=1, debug=False)  # port name, slave address (in decimal)
        # self.serial.baudrate = 9600  # baudrate
        # self.serial.bytesize = 8
        # self.serial.parity   = serial.PARITY_NONE
        # self.serial.stopbits = 1
        # self.serial.timeout  = 0.05      # seconds
        # self.address         = 1        # this is the slave address number
        # self.mode = minimalmodbus.MODE_RTU # rtu or ascii mode
        # self.clear_buffers_before_each_transaction = False

    def readPressure(self):
        return self.read_register(4)


class GetPressure:

    def __init__(self):

        global Debug
        # global pressureList
        # start = True

        # while start:
        self.pressure = self.readPressure()
        if Debug:
            self.pressure = random.randint(0, 100)
            if self.pressure > 75:
                self.pressure = nan
        # pressureList.append(pressure) 
        # pressure = str(random.randint(0, 100))
        # labelCurP.config(text = ' '.join(["Текущее значение:", str(pressure), "Бар"])) 
        # labelMaxP.config(text = ' '.join(["Максимальное значение", str(max(pressureList)), "Бар"])) 
        # root.update()
        # time.sleep(.1)
    def __float__(self):
        return(float(self.pressure))

    def __str__(self):
        return(str(self.pressure))

    def readPressure(self):
        try:
            pressureSensor = Device('/dev/ttyUSB0',1)
            pressureSensor.serial.baudrate = 9600  # baudrate
            pressureSensor.serial.bytesize = 8
            pressureSensor.serial.parity   = serial.PARITY_NONE
            pressureSensor.serial.stopbits = 1
            pressureSensor.serial.timeout  = 0.05      # seconds

            self.pressure = pressureSensor.readPressure()

            # print(self.pressure)
        except IOError:
            print("Failed to read from instrument")
            self.pressure = nan

        self.pressure = self.pressure/10
        # print(self.pressure)
        return(self.pressure)




    # def buttonClick(self):
    #     global start
    #     global pressureList
    #     if not start:
    #         pressureList = [0]
    #         labelMaxP.config(text = ' '.join(["Максимальное значение", str(max(pressureList)), "Бар"])) 
    #         button.config(text="Остановить измерение")
    #         meas()
    #     else:
    #         start = False 
    #         button.config(text="Начать измерение")













app = Pressureapp()
app.geometry('700x600')
# app.protocol("WM_DELETE_WINDOW", app.on_closing())
app.mainloop()
