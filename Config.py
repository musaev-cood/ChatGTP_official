import openai
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import pyttsx3
import soundfile as sf
import os

bot = Bot(token='6116196699:AAFuaTa_k3OrOwBnhu3vLwEOSrLDg1l_7Gw')
storage = MemoryStorage()
engine = pyttsx3.init()


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
    request = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=history,
        max_tokens=500,
        temperature=1,
    )
    resp_ai = request['choices'][0]['message']['content']
    data[-1]['answer'] = resp_ai.replace('\n', '')
    text = f"{message.from_user.username}\nQ:{data[-1]['question']}\nA:{data[-1]['answer']}"
    data.append({"question": None, "answer": None})
    if len(data) > 10:
        await state.update_data(history=[{"question": None, "answer": None}])
    await state.update_data(history=data)
    await SendMsgOrVoice(message, resp_ai)


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
        await message.bot.send_voice(message.from_user.id, await TextToSpeech(message, text))
