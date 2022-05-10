import logging
import requests
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '<YourToken>'


def form_anecdote_body(anec):
    return \
f"""
Id: {anec["id"]}
{anec["text"]}
"""


def start(update, context):
    reply_keyboard = [['/rand', '/add']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text(
        "Здравы будте!", 
        reply_markup=markup
    )


def get_all_random(update, context):
    data = requests.get("http://127.0.0.1:8081//anecdote/rand/all").json()
    update.message.reply_text(form_anecdote_body(data))


def get_unverified_random(update, context):
    data = requests.get("http://127.0.0.1:8081//anecdote/rand/unverified").json()
    update.message.reply_text(form_anecdote_body(data))


def get_verified_random(update, context):
    data = requests.get("http://127.0.0.1:8081/anecdote/rand").json()
    update.message.reply_text(form_anecdote_body(data))


def get_anec_by_id(update, context):
    print(context.args)


def adding_anecdote_start(update, context):
    update.message.reply_text(
        "Слушаю, анекдот. Чтобы отменить, напишите /back."
    )
    return 1


def anecdote_adding(update, context):
    text = update.message.text

    response = requests.post("http://127.0.0.1:8081/anecdote/", json={"text": text})

    if response.ok:
        update.message.reply_text("Разрывная")
    else:
        update.message.reply_text("Что-то пошло не так...")
    return ConversationHandler.END


def adding_anecdote_stop(update, context):
    update.message.reply_text(
        "Эх..."
    )
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    start_handler = CommandHandler("start", start)
    all_random_handler = CommandHandler("rand", get_all_random)
    unverified_random_handler = CommandHandler("trash", get_unverified_random)
    verified_random_handler = CommandHandler("vrand", get_verified_random)
    anec_by_id_handler = CommandHandler("get", get_anec_by_id)

    anecdote_adding_handler = ConversationHandler(
        entry_points=[CommandHandler('add', adding_anecdote_start)],

        states={
            1: [MessageHandler(Filters.text & ~Filters.command, anecdote_adding)],
        },

        fallbacks=[CommandHandler('back', adding_anecdote_stop)]
    )

    dp.add_handler(all_random_handler)
    dp.add_handler(unverified_random_handler)
    dp.add_handler(verified_random_handler)
    dp.add_handler(anecdote_adding_handler)
    dp.add_handler(anec_by_id_handler)
    dp.add_handler(start_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()