import sqlite3
from sqlite3 import Error

db = sqlite3.connect('server.db')

def sql_connection():
    try:
        db = sqlite3.connect("server.db")
        return db

    except Error:
        print("Ошибка")

#создание таблицы в БД
def create_table(db):
    cursor = db.cursor()

    cursor.execute("""create table if not exists groups(
            group_id integer PRIMARY KEY,
            group_screen_name text,
            group_name text)
    """)
    cursor.execute("""create table if not exists members(
            member_id integer,
            group_id integer,
            first_name  text,
            last_name   text,
            age integer)
    """)

def insert_group(db, group_id, group_screen_name, group_name):
    cursor = db.cursor()
    List = [group_id, group_screen_name, group_name]

    cursor.execute(f"select group_id from groups where group_id = {group_id}")
    if cursor.fetchone() is None:
        cursor.execute("insert into groups values(?,?,?);", List)
        db.commit()

def insert_members(db,  member_id, group_id, first_name, last_name, age):
    cursor = db.cursor()
    List = [member_id, group_id, first_name, last_name, age]

    cursor.execute(f"SELECT member_id, group_id FROM members WHERE group_id = {group_id} and member_id = {member_id}")
    if cursor.fetchone() is None:
        cursor.execute("insert into members values(?,?,?,?,?);", List)
        db.commit()

def getAverageAge(db, group_id):
    cursor = db.cursor()
    cursor.execute(f"SELECT age from members where members.group_id = {group_id} and age != 0")

    ages = cursor.fetchall()

    averageAge = 0

    for age in ages:
       averageAge += age[0]
    if len(ages) != 0:
        return averageAge / len(ages)
    else:
        return 1

def checkRepeats(db, member_id, group_id,):
    cursor = db.cursor()

    cursor.execute(f"SELECT member_id, group_id FROM members WHERE group_id = {group_id} and member_id = {member_id}")
    if cursor.fetchone() is None:
        return True
    else:
        return False

def getCountMembers(db, group_id):
    cursor = db.cursor()

    cursor.execute(f"SELECT	count(member_id) count FROM members WHERE	group_id = {group_id} AND age > 0")
    c = cursor.fetchall()
    for count in c:
       res = count[0]
    return res

def getS(db, group_id, M, count):
    cursor = db.cursor()

    cursor.execute(f"SELECT age FROM members WHERE group_id = {group_id} AND age > 0")
    ages = cursor.fetchall()
    sum = 0
    for age in ages:
        sum = sum + (age[0] - M)*(age[0] - M)

    return sum / (count - 1)

def getAges(db, group_id):
    cursor = db.cursor()
    cursor.execute(f"SELECT age from members where members.group_id = {group_id} and age != 0")

    res = cursor.fetchall()

    ages = []

    for age in res:
       ages.append(age[0])

    return ages