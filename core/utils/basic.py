import os
import random

from aiogram import types
from aiogram.types import FSInputFile, InputMediaPhoto

from config import WIN_ADVANCE, RETRY_FINE, LOGS, bot
from core.keyboards.basic import game_keyboard
from core.utils import database


async def ask_question(rating, call: types.CallbackQuery, connector, state, photo=False):
    persons = await database.get_persons(connector)
    answers = await database.get_answers(connector)
    questions = await database.get_questions(connector)

    if call.data == 'previous':
        state_data = await state.get_data()
        history, n = state_data['history'], state_data['n']
        quest_i, k = history[-1]
        for i in persons:
            if quest_i in answers[i]:
                rating[i] -= k * answers[i][quest_i]
                if k == answers[i][quest_i] == 0 or k == answers[i][quest_i] == 1:
                    rating[i] -= 0.5

        await state.update_data(rating=rating, quest_i=history[-1][0], history=history[:-1], n=n - 1)

    n = (await state.get_data()).get('n', 1)
    counter = {i: {1: 0, 0: 0, -1: 0} for i in questions}
    max_rating = rating[max(rating.keys(), key=lambda p: rating[p])]

    for i in persons:
        if max_rating - rating[i] < WIN_ADVANCE:
            for j in questions:
                answers[i][j] = 0 if j not in answers[i] else answers[i][j]
                counter[j][answers[i][j]] += 1 + (WIN_ADVANCE - max_rating + rating[i]) / 2

    history = (await state.get_data()).get('history', [])
    max_act = max([actual_question(i, counter, history) for i in questions])
    top_quest = list(filter(lambda i: max_act == actual_question(i, counter, history), questions))

    if LOGS:
        for i in sorted(persons.keys(), key=lambda i: rating[i], reverse=True)[:10]:
            print(f'{persons[i]}({rating[i]})', end=', ')
        print()
        print(counter)
        print([(questions[i], a) for i, a in history])

        for i in questions:
            print(i, actual_question(i, counter, history), end=', ')
        print()

        print(top_quest)

    max_rating = rating[max(rating.keys(), key=lambda p: rating[p])]
    progress = round((len(persons) - len([i for i in persons if max_rating - rating[i] < 2])) / len(persons) * 100)
    quest_i = random.choice(top_quest)

    if actual_question(quest_i, counter, history) <= 0:
        rating[[i for i in persons if max_rating == rating[i]][0]] += 3
        await state.update_data(rating=rating)

    text = f'{n}) Ваш персонаж {questions[quest_i]}?\nПрогресс: {progress}%'
    if not photo:
        bot_message = await call.message.edit_text(text, reply_markup=game_keyboard(len(history)))
    else:
        await call.message.delete()
        bot_message = await call.message.answer(text, reply_markup=game_keyboard(len(history)))

    await state.update_data(quest_i=quest_i, n=n + 1, bot_message_id=bot_message.message_id)


def actual_question(i, counter, history):
    retry = sum([RETRY_FINE if a else RETRY_FINE * 10 for q, a in history if q == i])
    reduce = sorted([counter[i][-1], counter[i][1]])
    if reduce[0] > 0:
        return reduce[0] - retry
    elif reduce[1] > 0 and counter[i][0] > 0:
        return (counter[i][1] - retry) / 10
    else:
        return 0


async def answer_message(data, state, text, keyboard, person_name=None):
    message: types.Message = data.message if isinstance(data, types.CallbackQuery) else data
    state_data = await state.get_data()

    if person_name:
        path = f'core/static/{person_name}.jpg'
        file = FSInputFile(path if os.path.exists(path) else 'core/static/none.jpg')
        try:
            await message.edit_media(InputMediaPhoto(media=file))
            return await message.edit_caption(caption=text, reply_markup=keyboard)
        except Exception:
            try:
                await message.delete()
            except Exception:
                try:
                    await bot.delete_message(message.chat.id, state_data.get('message_id'))
                except Exception:
                    pass
            mes_id = (await message.answer_photo(file, text, reply_markup=keyboard)).message_id
            await state.update_data(message_id=mes_id)
            return 0

    try:
        mes_id = (await message.edit_text(text, reply_markup=keyboard)).message_id
    except Exception:
        try:
            mes_id = state_data.get('message_id')
            await bot.edit_message_text(text, mes_id, message.chat.id, reply_markup=keyboard)
        except Exception:
            mes_id = (await message.answer(text, reply_markup=keyboard)).message_id
            try:
                await message.delete()
            except Exception:
                try:
                    await bot.delete_message(message.chat.id, state_data.get('message_id'))
                except Exception:
                    pass
    await state.update_data(message_id=mes_id)
