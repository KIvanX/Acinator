import asyncpg
from asyncpg import connect

from config import env


async def get_persons(connector: connect):
    persons = {}
    for line in await connector.fetch('''SELECT * FROM character'''):
        persons[line[0]] = line[1]
    return persons


async def get_questions(connector: connect):
    questions = {}
    for line in await connector.fetch('''SELECT * FROM question'''):
        questions[line[0]] = line[1]
    return questions


async def get_answers(connector: connect):
    answers = {}
    for line in await connector.fetch('''SELECT * FROM characters_facts'''):
        if not line[0] in answers:
            answers[line[0]] = set()
        answers[line[0]].add(line[1])

    return answers


async def get_connector():
    connection = await asyncpg.connect(database='acinator',
                                       host=env.str('DB_HOST'),
                                       user=env.str('DB_USER'),
                                       password=env.str('DB_PASSWORD'))
    return connection


async def add_question(connector: connect, text):
    await connector.execute('''INSERT INTO question VALUES(default, $1)''', text)
    questions = await get_questions(connector)
    return [i for i in questions if questions[i] == text][0]


async def add_character(connector: connect, name):
    await connector.execute('''INSERT INTO character VALUES(default, $1)''', name)
    characters = await get_persons(connector)
    return [i for i in characters if characters[i] == name][0]


async def add_answer(connector: connect, p_id: int, q_id: int):
    await connector.execute('''INSERT INTO characters_facts VALUES($1, $2)''', p_id, q_id)


async def delete_answer(connector: connect, p_id: int, q_id: int):
    await connector.execute('''DELETE FROM characters_facts WHERE character_id = $1 AND question_id = $2''',
                            p_id, q_id)


async def add_user(connector: connect, user_id: int):
    user = await connector.fetch("SELECT * FROM users WHERE id = $1", user_id)
    if not user:
        await connector.execute('INSERT INTO users VALUES($1, default, default, default)', user_id)


async def get_user(connector: connect, user_id: int):
    line = (await connector.fetch("SELECT * FROM users WHERE id = $1", user_id))[0]
    return {'id': line[0], 'is_admin': line[1], 'id_deleted': line[2], 'created_at': line[3]}


async def edit_user(connector: connect, user_id: int, data: dict):
    for key in data:
        await connector.execute(f'UPDATE users SET {key} = $1 WHERE id = $2', data[key], user_id)


async def delete_persons(connector: connect, p_id):
    await connector.execute('DELETE FROM character WHERE id = $1',  p_id)


async def delete_question(connector: connect, q_id):
    await connector.execute('DELETE FROM question WHERE id = $1',  q_id)
