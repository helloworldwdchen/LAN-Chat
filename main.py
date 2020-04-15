''' 
TODO
1.自动扫描局域网内活跃ip


2.连接状态获取

目前的方法浪费性能，应该优化。

'''
import tkinter as tk
import tkinter.messagebox
from socket import *
from code import *
import threading
import time
import inspect
import ctypes

def gethost():
    import socket
    host=socket.gethostbyname(socket.gethostname())
    print('当前主机名称为 : ' + socket.gethostname())
    print('当前主机的IP为: ' + host)
    return host

selfName = gethost()
# to_host
serverName = '192.168.121.130'
# to_vm
#serverName = '192.168.43.113'

serverPort = 50000
clientSocket = socket(AF_INET, SOCK_DGRAM)


def sendToServer(message):
    clientSocket.sendto(message.encode(), (serverName, serverPort))

window = tk.Tk()

window.title('my chat')

def center_window(w, h):
    # 获取屏幕 宽、高
    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    # 计算 x, y 位置
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    window.geometry('%dx%d+%d+%d' % (w, h, x, y))

center_window(500, 350)

text = tk.Text(window, height=8, width=46,font=('YaHei'))
text.place(relx=0.01, rely=0.01)

input_text = tk.Text(window, height=4, width=36,font=('YaHei'))
input_text.place(relx=0.01, rely=0.54)

name_lable = tk.Label(window,text='请输入昵称:',font=('YaHei',11))
name_lable.place(relx=0.01, rely=0.84)

name_entry = tk.Entry(window, font=('Arial', 14), width=10)
name_entry.place(relx=0.2, rely=0.84)

frame =  tk.Frame(window)

label =  tk.Label(frame,text = '在线状态：')
label.pack(side='left')

canvas = tk.Canvas(frame,bg='white',height=20,width = 20)
oval = canvas.create_oval(3,3,20,20,fill='yellow')

def change_(o):
    canvas.delete()
    if o == 1:
        oval = canvas.create_oval(3,3,20,20,fill='green')
    else:
        oval = canvas.create_oval(3,3,20,20,fill='red')

canvas.pack(side='left')

frame.place(relx=0.6, rely=0.84)

line = 0
def text_insert(string):
    if string == '\n':
        return
    global line
    if line == 8:
        text.delete(1.0,'end')
        line = 0
    text.insert('end', string)
    sendToServer(string)
    line=line+1

def text_add(string):
    if string == '\n':
        return
    global line
    if line == 8:
        text.delete(1.0,'end')
        line = 0
    text.insert('end', string)
    line=line+1

def button_send():
    if name_entry.get()!='':
        myname = name_entry.get()+':'
    else:
        tk.messagebox.showwarning(title='Hi', message='请输入昵称！')
        return 
    s = input_text.get(1.0,'end')
    input_text.delete(1.0, "end")
    text_insert(myname+s)

def func(event):
    if name_entry.get()!='':
        myname = name_entry.get()+':'
    else:
        tk.messagebox.showwarning(title='Hi', message='请输入昵称！')
        return 
    s = input_text.get(1.0,'end')
    input_text.delete(1.0, 'end')
    text_insert(myname+s[:-1])
    
button = tk.Button(window, text='发送', width=8, height=1, command=button_send)
button.place(relx=0.78, rely=0.64)

window.bind('<Return>',func)
window.resizable(0,0)

online = 0

def _timeout():
    global online
    print('not online!')
    change_(0)
    online = 2

def online_check():
    print('check')
    global online
    timer = threading.Timer(2,_timeout)
    timer.daemon=True
    timer.start()
    sendToServer('_check_online')
    while online != 2:
        if online == 1:
            print('yes, online!')
            timer.cancel()
            change_(1)
            break;

flag=False

def checking():
    global online
    while(flag == False):
        online = 0
        online_check()
        time.sleep(3)

check_thread = threading.Thread(target=checking)
check_thread.daemon=True
check_thread.start()

def UDPserver():
    global flag
    global online
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('',50000))
    while True:
        print('...')
        message, cilentAddress = serverSocket.recvfrom(2048)
        if(message.decode()=='_online_true'):
            online = 1
            continue
        if(message.decode()=='_check_online'):
            sendToServer('_online_true')
            continue
        if flag==True: break
        text_add(message)
    print('socket shutdown!')
    serverSocket.close()

thread_server = threading.Thread(target=UDPserver)
thread_server.daemon=True
thread_server.start()


window.mainloop();

flag=True;
clientSocket.sendto('close'.encode(), (selfName, serverPort))
clientSocket.close();
thread_server.join()
print('The programe is over!')
