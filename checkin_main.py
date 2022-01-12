from tkinter import *
from tkinter import messagebox
import PIL.Image, PIL.ImageTk
import tkinter
import time
import cv2
import os
import shutil
import csv
import pandas as pd
import pyttsx3
from threading import Thread
from core.def_predict import *
from core.def_capture import *
from core.def_train import *
from core.def_lowlightenhance import *

window = Tk()
window.title('XuanDuc Checkin App')

engine = pyttsx3.init()

video = cv2.VideoCapture(0)

canvas_w = video.get(cv2.CAP_PROP_FRAME_WIDTH)
canvas_h = video.get(cv2.CAP_PROP_FRAME_HEIGHT)

# canvas = Canvas(window, width=canvas_w, height=canvas_h, bg='red')
# canvas.pack()
#
# canvas_img = Canvas(window, width=canvas_w/2, height= canvas_h/2, bg= 'green')
# canvas_img.pack(side=BOTTOM)

frame1 = Frame()
frame1.pack(side=TOP, expand=True)

canvas = Canvas(frame1, width=canvas_w, height=canvas_h)
canvas.pack(side=LEFT)

canvas_img = Canvas(frame1, width=canvas_w / 2, height=canvas_h / 2)
canvas_img.pack(side=TOP)

photo = None
frame = None
count = 0
thread_predict = None
thread_register = None
list_all = list()
list_checkin = list()
var1 = tkinter.IntVar()
result = Label(window, text='Checkin: ', fg='red', font=('Arial', 30))
result.pack()
input_register = Entry(window)
input_register.pack(side=RIGHT, padx=3, pady=3)


def load_csv(path):
    df = pd.read_csv(path)
    data = df.values
    data = data.flatten()
    list_data = list()
    for i in data:
        list_data.append(i)
    return list_data


list_all = load_csv('list/list_all.csv')
list_checkin = load_csv('list/list_checkin.csv')


def check_list(list):
    top = Tk()
    top.geometry('400x200')
    top.title('Check list')
    Lb1 = Listbox(top, width=500)
    i = 1
    for j in list:
        Lb1.insert(i, j)
        i = i + 1
    Lb1.pack()
    top.mainloop()


def countdown(t):
    global input_register, list_all, result
    name_register = input_register.get()
    huong_dan_text = Label(window, text='Moi ban nhin vao camera va di chuyen dau nhe nhang ve cac huong')
    huong_dan_text.pack()
    count_down = Label(window, text='00:00')
    count_down.pack()
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        count_down.configure(text=timer)
        time.sleep(1)
        t -= 1
    # count_down.configure(text='Register success', fg='red')
    list_all.append(name_register)
    with open('list/list_all.csv', mode='w') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['ten'])
        for i in list_all:
            writer.writerow([i])
    result.configure(text='Register: ' + name_register)
    messagebox.showinfo('Dang ki', 'Dang ki ' + name_register + ' thanh cong.')
    count_down.destroy()
    huong_dan_text.destroy()


def checkin_func():
    global frame, result, list_checkin, var1

    if var1.get() == 1:
        frame = lowlight_enhance(frame)

    frame_show_resize = cv2.resize(frame, dsize=None, fx=0.5, fy=0.5)
    photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame_show_resize))
    canvas_img.create_image(0, 0, image=photo, anchor=tkinter.NW)

    name_predict = predict(PIL.Image.fromarray(frame))
    if name_predict == "Unknown":
        messagebox.showerror('Unknown', 'Please again!')
    elif name_predict in list_checkin:
        messagebox.showerror('Note', name_predict + ' chua checkout, ban can checkout truoc khi checkin!')
    else:
        result.configure(text='Checkin: ' + name_predict)
        list_checkin.append(name_predict)

        with open('list/list_checkin.csv', mode='w') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['ten'])
            for i in list_checkin:
                writer.writerow([i])

        with open('list/list_history.csv', mode='a') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            history_string = name_predict + " check in at " + time.ctime()
            writer.writerow([history_string])

        engine.say("Hello " + name_predict + ". You are check in successfully")
        engine.runAndWait()
        messagebox.showinfo('Checkin', name_predict + ': Checkin thanh cong.')


def start_thread_predict():
    thread_predict = Thread(target=checkin_func)
    # if thread.is_alive():
    #     thread.join()
    # else:
    #     thread.start()
    thread_predict.start()
    print(thread_predict.getName())


