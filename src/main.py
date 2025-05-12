import time

import schedule

from price_minecraft_checker import check_price_and_notify
from price_epic_checker import check_free_games_and_notify
from notifier import Notifier
from database import init_db


def main():
    init_db()
    notifier = Notifier()
    notifier.send_startup_notification()
    schedule.every(6).hours.do(check_price_and_notify)
    schedule.every(6).hours.do(check_free_games_and_notify)
    schedule.every(1).hours.do(notifier.check_whatsapp_connection_and_notify)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()