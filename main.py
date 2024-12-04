import os
import requests
from bs4 import BeautifulSoup
import telebot
import threading
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Directly input your Telegram bot token here
API_TOKEN = '7636464954:AAGSwsAMV6ZLQf3G_PSdCPkks7mjbecSTf4'  # Replace with your actual token
# Replace this with your actual group chat ID
ALLOWED_CHAT_ID = -1002442784134  # Ensure this is the correct group chat ID
# Replace this with your actual channel username
CHANNEL_USERNAME = 'LkSubOfficial'  # Ensure the correct channel username (without @)

bot = telebot.TeleBot(API_TOKEN, parse_mode='Markdown')

user_requests = {}  # Dictionary to store user requests keyed by user ID

# Function to check if user is a member of the channel
def is_member(user_id):
    try:
        member_status = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member_status.status in ['member', 'administrator', 'creator']
    except:
        return False

# Function to check if the message is from the allowed group
def is_allowed_group(message):
    return message.chat.id == ALLOWED_CHAT_ID

# Function to search movie link
def search(name):
    repnam = name.replace(" ", "+")
    linkgen = "https://piratelk.com/?s=" + repnam
    return linkgen

# Function to get response
def respon(ab):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.baiscope.lk/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    res = requests.get(ab, headers=headers)
    beso = BeautifulSoup(res.content, "lxml")
    return beso

# Function to get movie list
def movielist(beso):
    moviehref = []
    moviename = []
    fi = beso.find_all("h2", {"class": "post-box-title"})
    for i in fi:
        finda = i.find("a")
        findname = finda.string
        findurl = finda.get("href")
        moviename.append(findname)
        moviehref.append(findurl)
    return moviename, moviehref

# Function to download subtitle
def subdown(gopage, moviehref):
    xox = gopage - 1
    if xox >= 0:
        getli = moviehref[xox]
        res2 = requests.get(getli)
        sop = BeautifulSoup(res2.content, "lxml")
        fisub = sop.find("a", {"class": "download-link download-button aligncenter"})
        gethr = fisub.get("href")
        return gethr

# Function to generate subtitle name
def subnamegen(abc):
    x = abc
    sos = x[30:]
    ses = sos.split("/?")[0]
    return ses

# Function to save subtitle
def subsave(subs, ss):
    res3 = requests.get(subs)
    with open(ss + ".zip", "wb") as f:
        f.write(res3.content)
    print('Download success....')

# Function to clear user requests periodically
def clear_user_requests():
    while True:
        time.sleep(3600)  # Sleep for 3600 seconds (1 hour)
        user_requests.clear()
        print('Cleared user requests')

# Start the clear_user_requests function in a separate thread
threading.Thread(target=clear_user_requests, daemon=True).start()

# Handler for /find command
@bot.message_handler(commands=['find'])
def handle_find(message):
    if not is_allowed_group(message):
        bot.reply_to(message, "This bot can only be used in the designated group.")
        return

    user_id = message.from_user.id
    if not is_member(user_id):
        markup = InlineKeyboardMarkup()
        join_button = InlineKeyboardButton("🔅Join Now🔅", url=f"https://t.me/{CHANNEL_USERNAME}")
        markup.add(join_button)
        bot.send_message(
            message.chat.id, 
            "ම්ම්..🙄 ඔයා අපේ Main චැනල් එකට ජොයින් වෙලා නෑ..\n\n🥲නැත්තන් subtitles ගන්න වෙන්නේ නෑ..🥲\n\n😊පහලින් තියන 'Join Now' බට්න් එක ඔබලා ගිහින් අපේ Main චැනල් එකට ජොයින් වෙලා එන්නකෝ..", 
            reply_markup=markup
        )
        return

    name = message.text.split("/find ", 1)[1]
    link = search(name)
    beso = respon(link)
    moviename, moviehref = movielist(beso)

    if moviename:
        response = "Movie List:\n"
        for idx, moname in enumerate(moviename, 1):
            movn = moname.split("|")[0]
            response += f"🔰 {idx} ➡ {movn}\n"
        response += "\n🔸Reply with the movie number to get subtitles🔹"
        bot.reply_to(message, response)

        # Store the user's request with the movie list and links keyed by user ID
        user_requests[user_id] = {'moviename': moviename, 'moviehref': moviehref}

        # Schedule to clear the user's request after 1 hour
        threading.Timer(3600, lambda: user_requests.pop(user_id, None)).start()
    else:
        bot.reply_to(message, "Movie Not Found!")

# Handler for replying with the movie number
@bot.message_handler(func=lambda message: message.reply_to_message and message.reply_to_message.text.startswith("Movie List"))
def handle_reply(message):
    if not is_allowed_group(message):
        bot.reply_to(message, "This bot can only be used in the designated group.")
        return

    user_id = message.from_user.id
    if not is_member(user_id):
        markup = InlineKeyboardMarkup()
        join_button = InlineKeyboardButton("🔅Join Now🔅", url=f"https://t.me/{CHANNEL_USERNAME}")
        markup.add(join_button)
        bot.send_message(
            message.chat.id, 
            "ම්ම්..🙄 ඔයා අපේ Main චැනල් එකට ජොයින් වෙලා නෑ..\n\n🥲නැත්තන් subtitles ගන්න වෙන්නේ නෑ..🥲\n\n😊පහලින් තියන 'Join Now' බට්න් එක ඔබලා ගිහින් අපේ Main චැනල් එකට ජොයින් වෙලා එන්නකෝ..", 
            reply_markup=markup
        )
        return

    try:
        gopage = int(message.text.strip())
        user_data = user_requests.get(user_id)

        if user_data and 1 <= gopage <= len(user_data['moviename']):
            gethref = subdown(gopage, user_data['moviehref'])
            if gethref:
                subnameyes = subnamegen(gethref)
                subsave(gethref, subnameyes)

                # Upload file to Telegram group
                with open(subnameyes + ".zip", "rb") as file:
                    bot.send_document(message.chat.id, file)

                # Delete file after upload
                os.remove(subnameyes + ".zip")
            else:
                bot.reply_to(message, "Invalid movie number!")
        else:
            bot.reply_to(message, "Invalid movie number or no active search!")
    except ValueError:
        bot.reply_to(message, "Please reply with a valid movie number.")

# Handler for /conn command
@bot.message_handler(commands=['conn'])
def handle_conn(message):
    bot.reply_to(message, "🔆I am Alive 💫")

# Polling
bot.polling()






