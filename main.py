import re, os, logging, requests
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
# from flask import Flask, jsonify, request


# app = Flask(__name__)

# to make requirements.txt: pip freeze > requirements.txt
# to create procfile: echo web: gunicorn run:app >> Procfile
                    # echo web: python3 main.py >> Procfile


# setting up logging module, so you will know when (and why) things don't work as expected
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\! Send me an amazon link to see its price history\!',
        # reply_markup=ForceReply(selective=True),
    )
      

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help! \n Send me a link of an amazon product to see its price history. Keep in mind that not all products are indexed but has a huge product list in the Keepa database as of now. Price history currently available in these domains: [ com |in | de | uk | jp | fr | ca | cn | it | es | com.mx ].')
    
 
def get_asin_id_and_domain(text: str) -> bool:
    """Returns the ASIN id and domain of the product if the url is valid else returns None"""
    # get the url from the text
    url = re.search("(?P<url>https?://[^\s]+)", text)
    # return None if url is not found
    if not url:
        return None, None
    
    url = url.group("url")
    
    # check if the url is shortened url, expand it if so
    if url.split("//")[1][:4] == "amzn":
        site = requests.get(url)
        url = site.url
    
    # get the asin_id and domain from the url
    asin_id = re.findall("/(\w{10})[?/]", url)
    domain = re.findall(".(com|de|uk|jp|fr|ca|cn|it|es|in|com.mx)/", url)
    
    # return
    if len(asin_id) == 0:
        return None, None
    elif len(domain) == 0:
        return asin_id, None
    else:
        return asin_id[0], domain[0]
   
   
def get_price_history(update: Update, context: CallbackContext) -> None:
    """Sends the price history of the product"""
    
    # get the asin_id and domain
    asin_id, domain = get_asin_id_and_domain(text=update.message.text)
    
    # check valid link
    if not asin_id:
        update.message.reply_text("Enter a valid amazon link.")
    # check if price history available in domain country
    elif not domain:
        update.message.reply_text("Price history not available for your country.")
    # send the graph
    else:
        update.message.reply_text("Processing...")
        graph_url = f"https://graph.keepa.com/pricehistory.png?asin={asin_id}&domain={domain}&range=90"
        update.message.reply_photo(graph_url)


def main() -> None:
    """Start the bot."""
    BOT_TOKEN = os.getenv("BOT_AMAZON_PRICE_HISTORY_TOKEN")
    PORT = int(os.environ.get('PORT', '8443'))
    
    # Create the Updater and pass it your bot's token.
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, get_price_history))

    # log all errors
    dispatcher.add_error_handler(error)
    
    # # Start the Bot
    # updater.start_polling()
    updater.start_webhook(
        listen="0.0.0.0",
        port=int(PORT),
        url_path=BOT_TOKEN,
        webhook_url='https://amazon-price-history-bot-tg.herokuapp.com/' + BOT_TOKEN
    )

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
    