import os
import telebot
import psycopg2
import datetime

from dotenv import load_dotenv
load_dotenv()

from telebot import types, TeleBot

bot: TeleBot = telebot.TeleBot(os.getenv('botToken'))


def dbConnect():
    dataBaseName = os.getenv('dataBaseName')
    userName = os.getenv('userName')
    userPassword = os.getenv('userPassword')
    hostName = os.getenv('hostName')
    try:
        conn = psycopg2.connect(dbname=dataBaseName, user=userName, password=userPassword, host=hostName)
        return conn
    except:
        print('Can`t establish connection to database')

def isUserAlreadyRegistred(userId):
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.execute('select count(id_user) from users where id_user=%s', (userId,))
    if cursor.fetchone()[0] > 0:
        return True
    else:
        return False
def getUserType(id):
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.callproc('get_user_type', [id,])
    # print(cursor.fetchone()[0])
    return cursor.fetchone()[0]

def createTask(despId, categoryId, name, description, date):
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.callproc('create_task',[despId, categoryId, name, description, date])
    conn.commit()

def updateTask(userId, taskId, name, description, date):
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.callproc('update_task', [taskId, name, description])
    conn.commit()

def deleteTask(taskId):
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.callproc('delete_task', [taskId])
    conn.commit()
    print("removed")
def getTaskCategories():
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.execute("select id_category, name from category")
    return cursor

def getTaskCategoryDescription(categoryId):
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.execute("select description from category where id_category=%s", [categoryId,])
    return cursor.fetchone()[0]

def getTasksByCategory(categoryId):
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.callproc('get_task_light',[categoryId,])
    conn.commit()
    return cursor

# def getCategoryByTask()

def getTaskName(taskId):
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.execute('select name from tasks where id_task=%s',[taskId, ])
    return cursor.fetchone()[0]

def getTaskById(taskId):
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.callproc('get_task_full', [taskId, ])
    return cursor

def getAllTasksByDespId(userId):
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.callproc('get_tasks_by_desp_id', [userId, ])
    return cursor

def getTaskByVolId(userId):
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.callproc('get_task_by_vol_id', [userId,])
    return int(cursor.fetchone()[0])

def setTaskExecutor(taskId, userId):
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.callproc('assign_task', [taskId, userId])
    conn.commit()
    bot.send_message(userId, "Задание назначено!")

    cursor.execute('select id_desp from tasks where id_task=%s',[taskId,])
    # bot.send_message(cursor.fetchone()[0], )
    keyboard = types.InlineKeyboardMarkup()
    key_type = types.InlineKeyboardButton(text="выполнено",callback_data="d" +str(taskId))
    keyboard.add(key_type)
    bot.send_message(cursor.fetchone()[0], text="Ваше задание, "+getTaskName(taskId),reply_markup=keyboard)

def setTaskDone(taskId):
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.callproc('task_done', [taskId, ])
    conn.commit()

def notifyDesp():
    pass
def isVolOnTask(userId):
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.callproc('is_vol_on_task', [userId,])
    if int(cursor.fetchone()[0])>0:
        return True
    else:
        return False

def removeVolFromTask(taskId, userId):
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.callproc('remove_vol_from_task', [taskId ,userId])
    conn.commit()
    pass

def addUser(id, name, surname, address, phone, userName):
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.callproc('add_user', [id, str(name), str(surname), str(address), phone, userName])
    conn.commit()
    keyboard = types.InlineKeyboardMarkup()

    cursor.execute('select count(id_user_type) from user_types')
    currentId = 0
    for row in cursor:
        print(row)
        cursor.execute('select id_user_type, ru_user_type_name from user_types where id_user_type>%s and regestration_allowed=true', (currentId,))
        for row in cursor:
            currentId = row[0]
            key_type = types.InlineKeyboardButton(text=row[1], callback_data="r"+str(currentId))
            keyboard.add(key_type)
    bot.send_message(id, text="Ваша роль в проекте?", reply_markup=keyboard)

    cursor.close()
    conn.close()

