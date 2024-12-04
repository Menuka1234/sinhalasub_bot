import os
import requests
from bs4 import BeautifulSoup
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '7636464954:AAGSwsAMV6ZLQf3G_PSdCPkks7mjbecSTf4'  # Replace with your actual bot token
ALLOWED_CHAT_ID = -1002442784134  # Replace with your group chat ID
CHANNEL_USERNAME = 'LkSubOfficial'  # Replace with your channel username (without @)

bot = telebot.TeleBot(API_TOKEN, parse_mode='Markdown')

# Dictionary to store movie lists and their associated message IDs
search_results = {}

# Function to check if a user is a member of the channel
def is_member(user_id):
    try:
        member_status = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member_status.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False

# Function to search for movies
def search_movies(query):
    return f"https://piratelk.com/?s={query.replace(' ', '+')}"

# Function to parse movie list from search results
def get_movie_list(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "lxml")

    movie_names = []
    movie_links = []
    for post in soup.find_all("h2", {"class": "post-box-title"}):
        link = post.find("a")
        if link:
            movie_names.append(link.text.strip())
            movie_links.append(link['href'])

    return movie_names, movie_links

# Function to fetch subtitle link
def get_subtitle_link(index, movie_links):
    if 0 <= index < len(movie_links):
        url = movie_links[index]
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "lxml")
        download_link = soup.find("a", {"class": "download-link download-button aligncenter"})
        return download_link['href'] if download_link else None
    return None

# Function to save subtitle file
def save_subtitle(url, filename):
    response = requests.get(url)
    with open(f"{filename}.zip", "wb") as file:
        file.write(response.content)

# Command: /find
@bot.message_handler(commands=['find'])
def handle_find(message):
    if message.chat.id != ALLOWED_CHAT_ID:
        bot.reply_to(message, "This bot can only be used in the designated group.")
        return

    user_id = message.from_user.id
    if not is_member(user_id):
        markup = InlineKeyboardMarkup()
        join_button = InlineKeyboardButton("🔅Join Now🔅", url=f"https://t.me/{CHANNEL_USERNAME}")
        markup.add(join_button)
        bot.send_message(
            message.chat.id,
            "Please join our channel to access subtitles.",
            reply_markup=markup
        )
        return

    try:
        query = message.text.split(maxsplit=1)[1]
    except IndexError:
        bot.reply_to(message, "Please provide a movie name after the /find command.")
        return

    movie_names, movie_links = get_movie_list(search_movies(query))

    if movie_names:
        response = "Movie List:\n"
        for idx, name in enumerate(movie_names, 1):
            response += f"{idx}. {name}\n"
        response += "\nReply with the movie number to get subtitles."

        sent_message = bot.reply_to(message, response)
        search_results[sent_message.message_id] = {'moviename': movie_names, 'moviehref': movie_links}
    else:
        bot.reply_to(message, "No movies found!")

# Handle replies with movie numbers
@bot.message_handler(func=lambda message: message.reply_to_message and message.reply_to_message.message_id in search_results)
def handle_reply(message):
    if message.chat.id != ALLOWED_CHAT_ID:
        bot.reply_to(message, "This bot can only be used in the designated group.")
        return

    user_id = message.from_user.id
    if not is_member(user_id):
        markup = InlineKeyboardMarkup()
        join_button = InlineKeyboardButton("🔅Join Now🔅", url=f"https://t.me/{CHANNEL_USERNAME}")
        markup.add(join_button)
        bot.send_message(
            message.chat.id,
            "Please join our channel to access subtitles.",
            reply_markup=markup
        )
        return

    try:
        movie_index = int(message.text.strip()) - 1
        search_data = search_results[message.reply_to_message.message_id]

        if 0 <= movie_index < len(search_data['moviename']):
            subtitle_url = get_subtitle_link(movie_index, search_data['moviehref'])
            if subtitle_url:
                filename = search_data['moviename'][movie_index]
                save_subtitle(subtitle_url, filename)

                with open(f"{filename}.zip", "rb") as file:
                    bot.send_document(message.chat.id, file)

                os.remove(f"{filename}.zip")  # Remove the file after sending
            else:
                bot.reply_to(message, "Subtitle link not found.")
        else:
            bot.reply_to(message, "Invalid movie number.")
    except ValueError:
        bot.reply_to(message, "Please reply with a valid movie number.")

# Command: /conn
@bot.message_handler(commands=['conn'])
def handle_conn(message):
    bot.reply_to(message, "I am Alive!")

# Start the bot
bot.polling()

