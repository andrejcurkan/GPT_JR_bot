from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.openai_client import OpenAIClient
from keyboards.inline import get_quiz_topic_keyboard, get_quiz_after_keyboard
from config import IMAGE_PATHS, QUIZ_TOPICS
import logging
import aiofiles
import re

router = Router()
logger = logging.getLogger(__name__)
openai_client = OpenAIClient()


class QuizStates(StatesGroup):
    waiting_for_answer = State()


@router.message(Command("quiz"))
async def cmd_quiz(message: Message, state: FSMContext):
    """Обработчик команды /quiz"""
    await start_quiz(message, state)


@router.callback_query(F.data == "quiz")
async def callback_quiz(callback: CallbackQuery, state: FSMContext):
    """Обработчик callback для кнопки квиза"""
    await callback.answer()
    await start_quiz(callback.message, state, is_callback=True)


async def start_quiz(message: Message, state: FSMContext, is_callback: bool = False):
    """Запуск квиза"""
    try:
        # Инициализация счёта
        await state.update_data(quiz_score=0, quiz_total=0)

        caption = "❓ Выберите тему для квиза:"

        try:
            async with aiofiles.open(IMAGE_PATHS['quiz'], 'rb') as photo:
                if is_callback:
                    await message.edit_media(
                        media=InputMediaPhoto(media=photo, caption=caption),
                        reply_markup=get_quiz_topic_keyboard()
                    )
                else:
                    await message.answer_photo(
                        photo=photo,
                        caption=caption,
                        reply_markup=get_quiz_topic_keyboard()
                    )
        except Exception as e:
            logger.warning(f"Не удалось отправить изображение: {e}")
            if is_callback:
                await message.edit_text(
                    caption,
                    reply_markup=get_quiz_topic_keyboard()
                )
            else:
                await message.answer(
                    caption,
                    reply_markup=get_quiz_topic_keyboard()
                )

    except Exception as e:
        logger.error(f"Ошибка в start_quiz: {e}")


@router.callback_query(F.data.startswith("quiz_"))
async def select_quiz_topic(callback: CallbackQuery, state: FSMContext):
    """Выбор темы квиза"""
    await callback.answer()

    topic_key = callback.data.replace('quiz_', '')
    topic_name = QUIZ_TOPICS.get(topic_key, 'Общая тема')

    await state.update_data(
        current_topic=topic_key,
        current_question=None,
        current_correct_answer=None
    )

    await ask_quiz_question(callback, state, topic_name)
    await state.set_state(QuizStates.waiting_for_answer)


async def ask_quiz_question(update: CallbackQuery | Message, state: FSMContext, topic_name: str):
    """Генерация и отправка вопроса квиза"""
    try:
        question_text = await openai_client.get_quiz_question(topic_name)

        # Парсинг вопроса и ответа
        question_match = re.search(r'Вопрос:\s*(.+)', question_text)
        answer_match = re.search(r'Правильный ответ:\s*(.+)', question_text)

        if question_match and answer_match:
            question = question_match.group(1).strip()
            correct_answer = answer_match.group(1).strip()

            await state.update_data(
                current_question=question,
                current_correct_answer=correct_answer
            )

            data = await state.get_data()
            score_text = f" (Счёт: {data['quiz_score']}/{data['quiz_total']})" if data['quiz_total'] > 0 else ""

            question_text = f"❓ *Вопрос:* {question}\n\nОтправьте ваш ответ текстом:{score_text}"

            if isinstance(update, CallbackQuery):
                try:
                    await update.message.edit_caption(
                        caption=question_text,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.warning(f"Не удалось редактировать подпись: {e}")
                    await update.message.edit_text(
                        text=question_text,
                        parse_mode='Markdown'
                    )
            else:
                await update.answer(
                    question_text,
                    parse_mode='Markdown'
                )
        else:
            raise ValueError("Не удалось распарсить вопрос и ответ")

    except Exception as e:
        logger.error(f"Ошибка в ask_quiz_question: {e}")
        error_msg = "❌ Не удалось сгенерировать вопрос. Попробуйте другую тему."
        if isinstance(update, CallbackQuery):
            try:
                await update.message.edit_caption(caption=error_msg)
            except:
                await update.message.edit_text(text=error_msg)
        else:
            await update.answer(error_msg)


@router.message(QuizStates.waiting_for_answer, F.text)
async def handle_quiz_answer(message: Message, state: FSMContext):
    """Обработка ответа на вопрос квиза"""
    user_answer = message.text
    data = await state.get_data()

    current_question = data.get('current_question')
    correct_answer = data.get('current_correct_answer')

    if not current_question or not correct_answer:
        await message.answer("❌ Произошла ошибка. Начните квиз заново.")
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        # Валидация ответа через ChatGPT
        validation = await openai_client.validate_quiz_answer(current_question, user_answer, correct_answer)

        quiz_total = data['quiz_total'] + 1

        if "Правильно" in validation:
            quiz_score = data['quiz_score'] + 1
            result_text = "✅ *Правильно!*"
        else:
            quiz_score = data['quiz_score']
            result_text = f"❌ *Неправильно.* Правильный ответ: {correct_answer}"

        await state.update_data(quiz_score=quiz_score, quiz_total=quiz_total)

        score_text = f"\n\n📊 Счёт: {quiz_score}/{quiz_total}"

        await message.answer(
            f"{result_text}{score_text}",
            reply_markup=get_quiz_after_keyboard(),
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"Ошибка в handle_quiz_answer: {e}")
        await message.answer(
            "❌ Произошла ошибка при проверке ответа.",
            reply_markup=get_quiz_after_keyboard()
        )


@router.callback_query(F.data == "quiz_same_topic")
async def quiz_continue_same_topic(callback: CallbackQuery, state: FSMContext):
    """Продолжение квиза с той же темой"""
    await callback.answer()

    data = await state.get_data()
    topic_key = data.get('current_topic', 'science')
    topic_name = QUIZ_TOPICS.get(topic_key, 'Наука')

    await ask_quiz_question(callback, state, topic_name)