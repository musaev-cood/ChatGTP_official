from aiogram import Bot, Dispatcher, types
from aiogram import executor
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.filters.builtin import CommandHelp

bot = Bot(token='6116196699:AAFuaTa_k3OrOwBnhu3vLwEOSrLDg1l_7Gw')
dp = Dispatcher(bot)


async def on_startup(dispatcher):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Запустить бота"),
            types.BotCommand("helps", "Вывести справку")
        ]
    )


async def SendMsgOrVoice(message, text, replymark=None):
    await message.bot.send_message(message.from_user.id, text, reply_markup=replymark)


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(text="Начать чат с ИИ", callback_data="start")]])

    await SendMsgOrVoice(message, f"Привет, {message.from_user.full_name}! Этот бот предоставит доступ к ChatGPT.", kb)


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = ("Список команд: ",
            "/start - Начать диалог",
            "/help - Получить справку")

    await SendMsgOrVoice(message, "\n".join(text))


@dp.callback_query_handler(text='start')
async def chat_start(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(text="Закончить чат", callback_data="start"),
         InlineKeyboardButton(text="Стереть память", callback_data="start")]])

    await SendMsgOrVoice(call, "Отправть сообщение, чтобы начать переписку", kb)

executor.start_polling(dp, on_startup=on_startup)
