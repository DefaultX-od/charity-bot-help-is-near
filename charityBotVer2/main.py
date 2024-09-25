import datetime
from pyexpat.errors import messages

import telebot
import os

from db_task_calls import *
from db_user_calls import *

from telebot import types, TeleBot

bot: TeleBot = telebot.TeleBot(os.getenv('botToken'))

def notify_user(userId, operationCode):

    message = ''

    match operationCode:
        case 'wellcome':
            message='Поздравляем! Теперь вы являетесь участником данного благотворительного проекта./nДля продолжения необходимо выбрать вашу роль в проекте.'
        case '#03':
            message = 'Информация о вас была успешно обновлена!'
        case '#04':
            message = 'Ваш профиль был удален! Для возобновления сотрудничества вы сможете зарегестрироваться снова!'
        case '#06':
            message = 'Информация о задании была успешно обновлена!'
        case '#07':
            message = 'Задание было удалено!'
        case '#08':
            message = 'Вам успешно задана роль в проекте: '+ get_user_type(userId)
        case '#11v':
            message = 'Вы были успешно назначаны на задание!'
        case '#11d':
            message = 'На ваше задание был назначен волонтер! Узнать подробную информацию вы сможете простомотрев ваше задание!'
        case '#12v':
            message = 'Вы были сняты с задания!'
        case '#12d':
            message = 'Ваше задание потеряло своего волонтера! Узнать подробную информацию вы сможете простомотрев ваше задание!'
        case '#13v':
            message = 'Вы выполнили задание!'
        case '#13d':
            message = 'Ваше задание успешно отмечено как выполненное!'
        case '#17':
            message = 'Вы были заблокированны администратором!'


    bot.send_message(userId, message)
    pass

@bot.message_handler(commands=['special'])
def special(message):
    if is_user_registred(message.from_user.id):
        user_type = get_user_type(message.from_user.id)
        print(user_type)
        if user_type =='admin':
            keyboard = types.InlineKeyboardMarkup()
            key_type1 = types.InlineKeyboardButton(text='Управление пользователями', callback_data='#14')
            key_type2 = types.InlineKeyboardButton(text='Управление заданиями', callback_data='#18')
            keyboard.add(key_type1)
            keyboard.add(key_type2)
            pass
        elif user_type == 'blocked':
            bot.send_message(message.from_user.id, 'Вы заблокированы!')
            pass
        else:
            keyboard = types.InlineKeyboardMarkup()
            key_type1 = types.InlineKeyboardButton(text='Редактировать профиль', callback_data='#03' + str(message.from_user.id))
            key_type2 = types.InlineKeyboardButton(text='Удалить профиль', callback_data='#05' + str(message.from_user.id))
            keyboard.add(key_type1)
            keyboard.add(key_type2)
        bot.send_message(message.from_user.id, text='Выберите действие', reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, 'Давайте познакомимся, как вас зовут?')
        bot.register_next_step_handler(message, get_name, 'add')
    pass


@bot.message_handler(commands=['start'])
def start(message):
    if is_user_registred(message.from_user.id):
        if get_user_type(message.from_user.id) == 'blocked':
            bot.send_message(message.from_user.id, 'Вы заблокированы!')
            pass
        else:
            bot.send_message(message.from_user.id, 'Добро пожаловать обратно!')
            task(message)
    else:
        bot.send_message(message.from_user.id, 'Давайте познакомимся, как вас зовут?')
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
    contact = ''
    try:
        phone = int(message.text)
        try:
            contact = str('@' + message.from_user.username)
        except Exception:
            contact = str(phone)
        if phone >= 70000000000 and phone <= 89999999999:
            # bot.send_message(message.from_user.id, 'УРА!')
            get_role(message, name, surname, address, phone, contact, action)
        else:
            bot.send_message(message.from_user.id, 'Введите в формате 7/8xxxxxxxxxx')
            bot.register_next_step_handler(message, get_phone, name, surname, address, action)
    except Exception:
        bot.send_message(message.from_user.id, 'Цифрами, пожалуйста')
        bot.register_next_step_handler(message, get_phone, name, surname, address, action)

