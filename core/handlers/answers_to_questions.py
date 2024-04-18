import random

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from config import dp, bot
from core.handlers.basic import start_call
from core.keyboards.basic import fill_keyboard, fill_menu_keyboard, fill_data_keyboard, fill_select_num_keyboard
from core.utils import database
from core.states import GameStates


@dp.callback_query(F.data.in_(['fill', 'fill_q', 'fill_p', 'fill_left', 'fill_right']))
async def select_type_fill(call: types.CallbackQuery, state: FSMContext, connector):
    if call.data == 'fill':
        await state.clear()
        await call.message.edit_text(f'Выбери тип', reply_markup=fill_menu_keyboard())
    else:
        state_data = await state.get_data()
        if 'type' not in state_data:
            await state.set_state(GameStates.fillNumberData)
            await state.update_data(type=call.data[-1], page=0, message_id=call.message.message_id)
        f_type = (await state.get_data())['type']
        data = list((await (database.get_questions if f_type == 'q' else database.get_persons)(connector)).items())

        if call.data in ['fill_left', 'fill_right']:
            if call.data == 'fill_left':
                page = state_data['page'] - 1 if state_data['page'] > 0 else len(data) // 30
            else:
                page = state_data['page'] + 1 if state_data['page'] < len(data) // 30 else 0
            await state.update_data(page=page)
        page = (await state.get_data())['page']

        text = f'Введи номер {"факта" if f_type == "q" else "персонажа"}:\n'
        for i, t in data[page * 30: (page + 1) * 30]:
            text += f'{i}) {t}\n'
        await call.message.edit_text(text, reply_markup=fill_data_keyboard(page, len(data) // 30))


@dp.message(GameStates.fillNumberData)
async def select_num_data(message: types.Message, state: FSMContext, connector):
    state_data = await state.get_data()
    num = int(message.text)
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
        await call.answer('Больше нет вопросов без ответа')
        return await start_call(call, state) if 'p_id' in (await state.get_data()) else True

    p_id, q_id = random.choice(unknown)
    await state.update_data(p_id=p_id, q_id=q_id)
    await call.message.edit_text(f'{persons[p_id]} {questions[q_id]}?', reply_markup=fill_keyboard())
