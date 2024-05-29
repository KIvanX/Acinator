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

    quest_i = -1
    if call.data == 'previous':
        state_data = await state.get_data()
        history, n = state_data['history'], state_data['n']
        quest_i, k = history[-1]
        for i in persons:
            if quest_i in answers[i]:
                rating[i] -= k

        await state.update_data(rating=rating, quest_i=history[-1][0], history=history[:-1], n=n - 1)

    n = (await state.get_data()).get('n', 1)
    counter = {i: 0 for i in questions}
    max_rating = rating[max(rating.keys(), key=lambda p: rating[p])]
    applicants = list(filter(lambda p: rating[p] == max_rating, list(persons)))
    if len(applicants) < 3:
        applicants += list(filter(lambda p: rating[p] == max_rating - 1, list(persons)))[:len(applicants)]

    for i in applicants:
        for j in [q for q in questions if q in answers[i]]:
            counter[j] += 1

    history = (await state.get_data()).get('history', [])
    def act(q): return actual_question(q, counter[q], len(applicants), history)
    top_quest = sorted(list(questions), reverse=True, key=act)[:min(5, len(applicants))]

    if LOGS:
        print('_' * 100)
        print(f'applicants({len(applicants)}):', applicants)
        for i in sorted(persons.keys(), key=lambda i: rating[i], reverse=True)[:10]:
            print(f'{persons[i]}({rating[i]})', end=', ')
        print()
        print(counter)
        print([(questions[i], a) for i, a in history])
        print('act:', actual_question(top_quest[0], counter[top_quest[0]], len(applicants), history))

        print('top:', top_quest)

    max_rating = rating[max(rating.keys(), key=lambda p: rating[p])]
    progress = round((len(persons) - len(applicants)) / len(persons) * 100)
    quest_i = (random.choice(top_quest) if len(applicants) > 5 else top_quest[0]) if quest_i == -1 else quest_i

    if actual_question(quest_i, counter[quest_i], len(applicants), history) == 0:
        rating[[i for i in persons if max_rating == rating[i]][0]] += 3
        await state.update_data(rating=rating)

    text = f'{n}) Ваш персонаж {questions[quest_i]}?\nПрогресс: {progress}%'
    if not photo:
        bot_message = await call.message.edit_text(text, reply_markup=game_keyboard(len(history)))
    else:
        await call.message.delete()
        bot_message = await call.message.answer(text, reply_markup=game_keyboard(len(history)))

    await state.update_data(quest_i=quest_i, n=n + 1, bot_message_id=bot_message.message_id)


def actual_question(i, k, n, history):
    retry = sum([RETRY_FINE for q, a in history if q == i])
    return min(k, n - k) - retry


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
    except Exception as e:
        try:
            mes_id = state_data.get('message_id')
            await bot.edit_message_text(text, message.chat.id, mes_id, reply_markup=keyboard)
        except Exception as e:
            mes_id = (await message.answer(text, reply_markup=keyboard)).message_id
            try:
                await message.delete()
            except Exception as e:
                try:
                    await bot.delete_message(message.chat.id, state_data.get('message_id'))
                except Exception as e:
                    pass
    await state.update_data(message_id=mes_id)
