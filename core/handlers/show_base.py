
from aiogram import types, F
from aiogram.fsm.context import FSMContext

from config import dp, bot, PAGE_N
from core.keyboards.basic import show_data_keyboard, show_menu_keyboard, show_base_keyboard, ok_keyboard
from core.utils import database
from core.states import GameStates
from core.utils.basic import answer_message
from core.utils.database import delete_answer


@dp.callback_query(F.data.in_(['show', 'show_q', 'show_p', 'show_left', 'show_right', 'show_sort']))
async def select_type_show(call: types.CallbackQuery, state: FSMContext, connector):
    state_data = (await state.get_data())
    if call.data == 'show':
        await state.clear()
        return await call.message.edit_text(f'Выбери тип', reply_markup=show_menu_keyboard())

    sort_by = state_data.get('sort_by', 'ID')
    if call.data == 'show_sort':
        sort_by = 'NAME' if sort_by == 'ID' else 'ID'
        await state.update_data(sort_by=sort_by)

    await state.update_data(num='')
    if 'type' not in state_data:
        await state.set_state(GameStates.showNumberData)
        await state.update_data(type=call.data[-1], page=0, message_id=call.message.message_id)
    f_type = (await state.get_data())['type']
    data = list((await (database.get_questions if f_type == 'q' else database.get_persons)(connector)).items())
    data.sort(key=lambda e: e[0 if sort_by == 'ID' else 1])

    if call.data in ['show_left', 'show_right']:
        if call.data == 'show_left':
            page = state_data['page'] - 1 if state_data['page'] > 0 else len(data) // PAGE_N
        else:
            page = state_data['page'] + 1 if state_data['page'] < len(data) // PAGE_N else 0
        await state.update_data(page=page)

    page = (await state.get_data()).get('page', 0)
    text = f'Введи номер или часть текста {"факта" if f_type == "q" else "персонажа"}\n\n'
    for i, t in data[page * PAGE_N: (page + 1) * PAGE_N]:
        text += f'{i}) {t}\n'
    text += f'\n Стр. {page + 1} из {len(data) // PAGE_N + 1}'
    await answer_message(call, state, text, show_data_keyboard(sort_by))


@dp.message(GameStates.showNumberData)
async def select_num_data(message: types.Message, state: FSMContext, connector):
    state_data = await state.get_data()
    t = state_data["type"]

    if state_data.get('num'):
        num = state_data['num']
        if message.content_type == 'text':
            nums = message.text.replace('\n', ' ').replace(',', ' ')
            for n in nums.split(' '):
                p_id, q_id = (state_data['num'], n) if t == 'p' else (n, state_data['num'])
                await delete_answer(connector, int(p_id), int(q_id))
        elif message.content_type == 'photo' and t == 'p':
            persons = await database.get_persons(connector)
            file = await bot.get_file(message.photo[-1].file_id)
            await bot.download_file(file.file_path, f'core/static/{persons[num]}.jpg')
    else:
        if message.text.isdigit():
            num = int(message.text)
        else:
            data = await (database.get_questions if t == 'q' else database.get_persons)(connector)
            results = [k for k, v in data.items() if message.text.lower() in v.lower()]
            if not results:
                await message.delete()
                return await message.answer('Ничего не найдено', reply_markup=ok_keyboard())
            num = results[0]
        await state.update_data(num=num)

    await message.delete()
    data = (await (database.get_questions if t == 'q' else database.get_persons)(connector))
    answers = await database.get_answers(connector)
    text = f' {f"Факты о персонаже {data[num]}" if t == "p" else f"Персонажи, для которых верно {data[num]}"}:\n\n'
    base = await (database.get_questions if t == 'p' else database.get_persons)(connector)

    for p in answers:
        for q in answers[p]:
            if answers[p][q] == 1:
                if p == num and t == "p" or q == num and t == "q":
                    text += f'{q}) {base[p if t == "q" else q]}\n'

    person = (await database.get_persons(connector))[num] if t == "p" else None
    text += f'\nВведи номера {"фактов" if t == "p" else "персонажей"}, которых хочешь удалить'
    text += '\nЕсли хочешь изменить картинку персонажа, отправь ее мне'
    await answer_message(message, state, text, show_base_keyboard(t), person)
