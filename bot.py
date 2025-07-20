import os
import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from dotenv import load_dotenv
from database import Database
from pdf_generator import PDFGenerator
import io

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

PILL_NAME, PILL_DOSE, HEALTH_NOTE = range(3)

class PillsBot:
    def __init__(self):
        self.db = Database(os.getenv('DATABASE_URL'))
        self.pdf_generator = PDFGenerator()
        
        self.main_keyboard = ReplyKeyboardMarkup([
            [KeyboardButton("💊 Добавить таблетку")],
            [KeyboardButton("📝 Добавить заметку о состоянии")],
            [KeyboardButton("📊 Получить отчет PDF")]
        ], resize_keyboard=True)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        await update.message.reply_text(
            "Привет! Я бот для учета приема лекарств.\n\n"
            "Выберите действие:",
            reply_markup=self.main_keyboard
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        text = update.message.text
        
        if text == "💊 Добавить таблетку":
            await update.message.reply_text("Введите название таблетки:")
            return PILL_NAME
        elif text == "📝 Добавить заметку о состоянии":
            await update.message.reply_text("Введите заметку о вашем состоянии:")
            return HEALTH_NOTE
        elif text == "📊 Получить отчет PDF":
            await self.generate_report(update, context)
        else:
            await update.message.reply_text(
                "Пожалуйста, используйте кнопки меню.",
                reply_markup=self.main_keyboard
            )
    
    async def pill_name_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка названия таблетки"""
        context.user_data['pill_name'] = update.message.text
        await update.message.reply_text("Введите дозировку (например: 1 таблетка, 5мг, 2 капсулы):")
        return PILL_DOSE
    
    async def pill_dose_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка дозировки таблетки"""
        pill_name = context.user_data['pill_name']
        dose = update.message.text
        user_id = update.effective_user.id
        
        success = await self.db.add_pill(user_id, pill_name, dose)
        
        if success:
            await update.message.reply_text(
                f"✅ Записано: {pill_name} ({dose})\n"
                f"Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
                reply_markup=self.main_keyboard
            )
        else:
            await update.message.reply_text(
                "❌ Ошибка при сохранении. Попробуйте еще раз.",
                reply_markup=self.main_keyboard
            )
        
        return ConversationHandler.END
    
    async def health_note_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка заметки о состоянии"""
        note = update.message.text
        user_id = update.effective_user.id
        
        success = await self.db.add_health_note(user_id, note)
        
        if success:
            await update.message.reply_text(
                f"✅ Заметка сохранена\n"
                f"Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
                reply_markup=self.main_keyboard
            )
        else:
            await update.message.reply_text(
                "❌ Ошибка при сохранении. Попробуйте еще раз.",
                reply_markup=self.main_keyboard
            )
        
        return ConversationHandler.END
    
    async def generate_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Генерация PDF отчета"""
        user_id = update.effective_user.id
        
        await update.message.reply_text("📊 Генерирую отчет...")
        
        try:
            user_data = await self.db.get_user_data(user_id)
            
            if not user_data['pills'] and not user_data['notes']:
                await update.message.reply_text(
                    "📭 У вас пока нет записей для отчета.",
                    reply_markup=self.main_keyboard
                )
                return
            
            pdf_bytes = self.pdf_generator.generate_report(user_data, user_id)
            
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_file.name = f"pills_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            await update.message.reply_document(
                document=pdf_file,
                filename=pdf_file.name,
                caption="📊 Ваш отчет готов!",
                reply_markup=self.main_keyboard
            )
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            await update.message.reply_text(
                "❌ Ошибка при генерации отчета. Попробуйте позже.",
                reply_markup=self.main_keyboard
            )
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена операции"""
        await update.message.reply_text(
            "Операция отменена.",
            reply_markup=self.main_keyboard
        )
        return ConversationHandler.END
    
    def run(self):
        """Запуск бота"""
        application = Application.builder().token(os.getenv('BOT_TOKEN')).build()
        
        pill_conv_handler = ConversationHandler(
            entry_points=[MessageHandler(filters.Regex("💊 Добавить таблетку"), self.handle_message)],
            states={
                PILL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.pill_name_handler)],
                PILL_DOSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.pill_dose_handler)],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )
        
        note_conv_handler = ConversationHandler(
            entry_points=[MessageHandler(filters.Regex("📝 Добавить заметку о состоянии"), self.handle_message)],
            states={
                HEALTH_NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.health_note_handler)],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)]
        )
        
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(pill_conv_handler)
        application.add_handler(note_conv_handler)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        application.run_polling()

async def main():
    bot = PillsBot()
    await bot.db.connect()
    
    try:
        bot.run()
    finally:
        await bot.db.close()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())