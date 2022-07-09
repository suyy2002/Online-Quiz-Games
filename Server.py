import socket
import threading
import queue
import json  # json.dumps(some)打包   json.loads(some)解包
import time
from Answer import *

IP = ''
PORT = 8888
que = queue.Queue()  # 用于存放客户端答题信息的队列
users = []  # 用于存放在线用户的信息  [conn, user, addr]
lock = threading.Lock()  # 创建锁, 防止多个线程写入数据的顺序打乱


# 将在线玩家存入online列表并返回
def onlines():
    online = []
    for i in range(len(users)):
        online.append(users[i][1] + '  ' + str(users[i][3]) + ' 分')
    return online


class GameServer(threading.Thread):
    global users, que, lock  # 全局变量
    question = select_question()
    scores = [10, 8, 6, 4]
    score = 0

    def __init__(self, port):
        threading.Thread.__init__(self)  # 初始化线程
        self.ADDR = ('', port)  # 创建socket对象
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建TCP套接字

    # 用于接收所有客户端发送答案的函数
    def tcp_connect(self, conn, addr):
        # 连接后将用户信息添加到users列表
        user = conn.recv(1024)  # 接收用户名
        user = user.decode()  # 解码

        for i in range(len(users)):  # 判断用户名是否重复
            if user == users[i][1]:  # 如果用户名重复
                print('User already exist')
                user = '' + user + '_1'  # 增加一个后缀

        if user == 'no':  # 如果用户名为no, 则
            user = addr[0] + ':' + str(addr[1])  # 将ip和端口号作为用户名
        users.append([conn, user, addr, 0, True])  # 将用户信息添加到users列表
        print(' 新的连接:', addr, ':', user)  # 打印用户名
        d = onlines()  # 有新连接则刷新客户端的在线用户显示
        self.recv(d, addr)  # 发送在线用户信息
        try:
            while True:
                data = conn.recv(1024)  # 接收客户端发送的信息
                data = data.decode()  # 解码
                self.recv(data, addr)  # 保存信息到队列
        except:
            print(user + ' 断开连接')
            self.delUsers(conn, addr)  # 将断开用户移出users
            conn.close()

    # 判断断开用户在users中是第几位并移出列表, 刷新客户端的在线用户显示
    def delUsers(self, conn, addr):
        a = 0
        for i in users:  # 判断断开用户是第几位
            if i[0] == conn:  # 如果是第几位
                users.pop(a)  # 将用户移出users
                print(' 在线用户: ', end='')  # 打印剩余在线用户(conn)
                d = onlines()  # 刷新客户端的在线用户显示
                self.recv(d, addr)  # 发送在线用户信息
                print(d)  # 打印剩余在线用户
                break
            a += 1

    # 将接收到的信息(ip,端口以及发送的信息)存入que队列
    def recv(self, data, addr):
        lock.acquire()  # 获取锁
        try:
            que.put((addr, data))  # 将接收到的信息存入队列
        finally:   # 释放锁
            lock.release()

    # 将队列que中的答案进行正误判断并发送给客户端
    def sendData(self):
        while True:
            if not que.empty():  # 如果队列不为空
                data = ''
                message = que.get()  # 取出队列第一个元素
                if isinstance(message[1], str):  # 如果data是str则返回Ture
                    repeat_flag = 0  # 初始化重复标志
                    for j in range(len(users)):
                        if message[0] == users[j][2]:  # 判断是谁发的答案
                            reply = message[1].split(':;')  # 将答案分割成列表
                            if check_answer(self.question[0], reply[0]):  # 如果答案正确
                                if users[j][4]:  # 判断用户是已经答题了还是未答题
                                    reply[0] = '回答正确'
                                    if self.score < len(self.scores):  # 按照答题顺序加分
                                        users[j][3] += self.scores[self.score]  # 加分
                                        self.score += 1  # 加次序
                                    else:  # 第四个之后的答题加最小分
                                        users[j][3] += self.scores[-1]  # 加分
                                    users[j][4] = False  # 将用户状态改为False,表示已经答题
                                else:  # 如果用户已经答题,则不能重复答题
                                    reply[0] = '请勿重复提交'
                                    repeat_flag = j  # 此类消息只发给用户本身
                            else:  # 如果答案错误
                                reply[0] = '回答错误'
                                users[j][3] -= 2  # 减2分
                            message = (message[0], reply[0] + ':;' + reply[1] + ':;' + reply[2])  # 组合判断结果
                            data = ' ' + users[j][1] + '：' + message[1]  # 组合发送的信息
                            break
                    if repeat_flag != 0:  # 如果是重复提交,则只发给用户本身
                        users[repeat_flag][0].send(data.encode())
                    else:  # 如果不是重复提交,则发给所有用户
                        for i in range(len(users)):
                            users[i][0].send(data.encode())  # 发送给所有用户
                    d = onlines()  # 刷新客户端的玩家得分表
                    self.recv(d, 404)  # 发送给所有用户
                if isinstance(message[1], list):  # 同上
                    # 如果是list则打包后直接发送，更新得分表
                    data = json.dumps(message[1])  # 将list转换为json格式
                    for i in range(len(users)):   # 发送给所有用户
                        try:
                            users[i][0].send(data.encode())  # 发送给所有用户
                        except:
                            pass

    # 出题
    def getQuestion(self):
        last_answer = get_answer(self.question[0])  # 获取上一题的答案
        self.question = select_question()  # 随机选择一个题目
        data = ('本题答案：'+last_answer+'\n\n'+self.question[1]+':; 服务器 :;【出题】')  # 准备发送字符串
        for i in range(len(users)):
            users[i][4] = True  # 每个用户都可以提交答案
            users[i][0].send(data.encode())  # 发送给每个用户

    # 15秒执行一次
    def wait(self):
        while True:
            self.getQuestion()  # 出题
            self.score = 0  # 初始化得分次序
            time.sleep(15)  # 等待15秒

    # 启动服务器
    def run(self):
        que = threading.Thread(target=self.wait)
        que.start()  # 启动线程
        self.s.bind(self.ADDR)  # 绑定端口
        self.s.listen(5)
        print('服务器正在运行中...')
        q = threading.Thread(target=self.sendData)
        q.start()  # 启动线程
        while True:
            conn, addr = self.s.accept()  # 等待客户端连接
            t = threading.Thread(target=self.tcp_connect, args=(conn, addr))
            t.start()  # 启动线程


if __name__ == '__main__':
    PORT = int(input('请输入端口号：'))
    cserver = GameServer(PORT)  # 创建服务器对象
    cserver.start()  # 启动服务器
    while True:
        time.sleep(1)  # 等待
