
from aiogram import types, F
from aiogram.fsm.context import FSMContext

from config import dp, bot
from core.keyboards.basic import show_data_keyboard, show_menu_keyboard, show_base_keyboard
from core.utils import database
from core.states import GameStates


@dp.callback_query(F.data.in_(['show', 'show_q', 'show_p', 'show_left', 'show_right']))
async def select_type_show(call: types.CallbackQuery, state: FSMContext, connector):
    if call.data == 'show':
        await state.clear()
        await call.message.edit_text(f'Выбери тип', reply_markup=show_menu_keyboard())
    else:
        state_data = await state.get_data()
        if 'type' not in state_data:
            await state.set_state(GameStates.showNumberData)
            await state.update_data(type=call.data[-1], page=0, message_id=call.message.message_id)
        f_type = (await state.get_data())['type']
        data = list((await (database.get_questions if f_type == 'q' else database.get_persons)(connector)).items())

        if call.data in ['show_left', 'show_right']:
            if call.data == 'show_left':
                page = state_data['page'] - 1 if state_data['page'] > 0 else len(data) // 30
            else:
                page = state_data['page'] + 1 if state_data['page'] < len(data) // 30 else 0
            await state.update_data(page=page)
        page = (await state.get_data())['page']

        text = f'Введи номер {"факта" if f_type == "q" else "персонажа"}:\n'
        for i, t in data[page * 30: (page + 1) * 30]:
            text += f'{i}) {t}\n'
        await call.message.edit_text(text, reply_markup=show_data_keyboard(page, len(data) // 30))


@dp.message(GameStates.showNumberData)
async def select_num_data(message: types.Message, state: FSMContext, connector):
    state_data = await state.get_data()
    t = state_data["type"]
    num = int(message.text)
    await message.delete()
    data = (await (database.get_questions if t == 'q' else database.get_persons)(connector))
    answers = await database.get_answers(connector)
    text = f' {"Факты о" if t == "p" else "Персонажи, для которых верно"} "{data[num]}":\n\n'
    base = (await (database.get_questions if t == 'p' else database.get_persons)(connector))

    for p in answers:
        for q in answers[p]:
            if answers[p][q] == 1:
                if p == num and t == "p" or q == num and t == "q":
                    text += base[p if t == 'q' else q] + '\n'

    await bot.edit_message_text(text, message.chat.id, state_data['message_id'], reply_markup=show_base_keyboard(t))