def get_role(message, name, surname, address, phone, contact, action):

    if action=='add':
        add_user(message.from_user.id, name, surname, address, phone, contact)
        notify_user(message.from_user.id, 'wellcome')
    elif action=='edit':
        edit_user(message.from_user.id, name, surname, address, phone, contact)
        notify_user(message.from_user.id, '#03')

    cursor = get_roles_count()
    keyboard = types.InlineKeyboardMarkup()
    currentId = 0
    for row in cursor:
        print(row)
        cursor.execute(
            'select id_user_type, ru_user_type_name from user_types where id_user_type>%s and regestration_allowed=true',
            (currentId,))
        for row in cursor:
            currentId = row[0]
            key_type = types.InlineKeyboardButton(text=row[1], callback_data='#08' + str(currentId))
            keyboard.add(key_type)
    bot.send_message(message.from_user.id, text='Ваша роль в проекте?', reply_markup=keyboard)

@bot.message_handler(commands=['task'])
def task(message):
    if is_user_registred(message.from_user.id):
        if get_user_type(message.from_user.id) == 'desp':
            keyboard = types.InlineKeyboardMarkup()
            key_type1 = types.InlineKeyboardButton(text='Посмотреть ваши задания', callback_data='#02')
            key_type2 = types.InlineKeyboardButton(text='Разместить новое задание', callback_data='#01')
            keyboard.add(key_type1)
            keyboard.add(key_type2)
            bot.send_message(message.from_user.id, text='Выберите действие', reply_markup=keyboard)
            pass
        elif get_user_type(message.from_user.id) == 'vol':
            keyboard = types.InlineKeyboardMarkup()
            key_type1 = types.InlineKeyboardButton(text='Посмотреть ваши задания', callback_data='#02')
            key_type2 = types.InlineKeyboardButton(text='Взять новое задание', callback_data='#00')
            keyboard.add(key_type1)
            keyboard.add(key_type2)
            bot.send_message(message.from_user.id, text='Выберите действие', reply_markup=keyboard)
            pass
        elif get_user_type(message.from_user.id) == 'blocked':
            bot.send_message(message.from_user.id, 'Вы были заблокированы!')
            pass
    else:
        start(message)

def create_category(message):
    bot.send_message(message.chat.id, 'Введите название категории')
    bot.register_next_step_handler(message, get_category_name, 'create', 0)
    pass

def edit_category(message, categoryId):
    bot.send_message(message.chat.id, 'Введите название категории')
    bot.register_next_step_handler(message, get_category_name, 'edit', categoryId)
    pass

def get_category_name(message, action, categoryId):
    name = message.text
    bot.send_message(message.chat.id, 'Введите описание категории')
    bot.register_next_step_handler(message, get_category_description, action, name, categoryId)
    pass

def get_category_description(message, action, name, categoryId):
    description = message.text
    if action == 'create':
        createCategory(name, description)
    elif action == 'edit':
        updateCategory(categoryId, name, description)
    pass

def create_task(message, categoryId):
    bot.send_message(message.chat.id, 'Введите название задания')
    bot.register_next_step_handler(message, get_task_name, 'create', categoryId)


def get_task_name(message, action, id):
    name = message.text
    print(name)
    bot.send_message(message.from_user.id, 'Введите подробное описание задания')
    bot.register_next_step_handler(message, get_task_desription, action, name, id)


def get_task_desription(message, action, name, id):
    description = message.text
    bot.send_message(message.from_user.id, 'Введите дату в формате yyyy-mm-d')
    bot.register_next_step_handler(message, get_task_date, action, name, description, id)


