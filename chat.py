import time
import threading
import tkinter as tk
import tkinter.messagebox
import datetime
from socket import *
from tkinter import filedialog
import struct
import json
import os

targetName = '192.168.121.130'
# targetName = '127.0.0.1'
myname = ''
online = 0
canSend = 0

# 静态GUI部分
# -------------------------------------------------

window = tk.Tk()
window.title('my chat')


def center_window(w, h):
    # 获取屏幕 宽、高
    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    # 计算 x, y 位置
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    window.geometry('%dx%d+%d+%d' % (w, h, x, y))


center_window(600, 450)

top_frame = tk.Frame(window)

ip_lable = tk.Label(top_frame, text='对方IP:  ', font=('Arial', 12))
ip_lable.pack(side='left')

e = tk.StringVar()
e.set(targetName)
ip_entry = tk.Entry(top_frame, font=('Arial', 11), width=14, textvariable=e)
ip_entry.pack(side='left')

space_lable1 = tk.Label(top_frame, text=' ', font=('YaHei', 11))
space_lable1.pack(side='left')


def get_id():
    global targetName
    targetName = ip_entry.get()
    print('set ip:' + targetName)


get_ip_button = tk.Button(top_frame, text='确定', width=8, height=1, bd=1, command=get_id)
get_ip_button.pack(side='left')

space_lable1 = tk.Label(top_frame, text='       ', font=('YaHei', 11))
space_lable1.pack(side='left')

label = tk.Label(top_frame, text='在线状态：')
label.pack(side='left')

canvas = tk.Canvas(top_frame, bg='white', height=20, width=20)
oval = canvas.create_oval(3, 3, 20, 20, fill='yellow')


def change_(o):
    global canvas
    global oval
    global canSend
    canvas.delete()
    if o == 1:
        oval = canvas.create_oval(3, 3, 20, 20, fill='green')
        canSend = 1
    else:
        oval = canvas.create_oval(3, 3, 20, 20, fill='red')
        canSend = 0


canvas.pack(side='left')
top_frame.place(x=75, y=10)

text_frame = tk.Frame(window)

scroll = tkinter.Scrollbar(text_frame)
text = tk.Text(text_frame, height=15, width=70, font=('YaHei'), relief='sunken', bd=1, state='disable')
scroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
text.pack(side=tkinter.LEFT, fill=tkinter.Y)
scroll.config(command=text.yview)
text.config(yscrollcommand=scroll.set)
text.tag_config("tag1", foreground="green", font=('YaHei', 11))
text.tag_config("tag2", foreground="blue", font=('YaHei', 11))
text.pack()

text_frame.place(x=10, y=45)

input_text = tk.Text(window, height=4, width=72, font=('YaHei', 12), bd=1)
input_text.place(x=10, y=310)

name_lable = tk.Label(window, text='请输入昵称:', font=('YaHei', 11))
name_lable.place(x=50, y=395)

name_entry = tk.Entry(window, font=('Arial', 13), width=10)
name_entry.place(x=140, y=395)


# GUI修改部分
# ------------------------------------------------


def text_add(string):
    text.config(state='normal')
    text.insert('end', string)
    text.config(state='disable')
    text.see(1000.0)


def text_add_name(string):
    text.config(state='normal')
    text.insert('end', string, "tag1")
    text.config(state='disable')
    text.see(1000.0)


def text_add_name_myself():
    cur = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    string = myname + ' ' + cur + '\n'
    text.config(state='normal')
    text.insert('end', string, "tag2")
    text.config(state='disable')
    text.see(1000.0)


def send_message(string):
    serverPort = 50000
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((targetName, serverPort))
    clientSocket.send(string.encode('utf-8'))
    clientSocket.close()


def send_button_func():
    global myname
    global canSend
    if name_entry.get() != '':
        myname = name_entry.get()
    else:
        tk.messagebox.showwarning(title='Hi', message='请输入昵称！')
        return
    # print("hhh:",canSend)
    if canSend == 0:
        tk.messagebox.showwarning(title='警告', message='对方不在线！')
        return

    cur = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    string = input_text.get(1.0, 'end')
    stringTarget = myname + ' ' + cur + '$' + string
    send_message(stringTarget)
    text_add_name_myself()
    text_add(string)
    input_text.delete(1.0, "end")


send_button = tk.Button(window, text='发送', width=12, height=2, bd=1, command=send_button_func)
send_button.place(x=490, y=390)

run_flag = True
end_flag = True


def tcp_server():
    global run_flag
    serverPort = 50000
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', serverPort))
    serverSocket.listen(5)
    # print('The server is ready to receive')
    while run_flag:
        connectionSocket, addr = serverSocket.accept()
        try:
            sentence = connectionSocket.recv(1024).decode('utf-8')
            string = sentence.split('$')
            if string[0] == '_shutdown':
                break
            text_add_name(string[0] + '\n')
            text_add(string[1])
        except ConnectionRefusedError:
            break
        connectionSocket.close()
    print('TCP server shutdown!')
    serverSocket.close()


# TODO
# text tag

def click(event):
    os.system('start download')


text.tag_config("file_tag", foreground="#00ae9d", font=('YaHei', 13),underline = True)
text.tag_bind("file_tag", "<Button-1>", click)
def file_message(string):
    text.config(state='normal')
    text.insert('end', string, "file_tag")
    text.config(state='disable')
    text.see(1000.0)

