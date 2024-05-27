import random

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from config import dp, bot, PAGE_N
from core.handlers.basic import start_call
from core.keyboards.basic import fill_keyboard, fill_menu_keyboard, fill_data_keyboard, fill_select_num_keyboard, \
    ok_keyboard, new_question_keyboard
from core.utils import database
from core.states import GameStates
from core.utils.basic import answer_message


@dp.callback_query(F.data.in_(['fill', 'fill_q', 'fill_p', 'fill_left', 'fill_right', 'fill_sort']))
async def select_type_fill(call: types.CallbackQuery, state: FSMContext, connector):
    state_data = await state.get_data()
    if call.data == 'fill':
        await state.clear()
        return await answer_message(call, state, f'Выбери тип', fill_menu_keyboard())

    sort_by = state_data.get('sort_by', 'ID')
    if call.data == 'fill_sort':
        sort_by = 'NAME' if sort_by == 'ID' else 'ID'
        await state.update_data(sort_by=sort_by)

    if 'type' not in state_data:
        await state.set_state(GameStates.fillNumberData)
        await state.update_data(type=call.data[-1], page=0, message_id=call.message.message_id)
    f_type = (await state.get_data())['type']
    data = list((await (database.get_questions if f_type == 'q' else database.get_persons)(connector)).items())
    data.sort(key=lambda e: e[0 if sort_by == 'ID' else 1])

    if call.data in ['fill_left', 'fill_right']:
        if call.data == 'fill_left':
            page = state_data['page'] - 1 if state_data['page'] > 0 else len(data) // PAGE_N
        else:
            page = state_data['page'] + 1 if state_data['page'] < len(data) // PAGE_N else 0
        await state.update_data(page=page)
    page = (await state.get_data())['page']

    text = f'Введи номер или часть текста {"факта" if f_type == "q" else "персонажа"}\n\n'
    for i, t in data[page * PAGE_N: (page + 1) * PAGE_N]:
        text += f'{i}) {t}\n'
    text += f'\n Стр. {page + 1} из {len(data) // PAGE_N + 1}'
    await call.message.edit_text(text, reply_markup=fill_data_keyboard(sort_by))


@dp.message(GameStates.fillNumberData)
async def select_num_data(message: types.Message, state: FSMContext, connector):
    state_data = await state.get_data()

    if message.text.isdigit():
        num = int(message.text)
    else:
        data = await (database.get_questions if state_data["type"] == 'q' else database.get_persons)(connector)
        results = [k for k, v in data.items() if message.text.lower() in v.lower()]
        if not results:
            return await answer_message(message, state, 'Ничего не найдено', ok_keyboard())
        num = results[0]

    await message.delete()
    await state.update_data(num=num)
    data = (await (database.get_questions if state_data["type"] == 'q' else database.get_persons)(connector))

    text = f'Тебе будут предложены случайные вопросы с {"фактом" if state_data["type"] == "q" else "персонажем"} '
    await bot.edit_message_text(text + '"' + data[num] + '"', message.chat.id, state_data['message_id'],
                                reply_markup=fill_select_num_keyboard())


@dp.callback_query(F.data.in_(['fill_start', 'fill_yes', 'fill_no', 'fill_skip']))
async def fill(call: types.CallbackQuery, state: FSMContext, connector):
    state_data = await state.get_data()
    if call.data != 'fill_start':
        k = {'fill_yes': 1, 'fill_no': -1, 'fill_skip': 0}[call.data]
        await database.add_answer(connector, state_data['p_id'], state_data['q_id'], k)

    persons = await database.get_persons(connector)
    questions = await database.get_questions(connector)
    answers = await database.get_answers(connector)

    unknown = []
    for i in persons.keys():
        for j in questions.keys():
            if i not in answers or j not in answers[i]:
                unknown.append((i, j))

    if state_data.get('type'):
        unknown = list(filter(lambda pair: pair[0 if state_data['type'] == 'p' else 1] == state_data['num'], unknown))

    if not unknown:
        await answer_message(call, state, 'Больше нет вопросов без ответа', new_question_keyboard())
        return await start_call(call, state, connector) if 'p_id' in (await state.get_data()) else True

    p_id, q_id = random.choice(unknown)
    await state.update_data(p_id=p_id, q_id=q_id)
    await answer_message(call, state, f'{persons[p_id]} {questions[q_id]}?', fill_keyboard(), persons[p_id])


@dp.callback_query(F.data == 'add_new_question')
@dp.message(GameStates.addNewQuestion)
async def add_new_question(data, state: FSMContext, connector):
    await state.set_state(GameStates.addNewQuestion)
    if isinstance(data, types.Message):
        await database.add_question(connector, data.text)
        await data.delete()
        return await answer_message(data, state, '✅ Факт добавлен\n\nРекомендуется добавить персонажей через '
                                                 '📝 Выбрать факт, для которых он является правдой',
                                    new_question_keyboard())
    await answer_message(data, state, 'Отправь мне факт:', new_question_keyboard())