def get_task_date(message, action, name, description, id):
    try:
        date = datetime.date.fromisoformat(message.text)
        if action == 'edit':
            updateTask(message.from_user.id, id, name, description, date)
        elif action == 'create':
            createTask(message.from_user.id, id, name, description, date)
            bot.send_message(message.from_user.id, 'Ваше задание было размешено!')
            task(message)
    except ValueError:#14
        bot.send_message(message.from_user.id, 'Введите дату в формате yyyy-mm-d')
        bot.register_next_step_handler(message, get_task_date, action, name, description, id)


def show_tasks_categories(userId):
    keyboard = types.InlineKeyboardMarkup()
    cursor = getTaskCategories()
    role = get_user_type(userId)
    if role == 'admin':
        key_type1 = types.InlineKeyboardButton(text='Добавить', callback_data='#20')
        keyboard.add(key_type1)
    for row in cursor:
        key_type = types.InlineKeyboardButton(text=row[1], callback_data='#09' + str(row[0]))
        print(row)
        keyboard.add(key_type)
    bot.send_message(userId, text='Выберите категорию:', reply_markup=keyboard)

def show_tasks(call):
    categoryId = (int(call.data[3:len(call.data)]))
    print('cateid ' + str(categoryId))
    cursor = getTasksByCategory(categoryId)
    keyboard = types.InlineKeyboardMarkup()
    if cursor.rowcount > 0:
        for row in cursor:
            key_type = types.InlineKeyboardButton(text=row[1], callback_data='#10' + str(row[0]))
            keyboard.add(key_type)
        bot.send_message(call.message.chat.id, text='Выберите задание:', reply_markup=keyboard)
    else:
        bot.send_message(call.message.chat.id, 'В данной категории нет заданий, выберите другую категорию:')
        show_tasks_categories(call.message.chat.id)


def show_all_users_tasks(userId):
    if get_user_type(userId) == 'desp':

        if len(list(getAllTasksByDespId(userId))) > 0:
            cursor = getAllTasksByDespId(userId)
            for row in cursor:
                keyboard = types.InlineKeyboardMarkup()
                key1 = types.InlineKeyboardButton(text='Изменить', callback_data='#06' + str(row[0]))
                key3 = types.InlineKeyboardButton(text='Завершить', callback_data='#13' + str(row[0]))
                key2 = types.InlineKeyboardButton(text='Удалить', callback_data='#07' + str(row[0]))
                keyboard.add(key1, key2)
                keyboard.add(key3)
                bot.send_message(userId, text=row[1], reply_markup=keyboard)
        else:
            bot.send_message(userId, 'У вас нет текущих заданий!')

    elif get_user_type(userId) == 'vol':

        if isVolOnTask(userId):
            keyboard = types.InlineKeyboardMarkup()
            key_type = types.InlineKeyboardButton(text='отказаться', callback_data='#12' + str(getTaskByVolId(userId)))
            keyboard.add(key_type)
            bot.send_message(userId, text=show_task_description(getTaskByVolId(userId)), reply_markup=keyboard)
        else:
            bot.send_message(userId, 'У вас нет текущих заданий!')
    elif get_user_type(userId) == 'admin':
        cursor = getTasksByCategory()
        for row in cursor:
            keyboard = types.InlineKeyboardMarkup()
            key2 = types.InlineKeyboardButton(text='Удалить', callback_data='#07' + str(row[0]))
            keyboard.add(key2)
            bot.send_message(userId, text=row[1], reply_markup=keyboard)

    pass


def show_task_description(taskId):
    cursor = getTaskById(taskId)
    return cursor.fetchone()[1]
    # bot.send_message(call.message.chat.id, )


