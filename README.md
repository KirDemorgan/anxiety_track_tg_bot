# Telegram Бот для учета приема лекарств

Простой бот для отслеживания приема таблеток и состояния здоровья с возможностью экспорта в PDF.

## Функционал

- 💊 **Добавление записей о приеме таблеток** - название и дозировка
- 📝 **Заметки о состоянии** - текстовые записи о самочувствии
- 📊 **PDF отчеты** - статистика по дням с временными метками
- 🗄️ **PostgreSQL база данных** - надежное хранение данных
- 🐳 **Docker** - простой запуск в контейнерах

## Быстрый запуск с Docker

1. **Получите токен бота:**
   - Напишите @BotFather в Telegram
   - Создайте нового бота командой `/newbot`
   - Скопируйте токен

2. **Создайте .env файл:**
```bash
cp .env.example .env
```

3. **Заполните .env файл:**
```
BOT_TOKEN=your_telegram_bot_token
POSTGRES_PASSWORD=your_secure_password_here
TIMEZONE=Europe/Moscow
```
(остальные настройки можно оставить по умолчанию)

4. **Запустите с Docker Compose:**
```bash
docker-compose up -d
```

Готово! Бот запущен и готов к работе.

## Управление Docker

```bash
# Запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f bot

# Остановка
docker-compose down

# Перезапуск после изменений
docker-compose up -d --build
```

## Ручная установка (без Docker)

1. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

2. **Настройте PostgreSQL:**
```sql
CREATE DATABASE pills_bot;
CREATE USER pills_user WITH PASSWORD 'pills_password';
GRANT ALL PRIVILEGES ON DATABASE pills_bot TO pills_user;
```

3. **Создайте .env файл:**
```bash
cp .env.example .env
```

4. **Заполните .env файл:**
```
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql://pills_user:pills_password@localhost:5432/pills_bot
```

5. **Запустите:**
```bash
python run_bot.py
```

## Использование

1. Запустите бота командой `/start`
2. Используйте кнопки меню:
   - **💊 Добавить таблетку** - введите название и дозировку
   - **📝 Добавить заметку** - опишите свое состояние
   - **📊 Получить отчет** - скачайте PDF со статистикой

## Структура отчета

PDF отчет содержит данные, сгруппированные по дням:
- Дата
- Принятые лекарства с временем и дозировкой
- Заметки о состоянии с временем

## Требования

- Python 3.8+
- PostgreSQL 12+
- Telegram Bot Token