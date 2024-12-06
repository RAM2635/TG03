import logging
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import Bot, DefaultBotProperties
from aiogram.filters import Command

from dotenv import load_dotenv
import asyncio
import os
from db import init_db, add_student

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(
    token=BOT_TOKEN,
    session=AiohttpSession(),
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)


# Определение машины состояний
class StudentForm(StatesGroup):
    name = State()
    age = State()
    grade = State()


# Команда /start
@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Привет! Я помогу тебе зарегистрироваться. Как тебя зовут?")
    await state.set_state(StudentForm.name)


# Ввод имени
@router.message(StudentForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(StudentForm.age)


# Ввод возраста
@router.message(StudentForm.age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введи возраст числом.")
        return
    await state.update_data(age=int(message.text))
    await message.answer("В каком классе ты учишься?")
    await state.set_state(StudentForm.grade)


# Ввод класса
@router.message(StudentForm.grade)
async def process_grade(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_data["grade"] = message.text

    # Сохранение данных в базу данных
    add_student(user_data["name"], user_data["age"], user_data["grade"])

    await message.answer(
        f"Спасибо за регистрацию!\nИмя: {user_data['name']}\nВозраст: {user_data['age']}\nКласс: {user_data['grade']}"
    )
    await state.clear()


# Команда /cancel для выхода из любого состояния
@router.message(Command(commands=["cancel"]))
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Регистрация отменена.")


async def main():
    # Инициализация базы данных
    init_db()

    # Запуск бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
