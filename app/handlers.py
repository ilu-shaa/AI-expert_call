from aiogram import F, Router
from aiogram.filters import Command, BaseFilter
from aiogram.types import Message, CallbackQuery

import keyboards.start_keyboard as start_kb
from bot_answers import greetings

from workTools.WorkWithTTS import WorkWithTTS

class VoiceFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return bool(message.voice)

router = Router()
user_message = F.data.split()

@router.message(Command("start", "restart"))
async def command_start(message: Message):
    await message.answer(greetings, reply_markup = start_kb.start)

@router.callback_query(F.data == 'backStart')
async def question_start(callback: CallbackQuery):
    await callback.message.edit_text(greetings, reply_markup = start_kb.start)

@router.callback_query(F.data == 'performance')
async def question_start(callback: CallbackQuery):
    await callback.message.edit_text('Представление', reply_markup = start_kb.back_to_start) # запрос в нейронке

@router.callback_query(F.data == 'question')
async def question_start(callback: CallbackQuery):
    await callback.answer('Задайте вопрос текстом или голосом', show_alert = True)

@router.callback_query(F.data == 'compare')
async def question_start(callback: CallbackQuery):
    await callback.message.edit_text('Выберете продукт для сравнения', reply_markup = start_kb.back_to_start) # reply_markap = compare kb

@router.callback_query(F.data == 'voiceActing')
async def question_start(callback: CallbackQuery):
    await callback.answer('Напишите текст презентации', show_alert = True)