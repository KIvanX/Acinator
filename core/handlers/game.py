
from aiogram import types, F

from config import dp, bot, WIN_ADVANCE
from core.keyboards.basic import add_chance_keyboard, finish_keyboard, check_person_keyboard
from aiogram.fsm.context import FSMContext

from core.utils.basic import ask_question
from core.utils import database
from core.states import GameStates


@dp.callback_query(F.data.in_(['game', 'game_yes', 'game_no', 'game_skip', 'continue']))
async def game(call: types.CallbackQuery, state: FSMContext, connector):
    persons = await database.get_persons(connector)
    answers = await database.get_answers(connector)

    if call.data == "game":
        rating = {i: 0 for i in persons}
        await state.update_data(rating=rating)
    elif call.data != 'continue':
        rating = {int(k): v for k, v in (await state.get_data())['rating'].items()}
        quest_i = (await state.get_data())['quest_i']
        k = {'game_yes': 1, 'game_no': -1, 'game_skip': 0}[call.data]

        for i in persons:
            if quest_i in answers[i]:
                rating[i] += k * answers[i][quest_i]
                if k == answers[i][quest_i] == 0 or k == answers[i][quest_i] == 1:
                    rating[i] += 0.5

        history = (await state.get_data()).get('history', [])
        await state.update_data(history=history + [(quest_i, k)], rating=rating)

        rat = sorted(rating.values(), reverse=True)
        if rat[0] - rat[1] >= WIN_ADVANCE:
            i = sorted(persons.keys(), reverse=True, key=lambda p: rating[p])[0]
            return await call.message.edit_text(f'Ваш персонаж {persons[i]}?',
                                                reply_markup=check_person_keyboard())
    else:
        rating = {int(k): v for k, v in (await state.get_data())['rating'].items()}

    await ask_question(rating, call, connector, state)


@dp.callback_query(F.data.in_(['check_person_yes', 'check_person_no']))
async def check_person(call: types.CallbackQuery, state: FSMContext, connector):
    persons = await database.get_persons(connector)
    rating = {int(k): v for k, v in (await state.get_data())['rating'].items()}

    if call.data == 'check_person_yes':
        await call.message.edit_text('Ура! Я снова угадал!', reply_markup=finish_keyboard())

    if call.data == 'check_person_no':
        rating[max(persons, key=lambda p: rating[p])] = 0
        await state.update_data(chance=(await state.get_data()).get('chance', 0) + 1, rating=rating)
        if (await state.get_data()).get('chance', 0) % 3 == 0:
            await call.message.edit_text('Продолжим?', reply_markup=add_chance_keyboard())
        else:
            await ask_question(rating, call, connector, state)


@dp.callback_query(F.data.in_(['chance_no']))
async def fail_finish(call: types.CallbackQuery, state: FSMContext, connector):
    persons = await database.get_persons(connector)
    rating = {int(k): v for k, v in (await state.get_data())['rating'].items()}

    await state.update_data(message_id=call.message.message_id)
    await state.set_state(GameStates.newPersonName)
    text = 'Ты победил! Найди своего персонажа в списке. Если его нет, введи имя своего персонажа\n\n'
    for p in sorted(persons, key=lambda i: rating[i], reverse=True)[:10]:
        text += '<b>' + persons[p] + '</b>\n'
    await call.message.edit_text(text, reply_markup=finish_keyboard())


@dp.message(GameStates.newPersonName)
async def name_of_new_person(message: types.Message, state: FSMContext):
    mes_id = (await state.get_data())['message_id']

    await message.delete()
    await state.update_data(name=message.text)
    await state.set_state(GameStates.newPersonQuestion)
    await bot.edit_message_text('Придумай факт о твоем персонаже, который поможет отличить его от '
                                'других персонажей\n\nНапример: <code>Любит читать</code>, '
                                '<code>Очень высокий</code>, <code>Связан с нинзя</code>',
                                message.chat.id, mes_id, reply_markup=finish_keyboard())


@dp.message(GameStates.newPersonQuestion)
async def question_of_new_person(message: types.Message, state: FSMContext, connector):
    state_data = await state.get_data()
    quest = message.text[0].lower() + message.text[1:]

    await message.delete()
    p_id = await database.add_character(connector, state_data['name'])
    q_id = await database.add_question(connector, quest)
    await database.add_answer(connector, p_id, q_id, True)

    for q_id, answer in set([(e1, e2) for e1, e2 in (await state.get_data()).get('history', [])]):
        await database.add_answer(connector, p_id, q_id, answer)

    await bot.edit_message_text('Твой персонаж добавлен. Спасибо за информацию!', message.chat.id,
                                state_data['message_id'], reply_markup=finish_keyboard())
