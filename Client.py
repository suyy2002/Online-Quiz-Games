import socket
import threading
import json  # json.dumps(some)打包   json.loads(some)解包
import tkinter
import tkinter.messagebox
from tkinter.scrolledtext import ScrolledText  # 导入多行文本框用到的包

IP = ''
PORT = ''
user = ''
listbox1 = ''  # 用于显示在线用户的得分表
ii = 0  # 用于判断是开还是关闭列表框
users = []  # 在玩家列表
chat = '【答题】'  # 消息模式，默认【答题】

# 登陆窗口
loginRoot = tkinter.Tk()
loginRoot.title('知识竞答')
loginRoot['height'] = 110
loginRoot['width'] = 270
loginRoot.resizable(False, False)  # 限制窗口大小

IP1 = tkinter.StringVar()
IP1.set('127.0.0.1:8888')  # 默认显示的ip和端口
User = tkinter.StringVar()
User.set('')

# 服务器标签
labelIP = tkinter.Label(loginRoot, text='地址:端口')
labelIP.place(x=20, y=10, width=100, height=20)

entryIP = tkinter.Entry(loginRoot, width=80, textvariable=IP1)
entryIP.place(x=120, y=10, width=130, height=20)

# 用户名标签
labelUser = tkinter.Label(loginRoot, text='昵称')
labelUser.place(x=30, y=40, width=80, height=20)

entryUser = tkinter.Entry(loginRoot, width=80, textvariable=User)
entryUser.place(x=120, y=40, width=130, height=20)


# 登录按钮
def login(*args):
    global IP, PORT, user
    IP, PORT = entryIP.get().split(':')  # 获取IP和端口号
    PORT = int(PORT)  # 端口号需要为int类型
    user = entryUser.get()
    if not user:
        tkinter.messagebox.showerror('温馨提示', message='请输入任意的用户名！')
    else:
        loginRoot.destroy()  # 关闭窗口


loginRoot.bind('<Return>', login)  # 回车绑定登录功能
but = tkinter.Button(loginRoot, text='登录', command=login)
but.place(x=100, y=70, width=70, height=30)

loginRoot.mainloop()  # 进入消息循环

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建socket对象
s.connect((IP, PORT))  # 连接服务器
if user:
    s.send(user.encode())  # 发送用户名
else:
    s.send('no'.encode())  # 没有输入用户名则标记no

# 如果没有用户名则将ip和端口号设置为用户名
addr = s.getsockname()  # 获取客户端ip和端口号
addr = addr[0] + ':' + str(addr[1])
if user == '':
    user = addr

# 聊天窗口
# 创建图形界面
root = tkinter.Tk()
root.title('在线答题-' + user)  # 窗口命名为用户名
root['height'] = 400
root['width'] = 580
root.resizable(False, False)  # 限制窗口大小

# 创建多行文本框
listbox = ScrolledText(root)
listbox.place(x=5, y=0, width=450, height=320)
# 文本框使用的字体颜色
listbox.tag_config('red', foreground='red')
listbox.tag_config('blue', foreground='blue')
listbox.tag_config('green', foreground='green')
listbox.tag_config('pink', foreground='pink')
listbox.tag_config('brown', foreground='brown')
listbox.tag_config('black', foreground='black')
listbox.insert('end', '欢迎来到知识竞答 ！，每15秒发布一道题目\n答对加分，答错扣分，快来试试吧 ！', 'brown')

# 创建多行文本框, 显示在线用户得分表
listbox1 = tkinter.Listbox(root)
listbox1.place(x=445, y=0, width=120, height=320)


def showUsers():
    global listbox1, ii
    if ii == 1:
        listbox1.place(x=445, y=0, width=120, height=320)  # 显示在线用户得分表
        listbox.place(x=5, y=0, width=450, height=320)  # 显示消息列表
        ii = 0
    else:
        listbox1.place_forget()  # 隐藏控件
        listbox.place(x=5, y=0, width=570, height=320)  # 显示消息列表
        ii = 1


# 查看在线用户按钮
button1 = tkinter.Button(root, text='玩家列表', command=showUsers)  # 创建按钮
button1.place(x=485, y=320, width=90, height=30)   # 放置按钮

# 创建输入文本框和关联变量
a = tkinter.StringVar()
a.set('')
entry = tkinter.Entry(root, width=120, textvariable=a)
entry.place(x=5, y=350, width=570, height=40)


def send(*args):
    # 没有添加的话发送信息时会提示没有聊天对象
    users.append('【答题】')
    mes = entry.get() + ':;' + user + ':;' + chat
    s.send(mes.encode())
    a.set('')  # 发送后清空文本框


# 创建发送按钮
button = tkinter.Button(root, text='回答', command=send)  # 创建按钮
button.place(x=515, y=353, width=60, height=30)  # 放置按钮
root.bind('<Return>', send)  # 绑定回车发送信息


# 用于时刻接收服务端发送的信息并打印
def recv():
    global users
    while True:
        data = s.recv(1024)
        data = data.decode()
        # 没有捕获到异常则表示接收到的是在线用户列表
        try:
            data = json.loads(data)
            users = data
            listbox1.delete(0, tkinter.END)  # 清空列表框
            number = ('   在线玩家数: ' + str(len(data)))
            listbox1.insert(tkinter.END, number)
            listbox1.itemconfig(tkinter.END, fg='green', bg="#f0f0ff")
            listbox1.itemconfig(tkinter.END, fg='green')
            for i in range(len(data)):
                listbox1.insert(tkinter.END, (data[i]))
                listbox1.itemconfig(tkinter.END, fg='green')
        except:
            data = data.split(':;')
            data1 = data[0].strip()  # 答题正误
            data2 = data[1]  # 答题者的用户名
            data3 = data[2]  # 消息类型
            data1 = '\n' + data1
            if data3 == '【答题】':
                if data2 == user:
                    if data1 == '\n'+user+'：回答正确':
                        listbox.insert(tkinter.END, data1, 'green')  # 答对绿色显示
                    else:
                        listbox.insert(tkinter.END, data1, 'red')  # 答错红色显示
                else:
                    listbox.insert(tkinter.END, data1, 'blue')  # 其他玩家蓝色显示
                if len(data) == 4:
                    listbox.insert(tkinter.END, '\n' + data[3], 'pink')
            elif data3 == '【出题】':
                listbox.insert(tkinter.END, data1, 'black')  # 发布题目黑色显示
            listbox.see(tkinter.END)  # 显示在最后


r = threading.Thread(target=recv)
r.start()  # 开始线程接收信息

root.mainloop()
s.close()  # 关闭图形界面后关闭TCP连接
