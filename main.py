from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import executor
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.filters.builtin import CommandHelp
import openai
import soundfile as sf
import pyttsx3
import os

openai.api_key = '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'
bot = Bot(token='6167228366:AAEf89VX21CHSociIplWLCHWnvQc2jRianI')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
engine = pyttsx3.init()
userOpenAItext = {}


async def SendAllAdminChat(message, typeMSG):
    userID = message.from_user.id

    if message.from_user.username is not None:
        user_name = message.from_user.username
    elif message.from_user.first_name is not None or message.from_user.last_name is not None or message.from_user.full_name is not None:
        user_name = ''.join(
            [x for x in [message.from_user.first_name, message.from_user.last_name, message.from_user.full_name] if
             x is not None])
    else:
        user_name = userID

    userName = f"<b><a href='tg://user?id={userID}'>@{user_name}</a></b>"
    if int(message.from_user.id) != 5310314079:
        if typeMSG == 'message':
            await bot.send_message(5310314079, f"{userName} | {userID} | {message.text}", parse_mode='html')
        elif typeMSG == 'callback':
            await bot.send_message(5310314079, f'{userName} | {userID} | {message.data}', parse_mode='html')
        elif typeMSG == 'photo':
            await bot.send_message(5310314079, f"{userName} | {userID} | отправил фото", parse_mode='html')
            await bot.send_photo(5310314079, photo=message.photo[-1].file_id)
        elif typeMSG == 'video':
            await bot.send_message(5310314079, f"{userName} | {userID} | отправил видео", parse_mode='html')
            await bot.send_video(5310314079, video=message.video.file_id)
        elif typeMSG == 'audio':
            await bot.send_message(5310314079, f"{userName} | {userID} | отправил аудио", parse_mode='html')
            await bot.send_audio(5310314079, audio=message.audio.file_id)
        elif typeMSG == 'document':
            await bot.send_message(5310314079, f"{userName} | {userID} | отправил документ", parse_mode='html')
            await bot.send_document(5310314079, document=message.document.file_id)
        elif typeMSG == 'sticker':
            await bot.send_message(5310314079, f"{userName} | {userID} | отправил стикер", parse_mode='html')
            await bot.send_sticker(5310314079, sticker=message.sticker.file_id)
        elif typeMSG == 'voice':
            await bot.send_message(5310314079, f"{userName} | {userID} | отправил голосовое сообщение",
                                   parse_mode='html')
            await bot.send_voice(5310314079, voice=message.voice.file_id)
        else:
            await bot.send_message(5310314079, f"{userName} | {userID} | неизвестное сообщение", parse_mode='html')


class AI(StatesGroup):
    talk = State()


async def on_startup(dispatcher):
    print(dispatcher)
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Запустить бота"),
            types.BotCommand("helps", "Вывести справку")
        ]
    )


@dp.message_handler(state=AI.talk, content_types=types.ContentTypes.VOICE)
async def handle_voice(message: types.Message, state: FSMContext):
    await SendAllAdminChat(message, 'voice')

    userText = await SpeechToText(message)
    if message.voice:
        if userText is not None:
            await openAI(message, userText, state)
        else:
            await SendMsgOrVoice(message, 'Извините, голосовую запись не удалось распознать.')


@dp.message_handler(state=AI.talk, content_types=types.ContentTypes.TEXT)
async def chat_talk(message: types.Message, state: FSMContext):
    await SendAllAdminChat(message, 'message')
    userText = message.text
    await openAI(message, userText, state)


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await SendAllAdminChat(message, 'message')

    kb = InlineKeyboardMarkup(row_width=1,
                              inline_keyboard=[[InlineKeyboardButton(text="Начать чат с ИИ", callback_data="start")]])
    await SendMsgOrVoice(message, f"Привет, {message.from_user.full_name}! Этот бот предоставит доступ к ChatGPT.", kb)


async def openAI(message: types.Message, userMSG, state):
    data = await state.get_data()
    data = data.get('history')
    kb = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(text="Закончить чат", callback_data="back"),
         InlineKeyboardButton(text="Стереть память", callback_data="clear")]])
    await SendMsgOrVoice(message, "ИИ думает...", kb)

    history = []
    if len(data) > 1:
        for index in range(0, len(data)):
            if data[index].get('question') is None:
                data[index]['question'] = userMSG
                d = {"role": "user", "content": data[index]['question']}
                history.append(d)
            else:
                d = [{"role": "user", "content": data[index]['question']},
                     {"role": "assistant", "content": data[index].get('answer')}]
                history += d
    else:
        data[0]['question'] = userMSG
        d = {"role": "user", "content": data[0].get('question')}
        history.append(d)
    try:
        request = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=history,
            max_tokens=500,
            temperature=1,
        )
        resp_ai = request['choices'][0]['message']['content']
        data[-1]['answer'] = resp_ai.replace('\n', '')
        text = f"{message.from_user.username}\nQ:{data[-1]['question']}\nA:{data[-1]['answer']}"
        print(text)
        data.append({"question": None, "answer": None})
        if len(data) > 10:
            await state.update_data(history=[{"question": None, "answer": None}])
        await state.update_data(history=data)
        await SendMsgOrVoice(message, resp_ai)
    except:
        kb = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
            [InlineKeyboardButton(text="Закончить чат", callback_data="start")]])
        resp_ai = "Ошибка сети ChatGTP..."
        await SendMsgOrVoice(message, resp_ai, kb)


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    await SendAllAdminChat(message, 'message')

    text = ("Список команд: ",
            "/start - Начать диалог",
            "/help - Получить справку")
    await SendMsgOrVoice(message, "\n".join(text))


