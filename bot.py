import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import time
from pathlib import Path

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация бота
TOKEN = "6626403577:AAFWbkBs9-IaGZiZ-lzvURZrmQNR5eyjKNc"
INPUT_VOICE = "input.mp3"  # Telegram использует формат OGG для голосовых сообщений
OUTPUT_DOCX = "output.docx"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "Привет! Отправь мне голосовое сообщение, и я преобразую его в текстовый документ."
    )


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик голосовых сообщений"""
    try:
        # Получаем текущую рабочую директорию
        current_dir = Path.cwd()
        voice_path = current_dir / INPUT_VOICE
        output_path = current_dir / OUTPUT_DOCX

        logger.info(f"Текущая рабочая директория: {current_dir}")

        # Получаем голосовое сообщение
        voice = update.message.voice
        voice_file = await voice.get_file()

        logger.info(f"Получено голосовое сообщение, размер: {voice_file.file_size} байт")

        # Сохраняем оригинальный файл
        await voice_file.download_to_drive(custom_path=str(voice_path))

        # Проверяем, что файл сохранился
        if not voice_path.exists():
            raise Exception("Файл не был сохранен на диск")

        logger.info(f"Файл успешно сохранен: {voice_path}, размер: {voice_path.stat().st_size} байт")

        # Ваш код для обработки OGG файла
        # Здесь должен быть вызов вашего конвертера
        logger.info("Запуск обработки файла...")
        os.system(f"python main.py {voice_path}")

        # Проверяем результат
        if not output_path.exists():
            raise Exception("Файл DOCX не был создан")

        # Отправляем результат
        with open(output_path, 'rb') as doc_file:
            await update.message.reply_document(
                document=doc_file,
                caption="Вот текст из вашего голосового сообщения"
            )
        logger.info("Документ успешно отправлен пользователю")

    except Exception as e:
        logger.error(f"Ошибка обработки голоса: {e}", exc_info=True)
        await update.message.reply_text(
            f"Произошла ошибка при обработке: {str(e)}"
        )

    finally:
        # Удаляем временные файлы
        for file_path in [voice_path, output_path]:
            try:
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Удален временный файл: {file_path}")
            except Exception as e:
                logger.error(f"Ошибка при удалении файла {file_path}: {e}")


def main():
    """Запуск бота"""
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))

    # Запускаем бота
    application.run_polling()


if __name__ == "__main__":
    main()