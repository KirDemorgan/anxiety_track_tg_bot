#!/usr/bin/env python3
import asyncio
from bot import PillsBot

async def main():
    bot = PillsBot()
    await bot.db.connect()
    
    try:
        print("🤖 Бот запущен...")
        bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Остановка бота...")
    finally:
        await bot.db.close()
        print("✅ Бот остановлен")

if __name__ == '__main__':
    asyncio.run(main())