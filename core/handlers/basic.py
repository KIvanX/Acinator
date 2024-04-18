from aiogram import types, F
from aiogram.filters import Command

from config import dp
from core.keyboards.basic import get_main_keyboard
from aiogram.fsm.context import FSMContext

from core.utils.database import add_user, edit_user
from core.var import hello_text


@dp.message(Command(commands='start'))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    bot_message = await message.answer(hello_text, reply_markup=get_main_keyboard())
    await state.update_data(bot_message_id=bot_message.message_id)


@dp.callback_query(F.data == 'start')
async def start_call(call: types.CallbackQuery, state: FSMContext, connector):
    await edit_user(connector, call.message.chat.id, {'is_admin': True})
    await state.clear()
    await call.message.edit_text(hello_text, reply_markup=get_main_keyboard())



