import re
from telegram import LabeledPrice, ParseMode
from telegram.ext import PreCheckoutQueryHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.updater import Updater
from telegram.update import Update

if __name__ == "__main__":
    
    url = "https://www.amazon.in/gp/product/B073YSQ927/ref=ewc_pr_img_1?smid=ARENK22K2PQRH&psc=1"
    asin_id = re.findall('/\w{10}/', url)[0].strip("/")
    
    
    