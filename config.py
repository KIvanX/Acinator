
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from environs import Env


env = Env()
env.read_env()

DEBUG = env.bool('DEBUG')
WIN_ADVANCE = 2
RETRY_FINE = 1
PAGE_N = 25
LOGS = True
QUESTIONS_TO_OFFER = 15

bot = Bot(token=env.str('DEBUG_TOKEN' if DEBUG else 'TOKEN'), parse_mode='HTML')
storage = RedisStorage.from_url('redis://localhost:6379')
dp = Dispatcher(storage=storage)
