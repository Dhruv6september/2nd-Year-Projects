import random
import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from datetime import datetime
from PIL import Image, ImageFilter
import io

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def get_gemini_data():
    base_url = 'https://api.gemini.com/v1/symbols'
    response = requests.get(base_url)
    if response.status_code == 200:
        data = response.json()
        return f"Available trading pairs: {', '.join(data)}"
    else:
        return "Sorry, I couldn't fetch data from Gemini."

# Define the Gemini command
async def gemini(update: Update, context):
    gemini_info = get_gemini_data()
    await update.message.reply_text(gemini_info)


async def start(update: Update, context):
    user = update.message.from_user.first_name  # Get user's first name
    current_hour = datetime.now().hour  # Get the current hour
    
    # Determine the appropriate greeting based on the time of day
    if current_hour < 12:
        greeting = f"Good morning, {user}! 🌅"
    elif current_hour < 18:
        greeting = f"Good afternoon, {user}! ☀️"
    else:
        greeting = f"Good evening, {user}! 🌙"
    
    await update.message.reply_text(f"{greeting} I am Mickey, your Telegram bot for all things fun and useful. How can I assist you today? :)")

# Game States
CHOOSING, ACTION, FIGHT, FINAL_CHOICE = range(4)

def get_exchange_rate(from_currency, to_currency):
    api_key = "09e49fe5e3bcc1efcde7f37d"
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        rate = data['conversion_rate']
        return f"1 {from_currency.upper()} = {rate} {to_currency.upper()}"
    else:
        return "Sorry, I couldn't fetch the exchange rate at the moment."

# Define the currency command
async def convert_currency(update: Update, context):
    if len(context.args) < 2:
        await update.message.reply_text("Please provide the currencies in this format: /convert USD EUR")
    else:
        from_currency, to_currency = context.args[:2]
        rate = get_exchange_rate(from_currency, to_currency)
        await update.message.reply_text(rate)

def get_news():
    api_key = "768df22d0cfb4de382a613c0b751b432"
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json()['articles'][:5]  # Get the first 5 news articles
        news_list = "\n\n".join([f"{i+1}. {article['title']} - {article['source']['name']}" for i, article in enumerate(articles)])
        return f"📰 Latest News:\n{news_list}"
    else:
        return "Sorry, I couldn't fetch the news. Please try again later."

# Define the news command
async def news(update: Update, context):
    latest_news = get_news()
    await update.message.reply_text(latest_news)

def get_weather(city):
    api_key = "c7be99bc05b26796fd3ade94dd4052df"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:      
        data = response.json()
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"The weather in {city.capitalize()} is currently {weather} with a temperature of {temp}°C."
    else:
        return "Sorry, I couldn't fetch the weather. Please check the city name or try again later."

# Define the weather command
async def weather(update: Update, context):
    if len(context.args) == 0:
        await update.message.reply_text("Please provide a city name. Example: /weather London")
    else:
        city = ' '.join(context.args)
        weather_info = get_weather(city)
        await update.message.reply_text(weather_info)

# Fetch a random joke from the Official Joke API
def get_random_joke():
    response = requests.get("https://official-joke-api.appspot.com/random_joke")
    if response.status_code == 200:
        joke_data = response.json()
        joke = f"{joke_data['setup']} - {joke_data['punchline']}"
        return joke
    else:
        return "Sorry, I couldn't fetch a joke at the moment. Please try again later."

# Define the joke command
async def joke(update: Update, context):
    joke = get_random_joke()
    await update.message.reply_text(joke)

# Define the help command
async def help_command(update: Update, context):
    await update.message.reply_text("""Wanna know what all can I do for you? You can see the list below!:
/youtube : to get the URL for YouTube's home page!
/gmail : to get the URL for Gmail's Login page!
/spotify : to get the URL for Spotify's web player!
/linkedin : to get the URL for LinkedIn's Login page!
/facebook : to get the URL for Facebook's Login page!
/mickey: to get the bot's description!
/billboard: to get the most recent news from Billboard's website!
/adventure : to start the adventure game!
/studentportal: to get the website link to SRM student portal!
/joke : to hear a random joke!
/weather: to get weather information about any city in the world!
/news: to get the top 5 latest news from around the world
/convert <currency1> <currency2>: to know about the current exchange rate""")

