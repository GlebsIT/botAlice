# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
import datetime
import json
import logging
import sqlite3

# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request

app = Flask(__name__)

logging.basicConfig(filename="sample.log", level=logging.DEBUG)

# Хранилище данных о сессиях.
sessionStorage = {}


# Задаем параметры приложения Flask.
@app.route("/", methods=['POST'])
def main():
    # Функция получает тело запроса и возвращает ответ.
    # logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    handle_dialog(request.json, response)

    # logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )


# Функция для непосредственной обработки диалога.
def handle_dialog(req, res):
    user_id = req['session']['user_id']
    sessionStorage[user_id] = {'suggests': []}
    res['response']['buttons'] = get_suggests(user_id)
    session_id = req['session']['session_id']
    message_id = req['session']['message_id']
    request = req['request']['original_utterance'].lstrip()
    response = 'ok'
    button = ''
    id_parents = ''
    id_skill = ''
    command = ''
    database = "../gosyslyga/project.db"
    logging.info('work: %r \n', "work")

    conn = create_connection(database)
    message = [user_id, req['session']['message_id'], req['session']['session_id'],
               request]
    results = get__last_message(conn, user_id)

    if results != None and not req['session']['new']:
        logging.info('results: %r \n', results[0])
        id_parents = results[0]

    logging.info('request: %r \n', request)
    skill = get__skill(conn, id_parents, request)

    if skill != None:
        response = skill[0]
        button = skill[1].split(',')
        #logging.info('button: %r \n', button)
        id_skill = str(skill[2])
        #logging.info('skill: %r \n', skill)
        command = skill[3]
        logging.info('commanda: %r \n', command)

    sessionStorage[user_id] = {
        'suggests': button
    }

    res['response']['text'] = response

    # Создание кнопок
    res['response']['buttons'] = get_suggests(user_id)
    message.append(res['response']['text'])
    today = datetime.datetime.today()
    message.append(today)
    message.append(id_skill)
    with conn:
        logging.info('message: %r \n', message)
        create_message(conn, message)
    return
    #
    #     # try:
    #     #     curmessage.execute("SELECT * FROM messages WHERE session_id = ? ORDER BY message_id DESC LIMIT 1",(session_id))
    #     #     result = curmessage.fetchall()
    #     # except sqlite3.DatabaseError as err:
    #     #     logging.info("Error: %r", err)
    #     # else:
    #     #     conn.commit()
    #
    # if results[0] == "ваше имя":
    #     res['response']['text'] = 'Ваша фамилия'
    #     # create a database connection
    #     with conn:
    #         # create a new teacher
    #         teachers = (request, user_id)
    #         create_teacher(conn, teachers)
    #         message.append(res['response']['text'])
    #         create_message(conn, message)
    #
    #     return
    #
    # if results[0] == "ваше фамилия":
    #     res['response']['text'] = 'Ваша фамилия'
    #     # create a database connection
    #     with conn:
    #         # create a new teacher
    #         teachers = (request, user_id)
    #         create_teacher(conn, teachers)
    #         message.append(res['response']['text'])
    #         create_message(conn, message)
    #     return
    #
    # if results[0] == "ваше отчество":
    #     res['response']['text'] = 'Ваша фамилия'
    #     # create a database connection
    #     with conn:
    #         # create a new teacher
    #         teachers = (request, user_id)
    #         create_teacher(conn, teachers)
    #         message.append(res['response']['text'])
    #         create_message(conn, message)
    #
    #     return
    #
    # if req['request']['original_utterance'].lower() in [
    #     'зарегистрироваться',
    #     'регистрация'
    # ]:
    #     res['response']['text'] = 'Вы учитель или родитель?'
    #     sessionStorage[user_id] = {
    #         'suggests': [
    #             "учитель",
    #             "родитель"
    #         ]
    #     }
    #     res['response']['buttons'] = get_suggests(user_id)
    #     message.append(res['response']['text'])
    #     with conn:
    #         create_message(conn, message)
    #     return
    #
    # if req['request']['original_utterance'].lower() in [
    #     'учитель',
    #     'я преподаватель',
    #     'преподаватель',
    #     'педагог',
    #     'тренер',
    #     'я тренер',
    #     'я преподаватель'
    # ]:
    #     res['response']['text'] = 'Ваше имя'
    #     message.append(res['response']['text'])
    #     with conn:
    #         create_message(conn, message)
    #     return
    #
    #
    #
    # # Пользователь хочет выйти из навыка
    # if req['request']['original_utterance'].lower() in [
    #     'закрыть',
    #     'выйти',
    # ]:
    #     res['response']['text'] = 'Сессия убита'
    #     res['response']['end_session'] = True
    #     message.append(res['response']['text'])
    #     with conn:
    #         create_message(conn, message)
    #     return
    #
    # # Если нет, то убеждаем его купить слона!
    # res['response']['text'] = 'Все говорят "%s", а ты купи слона!' % (
    #     req['request']['original_utterance']
    # )
    # message.append(res['response']['text'])
    # with conn:
    #     create_message(conn, message)
    # res['response']['buttons'] = get_suggests(user_id)


# Функция возвращает подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = []
    if session['suggests'] == '':
        return suggests

    for suggest in session['suggests']:
        if suggest != '':
            suggests.append({'title': suggest, 'hide': True})

    logging.info('suggests: %r \n', suggests)
    return suggests


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        logging.info('error bd: %r', e)

    return None


def create_teacher(conn, teacher):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO teachers(name,user_id)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, teacher)
    return cur.lastrowid


def create_message(conn, message):
    """
    Create a new project into the projects table
    :param conn:
    :param message:
    :return: request
    """
    sql = ''' INSERT INTO messages(user_id,message_id,session_id,request,response,data_today,id_skill)
              VALUES(?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, message)
    return cur.lastrowid


def get__last_message(conn, user_id):
    """
    Get message
    :param conn:
    :param session_id:
    :return: rezult
    """

    curmessage = conn.cursor()
    curmessage.execute("SELECT id_skill FROM messages WHERE user_id = ? ORDER BY data_today DESC LIMIT 1",
                       (user_id,))

    return curmessage.fetchone()


def get__skill(conn, id_parents, template):
    """
    Get message
    :param conn:
    :param id_parents:
    :param template:
    :return: rezult
    """

    curskill = conn.cursor()
    curskill.execute(
        "SELECT response, button, id_logic, template, command FROM logic_skill WHERE id_parents = ? ",
        (id_parents, ))
    spisok = curskill.fetchall()

    if len(spisok) == 1:
        return spisok[0]

    for element in spisok:
        logging.info('element[3]: %r \n', element[3])
        if element[3] == template:
            return element

    for element in spisok:
        logging.info('element[3_2]: %r \n', element[3])
        if template in element[3]:
            return element


#def find_medicine(text,id_rec):
 #   conn = sqlite3.connect("project.db")
 #   cursor = conn.cursor()
#
 #   jsonfile=open('lp2019.json','r',encoding='utf_8_sig')
  #  l=text.split()
   # for stroka in json.load(jsonfile):
    #   if stroka['MNN'] in l:
     #      print (stroka['Price'])
      #     product = [(None, stroka["Barcode"],id_rec, stroka['MNN'],
       #           stroka['Count'], stroka['Price'],stroka['ReleaseForm'])]
        #   cursor.executemany("INSERT INTO recipe_product VALUES (?,?,?,?,?,?,?)", product)
         #  conn.commit()
          # break