def editUser(id, name, surname, address, phone, userName):
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.callproc('edit_user', [id, str(name), str(surname), str(address), phone, userName])
    conn.commit()
    keyboard = types.InlineKeyboardMarkup()

    cursor.execute('select count(id_user_type) from user_types')
    currentId = 0
    for row in cursor:
        print(row)
        cursor.execute('select id_user_type, ru_user_type_name from user_types where id_user_type>%s and regestration_allowed=true', (currentId,))
        for row in cursor:
            currentId = row[0]
            key_type = types.InlineKeyboardButton(text=row[1], callback_data="r"+str(currentId))
            keyboard.add(key_type)
    bot.send_message(id, text="Ваша роль в проекте?", reply_markup=keyboard)

    cursor.close()
    conn.close()

def removeUser(id):
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.callproc('delete_user', [id,])
    conn.commit()

def setUserRole():
    pass

@bot.message_handler(commands=['special'])
def special(message):
    if(isUserAlreadyRegistred(message.from_user.id)):
        keyboard = types.InlineKeyboardMarkup()
        key_type1 = types.InlineKeyboardButton(text="Редактировать профиль", callback_data="pe"+str(message.from_user.id))
        key_type2 = types.InlineKeyboardButton(text="Удалить профиль", callback_data="pd"+str(message.from_user.id))
        keyboard.add(key_type1)
        keyboard.add(key_type2)
        bot.send_message(message.from_user.id, text="Выберите действие над профилем", reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, "Давайте познакомимся, как вас зовут?")
        bot.register_next_step_handler(message, get_name)
    pass
@bot.message_handler(commands=['start'])
def start(message):
    if(isUserAlreadyRegistred(message.from_user.id)):
        bot.send_message(message.from_user.id, "Добро пожаловать обратно!")
        task(message)
    else:
        bot.send_message(message.from_user.id, "Давайте познакомимся, как вас зовут?")
        bot.register_next_step_handler(message, get_name, 'add')

def get_name(message, action):
    name = message.text
    bot.send_message(message.from_user.id, 'Какая у тебя фамилия?')
    bot.register_next_step_handler(message, get_surname, name, action)

def get_surname(message, name, action):
    surname = message.text
    bot.send_message(message.from_user.id, 'В каком городе вы проживаете?')
    bot.register_next_step_handler(message, get_address, name, surname, action)

def get_address(message, name, surname, action):
    address = message.text
    bot.send_message(message.from_user.id, 'Введите номер вашего телефона в формате 7/8xxxxxxxxxx')
    bot.register_next_step_handler(message, get_phone, name, surname, address, action)

def get_phone(message, name, surname, address, action):
    try:
        phone = int(message.text)
        if phone >= 70000000000 and phone <=89999999999:
            if action == 'add':
                addUser(message.from_user.id, name, surname, address, phone, str("@" + message.from_user.username))
            elif action == 'edit':
                editUser(message.from_user.id, name, surname, address, phone, str("@" + message.from_user.username))
        else:
            bot.send_message(message.from_user.id, 'Введите в формате 7/8xxxxxxxxxx')
            bot.register_next_step_handler(message, get_phone, name, surname, address, action, id)
    except Exception:
        bot.send_message(message.from_user.id, 'Цифрами, пожалуйста')
        bot.register_next_step_handler(message, get_phone, name, surname, address)


@bot.message_handler(commands=['task'])
def task(message):
    if isUserAlreadyRegistred(message.from_user.id):
        if getUserType(message.from_user.id) == "desp":
            keyboard = types.InlineKeyboardMarkup()
            key_type1 = types.InlineKeyboardButton(text="Посмотреть ваши задания", callback_data="alltasks")
            key_type2 = types.InlineKeyboardButton(text="Разместить новое задание", callback_data="yesdesp")
            keyboard.add(key_type1)
            keyboard.add(key_type2)
            bot.send_message(message.from_user.id, text="Выберите действие", reply_markup=keyboard)
        elif getUserType(message.from_user.id) == "vol":
            keyboard = types.InlineKeyboardMarkup()
            key_type1 = types.InlineKeyboardButton(text="Посмотреть ваши задания", callback_data="alltasks")
            key_type2 = types.InlineKeyboardButton(text="Взять новое задание", callback_data="yesvol")
            keyboard.add(key_type1)
            keyboard.add(key_type2)
            bot.send_message(message.from_user.id, text="Выберите действие", reply_markup=keyboard)
    else:
        start(message)

