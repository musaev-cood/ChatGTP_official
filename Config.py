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

async def SendMsgOrVoice(message, text, replymark=None):
    await message.bot.send_message(message.from_user.id, text, reply_markup=replymark)
