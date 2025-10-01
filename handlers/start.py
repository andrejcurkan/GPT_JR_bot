from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from keyboards.inline import get_main_keyboard
import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message):
    try:
        welcome_text = """
🤖 Добро пожаловать в ChatGPT бот!

Выберите одну из функций:

🎲 *Рандомный факт* - Интересные научные факты
💬 *ChatGPT* - Прямой диалог с ИИ
👤 *Диалог с личностью* - Общение с историческими личностями
❓ *Квиз* - Викторина на разные темы
🌐 *Переводчик* - Переводчик с поддержкой многих языков
🎤 *Голосовой чат* - Общение через голосовые сообщения

Выберите опцию ниже 👇
        """

        await message.answer(
            welcome_text,
            reply_markup=get_main_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Ошибка в cmd_start: {e}")


@router.callback_query(F.data == "start")
async def start_callback(callback: CallbackQuery):
    await callback.answer()

    welcome_text = """
🤖 Добро пожаловать в ChatGPT бот!

Выберите одну из функций:
    """

    await callback.message.edit_text(
        welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode='Markdown'
    )