def assign_task(taskId, call):
    if isVolOnTask(call.message.chat.id):
        bot.send_message(call.message.chat.id, 'Для того чтобы взять новое задание необходимо выполнить текущее!')
        keyboard = types.InlineKeyboardMarkup()
        key_type = types.InlineKeyboardButton(text='отказаться',
                                              callback_data='#12' + str(getTaskByVolId(call.message.chat.id)))
        keyboard.add(key_type)
        bot.send_message(call.message.chat.id, text=show_task_description(getTaskByVolId(call.message.chat.id)),
                         reply_markup=keyboard)
    else:
        setTaskExecutor(taskId, call.message.chat.id)
        print(taskId, call.message.chat.id)

    pass

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == '#00':
        show_tasks_categories(call.message.chat.id)

    elif call.data == '#01':
        show_tasks_categories(call.message.chat.id)

    elif call.data == '#02':
        show_all_users_tasks(call.message.chat.id)

    elif str(call.data[0:3]) == '#03':
        bot.send_message(call.message.chat.id, 'Введите имя')
        bot.register_next_step_handler(call.message, get_name, 'edit')
        pass

    elif str(call.data[0:3]) == '#04':
        userId = (int(call.data[3:len(call.data)]))
        notify_user(userId, '#04')
        delete_user(userId)

    elif str(call.data[0:3]) == '#05':
        userId = (int(call.data[3:len(call.data)]))
        keyboard = types.InlineKeyboardMarkup()
        key_type1 = types.InlineKeyboardButton(text='Да', callback_data='#04' + str(userId))
        key_type2 = types.InlineKeyboardButton(text='Нет', callback_data='npd' + str(userId))
        keyboard.add(key_type1)
        keyboard.add(key_type2)
        bot.send_message(call.message.chat.id, text='Вы уверены что хотите удалить профиль?', reply_markup=keyboard)

    elif str(call.data[0:3]) == '#06':
        taskId = (int(call.data[3:len(call.data)]))
        bot.send_message(call.message.chat.id, 'Введите название задания')
        bot.register_next_step_handler(call.message, get_task_name, 'edit', taskId)

    elif str(call.data[0:3]) == '#07':
        bot.delete_message(call.message.chat.id, call.message.id)
        taskId = (int(call.data[3:len(call.data)]))
        notify_user(call.message.chat.id, '#07')
        try:
            notify_user(get_vol_by_task_id(taskId), '#12v')
        except:
            print('no vol assigned!')
        deleteTask(taskId)


    elif str(call.data[0:3]) == '#08':
        roleId = int(call.data[3:len(call.data)])
        set_role(roleId, call.message.chat.id)
        notify_user(call.message.chat.id, '#08')

    elif str(call.data[0:3]) == '#09':
        categoryId = (int(call.data[3:len(call.data)]))
        if get_user_type(call.message.chat.id) == 'desp':
            bot.send_message(call.message.chat.id, getTaskCategoryDescription(categoryId))
            create_task(call.message, categoryId)
        elif get_user_type(call.message.chat.id) == 'vol':
            bot.send_message(call.message.chat.id, getTaskCategoryDescription(categoryId))
            # bot.delete_message(call.message.chat.id, call.message.id)
            show_tasks(call)
        elif get_user_type(call.message.chat.id) == 'admin':
            keyboard = types.InlineKeyboardMarkup()
            key_type1 = types.InlineKeyboardButton(text='Изменить', callback_data='#21'+str(categoryId))
            key_type2 = types.InlineKeyboardButton(text='Удалить', callback_data='#22'+str(categoryId))
            key_type3 = types.InlineKeyboardButton(text='Просмотреть', callback_data='#23'+str(categoryId))
            keyboard.add(key_type1, key_type2, key_type3)
            bot.send_message(call.message.chat.id, text=getTaskCategoryDescription(categoryId), reply_markup=keyboard)
            pass

    elif str(call.data[0:3]) == '#10':
        taskId = (int(call.data[3:len(call.data)]))
        show_task_description(taskId)
        keyboard = types.InlineKeyboardMarkup()
        if get_user_type(call.message.chat.id) == 'vol':
            key_type = types.InlineKeyboardButton(text='Взяться', callback_data='#11' + str(taskId))
            keyboard.add(key_type)
        elif get_user_type(call.message.chat.id) == 'admin':
            key_type = types.InlineKeyboardButton(text='Удалить', callback_data='#07'+str(taskId))
            keyboard.add(key_type)
        bot.send_message(call.message.chat.id, text=show_task_description(taskId), reply_markup=keyboard)

    elif str(call.data[0:3]) == '#11':
        taskId = (int(call.data[3:len(call.data)]))
        print('asign ' + str(taskId))
        assign_task(taskId, call)
        notify_user(call.message.chat.id, '#11v')
        notify_user(get_desp_by_task_id(taskId), '#11d')
        pass
    elif str(call.data[0:3]) == '#12':
        taskId = (int(call.data[3:len(call.data)]))
        print(taskId)
        removeVolFromTask(taskId, call.message.chat.id)
        notify_user(call.message.chat.id, '#12v')
        try:
            notify_user(get_desp_by_task_id(taskId), '#12d')
        except:
            print('no vol is on this task!')
        pass

    elif str(call.data[0:3]) == '#13':
        taskId = (int(call.data[3:len(call.data)]))
        setTaskDone(taskId)
        notify_user(call.message.chat.id, '#13d')
        try:
            notify_user(get_vol_by_task_id(taskId), '#13v')
        except:
            print('no vol is on this task!')
        pass
    
    elif call.data == '#14':
        cursor = get_roles_count()
        keyboard = types.InlineKeyboardMarkup()
        currentId = 0
        for row in cursor:
            print(row)
            cursor.execute(
                'select id_user_type, ru_user_type_name from user_types where id_user_type>%s and regestration_allowed=true',
                (currentId,))
            for row in cursor:
                currentId = row[0]
                key_type = types.InlineKeyboardButton(text=row[1], callback_data='#15'+str(row[0]))
                keyboard.add(key_type)
            bot.send_message(call.message.chat.id, text='Выберите категорию пользователей для управления', reply_markup=keyboard)
        pass

    elif str(call.data[0:3]) == '#15':
        roleId = (int(call.data[3:len(call.data)]))
        cursor = get_users_by_type(roleId)
        keyboard = types.InlineKeyboardMarkup()
        for row in cursor:
            key_type = types.InlineKeyboardButton(text=row[1], callback_data='#16' + str(row[0]))
            keyboard.add(key_type)
        bot.send_message(call.message.chat.id, text='Выберите пользователя для управления',
                         reply_markup=keyboard)

    elif str(call.data[0:3]) == '#16':
        userId = (int(call.data[3:len(call.data)]))
        cursor = get_user_info(userId)
        for row in cursor:
            keyboard = types.InlineKeyboardMarkup()
            key_type1 = types.InlineKeyboardButton(text='Удалить', callback_data='#05' + str(row[0]))
            key_type2 = types.InlineKeyboardButton(text='Заблокировать', callback_data='#17' + str(row[0]))
            keyboard.add(key_type1, key_type2)
        bot.send_message(call.message.chat.id, text=row[1], reply_markup=keyboard)

    elif str(call.data[0:3]) == '#17':
        userId = (int(call.data[3:len(call.data)]))
        set_role(4, userId)
        bot.send_message(userId, 'Вы были заблокированы!')
        bot.send_message(call.message.chat.id, 'Пользователь был заблокирован!')
        pass

    elif call.data == '#18':
        keyboard = types.InlineKeyboardMarkup()
        key_type1 = types.InlineKeyboardButton(text='Управление категориями', callback_data='#19')
        keyboard.add(key_type1)
        bot.send_message(call.message.chat.id, text='Выберите действие', reply_markup=keyboard)
        pass

    elif call.data == '#19':
        show_tasks_categories(call.message.chat.id)
        pass

    elif call.data == '#20':
        create_category(call.message)
        pass

    elif str(call.data[0:3]) == '#21':
        categoryId = (int(call.data[3:len(call.data)]))
        edit_category(call.message, categoryId)
        pass

    elif str(call.data[0:3]) == '#22':
        categoryId = (int(call.data[3:len(call.data)]))
        deleteCategory(categoryId)
        pass

    elif str(call.data[0:3]) == '#23':
        show_tasks(call)
        pass


bot.polling(non_stop=True)