def file_send_server(dir):
    filename = dir.split('/')[-1]
    # print(filename)
    share_dir = '/'.join(dir.split('/')[0:-1])
    cur = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # print(share_dir)
    serverPort = 51000
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((targetName, serverPort))
    clientSocket.send('__ready'.encode('utf-8'))
    try:
        # 以读的方式打开文件,读取文件内容发送给客户端
        # 第一步：制作固定长度的报头
        header_dic = {
            'filename': filename,  # 1.txt
            'file_size': os.path.getsize(r'%s\%s' % (share_dir, filename)),  # 路径/1.txt
            'username': myname,
            'servertime': cur
        }

        header_json = json.dumps(header_dic)
        header_bytes = header_json.encode('utf-8')

        # 第二步：先发送报头的长度
        clientSocket.send(struct.pack('i', len(header_bytes)))

        # 第三步:再发报头
        clientSocket.send(header_bytes)

        # 第四步：再发送真实的数据
        with open('%s/%s' % (share_dir, filename), 'rb') as f:
            for line in f:
                clientSocket.send(line)
    except ConnectionResetError:  # 适用于windows操作系统
        pass
    text_add_name_myself()
    text_add(dir+'\n')
    clientSocket.close()


def file_receive_server():
    download_dir = os.getcwd() + '/download'
    serverPort = 51000
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', serverPort))
    serverSocket.listen(5)
    while run_flag:
        connectionSocket, addr = serverSocket.accept()
        msg = connectionSocket.recv(7).decode('utf-8')
        if msg != '__ready':
            continue
        elif msg == '__shutd':
            break
        print('开始接收')
        obj = connectionSocket.recv(4)
        header_size = struct.unpack('i', obj)[0]

        # 第二步：再收报头
        header_bytes = connectionSocket.recv(header_size)

        # 第三步：从报头中解析出对真实数据的描述信息
        header_json = header_bytes.decode('utf-8')
        header_dic = json.loads(header_json)
        '''
        header_dic = {
            'filename': filename,  # 1.txt
            'file_size': os.path.getsize(r'%s\%s' % (share_dir, filename))  # 路径/1.txt
        }    
        '''

        total_size = header_dic['file_size']
        file_name = header_dic['filename']
        username = header_dic['username']
        servertime = header_dic['servertime']
        # 第四步：接收真实的数据
        isExists = os.path.exists(download_dir)
        if not isExists:
            os.makedirs(download_dir)
        with open(r'%s\%s' % (download_dir, file_name), 'wb') as f:
            recv_size = 0
            while recv_size < total_size:
                line = connectionSocket.recv(1024)
                f.write(line)
                recv_size += len(line)
                print('总大小：%s   已下载大小：%s' % (total_size, recv_size))
            print('接收完成')
        text_add_name(username+' '+servertime+'\n')
        file_message(file_name+'\n')
    print('file_receive_TCP shutdown')
    serverSocket.close()


def file_send():
    global myname
    if name_entry.get() != '':
        myname = name_entry.get()
    else:
        tk.messagebox.showwarning(title='Hi', message='请输入昵称！')
        return
    if canSend == 0:
        tk.messagebox.showwarning(title='警告', message='对方不在线！')
        return

    Filepath = filedialog.askopenfilename()
    if Filepath == '':
        return
    print(Filepath)
    file_send_server(Filepath)


file_send_button = tk.Button(window, text='选择文件发送', width=12, height=2, bd=1, command=file_send)
file_send_button.place(x=380, y=390)


def sendToServer(message):
    serverPort = 50000
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.sendto(message.encode(), (targetName, serverPort))
    clientSocket.close()


def UDPserver():
    global online
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', 50000))
    while run_flag:
        # print('...')
        message, cilentAddress = serverSocket.recvfrom(2048)
        if message.decode() == '_online_true':
            online = 1
            continue
        if message.decode() == '_check_online':
            if run_flag:
                sendToServer('_online_true')
            continue
        if message.decode() == '_shutdown':
            break
    print('UDP server shutdown!')
    serverSocket.close()


def _timeout():
    global online
    print('not online!')
    if end_flag:
        change_(0)
    online = 2


def online_check():
    # print('check')
    global online
    timer = threading.Timer(1, _timeout)
    timer.daemon = True
    timer.start()
    sendToServer('_check_online')
    while online != 2 and run_flag:
        if online == 1:
            # print('yes, online!')
            timer.cancel()
            change_(1)
            break


def checking():
    global online
    global end_flag
    while end_flag:
        online = 0
        online_check()
        time.sleep(3)


def send_end_message():
    serverPort = 50000
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.sendto('_shutdown'.encode(), ('127.0.0.1', serverPort))
    clientSocket.close()

    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect(('127.0.0.1', serverPort))
    clientSocket.send('_shutdown'.encode('utf-8'))
    clientSocket.close()

    serverPort = 51000
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect(('127.0.0.1', serverPort))
    clientSocket.send('__shutd'.encode('utf-8'))


'''
window.bind('<Return>',func)
window.resizable(0,0)
'''

# 运行
# --------------------------------------------

check_thread = threading.Thread(target=checking)
check_thread.daemon = True
check_thread.start()

server_Thread = threading.Thread(target=tcp_server)
server_Thread.daemon = True
server_Thread.start()

UDP_Thread = threading.Thread(target=UDPserver)
UDP_Thread.daemon = True
UDP_Thread.start()

file_send_thread = threading.Thread(target=file_receive_server)
file_send_thread.daemon = True
file_send_thread.start()

print('server is running now')
window.mainloop()
end_flag = False
send_end_message()

run_flag = False
check_thread.join()
server_Thread.join()
UDP_Thread.join()
print('bye!')
