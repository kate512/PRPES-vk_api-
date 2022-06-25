import vk_api
import withDB
import datetime
import math
import scipy.stats as sps

now = datetime.datetime.now()

# соединение с базой данных
db = withDB.sql_connection()
withDB.create_table(db)

#нахождение групп по заданному короткому имени сообщества(id)
def getGroups(screenName):
    groupsId = []
    groups = session.method("groups.getById", {"group_ids": screenName})
    for group in groups:
        withDB.insert_group(db, group["id"], group["screen_name"], group["name"])
        print("Введенные группы: id=", group["id"], "name=", group["name"])
        groupsId.append(group["id"])
    return groupsId

def getMembers(groupsId):
    membersStr = ""
    for groupId in groupsId:
        # Получаем id подписчиков
        members = session.method("groups.getMembers", {"group_id": groupId})["items"]
        # все id подписчиков помещаем в строку
        for memStr in members:
            membersStr += str(memStr) + ","
        # получаем информацию о подписчиков пачкой
        memberInfo = session.method("users.get", {"user_ids": membersStr, "fields": 'bdate'})
        membersStr = ""
        # проходимся по каждому пользоваетелю отдельно
        for i in range(0, len(memberInfo)):
            if withDB.checkRepeats(db, memberInfo[i]["id"], groupId):
                # проверяем наличие поля с днем рождения и наличия года в нем
                if 'bdate' in memberInfo[i] and len(memberInfo[i]["bdate"]) > 7:
                    bdate_year = memberInfo[i]['bdate'].split('.')
                    year = now.year - int(bdate_year[2])
                else:
                    year = 0
                withDB.insert_members(db, memberInfo[i]["id"], groupId, memberInfo[i]["first_name"], memberInfo[i]["last_name"], int(year))

def result(groupsId):
    print("Нулевая гипотеза: обе группы схожи по возрастному критерию \nАльтернатияная гипотеза: группы различны")
    # достоверность результатов теста составляет 95% alfa = 0.05
    # степень свободы
    n0 = withDB.getCountMembers(db, groupsId[0])
    n1 = withDB.getCountMembers(db, groupsId[1])
    df = n0 + n1 - 2
    # расчет Т статистики
    M0 = withDB.getAverageAge(db, groupsId[0])
    M1 = withDB.getAverageAge(db, groupsId[1])
    d = math.sqrt(withDB.getS(db, groupsId[0], M0, n0) / n0 + withDB.getS(db, groupsId[1], M1, n1) / n1)

    t = math.fabs(M0 - M1) / d
    # расчет Т критического альфа = 0,05 и степеней свободы = df
    tkr, p2 = sps.ttest_ind(withDB.getAges(db, groupsId[0]), withDB.getAges(db, groupsId[1]))
    tkr = math.fabs(tkr)
    print("Средний возраст подписчиков:\n       группы", groupsId[0], " -> ", '%.2f' % M0, "\n       группы", groupsId[1], " -> ", '%.2f' % M1)
    print("ВЫВОД:")
    if t > tkr:
        return print(
            "Нулевая гипотеза отвергается, группы различны по возрастному параметру так как вычисленное значение критерия( t=",
            '%.2f' % t, ") > табличного( tkr=", '%.2f' % tkr, ")")
    else:
        return print(
            "Нулевая гипотеза принимается, группы схожи по возрастному параметру так как вычисленное значение критерия( t=",
            '%.2f' % t, ") < табличного( tkr=", '%.2f' % tkr, ")")

######################################################################################################

token = input("Введите токен: ")

session = vk_api.VkApi(token=token)
vk = session.get_api()

screenNameGroups = input("Введите id(screen_name) групп для сравнения через запятую: ")

dbAdd = ""
while dbAdd != "1" and dbAdd != "2":
    dbAdd = input("Найти и добавить новую информацию для поиска или искать в базе?  1/2 ")
    if dbAdd != "1" and dbAdd != "2":
        print("попробуйте снова")

if dbAdd == "1":
    groupsId = getGroups(screenNameGroups)
    getMembers(groupsId)
    result(groupsId)

print("Success")


