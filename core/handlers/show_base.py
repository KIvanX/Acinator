
from aiogram import types, F
from aiogram.fsm.context import FSMContext

from config import dp, bot, PAGE_N
from core.keyboards.basic import show_data_keyboard, show_menu_keyboard, show_base_keyboard, ok_keyboard, \
    new_question_keyboard, new_question_check_keyboard, back_to_base_keyboard, back_to_base_element_keyboard
from core.utils import database
from core.states import GameStates
from core.utils.basic import answer_message
from core.utils.database import delete_answer


@dp.callback_query(F.data.in_(['base', 'base_q', 'base_p', 'base_left', 'base_right', 'base_sort']))
async def select_type_show(call: types.CallbackQuery, state: FSMContext, connector):
    state_data = (await state.get_data())
    if call.data == 'base':
        await state.clear()
        return await call.message.edit_text(f'Выбери тип', reply_markup=show_menu_keyboard())

    sort_by = state_data.get('sort_by', 'ID')
    if call.data == 'base_sort':
        sort_by = 'NAME' if sort_by == 'ID' else 'ID'
        await state.update_data(sort_by=sort_by)

    await state.update_data(num='')
    if 'type' not in state_data:
        await state.set_state(GameStates.showNumberData)
        await state.update_data(type=call.data[-1], page=0, message_id=call.message.message_id)
    f_type = (await state.get_data())['type']
    data = list((await (database.get_questions if f_type == 'q' else database.get_persons)(connector)).items())
    data.sort(key=lambda e: e[0 if sort_by == 'ID' else 1])

    if call.data in ['base_left', 'base_right']:
        if call.data == 'base_left':
            page = state_data['page'] - 1 if state_data['page'] > 0 else len(data) // PAGE_N
        else:
            page = state_data['page'] + 1 if state_data['page'] < len(data) // PAGE_N else 0
        await state.update_data(page=page, message_id=call.message.message_id)

    page = (await state.get_data()).get('page', 0)
    text = f'Введи номер или часть текста {"факта" if f_type == "q" else "персонажа"}\n\n'
    for i, t in data[page * PAGE_N: (page + 1) * PAGE_N]:
        text += f'{i}) {t}\n'
    text += f'\n Стр. {page + 1} из {len(data) // PAGE_N + 1}'
    await answer_message(call, state, text, show_data_keyboard(sort_by))


@dp.callback_query(F.data == 'base_element')
@dp.message(GameStates.showNumberData)
async def select_num_data(data, state: FSMContext, connector):
    message: types.Message = data if isinstance(data, types.Message) else data.message
    state_data = await state.get_data()
    t = state_data["type"]
    base = await (database.get_questions if t == 'p' else database.get_persons)(connector)
    base_e = await (database.get_questions if t == 'q' else database.get_persons)(connector)

    num = state_data['num']
    if isinstance(data, types.Message) and state_data.get('num'):
        if message.content_type == 'text':
            if message.text.strip() == 'DELETE':
                if t == 'p':
                    await database.delete_persons(connector, num)
                else:
                    await database.delete_question(connector, num)
                await message.delete()
                return await answer_message(message, state, 'Удалено', back_to_base_keyboard(t))
            nums = message.text.replace('\n', ' ').replace(',', ' ')
            for n in nums.split(' '):
                p_id, q_id = (state_data['num'], n) if t == 'p' else (n, state_data['num'])
                await delete_answer(connector, int(p_id), int(q_id))
        elif message.content_type == 'photo' and t == 'p':
            persons = await database.get_persons(connector)
            file = await bot.get_file(message.photo[-1].file_id)
            await bot.download_file(file.file_path, f'core/static/{persons[num]}.jpg')
    elif isinstance(data, types.Message):
        if message.text.isdigit():
            num = int(message.text)
        else:
            results = [k for k, v in base_e.items() if message.text.lower() in v.lower()]
            if not results:
                await message.delete()
                return await message.answer('Ничего не найдено', reply_markup=ok_keyboard())
            num = results[0]
        await state.update_data(num=num)
    else:
        await state.update_data(key_word=False)
        await state.set_state(GameStates.showNumberData)

    await message.delete()
    answers = await database.get_answers(connector)
    text = f'<u>{f"Факты о персонаже {base_e[num]}" if t == "p" else f"Персонажи с фактом: {base_e[num]}"} (_N)</u>\n'

    n = 0
    for p in answers:
        for q in answers[p]:
            if p == num and t == "p" or q == num and t == "q":
                n += 1
                if n < 50:
                    text += f'{q}) {base[q]}\n' if t == "p" else f'{p}) {base[p]}\n'
    text = text.replace('_N', str(n))

    person = (await database.get_persons(connector))[num] if t == "p" else None
    text += f'\nВведи номера {"фактов" if t == "p" else "персонажей"}, чтобы удалить связь\n'
    if t == 'p':
        text += '\nЕсли хочешь изменить картинку персонажа, отправь ее мне'
    text += f'\nДля удаления этого {"персонажа" if t == "p" else "факта"} введи DELETE'
    await answer_message(data, state, text, show_base_keyboard(t), person)


@dp.callback_query(F.data == 'add_new')
@dp.message(GameStates.addNewSome)
async def add_new(data, state: FSMContext, connector):
    await state.set_state(GameStates.addNewSome)
    state_data = await state.get_data()
    t = state_data["type"]
    base = await (database.get_questions if t == 'p' else database.get_persons)(connector)

    if isinstance(data, types.CallbackQuery):
        return await answer_message(data, state, 'Введи ключевое слово для поиска:', back_to_base_element_keyboard())

    if state_data.get('key_word'):
        p_id, q_id = (state_data['num'], int(data.text)) if t == 'p' else (int(data.text), state_data['num'])
        await database.add_answer(connector, p_id, q_id)
        await data.delete()
        await state.set_state()
        return await answer_message(data, state, '✅ Добавлено', back_to_base_element_keyboard())

    text, n = f'<u>Найденные {"факты" if t == "p" else "персонажи"} (_N)</u>\n', 0
    for i, txt in base.items():
        if data.text.lower() in txt.lower():
            n += 1
            if n < 50:
                text += f'{i}) {txt}\n'
    text = text.replace('_N', str(n))
    text += f'\n\nВведи номер нужного {"факта" if t == "p" else "персонажа"}'
    await state.update_data(key_word=True)
    await data.delete()
    await answer_message(data, state, text, back_to_base_element_keyboard())


@dp.callback_query(F.data == 'add_new_question')
@dp.callback_query(F.data == 'add_quest')
@dp.message(GameStates.addNewQuestion)
async def add_new_question(data, state: FSMContext, connector):
    await state.set_state(GameStates.addNewQuestion)
    if isinstance(data, types.Message):
        questions = await database.get_questions(connector)
        text, n = f'<u>Найденные факты (_N)</u>\n', 0
        for q_id, question in questions.items():
            if data.text.lower() in question.lower():
                n += 1
                if n < 50:
                    text += f'{q_id}) {question}\n'
        text = text.replace('_N', str(n))

        await state.update_data(check_quest=data.text)
        await data.delete()
        return await answer_message(data, state, text, new_question_check_keyboard())
    elif data.data == 'add_quest':
        await database.add_question(connector, (await state.get_data())['check_quest'])
        return await answer_message(data, state, '✅ Факт добавлен\n\nРекомендуется добавить персонажей через '
                                                 'Вопросы -> Выбрать факт, для которых этот факт является правдой',
                                    new_question_keyboard())
    await answer_message(data, state, 'Отправь мне ключевое слово факта, я поищу его в базе:',
                         new_question_keyboard())