def create_task(message, categoryId):
    bot.send_message(message.chat.id, "Введите название задания")
    bot.register_next_step_handler(message, get_task_name, "create", categoryId)

def get_task_name(message, action, id):
    name = message.text
    print(name)
    bot.send_message(message.from_user.id,"Введите подробное описание задания")
    bot.register_next_step_handler(message, get_task_desription, action, name, id)

def get_task_desription(message, action, name, id):
    description = message.text
    bot.send_message(message.from_user.id, "Введите дату в формате yyyy-mm-d")
    bot.register_next_step_handler(message, get_task_date, action, name, description, id)

def get_task_date (message, action, name, description, id):
    try:
        date = datetime.date.fromisoformat(message.text)
        if action == "edit":
            updateTask(message.from_user.id, id, name, description, date)
        elif action == "create":
            createTask(message.from_user.id, id, name, description, date)
            bot.send_message(message.from_user.id, "Ваше задание было размешено!")
            task(message)
    except ValueError:
        bot.send_message(message.from_user.id, "Введите дату в формате yyyy-mm-d")
        bot.register_next_step_handler(message, get_task_date, action, name, description, id)

def show_tasks_categories(userId):
    keyboard = types.InlineKeyboardMarkup()
    cursor = getTaskCategories()

    for row in cursor:
        print(row)
        key_type = types.InlineKeyboardButton(text=row[1], callback_data="c" + str(row[0]))
        keyboard.add(key_type)
    bot.send_message(userId, text="Выберите категорию:", reply_markup=keyboard)
def show_tasks(call):
    categoryId = (int(call.data[1:len(call.data)]))
    print("cateid "+str(categoryId))
    cursor = getTasksByCategory(categoryId)
    keyboard = types.InlineKeyboardMarkup()
    if cursor.rowcount>0:
        for row in cursor:
            print(row[1]+"djkldsf")
            key_type = types.InlineKeyboardButton(text=row[1], callback_data="t" + str(row[0]))
            keyboard.add(key_type)
        bot.send_message(call.message.chat.id, text="Выберите задание:", reply_markup=keyboard)
    else:
        bot.send_message(call.message.chat.id, "В данной категории нет заданий, выберите другую категорию:")
        show_tasks_categories(call.message.chat.id)

def show_all_users_tasks(userId):
    if getUserType(userId)=='desp':

        if len(list(getAllTasksByDespId(userId))) > 0:
            cursor = getAllTasksByDespId(userId)
            for row in cursor:
                keyboard = types.InlineKeyboardMarkup()
                key1 = types.InlineKeyboardButton(text="Изменить", callback_data="et" + str(row[0]))
                key3 = types.InlineKeyboardButton(text="Завершить", callback_data="d" + str(row[0]))
                key2 = types.InlineKeyboardButton(text="Удалить", callback_data="dt" + str(row[0]))
                keyboard.add(key1, key2)
                keyboard.add(key3)
                bot.send_message(userId, text=row[1], reply_markup=keyboard)
        else:
            bot.send_message(userId, "У вас нет текущих заданий!")

    elif getUserType(userId) == 'vol':

        if isVolOnTask(userId):
            keyboard = types.InlineKeyboardMarkup()
            key_type = types.InlineKeyboardButton(text="отказаться",callback_data="dv" + str(getTaskByVolId(userId)))
            keyboard.add(key_type)
            bot.send_message(userId, text=show_task_description(getTaskByVolId(userId)),reply_markup=keyboard)
        else:
            bot.send_message(userId, "У вас нет текущих заданий!")
    pass

def show_task_description(taskId):
    cursor = getTaskById(taskId)
    return cursor.fetchone()[1]
    # bot.send_message(call.message.chat.id, )