# Adventure game starts here
async def adventure_start(update: Update, context):
    await update.message.reply_text(
        "🌳 Welcome to the Interactive Adventure Game!\n"
        "You are a brave traveler standing at a mysterious forest entrance. 🌲\n"
        "A strange fog surrounds you.\n"
        "Will you go *left* to explore the ancient ruins, or *right* towards the dense forest?\n"
        "Type 'left' or 'right' to choose your path."
    )
    return CHOOSING

# Handle the user's choice in the adventure game
async def choose_path(update: Update, context):
    choice = update.message.text.lower()

    if choice == 'left':
        await update.message.reply_text(
            "🏛️ You chose to explore the ancient ruins.\n"
            "As you approach, you hear eerie noises from inside the crumbling structure. \n"
            "Do you *enter* the ruins or *run* back to safety?\n"
            "Type 'enter' or 'run'."
        )
        return ACTION

    elif choice == 'right':
        await update.message.reply_text(
            "🌲 You venture into the dense forest. The trees whisper as you walk.\n"
            "Suddenly, a wild creature appears in front of you! 🐺\n"
            "Will you *fight* or *run*?\n"
            "Type 'fight' or 'run'."
        )
        return FIGHT

    else:
        await update.message.reply_text("I don't understand that. Please type 'left' or 'right'.")
        return CHOOSING

# Handle the next action based on the user's previous choice
async def next_action(update: Update, context):
    action = update.message.text.lower()

    if action == 'enter':
        random_event = random.choice(["find a treasure chest", "encounter a ghost", "fall into a trap"])
        if random_event == "find a treasure chest":
            await update.message.reply_text("💰 You enter the ruins and stumble upon a hidden treasure chest filled with gold! You win!")
        elif random_event == "encounter a ghost":
            await update.message.reply_text("👻 A ghost appears and haunts you out of the ruins. Better luck next time!")
        else:
            await update.message.reply_text("🚨 You fall into a trap and the ruins collapse. Game over.")
        return ConversationHandler.END

    elif action == 'run':
        await update.message.reply_text("You run back to safety, but the adventure isn't over yet. Would you like to try again? Type /adventure to restart!")
        return ConversationHandler.END

    else:
        await update.message.reply_text("I don't understand that. Please type 'enter' or 'run'.")
        return ACTION

# Handle the fight scenario
async def fight(update: Update, context):
    action = update.message.text.lower()

    if action == 'fight':
        if random.random() > 0.5:  # Random chance to win the fight
            await update.message.reply_text("⚔️ You bravely fight the wild creature and emerge victorious! You find a secret passage leading to hidden treasures!")
            return FINAL_CHOICE
        else:
            await update.message.reply_text("😔 The creature is too strong. You are defeated. Better luck next time!")
            return ConversationHandler.END

    elif action == 'run':
        await update.message.reply_text("You run deeper into the forest. Suddenly, you find yourself lost in a maze of trees. Game over.")
        return ConversationHandler.END

    else:
        await update.message.reply_text("I don't understand that. Please type 'fight' or 'run'.")
        return FIGHT

# Final decision after winning the fight
async def final_decision(update: Update, context):
    await update.message.reply_text(
        "🎉 You reach a room filled with treasures and mysterious artifacts.\n"
        "Do you *take* the treasure or *leave* it and explore further?\n"
        "Type 'take' or 'leave'."
    )
    return FINAL_CHOICE

# Handle the final choice of the game
async def handle_final_choice(update: Update, context):
    choice = update.message.text.lower()

    if choice == 'take':
        await update.message.reply_text("💰 You take the treasure and live a life of wealth and luxury. You win!")
    elif choice == 'leave':
        await update.message.reply_text("🔍 You leave the treasure behind and venture deeper into the unknown. Who knows what mysteries await you?")
    else:
        await update.message.reply_text("I don't understand that. Please type 'take' or 'leave'.")
        return FINAL_CHOICE

    return ConversationHandler.END

# Define other command handlers (gmail, facebook, etc.)
async def gmail(update: Update, context):
    await update.message.reply_text("Link to Gmail to access all those mails that you haven't opened in like a thousand years: https://www.gmail.com/login")

