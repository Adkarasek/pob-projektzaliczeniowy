import os
import tkinter
from tkinter import *
import tkinter.filedialog
import cv2
import matplotlib.pyplot as plt
import numpy
import time


def donothing():
    print("doNothing")


class Main():
    currentWindow = 1  # aktywne okienko

    def __init__(self, *args, **kwargs):  # Zbiera informacje o tej klasie, to jest klasa Main
        root = Tk()
        menubar = Menu(root)
        root.title("POB Adrian Karasek 18109")
        root.geometry("400x500")
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Otwórz", command=lambda: Image(self))
        filemenu.add_command(label="Zapisz", command=lambda: self.currentWindow.ImageToFile())
        filemenu.add_command(label="Duplikuj", command=lambda: Image(self, 0, self.currentWindow))
        filemenu.add_separator()
        filemenu.add_command(label="Wyjście", command=root.quit)
        menubar.add_cascade(label="Plik", menu=filemenu)

        lab1menu = Menu(menubar, tearoff=0)
        lab1menu.add_command(label="Histogram", command=lambda: self.currentWindow.CreateHistogram())
        lab1menu.add_command(label="Tablica LUT", command=lambda: self.currentWindow.LutTable())
        menubar.add_cascade(label="Lab1", menu=lab1menu)

        lab2menu = Menu(menubar, tearoff=0)
        lab2menu.add_command(label="Rozciągnij histogram", command=lambda: self.currentWindow.StretchHistogram())
        lab2menu.add_separator()
        lab2menu.add_command(label="Odwróć kolory", command=lambda: self.currentWindow.InvertColors())
        lab2menu.add_command(label="Binaryzacja", command=lambda: self.currentWindow.BinaryThreshold(self.p1.get()))
        lab2menu.add_command(label="Binaryzacja z zachowaniem odcieni szarości",
                             command=lambda: self.currentWindow.BinaryGrayThreshold(self.p1.get()))
        menubar.add_cascade(label="Lab2", menu=lab2menu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Help Index", command=donothing)
        helpmenu.add_command(label="About...", command=donothing)
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.p1 = Scale(root, from_=0, to=255, orient = HORIZONTAL)
        labelP1 = Label(root, text="Slider P1 (binaryzacja)")
        labelP1.grid(row=0, column=0)
        self.p1.grid(row=0, column=1)
        self.p1.bind("<ButtonRelease-1>", self.updateSliderP2)
        self.p2 = Scale(root, from_=0, to=255, orient = HORIZONTAL)
        labelP2 = Label(root, text="Slider P2")
        labelP2.grid(row = 1, column = 0)

        self.p2.grid(row = 1, column = 1)
        root.config(menu=menubar)
        root.mainloop()

    def updateSliderP2(self,event):
        self.p2.configure(from_ = self.p1.get())

    def getCurrentWindow(self, window):
        self.currentWindow = window
        print(self.currentWindow)


class Image():
    def __init__(self, parent, flag=1, window=0, *args, **kwargs):
        def clicked(event, x, y, flags, params):
            if event == cv2.EVENT_LBUTTONDOWN:
                print(self)
                Main.getCurrentWindow(parent, self)
            self.parent = parent

        if flag == 1:
            imgPath = tkinter.filedialog.askopenfilename(initialdir=os.getcwd())  # dialog do otwarcia pliku
            if (imgPath == ""):  # sprawdza czy sciezka jest wybrana, jezeli nie to konczy funkcje
                del self
            self.image = cv2.imread(imgPath, cv2.IMREAD_UNCHANGED)
            self.title = f"{os.path.basename(imgPath)}"
            self.shape = self.image.shape
            self.data = (self.image.tolist())
            cv2.imshow(self.title, self.image)
            cv2.setMouseCallback(self.title, clicked, self.title)
        else:
            self.image = window.image
            self.title = window.title + ' '
            self.shape = window.image.shape
            self.data = window.image
            print(self.title)
            cv2.imshow(self.title, self.image)
            cv2.setMouseCallback(self.title, clicked, self.title)

    def ImageToFile(self):
        imgPath = tkinter.filedialog.asksaveasfilename(initialdir=os.getcwd(), initialfile=self.title,
                                                       defaultextension='.',
                                                       filetypes=[(".bmp", ".bmp"),
                                                                  (".jpg", ".jpg")])  # dialog do zapisu pliku
        if (imgPath == ""):  # sprawdza czy sciezka jest wybrana, jezeli nie to konczy funkcje
            return
        array = numpy.array(self.data, dtype=numpy.uint8)
        cv2.imwrite(str(imgPath), array)

    def CreateHistogram(self):
        shape = len(self.shape)
        if shape == 2:
            xAxis = list(range(0, 256))
            yAxisCount = [0] * 256
            for items in self.data:
                for item in items:
                    yAxisCount[item] += 1
            plt.figure()
            plt.title("Histogram " + self.title)
            plt.bar(xAxis, yAxisCount, color="black")
            plt.show()
        if shape == 3:
            xAxis = list(range(0, 256))
            yAxisCountR = [0] * 256
            yAxisCountG = [0] * 256
            yAxisCountB = [0] * 256
            for items in self.data:
                for item in items:
                    yAxisCountB[item[0]] += 1
                    yAxisCountG[item[1]] += 1
                    yAxisCountR[item[2]] += 1
            plt.title("RHistogram " + self.title)
            plt.bar(xAxis, yAxisCountR, color="red")
            plt.figure()
            plt.title("GHistogram " + self.title)
            plt.bar(xAxis, yAxisCountG, color="green")
            plt.figure()
            plt.title("BHistogram " + self.title)
            plt.bar(xAxis, yAxisCountB, color="blue")
            plt.show()

    def getLutValues(self, data):
        table = [0] * 256
        for element in data:
            for pixel in element:
                table[pixel] += 1
        return table

    def StretchHistogram(self):
        shape = len(self.shape)
        if shape == 2:
            imSum = sum(self.data, [])
            maxVal = max(imSum)
            minVal = min(imSum)
            a = -1
            tmpImage = self.data
            for element in self.data:
                b = -1
                a += 1
                for pixel in element:
                    b += 1
                    tmpImage[a][b] = round((pixel - minVal) * (255 / (maxVal - minVal)))
            array = numpy.array(tmpImage, dtype=numpy.uint8)
            self.data = tmpImage
            cv2.imshow(self.title, array)
            cv2.waitKey(1)

    def InvertColors(self):  # tutaj nie weim o co chodzi...
        shape = len(self.shape)
        if shape == 2:
            tmp = self.data
            a = -1;
            for element in self.data:
                a += 1
                b = 0
                for pixel in element:
                    tmp[a][b] = 255 - pixel

                    b += 1

            array = numpy.array(tmp, dtype=numpy.uint8)
            self.data = tmp
            cv2.imshow(self.title, array)
            cv2.waitKey(1)

    def BinaryThreshold(self, w):

        shape = len(self.shape)
        if shape == 2:
            tmp = self.data
            for i in range(len(self.data)):
                for j in range(len(self.data[i])):
                    if self.data[i][j] > w:
                        self.data[i][j] = 255
                    else:
                        self.data[i][j] = 0

        array = numpy.array(self.data, dtype=numpy.uint8)
        cv2.imshow(self.title, array)
        cv2.waitKey(1)

    def BinaryGrayThreshold(self, w):

        shape = len(self.shape)
        if shape == 2:
            tmp = self.data
            for i in range(len(self.data)):
                for j in range(len(self.data[i])):
                    if self.data[i][j] < w:
                        self.data[i][j] = 0

        array = numpy.array(self.data, dtype=numpy.uint8)
        cv2.imshow(self.title, array)
        cv2.waitKey(1)

    def LutTable(self):
        def updateValue(event):
            sliderval = slider.get()
            mytext2 = "Wartość \t"
            mytext = "Ilość \t"
            for i in range(10):
                mytext2 += str(i + sliderval)
                mytext2 += "\t"
                mytext += str(lutValues[i + sliderval])
                mytext += "\t"

            label0.configure(text=mytext2)
            labelv0.configure(text=mytext)

        shape = len(self.shape)
        if shape == 2:
            lutValues = self.getLutValues(self.data)
        lut = Tk()
        lut.title("Tablica lut "+self.title)
        label0 = Label(lut, text="\n 0", borderwidth=4)
        label0.grid(row=0, column=0)
        labelv0 = Label(lut, text=lutValues[0], borderwidth=4)
        labelv0.grid(row=1, column=0)
        slider = Scale(lut, from_=0, to=251, orient=HORIZONTAL, length = 400)
        slider.grid(row=3, column=0, columnspan=5)

        slider.bind("<ButtonRelease-1>", updateValue)
        updateValue(1)
        lut.mainloop()


if __name__ == "__main__":
    app = Main()
