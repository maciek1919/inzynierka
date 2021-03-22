import threading
import tkinter as Tk
import re

from scipy.signal import savgol_filter
from tsmoothie.smoother import *
import serial


class Prox(Tk.Entry):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.var = Tk.StringVar(master)
        self.var.trace('w', self.validate)
        Tk.Entry.__init__(self, master, textvariable=self.var, **kwargs)
        self.get, self.set = self.var.get, self.var.set

    def validate(self, *args):
        value = self.get()
        if not value.isdigit():
            self.set(''.join(x for x in value if x.isdigit()))


def clicked(a, b, c):
    # if len(a.get()) == 0 or len(b.get()) == 0 or len(c.get()) == 0:
    # popupmsg("Wprowadź poprawne dane!")
    # else:
    global keepGoing
    keepGoing = True
    # th = threading.Thread(target = readData, args=(float(a.get()), float(b.get()), float(c.get())))
    th = threading.Thread(target=readData, args=(7, 68, 178))
    th.daemon = True
    th.start()

    # print(float(a.get()), float(b.get()))
    # readData()


def popupmsg(msg):
    popup = Tk.Tk()
    popup.wm_title("ERROR")
    label = Tk.Label(popup, text=msg)
    label.pack(side="top", fill="x", pady=10)
    B1 = Tk.Button(popup, text="Okay", command=popup.destroy)
    B1.pack()
    popup.mainloop()

def clean():
    with open("przemieszczenie.txt", "a") as file:
        file.truncate(0)
        file.close()
    with open("predkosc.txt", "a") as file1:
        file1.truncate(0)
        file1.close()
    with open("przyspieszenie.txt", "a") as file3:
        file3.truncate(0)
        file3.close()
    with open("moc.txt", "a") as file4:
        file4.truncate(0)
        file4.close()

def stop():
    global keepGoing
    keepGoing = False


def smoothing(file,size):
    i = 0
    setlist = []
    result = ""
    with open(file, "r") as file1:
        for line in file1:
            inner_list = [elt.strip() for elt in line.split(',')]
            setlist.append(float(inner_list[1]))
    yhat = savgol_filter(setlist, size, 3)
    with open(file, "r") as file2:
        for line in file2:
            list = line.split(",")
            list[1] = str(yhat[i])
            line = ",".join(list)
            result += line + '\n'
            i = i + 1
    f = open(file, "w")
    f.write(result)
    f.close()


def readData(m1, m2, h1):  # m1 - masa ciezaru, m2-masa miesni h1- dlugosc ciala

    try:
        arduinoData = serial.Serial("/dev/ttyACM0", timeout=1)
    except:
        print('Please check the port')



    timestamp = str(serial.time.time())
    count = 0
    rawdata = []
    P = []
    J = 0.000193152  # moment bezwładnosci krazka podany w kg*m^2
    r = 0.0685  # promien krazka w m
    m_sum = 7.4484 + 0.76694 * m2 - 0.05192 * h1 + m1  # dla masy ciala 80, ciezaru 50, wzrost 180 - 109,458kg
    g = 9.8  # przyspieszenie ziemnskie w m/s^2
    A = J + (m_sum * r ** 2)
    B = m_sum * g * r
    Fsmyczy = 150 / 1000 * g
    C = Fsmyczy * r
    fik = 0  # fi aktualne
    fik_1 = 0  # fi poprzednie
    fik_2 = 0  # fi poprzednie (fi akutalne -2)
    t_s = 0.01  # czas probkowania w sek
    P_lift = 0
    fikakt = 0
    fik_pop = 0
    fik_poppop = 0
    t = 0
    t1 = 0
    tc = 0
    v = 0
    i = 0
    a=0
    smoothed = []
    smoothed1 = []
    wygladzone=[]
    wygladzone1=[]
    while keepGoing:
        c = [float(s) for s in re.findall('\\d+', str(arduinoData.readline()))]  # Wczytanie outputu z arduino
        if c:
            i = i + 1
            # OBLICZENIA
            fik_poppop = fik_pop
            fik_pop = fikakt
            fikakt = c[-1]

            fik_2 = fik_1
            fik_1 = fik
            fik = (c[-1] / 200) * 3.14  # odczyt kąta w radianach

            t1 = t
            t = c[0] / 1000
            t_s = t - t1
            if t_s > 1 or t_s == 0 or t_s < 0.0001:
                t_s = 0.01
            v1 = v
            v = (fik - fik_1) * r / t_s
            a1 = a
            a = (v - v1) / t_s
            tc = tc + t_s

            #wygladzone.append(a)
            #wygladzone1.append(v1)
            #if len(wygladzone)>51 and len(wygladzone1)>51:
            #    smoothed = savgol_filter(smoothed, 51, 3)
            #    smoothed1 = savgol_filter(smoothed1, 51, 3)

            fi_prim = (fik - fik_1) / t_s  # pierwsza pochodna kąta
            fi_bis = (fik - 2 * fik_1 + fik_2) / (
                    t_s ** 2)  # druga pochodna kąta (2*fik_1 > fik+fik_2) - zdarzaja sie ujemne wartosci

            P_lift = A * fi_prim * fi_bis + B * fi_prim + C * fi_prim  # moc całkowita wyrażona w W
            # print(c, " ----MOC---- ", "{:.2f}".format(P_lift), " FI akt: ", fikakt, "FI pop: ", fik_pop, "FI poppop: ", fik_poppop, timestamp )
            # print(fik, fik_1, fik_2, "MASA do obliczen: ", m_sum, " pochodne:", fi_prim, fi_bis,"{:.2f}".format(P_lift)," W - time: ", timestamp)
            # print(arduino,"MOC: "
            # "{:.2f}".format(P_lift), )
            print(t_s)

            with open("file.txt", "a") as file:
                file.write(
                    "Odczyt z enkodera: {} , Moc: {} , FI akt: {} , FI pop: {} , FI poppop: {} , różnica czasu: {}\n".format(
                        c, "{:.2f}".format(P_lift), fikakt, fik_pop, fik_poppop, t_s))
                # file.write(c, " ----MOC---- ", "{:.2f}".
                # format(P_lift), " FI akt: ", fikakt, "FI pop: ", fik_pop, "FI poppop: ", fik_poppop, t_s)
            with open("przemieszczenie.txt", "a") as file:
                file.write("{},{}\n".format(tc, fik * r))
                file.close()

            with open("predkosc.txt", "a") as file1:
                #if i>51:
                ##    file1.write(
                 #       "{},{}\n".format(tc, wygladzone1[i-51]))
                #else:
                    file1.write("{},{}\n".format(tc, v))
                    file1.close()
            with open("przyspieszenie.txt", "a") as file2:
                #if i>51:
                #    file2.write(
                #        "{},{}\n".format(tc, wygladzone[i - 51]))
                #else:
                file2.write(
                    "{},{}\n".format(tc, a)
                )
                file2.close()

            with open("moc.txt", "a") as file3:
                file3.write("{},{}\n".format(tc, P_lift))
                file3.close()