async def facebook(update: Update, context):
    await update.message.reply_text("Link to Facebook to socialise with your friends or make new ones: https://www.facebook.com/login")

async def youtube(update: Update, context):
    await update.message.reply_text("Link to YouTube to surf new video content: https://www.youtube.com/home-page")

async def linkedin(update: Update, context):
    await update.message.reply_text("Link to LinkedIn to make yourself a professional dashboard: https://www.linkedin.com/login")

async def spotify(update: Update, context):
    await update.message.reply_text("Link to Spotify to relax a little: https://www.spotify.com")
 
async def mickey(update: Update, context):
    await update.message.reply_text("""Mickey Bot: Your Friendly All-in-One Telegram Companion!

🤖 Introducing Mickey Bot: Your All-in-One Telegram Companion!

Mickey Bot is designed to make your life easier and more entertaining with just a few taps! Whether you need quick access to essential resources, want to enjoy a fun game, or simply need a good laugh, Mickey is here to assist you.

🌟 Features:
Quick Links: Instantly access popular websites like YouTube, Gmail, Facebook, LinkedIn, and Spotify with simple commands. No need to search—just type and go!

Interactive Adventure Game: Embark on a thrilling text-based adventure where your choices determine the outcome. Explore ancient ruins or venture into a dense forest; the adventure awaits!

Daily Humor: Brighten your day with a random joke fetched from the Official Joke API. Laughter is just a command away!

Latest News: Stay informed with the top headlines from around the world and updates from Billboard's latest hits.

Weather Updates: Get real-time weather information for any city you choose, ensuring you're always prepared for the elements.

Currency Converter: Check the latest exchange rates between different currencies with ease.

Always Here to Help: Just type /help to see the full range of services Mickey offers. Your helpful companion is always ready to assist you!

💬 How to Get Started:
Simply type /start to greet Mickey and discover all the exciting features at your fingertips. Whether you’re looking for information, entertainment, or just a bit of fun, Mickey is your go-to bot for all things enjoyable and useful!""")    

async def billboard(update: Update, context):
    await update.message.reply_text("The most recent news from Billboard's website: https://www.billboard.com/vcategory/billboard-news/")

async def studentportal(update: Update, context):
    await update.message.reply_text("Link to SRM Student portal to check your attendance to see if you can bunk classes, OH NO! I meant to check your progress in college: https://sp.srmist.edu.in/srmiststudentportal/students/loginManager/youLogin.jsp")

# Handle unknown text messages
async def unknown_text(update: Update, context):
    await update.message.reply_text(f"Sorry I can't recognize you :( , you said '{update.message.text}'. You're a stranger to me >:|")

# Handle unknown commands
async def unknown(update: Update, context):
    await update.message.reply_text(f"Sorry '{update.message.text}' is not a valid command :(")

# Main function to run the bot
def main():
    application = Application.builder().token("7236577890:AAEeoKyoZX2QPITkvmprcQsMS1cON6euDG4").build()

    # Add handlers for the game conversation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('adventure', adventure_start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT, choose_path)],
            ACTION: [MessageHandler(filters.TEXT, next_action)],
            FIGHT: [MessageHandler(filters.TEXT, fight)],
            FINAL_CHOICE: [MessageHandler(filters.TEXT, handle_final_choice)]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    # Add all other handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("youtube", youtube))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("linkedin", linkedin))
    application.add_handler(CommandHandler("gmail", gmail))
    application.add_handler(CommandHandler("spotify", spotify))
    application.add_handler(CommandHandler("billboard", billboard))
    application.add_handler(CommandHandler("facebook", facebook))
    application.add_handler(CommandHandler("mickey", mickey))
    application.add_handler(CommandHandler("studentportal", studentportal))
    application.add_handler(CommandHandler("joke", joke))  # New joke handler
    application.add_handler(CommandHandler("weather", weather))#Weather 
    application.add_handler(CommandHandler("news", news))#news
    application.add_handler(CommandHandler("convert", convert_currency))#currencyconveter
    application.add_handler(conv_handler)

    # Filters out unknown commands
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Filters out unknown messages
    application.add_handler(MessageHandler(filters.TEXT, unknown_text))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
