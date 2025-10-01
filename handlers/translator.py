from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.openai_client import OpenAIClient
from keyboards.inline import get_language_keyboard, get_translate_after_keyboard
from config import IMAGE_PATHS, LANGUAGES
import logging
import aiofiles

router = Router()
logger = logging.getLogger(__name__)
openai_client = OpenAIClient()


class TranslateStates(StatesGroup):
    waiting_for_text = State()


@router.message(Command("translate"))
@router.callback_query(F.data == "translate")
async def start_translator(update: Message | CallbackQuery, state: FSMContext):
    try:
        if isinstance(update, CallbackQuery):
            message = update.message
            await update.answer()
        else:
            message = update

        caption = "🌐 Выберите язык для перевода:"

        try:
            async with aiofiles.open(IMAGE_PATHS['translate'], 'rb') as photo:
                if isinstance(update, CallbackQuery):
                    await message.edit_media(
                        media=InputMediaPhoto(media=photo, caption=caption),
                        reply_markup=get_language_keyboard()
                    )
                else:
                    await message.answer_photo(
                        photo=photo,
                        caption=caption,
                        reply_markup=get_language_keyboard()
                    )
        except:
            if isinstance(update, CallbackQuery):
                await message.edit_text(
                    caption,
                    reply_markup=get_language_keyboard()
                )
            else:
                await message.answer(
                    caption,
                    reply_markup=get_language_keyboard()
                )

    except Exception as e:
        logger.error(f"Ошибка в start_translator: {e}")


@router.callback_query(F.data.startswith("lang_"))
async def select_language(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    lang_code = callback.data.replace('lang_', '')
    lang_name = LANGUAGES.get(lang_code, 'язык')

    await state.update_data(target_language=lang_code)

    caption = f"🌐 Выбран язык: {lang_name}\n\nОтправьте текст для перевода:"

    try:
        await callback.message.edit_caption(
            caption=caption,
            reply_markup=get_translate_after_keyboard()
        )
    except:
        await callback.message.edit_text(
            caption,
            reply_markup=get_translate_after_keyboard()
        )

    await state.set_state(TranslateStates.waiting_for_text)


@router.message(TranslateStates.waiting_for_text, F.text)
async def handle_translation(message: Message, state: FSMContext):
    text_to_translate = message.text
    data = await state.get_data()
    target_language = data.get('target_language', 'en')

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        translation = await openai_client.translate_text(text_to_translate, target_language)
        lang_name = LANGUAGES.get(target_language, 'выбранный язык')

        await message.answer(
            f"🌐 *Перевод на {lang_name}:*\n\n{translation}",
            reply_markup=get_translate_after_keyboard(),
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"Ошибка в handle_translation: {e}")
        await message.answer(
            "❌ Произошла ошибка при переводе.",
            reply_markup=get_translate_after_keyboard()
        )