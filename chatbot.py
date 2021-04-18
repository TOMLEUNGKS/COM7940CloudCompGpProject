from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup 
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

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

import matplotlib.pyplot as plt

############################################### Main ##################################################
############################################### Main ##################################################
############################################### Main ##################################################

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
##########################################################################################################   


############################## Handlers for weight management function ###################################
    dispatcher.add_handler(CommandHandler("start", weight_start))
    dispatcher.add_handler(CommandHandler("weight", weight_store))
    dispatcher.add_handler(CommandHandler("height", height_store))
    dispatcher.add_handler(CommandHandler("bmi", bmi_calculator))
##########################################################################################################   
   
    updater.dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()

############################################### Main ##################################################
############################################### Main ##################################################
############################################### Main ##################################################


######################################## weight management function ################################################

def weight_start(update: Update, context: CallbackContext):
    """Send a welcome message."""
    update.message.reply_text(
        "Hi! Just type in your current height (/height) in cm and weight (/weight) in Kg and I'll store it for you!"
    )

def weight_store(update: Update, context: CallbackContext):
    """Send a number (weight) when the command /weight is issued."""
    client = MongoClient("mongodb+srv://comp7940group1:comp7940group1@cluster0.vyq4q.mongodb.net/Message-DB?retryWrites=true&w=majority")

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
    client = MongoClient("mongodb+srv://comp7940group1:comp7940group1@cluster0.vyq4q.mongodb.net/Message-DB?retryWrites=true&w=majority")

    try: 
        db = client.user
        logging.info(context.args[0])
        number = context.args[0]   # /add keyword <-- this should store the keyword
        result = db.height.insert_one({'height': number})
        update.message.reply_text("Height is stored successfully")
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /height <keyword>')

def bmi_calculator(update: Update, context: CallbackContext):
    """Calculate the BMI value based on the stored height and weight"""
    client = MongoClient("mongodb+srv://comp7940group1:comp7940group1@cluster0.vyq4q.mongodb.net/Message-DB?retryWrites=true&w=majority")
    db = client.user
    update.message.reply_text('BMIBMIBMI')

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
        update.message.reply_text("You BMI is "+ str(BMI) + "! You are over weight.")
    elif BMI <= 34.9:
        update.message.reply_text("You BMI is "+ str(BMI) + "! You are severely over weight.")
    elif BMI <= 39.9:
        update.message.reply_text("You BMI is "+ str(BMI) + "! You are obese.")
    else:
        update.message.reply_text("You BMI is "+ str(BMI) + "! You are severely obese.")

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
-Perform each move at maximum effort for 45 seconds and then rest for 15 seconds\n\
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
