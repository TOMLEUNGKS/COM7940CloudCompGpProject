from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup 
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import configparser
import logging
import telebot

from pymongo import MongoClient


def main():
    
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(
        token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

############################## Handlers for workout guide function #######################################
    updater.dispatcher.add_handler(CommandHandler('workout', workout_command))
    updater.dispatcher.add_handler(CallbackQueryHandler(main_menu, pattern='main'))
    updater.dispatcher.add_handler(CallbackQueryHandler(advanced, pattern='advanced'))
    updater.dispatcher.add_handler(CallbackQueryHandler(intermediate, pattern='intermediate'))
    updater.dispatcher.add_handler(CallbackQueryHandler(beginner, pattern='beginner'))
    dispatcher.add_handler(CommandHandler("add", add))
##########################################################################################################      
    updater.dispatcher.add_error_handler(error)
    
    updater.start_polling()
    updater.idle()

def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    
    client = MongoClient("mongodb+srv://comp7940group1:comp7940group1@cluster0.vyq4q.mongodb.net/Message-DB?retryWrites=true&w=majority")

    try: 
        db = client.add
        logging.info(context.args[0])
        msg = context.args[0]   # /add keyword <-- this should store the keyword
        result = db.test.insert_one({'test': msg})
        update.message.reply_text("added")
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')
##############################Workout Guide Function #####################################################
def workout_command(bot, update):
    bot.message.reply_text(main_menu_message(),
                         reply_markup=main_menu_keyboard())

def main_menu(bot, update):
    bot.callback_query.message.edit_text(main_menu_message(),
                          reply_markup=main_menu_keyboard())

def advanced(bot, update):
    bot.callback_query.message.edit_text(advanced_message(),
                          reply_markup=None)

def intermediate(bot, update):
    bot.callback_query.message.edit_text(intermediate_message(),
                          reply_markup=None)
def beginner(bot, update):
    bot.callback_query.message.edit_text(beginner_message(),
                          reply_markup=None)
def main_menu_message():
    return 'Please select the desired difficulty for you full-body workout:'

def advanced_message():
    return 'Advanced Exercise:\n\
-Jumping Jacks\n\
-Squat to Curtsy Lunge\n\
-High Knees\n\
-Push-up to Double Shoulder Tap  \n\
-Plyo Lunge\n\
-Sit-up to Glute Bridge\n\
-Finisher: Broad Jump to Burpee\n\
Instructions:\n\
-Do the first six exercises for 1 minute each.\n\
-Do 2 rounds, resting for 1 minute in between rounds.\n\
-Rest 1 minute, and then do the finisher exercise for 1 minute.'
def intermediate_message():
    return 'Intermiediate Exercise:\n\
-Squat to overhead press\n\
-Push-up with renegade row\n\
-Glute bridge with skull-crusher\n\
-Leg lift  \n\
-Burpee with push-up\n\
Instructions:\n\
-Perfrom each move at maximum effort for 45 seconds and then rest for 15 seconds\n\
-Do 3 rounds, resting for 1 minute in between rounds.'
def beginner_message():
    return 'Beginner Exercise:\n\
-Squat Thrust\n\
-Plank Hip Dip\n\
-Lateral Lunge to Single-Leg Hop\n\
-Forearm Plank Reach Out  \n\
-Shoulder Taps\n\
Instructions:\n\
-Perfrom each move at maximum effort for 30 seconds and then rest for 30 seconds\n\
-Do 3 rounds, resting for 2 minute in between rounds.'
    
def main_menu_keyboard():
  keyboard = [[InlineKeyboardButton('Advanced', callback_data='advanced')],
              [InlineKeyboardButton('Intermediate', callback_data='intermediate')],
              [InlineKeyboardButton('Beginner', callback_data='beginner')],]
  return InlineKeyboardMarkup(keyboard)
###########################################################################################################  
def error(update, context):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    main()