def checkout_func():
    print('checkout')
    global frame, result, list_checkin, var1

    if var1.get() == 1:
        frame = lowlight_enhance(frame)

    frame_show_resize = cv2.resize(frame, dsize=None, fx=0.5, fy=0.5)
    photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame_show_resize))
    canvas_img.create_image(0, 0, image=photo, anchor=tkinter.NW)

    name_predict = predict(PIL.Image.fromarray(frame))
    if name_predict == "Unknown":
        messagebox.showerror('Unknown', 'Please again!')
    elif name_predict in list_checkin:
        result.configure(text='Checkout: ' + name_predict)
        list_checkin.remove(name_predict)

        with open('list/list_checkin.csv', mode='w') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['ten'])
            for i in list_checkin:
                writer.writerow([i])

        with open('list/list_history.csv', mode='a') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            history_string = name_predict + " check out at " + time.ctime()
            writer.writerow([history_string])

        engine.say("Hello " + name_predict + ". You are check out successfully")
        engine.runAndWait()
        messagebox.showinfo('Checkout', name_predict + ': Checkout thanh cong.')
    else:
        messagebox.showerror('Note', name_predict + ' chua checkin, ban can checkin truoc khi checkout!')


def start_thread_checkout():
    thread_checkout = Thread(target=checkout_func)
    thread_checkout.start()
    print(thread_checkout.getName())


def register_func():
    global input_register, video
    name_register = input_register.get()
    capture_image(video, name_register)
    append_data('register/')
    list_checkin.append(name_register)
    dir1 = os.path.join('register', 'train', name_register)
    dir2 = os.path.join('register', 'test', name_register)
    try:
        shutil.rmtree(dir1)
        shutil.rmtree(dir2)
        print('Delete success')
    except:
        print('Delete error')

    with open('list/list_checkin.csv', mode='w') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['ten'])
        for i in list_checkin:
            writer.writerow([i])
    with open('list/list_history.csv', mode='a') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            history_string = name_register + " check in at " + time.ctime()
            writer.writerow([history_string])


def start_thread_register():
    # dir1 = os.path.join('register', 'train', input_register.get())
    # dir2 = os.path.join('register', 'test', input_register.get())
    global list_all
    if input_register.get() == '':
        messagebox.showwarning('Note', 'Ban chua nhap ten de dang ki.')
    elif input_register.get() in list_all:
        messagebox.showerror('Note', 'Ten da ton tai!')
    else:
        thread_register = Thread(target=register_func)
        thread_countdown = Thread(target=countdown, args=(15,))
        thread_register.start()
        thread_countdown.start()
        print('Register: ' + thread_register.getName())
        print('Countdown: ' + thread_countdown.getName())


button_predict = Button(window, text="Check In", command=start_thread_predict)
button_predict.pack(side=LEFT, padx=5, pady=5, ipadx=3, ipady=3)
button_checkout = Button(window, text="Check Out", command=start_thread_checkout)
button_checkout.pack(side=LEFT, padx=5, pady=5, ipadx=3, ipady=3)
c1 = Checkbutton(window, text='Low-light', variable=var1, onvalue=1, offvalue=0)
c1.pack(side=LEFT, padx=5, pady=5, ipadx=3, ipady=3)
button_register = Button(window, text="Register", command=start_thread_register)
button_register.pack(side=RIGHT, padx=5, pady=5, ipadx=3, ipady=3)
button_list_all = Button(window, text="Check list all", command=lambda: check_list(list_all))
button_list_all.pack(side=BOTTOM, padx=3, pady=3, ipadx=3, ipady=3)
button_list_checkin = Button(window, text="Check list checkin", command=lambda: check_list(list_checkin))
button_list_checkin.pack(side=BOTTOM, padx=3, pady=3, ipadx=3, ipady=3)
button_history = Button(window, text="Check history", command=lambda: check_list(load_csv('list/list_history.csv')))
button_history.pack(side=BOTTOM, padx=3, pady=3, ipadx=3, ipady=3)


def update_frame():
    global canvas, photo, count, frame
    ret, frame = video.read()
    frame = cv2.resize(frame, dsize=None, fx=1, fy=1)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
    canvas.create_image(0, 0, image=photo, anchor=tkinter.NW)
    count = count + 1
    window.after(1, update_frame)


update_frame()

window.mainloop()