def assign_task(taskId, call):
    if isVolOnTask(call.message.chat.id):
        bot.send_message(call.message.chat.id,"Для того чтобы взять новое задание необходимо выполнить текущее!")
        keyboard = types.InlineKeyboardMarkup()
        key_type = types.InlineKeyboardButton(text="отказаться", callback_data="dv" + str(getTaskByVolId(call.message.chat.id)))
        keyboard.add(key_type)
        bot.send_message(call.message.chat.id, text=show_task_description(getTaskByVolId(call.message.chat.id)), reply_markup=keyboard)
    else:
        setTaskExecutor(taskId, call.message.chat.id)
        print(taskId, call.message.chat.id)

    pass

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    conn = dbConnect()
    cursor = conn.cursor()

    if call.data == 'yesvol':
        show_tasks_categories(call.message.chat.id)

    elif call.data == 'yesdesp':
        show_tasks_categories(call.message.chat.id)

    elif call.data == 'alltasks':
        show_all_users_tasks(call.message.chat.id)

    elif call.data == 'newtask':
        show_tasks_categories(call.message.chat.id)

    elif str(call.data[0:2]) == 'pe':
        bot.send_message(call.message.chat.id, "Введите имя")
        bot.register_next_step_handler(call.message, get_name, "edit")
        pass

    elif str(call.data[0:3]) == 'ypd':
        userId=(int(call.data[3:len(call.data)]))
        removeUser(userId)
        bot.send_message(call.message.chat.id, "Ваш профиль был удален! Для возобновления сотрудничества вы сможете зарегестрироваться снова!")

    elif str(call.data[0:2]) == 'pd':
        keyboard = types.InlineKeyboardMarkup()
        key_type1 = types.InlineKeyboardButton(text="Да", callback_data="ypd"+str(call.message.chat.id))
        key_type2 = types.InlineKeyboardButton(text="Нет", callback_data="npd"+str(call.message.chat.id))
        keyboard.add(key_type1)
        keyboard.add(key_type2)
        bot.send_message(call.message.chat.id, text="Вы уверены что хотите удалить профиль?", reply_markup=keyboard)

    elif str(call.data[0:2]) == "et":
        taskId=(int(call.data[2:len(call.data)]))
        bot.send_message(call.message.chat.id, "Введите название задания")
        bot.register_next_step_handler(call.message, get_task_name, "edit", taskId, call.message.id)

    elif str(call.data[0:2]) == "dt":
        bot.delete_message(call.message.chat.id, call.message.id)
        taskId=(int(call.data[2:len(call.data)]))
        deleteTask(taskId)

    elif call.data[0] == 'r':
        roleId = int(call.data[1:len(call.data)])
        cursor.execute("update users set id_user_type=%s where id_user=%s",(roleId, call.message.chat.id))
        conn.commit()
        bot.send_message(call.message.chat.id, "Теперь вы учавствуете в проекте как "+getUserType(call.message.chat.id))

    elif call.data[0] == 'c':
        categoryId=(int(call.data[1:len(call.data)]))
        bot.send_message(call.message.chat.id, getTaskCategoryDescription(categoryId))
        if getUserType(call.message.chat.id)=='desp':
            create_task(call.message, categoryId)
        elif getUserType(call.message.chat.id)=='vol':
            # bot.delete_message(call.message.chat.id, call.message.id)
            show_tasks(call)

    elif call.data[0] == 't':
        taskId=(int(call.data[1:len(call.data)]))
        show_task_description(taskId)
        keyboard = types.InlineKeyboardMarkup()
        key_type = types.InlineKeyboardButton(text="Взяться", callback_data="at" + str(taskId))
        keyboard.add(key_type)
        bot.send_message(call.message.chat.id, text=show_task_description(taskId), reply_markup=keyboard)

    elif str(call.data[0:2]) == "at":
        taskId=(int(call.data[2:len(call.data)]))
        print ("asign "+str(taskId))
        assign_task(taskId, call)
        pass
    elif str(call.data[0:2]) == "dv":
        taskId = (int(call.data[2:len(call.data)]))
        print(taskId)
        removeVolFromTask(taskId, call.message.chat.id)
        bot.send_message(call.message.chat.id, "Вы были сняты с задания")
        pass

    elif str(call.data[0:1]) == 'd':
        taskId = (int(call.data[1:len(call.data)]))
        setTaskDone(taskId)

bot.polling(non_stop=True)