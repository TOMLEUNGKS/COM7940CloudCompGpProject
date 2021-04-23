from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, ConversationHandler
import telegram
import configparser
import logging
import csv
import telebot
import matplotlib
import tempfile
import numpy as np
import pandas as pd
import pendulum
from pandas.plotting import register_matplotlib_converters
from pymongo import MongoClient

#dependencies for Sleeping Quality Function
from typing import Dict

############################################### Main ##################################################

config = configparser.ConfigParser()
config.read('config.ini')
client = MongoClient(config['MONGODB']['client_link'])

def main():
    
    matplotlib.use("agg")
    register_matplotlib_converters()

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

############################## Handlers for weight management function ###################################
    dispatcher.add_handler(CommandHandler("start", weight_start))
    dispatcher.add_handler(CommandHandler("weight", weight_store))
    dispatcher.add_handler(CommandHandler("height", height_store))
    dispatcher.add_handler(CommandHandler("bmi", bmi_calculator))
    dispatcher.add_handler(CommandHandler("stats", weight_stats))

############################## Handlers for sleeping quality function ###################################
    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('sleep', sleep)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex('^(No. of hours of sleep|Time taken to fall asleep|Issues encountered)$'), regular_choice
                ),
                MessageHandler(Filters.regex('^Something else...$'), custom_choice),
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')), regular_choice
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    received_information,
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
    )

    dispatcher.add_handler(conv_handler)

###########################################################################################################
    updater.dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()
############################################### Main ##################################################



######################################## weight management function ################################################

def weight_start(update: Update, context: CallbackContext):
    """Send a welcome message."""
    update.message.reply_text(
        "Hi! Just type in your current height (/height) in cm and weight (/weight) in Kg and I'll store it for you!"
    )
    update.message.reply_text(
        "Afterward you can check you stats with /stats and BMI with /bmi"
    )
    update.message.reply_text(
        "Also I can suggest some workouts (/workout )for you "
    )

    update.message.reply_text(
        "Or you may evaluate your sleeping quality by typing /sleep"
    )

def weight_store(update: Update, context: CallbackContext):
    """Send a number (weight) when the command /weight is issued."""

    try: 
        db = client.user
        logging.info(context.args[0])
        number = context.args[0]   # /add keyword <-- this should store the keyword
        result = db.weight.insert_one({'weight': number})
        update.message.reply_text("Weight is stored successfully")
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /weight <keyword>')
    
def height_store(update: Update, context: CallbackContext):
    """Send a number (weight) when the command /weight is issued."""

    try: 
        db = client.user
        logging.info(context.args[0])
        number = context.args[0]   # /add keyword <-- this should store the keyword
        result = db.height.insert_one({'height': number})
        update.message.reply_text("Height is stored successfully")
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /height <keyword>')

def weight_stats(update: Update, context: CallbackContext):
    """check the weight stats"""
    db = client.user
    weight = db.weight.find({})   # /find the weight information 
    weight_data = [w for w in weight] 
    data = []
    for w in weight_data:
        data.append(int(w['weight']))
    w = data[len(weight_data) -1]
    min_weight = min(data)
    max_weight = max(data)
    means_weight = Average(data)
    means_weight = round(means_weight, 2)

    update.message.reply_text("Your most recent weight is "+  str(w) )
    update.message.reply_text("Your weight mean is "+ str(means_weight) + "kg! The minimum was " + str(min_weight) + "kg and maximum was " + str(max_weight)+ "kg.")


