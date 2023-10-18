from BotModule.bot import app
from QuickRestoModule.quickResto import QuickResto
from static.configuration.utils import spreadsheet, scheduler

if __name__ == "__main__":
    quick_api = QuickResto(
        app,
        spreadsheet,
    )
    scheduler.add_job(quick_api.shift_manager, "interval", seconds=60)
    scheduler.start()

    try:
        app.run()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

