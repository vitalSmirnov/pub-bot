from pyrogram import idle

from BotModule.bot import app, quick_integration
import asyncio


async def main():
    await app.start()
    asyncio.create_task(quick_integration())

    await idle()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        app.stop()
        exit()
