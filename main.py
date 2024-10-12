from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import *

api = '7735380637:AAHpdvn8A9aM7zctdMPntzEHaUfJoATj5wY'
bot = Bot(api)
dp = Dispatcher(bot, storage = MemoryStorage())

kb = ReplyKeyboardMarkup()
button4 = KeyboardButton(text='Регистрация')
button1 = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
button3 = KeyboardButton(text='Купить')
kb.add(button1,button2,button3,button4)
kb.resize_keyboard

keybord = InlineKeyboardMarkup()
but1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
but2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
keybord.add(but1,but2)

keybord_for_buy = InlineKeyboardMarkup()
but3 = InlineKeyboardButton(text='Product1', callback_data='product_buying')
but4 = InlineKeyboardButton(text='Product2', callback_data='product_buying')
but5 = InlineKeyboardButton(text='Product3', callback_data='product_buying')
but6 = InlineKeyboardButton(text='Product4', callback_data='product_buying')
keybord_for_buy.add(but3, but4, but5, but6)

class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State()
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)

@dp.message_handler(text = 'Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=keybord)

@dp.message_handler(text = 'Купить')
async def get_buying_list(message):
    c_f = get_all_products()
    for i in range(0,4):
        await message.answer(f'Название: {c_f[i][1]} | Описание: {c_f[i][2]}| Цена: {c_f[i][3]}')
        with open(f'{i}.jpg', 'rb') as img:
            await message.answer_photo(img)
    await message.answer('Выберите продукт для покупки: ', reply_markup=keybord_for_buy)

@dp.callback_query_handler(text = 'product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')

@dp.callback_query_handler(text = 'formulas')
async def get_formulas(call):
    await call.message.answer('для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5')

@dp.callback_query_handler(text = 'calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()

@dp.message_handler(state = UserState.age)
async def set_growth(message, state):
    await state.update_data(возраст=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def  set_weight(message, state):
    await state.update_data(рост=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(вес=message.text)
    data = await state.get_data()
    calories = 10*int(data['возраст'])+6.25*int(data['рост'])-5*int(data['вес'])+5
    await message.answer(f"Ваша норма калорий {calories}")
    await state.finish()

@dp.message_handler(text = 'Регистрация')
async def sing_up(message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()

@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    i_i = is_included(message.text)
    if i_i is True:
        await message.answer("Введите свой email:",)
    else:
        await state.update_data(username=message.text)
        await message.answer('Пользователь существует, введите другое имя')
        await RegistrationState.email.set()

@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer('Введите свой возраст:')
    await RegistrationState.age.set()

@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=message.text)
    data = await state.get_data()
    add_user(data['username'], data['email'], data['age'])
    await state.finish()



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
