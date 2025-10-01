import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Проверка наличия токенов
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env файле")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY не найден в .env файле")

# Настройки изображений
IMAGE_PATHS = {
    'random': 'images/random.jpg',
    'gpt': 'images/gpt.jpg',
    'talk': 'images/talk.jpg',
    'quiz': 'images/quiz.jpg',
    'translate': 'images/translate.jpg',
    'voice': 'images/voice.jpg'
}

# Промпты для личностей
PERSONALITIES = {
    'einstein': "Ты Альберт Эйнштейн. Говори как великий физик, используй научные термины и будь немного рассеянным профессором.",
    'shakespeare': "Ты Уильям Шекспир. Говори на старинном английском стиле, используй поэтические выражения и метафоры.",
    'tesla': "Ты Никола Тесла. Говори как гениальный изобретатель, будь немного эксцентричным и страстным в отношении науки.",
    'cleopatra': "Ты Клеопатра. Говори как древнеегипетская царица - властно, мудро и с достоинством."
}

# Темы для квиза
QUIZ_TOPICS = {
    'science': "Наука и технологии",
    'history': "История",
    'geography': "География",
    'literature': "Литература"
}

# Языки для переводчика
LANGUAGES = {
    'en': 'Английский',
    'es': 'Испанский',
    'fr': 'Французский',
    'de': 'Немецкий',
    'it': 'Итальянский',
    'ja': 'Японский'
}