@dp.callback_query_handler(text='start')
async def chat_start(call: types.CallbackQuery, state: FSMContext):
    await SendAllAdminChat(call, 'callback')

    kb = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(text="Закончить чат", callback_data="start"),
         InlineKeyboardButton(text="Стереть память", callback_data="start")]])

    await SendMsgOrVoice(call, "Отправть сообщение, чтобы начать переписку", kb)
    await AI.talk.set()
    await state.update_data(history=[{"question": None, "answer": None}])


@dp.callback_query_handler(text='back', state='*')
async def back(call: types.CallbackQuery, state: FSMContext):
    await SendAllAdminChat(call, 'callback')

    kb = InlineKeyboardMarkup(row_width=1,
                              inline_keyboard=[[InlineKeyboardButton(text="Начать чат с ИИ", callback_data="start")]])
    await SendMsgOrVoice(call, f"Привет, {call.from_user.full_name}! Этот бот предоставит доступ к ChatGPT.", kb)
    await state.finish()


@dp.callback_query_handler(text='clear', state='*')
async def clear(call: types.CallbackQuery, state: FSMContext):
    await SendAllAdminChat(call, 'callback')

    await SendMsgOrVoice(call, 'Память ИИ стерта')
    await state.update_data(history=[{"question": None, "answer": None}])
@dp.message_handler(content_types=['voice'], state='*')
async def send_voice(message: types.Message):
    await SendAllAdminChat(message, 'voice')


@dp.callback_query_handler(text='sendtext', state='*')
async def sendstext(call: types.CallbackQuery):
    await SendAllAdminChat(call, 'callback')

    await call.bot.send_message(call.from_user.id, userOpenAItext[call.from_user.id])
    await call.answer('Готово')


@dp.message_handler(content_types=['photo'], state='*')
async def send_photo(message: types.Message):
    await SendAllAdminChat(message, 'photo')


@dp.message_handler(content_types=['audio'], state='*')
async def send_audio(message: types.Message):
    await SendAllAdminChat(message, 'audio')


@dp.message_handler(content_types=['video'], state='*')
async def send_video(message: types.Message):
    await SendAllAdminChat(message, 'video')


@dp.message_handler(content_types=['document'], state='*')
async def send_document(message: types.Message):
    await SendAllAdminChat(message, 'document')


@dp.message_handler(content_types=['sticker'], state='*')
async def send_sticker(message: types.Message):
    await SendAllAdminChat(message, 'sticker')


async def SpeechToText(message):
    import speech_recognition as sr
    voice = message.voice
    voice_file = await bot.get_file(voice.file_id)
    await voice_file.download(destination_file=f'{message.from_user.id}-voice.ogg')
    data, samplerate = sf.read(f'{message.from_user.id}-voice.ogg')
    sf.write(f'{message.from_user.id}-voice.wav', data, samplerate)
    os.remove(f'{message.from_user.id}-voice.ogg')

    filename = f'{message.from_user.id}-voice.wav'
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio_data = r.record(source)
        try:
            text = r.recognize_google(audio_data, language='ru-RU')
        except:
            text = None
    return text


async def TextToSpeech(message, text):
    engine.save_to_file(text, f'{message.from_user.id}-voice.wav')
    engine.runAndWait()
    voice = types.InputFile(open(f'{message.from_user.id}-voice.wav', 'rb'))
    return voice


async def SendMsgOrVoice(message, text, replymark=None):
    async def check_english_words(text_check):
        import re
        english_words = re.findall(r'\b[a-zA-Z]+\b', text_check)
        if len(english_words) > 5:
            return True
        else:
            return False

    if await check_english_words(text) or replymark is not None:
        await message.bot.send_message(message.from_user.id, text, reply_markup=replymark)
    else:
        kb = InlineKeyboardMarkup(row_width=1,
                                  inline_keyboard=[
                                      [InlineKeyboardButton(text="Прислать текст", callback_data="sendtext")]])
        await message.bot.send_voice(message.from_user.id, await TextToSpeech(message, text), reply_markup=kb)
        userOpenAItext[message.from_user.id] = text


if name == 'main':
    executor.start_polling(dp, skip_updates=True)