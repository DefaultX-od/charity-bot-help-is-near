import db_connector

def is_user_registred(user_id):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.execute('select count(id_user) from users where id_user=%s', (user_id,))
    if cursor.fetchone()[0] > 0:
        cursor.close()
        conn.close()
        return True
    else:
        cursor.close()
        conn.close()
        return False


def add_user(id, name, surname, address, phone, user_name):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.callproc('add_user', [id, str(name), str(surname), str(address), phone, user_name])
    conn.commit()
    cursor.close()
    conn.close()


def set_role(roleId, userId):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.execute("update users set id_user_type=%s where id_user=%s", (roleId, userId))
    conn.commit()
    cursor.close()
    conn.close()


def get_roles_count():
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.execute('select count(id_user_type) from user_types')
    return cursor

 #        bot.send_message(call.message.chat.id,
 #                         "Теперь вы учавствуете в проекте как " + getUserType(call.message.chat.id))

def get_user_type(id):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.callproc('get_user_type', [id, ])
    data = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return data


def edit_user(id, name, surname, address, phone, user_name):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.callproc('edit_user', [id, str(name), str(surname), str(address), phone, user_name])
    conn.commit()
    cursor.close()
    conn.close()


def delete_user(id):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.callproc('delete_user', [id, ])
    conn.commit()
    cursor.close()
    conn.close()

def get_users_by_type(id):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.callproc('get_users_by_type', [id, ])
    return cursor

def get_user_info(id):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.callproc('get_user_info', [id, ])
    return cursor

def get_desp_by_task_id(id):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.callproc('get_desp_by_task_id', [id, ])
    data = cursor.fetchone()[0]
    return data

def get_vol_by_task_id(id):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.callproc('get_vol_by_task_id', [id, ])
    data = cursor.fetchone()[0]
    return data
