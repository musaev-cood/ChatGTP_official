from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import executor
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.filters.builtin import CommandHelp
import pyttsx3

from Config import bot
from Config import engine
from Config import SendMsgOrVoice

openai.api_key = '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'
dp = Dispatcher(bot, storage=Congig.storage)



class AI(StatesGroup):
    talk = State()


async def on_startup(dispatcher):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Запустить бота"),
            types.BotCommand("helps", "Вывести справку")
        ]
    )


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=1,
                              inline_keyboard=[[InlineKeyboardButton(text="Начать чат с ИИ", callback_data="start")]])
    await SendMsgOrVoice(message, f"Привет, {message.from_user.full_name}! Этот бот предоставит доступ к ChatGPT.", kb)


@dp.callback_query_handler(text='start')
async def chat_start(call: types.CallbackQuery, state: FSMContext):
    kb = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(text="Закончить чат", callback_data="start"),
         InlineKeyboardButton(text="Стереть память", callback_data="start")]])

    await SendMsgOrVoice(call, "Отправть сообщение, чтобы начать переписку", kb)
    await AI.talk.set()
    await state.update_data(history=[{"question": None, "answer": None}])


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = ("Список команд: ",
            "/start - Начать диалог",
            "/help - Получить справку")
    await SendMsgOrVoice(message, "\n".join(text))


@dp.callback_query_handler(text='back', state='*')
async def back(call: types.CallbackQuery, state: FSMContext):
    kb = InlineKeyboardMarkup(row_width=1,
                              inline_keyboard=[[InlineKeyboardButton(text="Начать чат с ИИ", callback_data="start")]])
    await SendMsgOrVoice(call, f"Привет, {call.from_user.full_name}! Этот бот предоставит доступ к ChatGPT.", kb)
    await state.finish()


@dp.callback_query_handler(text='clear', state='*')
async def clear(call: types.CallbackQuery, state: FSMContext):
    await SendMsgOrVoice(call, 'Память ИИ стерта')
    await state.update_data(history=[{"question": None, "answer": None}])


executor.start_polling(dp, on_startup=on_startup)
