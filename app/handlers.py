from aiogram import F, Router, Bot
from aiogram.filters import Command, BaseFilter
from aiogram.types import Message, CallbackQuery, BufferedInputFile, InputMediaAudio, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from io import BytesIO

import keyboards.start_keyboard as start_kb

from static_files.bot_answers import GREETINGS

from workTools.WorkWithTTS import WorkWithTTS

#Можно использовать чтобы отслеживать голосовые сообщения
class VoiceFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return bool(message.voice)

class Flag(StatesGroup):
    presentation_text = State()

router = Router()
user_message = F.data.split()

@router.message(Command("start", "restart"))
async def command_start(message: Message):
    await message.answer(GREETINGS, reply_markup = start_kb.start)

@router.callback_query(F.data == 'backStartDelete')
async def back_to_start(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(GREETINGS, reply_markup = start_kb.start)

@router.callback_query(F.data == 'backStart')
async def back_to_start(callback: CallbackQuery):
    await callback.message.edit_text(GREETINGS, reply_markup = start_kb.start)

@router.callback_query(F.data == 'performance')
async def performance(callback: CallbackQuery, bot: Bot):
    await bot.edit_message_media(
            chat_id = callback.message.chat.id,
            message_id = callback.message.message_id,
            media = InputMediaAudio(
                media = FSInputFile('C:/Users/Proger/Documents/AI-expert_call/app/static_files/TTS.mp3'), #TODO: аудио с представлением продукта
                caption = 'Представление продукта' #TODO: текст с представлением продукта
            ),
            reply_markup = start_kb.back_to_start_delete
        )

@router.callback_query(F.data == 'question')
async def question(callback: CallbackQuery):
    await callback.answer('Задайте вопрос текстом или голосом', show_alert = True)

@router.callback_query(F.data == 'compare')
async def compare(callback: CallbackQuery):
    await callback.message.edit_text('Выберете продукт для сравнения', reply_markup = start_kb.back_to_start) # reply_markap = compare kb

@router.callback_query(F.data == 'certificate')
async def compare(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Информация о сертификации", reply_markup = start_kb.back_to_start) #TODO: информация по сертификации

@router.callback_query(F.data == 'features')
async def compare(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Технические характеристики", reply_markup = start_kb.back_to_start) #TODO: тех хар-ки

#TODO: удалить пример отправки аудио
#Как пример отправки аудио
@router.callback_query(F.data == 'voiceActing')
async def voice_Acting_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Flag.presentation_text)
    await callback.answer('Напишите текст презентации', show_alert = True)

@router.message(Flag.presentation_text)
async def voice_Acting_end(message: Message, state: FSMContext):
    await state.update_data(presentation_text = message.text)
    await state.clear()
    auido_bytes = BytesIO()
    tts = WorkWithTTS.text_to_speech(text = message.text, language = 'ru')
    tts.write_to_fp(auido_bytes)
    auido_bytes.seek(0)
    audio = BufferedInputFile(file = auido_bytes.read(), filename = "voice.mp3")
    await message.answer_audio(audio = audio)