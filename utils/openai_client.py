import openai
from openai import AsyncOpenAI
import logging
from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    async def get_chat_response(self, prompt: str, system_prompt: str = None, max_tokens: int = 1000) -> str:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Ошибка OpenAI: {e}")
            return "Извините, произошла ошибка при обработке запроса."

    async def get_random_fact(self) -> str:
        prompt = "Расскажи интересный научный факт. Будь кратким, но информативным. Ответ должен быть не более 150 слов."
        return await self.get_chat_response(prompt)

    async def get_quiz_question(self, topic: str) -> str:
        prompt = f"Сгенерируй интересный вопрос по теме {topic}. Вопрос должен быть с одним правильным ответом. Формат: Вопрос: [вопрос] Правильный ответ: [ответ]"
        return await self.get_chat_response(prompt)

    async def validate_quiz_answer(self, question: str, user_answer: str, correct_answer: str) -> str:
        prompt = f"""Вопрос: {question}
        Правильный ответ: {correct_answer}
        Ответ пользователя: {user_answer}

        Проанализируй ответ пользователя и определи, правильный ли он. Учти возможные синонимы и небольшие неточности в формулировке.
        Верни только "Правильно" или "Неправильно"."""

        return await self.get_chat_response(prompt)

    async def translate_text(self, text: str, target_language: str) -> str:
        language_names = {
            'en': 'английский',
            'es': 'испанский',
            'fr': 'французский',
            'de': 'немецкий',
            'it': 'итальянский',
            'ja': 'японский'
        }

        prompt = f"Переведи следующий текст на {language_names[target_language]} язык: {text}"
        return await self.get_chat_response(prompt)

    async def transcribe_audio(self, audio_file) -> str:
        try:
            transcription = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            return transcription.text
        except Exception as e:
            logger.error(f"Ошибка транскрибации: {e}")
            return None

    async def text_to_speech(self, text: str) -> bytes:
        try:
            response = await self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            return response.content
        except Exception as e:
            logger.error(f"Ошибка синтеза речи: {e}")
            return None