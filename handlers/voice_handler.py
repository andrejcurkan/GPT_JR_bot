from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.openai_client import OpenAIClient
from keyboards.inline import get_end_keyboard
from config import IMAGE_PATHS
import logging
import aiofiles
import io

router = Router()
logger = logging.getLogger(__name__)
openai_client = OpenAIClient()


class VoiceStates(StatesGroup):
    waiting_for_voice = State()


@router.message(Command("voice"))
@router.callback_query(F.data == "voice")
async def start_voice_chat(update: Message | CallbackQuery, state: FSMContext):
    try:
        if isinstance(update, CallbackQuery):
            message = update.message
            await update.answer()
        else:
            message = update

        caption = "🎤 Голосовой режим активирован! Отправьте голосовое сообщение или текст."

        try:
            async with aiofiles.open(IMAGE_PATHS['voice'], 'rb') as photo:
                if isinstance(update, CallbackQuery):
                    await message.edit_media(
                        media=InputMediaPhoto(media=photo, caption=caption),
                        reply_markup=get_end_keyboard()
                    )
                else:
                    await message.answer_photo(
                        photo=photo,
                        caption=caption,
                        reply_markup=get_end_keyboard()
                    )
        except:
            if isinstance(update, CallbackQuery):
                await message.edit_text(
                    caption,
                    reply_markup=get_end_keyboard()
                )
            else:
                await message.answer(
                    caption,
                    reply_markup=get_end_keyboard()
                )

        await state.set_state(VoiceStates.waiting_for_voice)

    except Exception as e:
        logger.error(f"Ошибка в start_voice_chat: {e}")


@router.message(VoiceStates.waiting_for_voice, F.voice)
async def handle_voice_message(message: Message, state: FSMContext):
    voice = message.voice
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        # Скачивание голосового сообщения
        voice_file = await message.bot.get_file(voice.file_id)
        voice_bytes = await message.bot.download_file(voice_file.file_path)

        # Транскрибация
        audio_file = io.BytesIO(voice_bytes.read())
        audio_file.name = "voice.ogg"

        transcribed_text = await openai_client.transcribe_audio(audio_file)

        if not transcribed_text:
            await message.answer(
                "❌ Не удалось распознать голосовое сообщение.",
                reply_markup=get_end_keyboard()
            )
            return

        await message.answer(
            f"🎤 *Распознанный текст:* {transcribed_text}",
            parse_mode='Markdown'
        )

        # Получение ответа от ChatGPT
        response = await openai_client.get_chat_response(transcribed_text)

        # Преобразование ответа в речь
        audio_response = await openai_client.text_to_speech(response)

        if audio_response:
            await message.answer_voice(
                voice=io.BytesIO(audio_response),
                caption=f"🤖 *Ответ:* {response}",
                reply_markup=get_end_keyboard(),
                parse_mode='Markdown'
            )
        else:
            await message.answer(
                f"🤖 *Ответ:* {response}",
                reply_markup=get_end_keyboard(),
                parse_mode='Markdown'
            )

    except Exception as e:
        logger.error(f"Ошибка в handle_voice_message: {e}")
        await message.answer(
            "❌ Произошла ошибка при обработке голосового сообщения.",
            reply_markup=get_end_keyboard()
        )


@router.message(VoiceStates.waiting_for_voice, F.text)
async def handle_voice_text_message(message: Message, state: FSMContext):
    user_message = message.text

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        response = await openai_client.get_chat_response(user_message)

        # Преобразование ответа в речь
        audio_response = await openai_client.text_to_speech(response)

        if audio_response:
            await message.answer_voice(
                voice=io.BytesIO(audio_response),
                caption=f"🤖 *Ответ:* {response}",
                reply_markup=get_end_keyboard(),
                parse_mode='Markdown'
            )
        else:
            await message.answer(
                f"🤖 *Ответ:* {response}",
                reply_markup=get_end_keyboard(),
                parse_mode='Markdown'
            )

    except Exception as e:
        logger.error(f"Ошибка в handle_voice_text_message: {e}")
        await message.answer(
            "❌ Произошла ошибка при обработке сообщения.",
            reply_markup=get_end_keyboard()
        )