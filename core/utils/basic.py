import random

from config import WIN_ADVANCE, RETRY_FINE
from core.keyboards.basic import game_keyboard
from core.utils import database


async def ask_question(rating, call, connector, state):
    persons = await database.get_persons(connector)
    answers = await database.get_answers(connector)
    questions = await database.get_questions(connector)

    n = (await state.get_data()).get('n', 1)
    counter = {i: {1: 0, 0: 0, -1: 0} for i in questions}
    max_rating = rating[max(rating.keys(), key=lambda p: rating[p])]

    for i in persons:
        if max_rating - rating[i] < WIN_ADVANCE:
            for j in questions:
                answers[i][j] = 0 if j not in answers[i] else answers[i][j]
                counter[j][answers[i][j]] += 1 + (WIN_ADVANCE - max_rating + rating[i]) / 2

    for i in sorted(persons.keys(), key=lambda i: rating[i], reverse=True)[:10]:
        print(f'{persons[i]}({rating[i]})', end=', ')
    print()

    print(counter)
    history = (await state.get_data()).get('history', [])
    print([(questions[i], a) for i, a in history])

    for i in questions:
        print(i, actual_question(i, counter, history), end=', ')
    print()

    max_act = max([actual_question(i, counter, history) for i in questions])
    top_quest = list(filter(lambda i: max_act == actual_question(i, counter, history), questions))
    print(top_quest)

    max_rating = rating[max(rating.keys(), key=lambda p: rating[p])]
    progress = round((len(persons) - len([i for i in persons if max_rating - rating[i] < 2])) / len(persons) * 100)
    quest_i = random.choice(top_quest)

    if actual_question(quest_i, counter, history) <= 0:
        rating[[i for i in persons if max_rating == rating[i]][0]] += 3
        await state.update_data(rating=rating)

    bot_message = await call.message.edit_text(f'{n}) Ваш персонаж {questions[quest_i]}?\nПрогресс: {progress}%',
                                               reply_markup=game_keyboard())

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
