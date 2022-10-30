import telegram

from pars.parfile_reader import parfile_reader


def telegram_bot(parfile):
    telegram_pars = parfile_reader(parfile)


def telegram_bot_send_message(message, telegram_pars="./pars/telegram_api.json"):
    telegram_pars = parfile_reader(telegram_pars)
    bot = telegram.Bot(telegram_pars['api_key'])
    bot.sendMessage(
        chat_id=telegram_pars["chat_id"],
        text=message
    )

if __name__ == '__main__':
    telegram_bot_send_message("hello", telegram_pars="./pars/telegram_api.json")