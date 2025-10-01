from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import Command
from utils.openai_client import OpenAIClient
from keyboards.inline import get_random_fact_keyboard
from config import IMAGE_PATHS
import logging
import aiofiles

router = Router()
logger = logging.getLogger(__name__)
openai_client = OpenAIClient()


@router.message(Command("random"))
async def cmd_random(message: Message):
    """Обработчик команды /random"""
    await handle_random_fact(message)


@router.callback_query(F.data == "random")
async def callback_random(callback: CallbackQuery):
    """Обработчик callback для кнопки случайного факта"""
    await callback.answer()
    await handle_random_fact(callback.message, is_callback=True)


async def handle_random_fact(message: Message, is_callback: bool = False):
    """Основная логика обработки случайного факта"""
    try:
        sent_message = None

        # Отправка изображения
        try:
            async with aiofiles.open(IMAGE_PATHS['random'], 'rb') as photo:
                if is_callback:
                    # Для callback сначала редактируем существующее сообщение
                    sent_message = await message.edit_media(
                        media=InputMediaPhoto(
                            media=photo,
                            caption="🔍 Ищу интересный факт..."
                        )
                    )
                else:
                    # Для команды отправляем новое сообщение
                    sent_message = await message.answer_photo(
                        photo=photo,
                        caption="🔍 Ищу интересный факт..."
                    )
        except Exception as e:
            logger.warning(f"Не удалось отправить изображение: {e}")
            # Если изображение не найдено, отправляем текстовое сообщение
            if is_callback:
                sent_message = await message.edit_text("🔍 Ищу интересный факт...")
            else:
                sent_message = await message.answer("🔍 Ищу интересный факт...")

        # Получение факта от ChatGPT
        fact = await openai_client.get_random_fact()

        response_text = f"🎯 *Интересный факт:*\n\n{fact}"

        # Обновление сообщения с результатом
        if sent_message and sent_message.photo:
            # Если сообщение содержит фото, редактируем подпись
            await sent_message.edit_caption(
                caption=response_text,
                reply_markup=get_random_fact_keyboard(),
                parse_mode='Markdown'
            )
        else:
            # Если сообщение текстовое, редактируем текст
            await sent_message.edit_text(
                text=response_text,
                reply_markup=get_random_fact_keyboard(),
                parse_mode='Markdown'
            )

    except Exception as e:
        logger.error(f"Ошибка в handle_random_fact: {e}")
        error_text = "❌ Произошла ошибка при получении факта. Попробуйте позже."

        try:
            if is_callback:
                await message.edit_text(
                    text=error_text,
                    reply_markup=get_random_fact_keyboard()
                )
            else:
                await message.answer(
                    text=error_text,
                    reply_markup=get_random_fact_keyboard()
                )
        except Exception as edit_error:
            logger.error(f"Ошибка при отправке сообщения об ошибке: {edit_error}")