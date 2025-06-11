from aiogram import F, Router, Bot
from aiogram.filters import Command, BaseFilter
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import os

import keyboards.start_keyboard as start_kb
from bot_answers import greetings

from workTools.WorkWithTTS import WorkWithTTS

class VoiceFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return bool(message.voice)

class Flag(StatesGroup):
    presentation_text = State()

router = Router()
user_message = F.data.split()

@router.message(Command("start", "restart"))
async def command_start(message: Message):
    await message.answer(greetings, reply_markup = start_kb.start)

@router.callback_query(F.data == 'backStart')
async def back_to_start(callback: CallbackQuery):
    await callback.message.edit_text(greetings, reply_markup = start_kb.start)

@router.callback_query(F.data == 'performance')
async def performance(callback: CallbackQuery):
    await callback.message.edit_text('Представление', reply_markup = start_kb.back_to_start) # запрос в нейронке

@router.callback_query(F.data == 'question')
async def question(callback: CallbackQuery):
    await callback.answer('Задайте вопрос текстом или голосом', show_alert = True)

@router.callback_query(F.data == 'compare')
async def compare(callback: CallbackQuery):
    await callback.message.edit_text('Выберете продукт для сравнения', reply_markup = start_kb.back_to_start) # reply_markap = compare kb

@router.callback_query(F.data == 'voiceActing')
async def voice_Acting_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Flag.presentation_text)
    await callback.answer('Напишите текст презентации', show_alert = True)

@router.message(Flag.presentation_text)
async def voice_Acting_end(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(presentation_text = message.text)
    await state.clear()
    WorkWithTTS.text_to_speech(text = message.text, language = 'ru')
    audio = FSInputFile('TTS.mp3')
    await bot.send_audio(message.chat.id, audio)
    os.remove('TTS.mp3')