from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.openai_client import OpenAIClient
from keyboards.inline import get_personality_keyboard, get_end_keyboard
from config import IMAGE_PATHS, PERSONALITIES
import logging
import aiofiles

router = Router()
logger = logging.getLogger(__name__)
openai_client = OpenAIClient()


class PersonalityStates(StatesGroup):
    waiting_for_message = State()


@router.message(Command("talk"))
async def cmd_talk(message: Message, state: FSMContext):
    """Обработчик команды /talk"""
    await start_personality_chat(message, state)


@router.callback_query(F.data == "talk")
async def callback_talk(callback: CallbackQuery, state: FSMContext):
    """Обработчик callback для кнопки диалога с личностью"""
    await callback.answer()
    await start_personality_chat(callback.message, state, is_callback=True)


async def start_personality_chat(message: Message, state: FSMContext, is_callback: bool = False):
    """Запуск выбора личности"""
    try:
        caption = "👤 Выберите историческую личность для диалога:"

        try:
            async with aiofiles.open(IMAGE_PATHS['talk'], 'rb') as photo:
                if is_callback:
                    await message.edit_media(
                        media=InputMediaPhoto(media=photo, caption=caption),
                        reply_markup=get_personality_keyboard()
                    )
                else:
                    await message.answer_photo(
                        photo=photo,
                        caption=caption,
                        reply_markup=get_personality_keyboard()
                    )
        except Exception as e:
            logger.warning(f"Не удалось отправить изображение: {e}")
            if is_callback:
                await message.edit_text(
                    caption,
                    reply_markup=get_personality_keyboard()
                )
            else:
                await message.answer(
                    caption,
                    reply_markup=get_personality_keyboard()
                )

    except Exception as e:
        logger.error(f"Ошибка в start_personality_chat: {e}")


@router.callback_query(F.data.startswith("personality_"))
async def select_personality(callback: CallbackQuery, state: FSMContext):
    """Выбор конкретной личности"""
    await callback.answer()

    personality_key = callback.data.replace('personality_', '')
    personality_name = {
        'einstein': 'Альберт Эйнштейн',
        'shakespeare': 'Уильям Шекспир',
        'tesla': 'Никола Тесла',
        'cleopatra': 'Клеопатра'
    }.get(personality_key, 'Личность')

    await state.update_data(
        current_personality=personality_key,
        personality_prompt=PERSONALITIES[personality_key]
    )

    caption = f"👤 Теперь вы общаетесь с {personality_name}! Отправьте ваше сообщение."

    try:
        # Пытаемся редактировать медиа
        await callback.message.edit_caption(
            caption=caption,
            reply_markup=get_end_keyboard()
        )
    except Exception as e:
        logger.warning(f"Не удалось редактировать подпись: {e}")
        # Если не получилось, редактируем текст
        try:
            await callback.message.edit_text(
                text=caption,
                reply_markup=get_end_keyboard()
            )
        except Exception as edit_error:
            logger.error(f"Не удалось редактировать сообщение: {edit_error}")
            # Если и это не получилось, отправляем новое сообщение
            await callback.message.answer(
                text=caption,
                reply_markup=get_end_keyboard()
            )

    await state.set_state(PersonalityStates.waiting_for_message)


@router.message(PersonalityStates.waiting_for_message, F.text)
async def handle_personality_message(message: Message, state: FSMContext):
    """Обработка сообщений в режиме диалога с личностью"""
    user_message = message.text
    data = await state.get_data()

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        personality_prompt = data.get('personality_prompt', '')
        response = await openai_client.get_chat_response(user_message, personality_prompt)

        personality_name = {
            'einstein': 'Эйнштейн',
            'shakespeare': 'Шекспир',
            'tesla': 'Тесла',
            'cleopatra': 'Клеопатра'
        }.get(data.get('current_personality', ''), 'Личность')

        await message.answer(
            f"👤 *{personality_name}:*\n\n{response}",
            reply_markup=get_end_keyboard(),
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"Ошибка в handle_personality_message: {e}")
        await message.answer(
            "❌ Произошла ошибка при обработке сообщения.",
            reply_markup=get_end_keyboard()
        )