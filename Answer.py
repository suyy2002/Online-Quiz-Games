import random
import pymysql


# 连接数据库
def connect_db():
    db = pymysql.connect(host='localhost',
                         port=3306,
                         user='root',
                         passwd='mysqlpass',
                         db='question',
                         charset='utf8')
    return db

# 查询数据条数
def query_count():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('select max(id) from list')
    data = cursor.fetchall()
    db.close()
    return data[0][0]

# 选择问题
def select_question():
    count = query_count()
    num = random.randint(1, count)
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('select id,question from list where id = %s', num)
    data = cursor.fetchall()
    db.close()
    return data[0]

# 检查答案
def check_answer(id, answer):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('select answer from list where id = %s', id)
    data = cursor.fetchall()
    db.close()
    if data[0][0] == answer:
        return True
    else:
        return False

# 返回答案
def get_answer(id):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('select answer from list where id = %s', id)
    data = cursor.fetchall()
    db.close()
    return data[0][0]
