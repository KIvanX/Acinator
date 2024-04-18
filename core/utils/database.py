from pprint import pprint

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
    for line in await connector.fetch('''SELECT * FROM character_question'''):
        if not line[0] in answers:
            answers[line[0]] = {}
        answers[line[0]][line[1]] = line[2]

    return answers


async def add_question(connector: connect, text):
    await connector.execute('''INSERT INTO question VALUES(default, $1)''', text)
    questions = await get_questions(connector)
    return [i for i in questions if questions[i] == text][0]


async def add_character(connector: connect, name):
    await connector.execute('''INSERT INTO character VALUES(default, $1)''', name)
    characters = await get_persons(connector)
    return [i for i in characters if characters[i] == name][0]


async def add_answer(connector: connect, p_id: int, q_id: int, answer: bool):
    await connector.execute('''INSERT INTO character_question VALUES($1, $2, $3)''', p_id, q_id, answer)


async def add_user(connector: connect, user_id: int):
    user = await connector.fetch("SELECT * FROM users WHERE id = $1", user_id)
    if not user:
        await connector.execute('INSERT INTO users VALUES($1, default, default, default)', user_id)


async def edit_user(connector: connect, user_id: int, data: dict):
    for key in data:
        await connector.execute(f'UPDATE users SET {key} = $1 WHERE id = $2', data[key], user_id)
