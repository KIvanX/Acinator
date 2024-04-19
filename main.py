import asyncpg
from aiogram import types
from config import bot, dp, env
from core.handlers import basic, game, add_person, answers_to_questions, show_base
import asyncio
from core.middlewares import add_user, basic
from core.utils.database import edit_user


@dp.startup()
async def on_start():
    commands = [types.BotCommand(command='start', description='Старт')]
    await bot.set_my_commands(commands)


@dp.shutdown()
async def on_final():
    await bot.session.close()


@dp.my_chat_member()
async def on_final(update: types.Update, connector):
    if update.new_chat_member.status == 'kicked':
        await edit_user(connector, update.chat.id, {'is_deleted': True})
    elif update.new_chat_member.status == 'member':
        await edit_user(connector, update.chat.id, {'is_deleted': False})


async def main():
    dp.update.middleware.register(basic.DatabaseConnectorMiddleware())
    dp.message.middleware.register(add_user.AddUserMiddleware())

    print('Processing...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
