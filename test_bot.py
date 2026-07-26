import asyncio
from aiogram import Bot, Dispatcher

TOKEN = "8580249375:AAF54sttmFOhAXOyhW5abKDY0zXERPiQ8vM"

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():
    print("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())