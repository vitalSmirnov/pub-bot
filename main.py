from pyrogram import idle

from BotModule.bot import app, quick_integration
import asyncio


async def main():
    await app.start()
    asyncio.create_task(quick_integration())
    try:
        await idle()
    except (KeyboardInterrupt, SystemExit):
        app.stop()
        exit()


if __name__ == "__main__":
    asyncio.run(main(), debug=True)
