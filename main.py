from bot import app
from quick_resto_integration import QuickResto
from utils import scheduler, spreadsheet

if __name__ == "__main__":
    quick_api = QuickResto(
        app,
        spreadsheet,
    )
    scheduler.add_job(quick_api.shift_manager, "interval", seconds=30)
    scheduler.start()

    try:
        app.run()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

