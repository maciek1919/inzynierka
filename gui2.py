from tkinter import *
from tkinter import ttk
import numpy as np
import mplcursors as mplcursors
from matplotlib import style, animation
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk as NavigationToolbar2TkAgg

import methods

style.use('ggplot')
f = Figure(figsize=(12, 9), dpi=100)
a = f.add_subplot(411)
b = f.add_subplot(412)
c1 = f.add_subplot(413)
d = f.add_subplot(414)


def animate(i):
    pullData = open('przemieszczenie.txt', 'r').read()
    pullData1 = open('predkosc.txt', 'r').read()
    pullData2 = open('przyspieszenie.txt', 'r').read()
    pullData3 = open('moc.txt', 'r').read()
    dataArray = pullData.split('\n')
    dataArray1 = pullData1.split('\n')
    dataArray2 = pullData2.split('\n')
    dataArray3 = pullData3.split('\n')
    xar = []
    yar = []
    xbr = []
    ybr = []
    xcr = []
    ycr = []
    xdr = []
    ydr = []
    for eachLine in dataArray:
        if len(eachLine) > 1:
            x, y = eachLine.split(',')
            xar.append(float(x))
            yar.append(float(y))
    for eachLine in dataArray1:
        if len(eachLine) > 1:
            x1, y1 = eachLine.split(',')
            xbr.append(float(x1))
            ybr.append(float(y1))
    for eachLine in dataArray2:
        if len(eachLine) > 1:
            x2, y2 = eachLine.split(',')
            xcr.append(float(x2))
            ycr.append(float(y2))
    for eachLine in dataArray3:
        if len(eachLine) > 1:
            x3, y3 = eachLine.split(',')
            xdr.append(float(x3))
            ydr.append(float(y3))
    a.clear()
    a.plot(xar, yar)
    b.clear()
    b.plot(xbr, ybr)
    c1.clear()
    c1.plot(xcr, ycr)
    d.clear()
    d.plot(xdr, ydr)

    return a, b, c1, d


class Application(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.master.title("Aplikacja do pomiaru mocy")
        frame1 = LabelFrame(master, text='Dane ćwiczącego', width=1500, height=130, bd=5)
        frame1.grid(row=0, column=0, sticky=W + E + N + S)
        label = ttk.Label(master=frame1, text="Wprowadz mase człowieka [kg]: ")
        label.grid(column=0, row=0, sticky=W)
        label1 = ttk.Label(master=frame1, text="Wprowadz mase obciazenia [kg]: ")
        label1.grid(column=0, row=1, sticky=W)
        label2 = ttk.Label(master=frame1, text="Wprowadz wzrost ćwiczącego [cm]: ")
        label2.grid(column=0, row=2, sticky=W)
        frame1.txtEntry = methods.Prox(frame1, width=15)
        frame1.txtEntry1 = methods.Prox(frame1, width=15)
        frame1.txtEntry2 = methods.Prox(frame1, width=15)
        frame1.txtEntry.grid(column=1, row=0)
        frame1.txtEntry1.grid(column=1, row=1)
        frame1.txtEntry2.grid(column=1, row=2)
        btn = ttk.Button(master=frame1, text="Zacznij pomiary",
                         command=lambda: methods.clicked(frame1.txtEntry, frame1.txtEntry1, frame1.txtEntry2))
        btn.grid(column=0, row=5, sticky=W)
        btn1 = ttk.Button(frame1, text="Koniec pomiarów", command=lambda: methods.stop())
        btn1.grid(column=0, row=5, sticky=E)
        btn2 = ttk.Button(frame1, text="Wygladz pomiary", command=lambda: [methods.smoothing("przyspieszenie.txt", 151),
                                                                           methods.smoothing("predkosc.txt", 51),
                                                                           methods.smoothing('moc.txt', 51)])
        btn2.grid(column=0, row=6, sticky=W)
        btn3 = ttk.Button(frame1, text="Wyczysc pomiary", command=lambda: methods.clean())
        btn3.grid(column=0, row=6, sticky=E)

        frame2 = Frame(master)
        frame2.grid(row=0, column=1, sticky=W + E + N + S)
        f.text(0.5, 0.04, 'Time [s]', ha='center', va='center')
        f.text(0.07, 0.4, 'Acceleration [m/s^2]', ha='center', va='center', rotation='vertical')
        f.text(0.07, 0.6, 'Velocity [m/s]', ha='center', va='center', rotation='vertical')
        f.text(0.07, 0.8, 'Displacement [m]', ha='center', va='center', rotation='vertical')
        f.text(0.07, 0.2, 'Power [W]', ha='center', va='center', rotation='vertical')

        canvas = FigureCanvasTkAgg(f, frame2)
        canvas.draw()
        canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
        toolbar = NavigationToolbar2TkAgg(canvas, frame2)
        toolbar.update()
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)


root = Tk()
root.geometry("1580x950")
root.resizable(False, False)
app = Application(master=root)
ani1 = animation.FuncAnimation(f, animate, interval=1)
app.mainloop()
