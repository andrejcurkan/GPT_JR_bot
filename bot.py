import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import TELEGRAM_TOKEN

# Импорт обработчиков
from handlers.start import router as start_router
from handlers.random_fact import router as random_fact_router
from handlers.gpt_chat import router as gpt_chat_router
from handlers.personality_chat import router as personality_chat_router
from handlers.quiz import router as quiz_router
from handlers.translator import router as translator_router
from handlers.voice_handler import router as voice_handler_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=TELEGRAM_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрация роутеров
    dp.include_router(start_router)
    dp.include_router(random_fact_router)
    dp.include_router(gpt_chat_router)
    dp.include_router(personality_chat_router)
    dp.include_router(quiz_router)
    dp.include_router(translator_router)
    dp.include_router(voice_handler_router)

    # Запуск бота
    try:
        logger.info("Бот запущен")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())