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

router = Router()
logger = logging.getLogger(__name__)
openai_client = OpenAIClient()


class GPTStates(StatesGroup):
    waiting_for_message = State()


@router.message(Command("gpt"))
@router.callback_query(F.data == "gpt")
async def start_gpt_chat(update: Message | CallbackQuery, state: FSMContext):
    try:
        if isinstance(update, CallbackQuery):
            message = update.message
            await update.answer()
        else:
            message = update

        caption = "💬 Режим ChatGPT активирован! Отправьте ваш вопрос или сообщение."

        try:
            async with aiofiles.open(IMAGE_PATHS['gpt'], 'rb') as photo:
                if isinstance(update, CallbackQuery):
                    await message.edit_media(
                        media=InputMediaPhoto(media=photo, caption=caption)
                    )
                else:
                    await message.answer_photo(
                        photo=photo,
                        caption=caption
                    )
        except:
            if isinstance(update, CallbackQuery):
                await message.edit_text(caption)
            else:
                await message.answer(caption)

        await state.set_state(GPTStates.waiting_for_message)

    except Exception as e:
        logger.error(f"Ошибка в start_gpt_chat: {e}")


@router.message(GPTStates.waiting_for_message, F.text)
async def handle_gpt_message(message: Message, state: FSMContext):
    user_message = message.text

    # Показываем, что бот печатает
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        response = await openai_client.get_chat_response(user_message)

        await message.answer(
            f"🤖 *ChatGPT:*\n\n{response}",
            reply_markup=get_end_keyboard(),
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"Ошибка в handle_gpt_message: {e}")
        await message.answer(
            "❌ Произошла ошибка при обработке запроса. Попробуйте позже.",
            reply_markup=get_end_keyboard()
        )