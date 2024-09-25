import db_connector

def createCategory(name, description):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.callproc('create_category', [name, description])
    conn.commit()

def updateCategory(categoryId, name, description):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.callproc('update_category', [categoryId, name, description])
    conn.commit()

def deleteCategory(categoryId):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.callproc('delete_category', [categoryId, ])
    conn.commit()

def createTask(despId, categoryId, name, description, date):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.callproc('create_task', [despId, categoryId, name, description, date])
    conn.commit()


def updateTask(userId, taskId, name, description, date):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.callproc('update_task', [taskId, name, description])
    conn.commit()


def deleteTask(taskId):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.callproc('delete_task', [taskId])
    conn.commit()
    print("removed")


def getTaskCategories():
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.execute("select id_category, name from category")
    return cursor


def getTaskCategoryDescription(categoryId):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.execute("select description from category where id_category=%s", [categoryId, ])
    return cursor.fetchone()[0]


def getTasksByCategory(categoryId):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.callproc('get_task_light', [categoryId, ])
    conn.commit()
    return cursor


def getTaskName(taskId):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.execute('select name from tasks where id_task=%s', [taskId, ])
    return cursor.fetchone()[0]


def getTaskById(taskId):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.callproc('get_task_full', [taskId, ])
    return cursor


def getAllTasksByDespId(userId):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.callproc('get_tasks_by_desp_id', [userId, ])
    return cursor


def getTaskByVolId(userId):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.callproc('get_task_by_vol_id', [userId, ])
    return int(cursor.fetchone()[0])


def setTaskExecutor(taskId, userId):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.callproc('assign_task', [taskId, userId])
    conn.commit()


def setTaskDone(taskId):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.callproc('task_done', [taskId, ])
    conn.commit()


def isVolOnTask(userId):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.callproc('is_vol_on_task', [userId, ])
    if int(cursor.fetchone()[0]) > 0:
        return True
    else:
        return False


def removeVolFromTask(taskId, userId):
    conn = db_connector.connect()
    cursor = conn.cursor()
    cursor.callproc('remove_vol_from_task', [taskId, userId])
    conn.commit()
