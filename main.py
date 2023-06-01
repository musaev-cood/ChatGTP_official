from aiogram import Bot, Dispatcher, types
from aiogram import executor

bot = Bot(token='6116196699:AAFuaTa_k3OrOwBnhu3vLwEOSrLDg1l_7Gw')
dp = Dispatcher(bot)


async def on_startup(dispatcher):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Запустить бота"),
            types.BotCommand("helps", "Вывести справку")
        ]
    )


executor.start_polling(dp, on_startup=on_startup)
