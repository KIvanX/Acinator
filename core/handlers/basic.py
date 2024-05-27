from aiogram import types, F
from aiogram.filters import Command

from config import dp
from core.keyboards.basic import get_main_keyboard
from aiogram.fsm.context import FSMContext

from core.utils.basic import answer_message
from core.utils.database import get_user
from core.var import hello_text


@dp.message(Command(commands='start'))
async def start(message: types.Message, state: FSMContext, connector):
    await state.clear()
    user = await get_user(connector, message.from_user.id)
    bot_message = await message.answer(hello_text, reply_markup=get_main_keyboard(is_admin=user))
    await state.update_data(bot_message_id=bot_message.message_id)


@dp.callback_query(F.data == 'start')
async def start_call(call: types.CallbackQuery, state: FSMContext, connector):
    await state.clear()
    user = await get_user(connector, call.message.chat.id)
    await answer_message(call, state, hello_text, get_main_keyboard(is_admin=user))


@dp.callback_query(F.data == 'del')
async def delete_message(call: types.CallbackQuery):
    await call.message.delete()