def bmi_calculator(update: Update, context: CallbackContext):
    """Calculate the BMI value based on the stored height and weight"""
    db = client.user

    weight = db.weight.find({})   # /find the weight information 
    weight_data = [w for w in weight] 
    w1 = weight_data[len(weight_data) -1]
    w1 = int(w1['weight'])

    height = db.height.find({}) # /find the height information 
    height_data = [h for h in height] 
    h1 = height_data[len(height_data) -1]
    h1 = int(h1['height'])

    BMI = w1 / (h1/100)**2
    BMI = round(BMI, 2)
    if BMI <= 18.4:
        update.message.reply_text("You BMI is "+ str(BMI) + "! You are underweight.")
    elif BMI <= 24.9:
        update.message.reply_text("You BMI is "+ str(BMI) + "! You are healthy.")
    elif BMI <= 29.9:
        update.message.reply_text("You BMI is "+ str(BMI) + "! You are over weight. let me recommend some /workout for you.")
    elif BMI <= 34.9:
        update.message.reply_text("You BMI is "+ str(BMI) + "! You are severely over weight. /workout will be good for your health.")
    elif BMI <= 39.9:
        update.message.reply_text("You BMI is "+ str(BMI) + "! You are obese. let me recommend some /workout for you, it is good for your health.")
    else:
        update.message.reply_text("You BMI is "+ str(BMI) + "! You are severely obese. You definitely require some /workout.")

def Average(lst):
    return sum(lst) / len(lst)

######################################## weight management function ################################################


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
    db=client.workouts
    workouts = db.advancedWorkout.find()
    instructions = db.advancedInstructions.find()
    work = []
    ins = []
    for workout in workouts:
        work.append(workout["workout"])
    for instruction in instructions:
        ins.append(instruction["instruction"])
    return ("\n".join(work + ins))
def intermediate_message():
    db=client.workouts
    workouts = db.intermediateWorkout.find()
    instructions = db.intermediateInstructions.find()
    work = []
    ins = []
    for workout in workouts:
        work.append(workout["workout"])
    for instruction in instructions:
        ins.append(instruction["instruction"])
    return ("\n".join(work + ins))
def beginner_message():
    db=client.workouts
    workouts = db.beginnerWorkout.find()
    instructions = db.beginnerInstructions.find()
    work = []
    ins = []
    for workout in workouts:
        work.append(workout["workout"])
    for instruction in instructions:
        ins.append(instruction["instruction"])
    return ("\n".join(work + ins))
    
def main_menu_keyboard():
  keyboard = [[InlineKeyboardButton('Advanced', callback_data='advanced')],
              [InlineKeyboardButton('Intermediate', callback_data='intermediate')],
              [InlineKeyboardButton('Beginner', callback_data='beginner')],]
  return InlineKeyboardMarkup(keyboard)
###########################################################################################################  

##############################Sleeping Quality Function #####################################################

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [
    ['No. of hours of sleep', 'Time taken to fall asleep'],
    ['Issues encountered', 'Something else...'],
    ['Done'],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data: Dict[str, str]) -> str:
    facts = list()

    for key, value in user_data.items():
        facts.append(f'{key} - {value}')

    return "\n".join(facts).join(['\n', '\n'])


def sleep(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(
        "Yay! Time to evaluate your sleeping quality. We will have an in-depth conversation. Let's crack on!",
        reply_markup=markup,
    )

    return CHOOSING


def regular_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(f'Your {text.lower()}? Yes, I would love to hear about that! Please provide your input below.')

    return TYPING_REPLY


def custom_choice(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(
        'Alright, please send me the category first, for example "The need of taking medicine"'
    )

    return TYPING_CHOICE


def received_information(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    update.message.reply_text(
        "Neat! Just so you know, this is what you already told me:"
        f"{facts_to_str(user_data)} You can tell me more, or change your opinion"
        " on something.",
        reply_markup=markup,
    )

    return CHOOSING


def done(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']
    update.message.reply_text(
        f"I learned these facts about you: {facts_to_str(user_data)}")
    update.message.reply_text(
        "If your no. of hours of sleep is less than 6 hours,")
    update.message.reply_text(
        "or it takes more than 1 hour to fall asleep,")
    update.message.reply_text(
        "or you encounter other issues in connection with sleeping,")
    update.message.reply_text(
        "please consult your family docter or your can learn more here:")
    update.message.reply_text(
        "https://www.sleep.org/sleep-quantity-different-sleep-quality/")
    user_data.clear()
    return ConversationHandler.END

##############################Sleeping Quality Function #####################################################


def error(update, context):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    main()
