import tweepy
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import time

# Конфигурация Twitter API (получите на developer.twitter.com)
TWITTER_API_KEY = "ВАШ_API_KEY"
TWITTER_API_SECRET = "ВАШ_API_SECRET"
TWITTER_ACCESS_TOKEN = "ВАШ_ACCESS_TOKEN"
TWITTER_ACCESS_SECRET = "ВАШ_ACCESS_SECRET"

# Конфигурация Telegram бота (токен от @BotFather)
TELEGRAM_TOKEN = "ВАШ_TELEGRAM_TOKEN"
TELEGRAM_CHAT_ID = "ВАШ_CHAT_ID"  # Узнать через @userinfobot

# Инициализация Twitter API
auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
twitter_api = tweepy.API(auth)

# Список отслеживаемых аккаунтов (можно менять через команды)
tracked_accounts = ["elonmusk"]  # Пример стартового списка

# Инициализация Telegram бота
bot = Bot(token=TELEGRAM_TOKEN)

# ===== КОМАНДЫ БОТА ===== #
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🐦 **Twitter Tracker Bot**\n\n"
        "Отслеживаю новые твиты из списка аккаунтов.\n\n"
        "🔹 /add username - добавить аккаунт\n"
        "🔹 /remove username - удалить аккаунт\n"
        "🔹 /list - показать список отслеживаемых"
    )

def add_account(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("❌ Укажите username (без @). Пример: /add elonmusk")
        return
    
    username = context.args[0].lower()
    if username in tracked_accounts:
        update.message.reply_text(f"❌ @{username} уже в списке!")
    else:
        tracked_accounts.append(username)
        update.message.reply_text(f"✅ @{username} добавлен в отслеживание!")

def remove_account(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("❌ Укажите username (без @). Пример: /remove elonmusk")
        return
    
    username = context.args[0].lower()
    if username in tracked_accounts:
        tracked_accounts.remove(username)
        update.message.reply_text(f"✅ @{username} удалён из списка!")
    else:
        update.message.reply_text(f"❌ @{username} не найден в отслеживаемых.")

def list_accounts(update: Update, context: CallbackContext):
    if not tracked_accounts:
        update.message.reply_text("📭 Список отслеживаемых аккаунтов пуст.")
    else:
        accounts_list = "\n".join([f"🔹 @{acc}" for acc in tracked_accounts])
        update.message.reply_text(f"📋 **Отслеживаемые аккаунты:**\n\n{accounts_list}")

# ===== ПРОВЕРКА НОВЫХ ТВИТОВ ===== #
def check_new_tweets(context: CallbackContext):
    if not tracked_accounts:
        return
    
    for username in tracked_accounts:
        try:
            tweets = twitter_api.user_timeline(screen_name=username, count=1, tweet_mode="extended")
            if not tweets:
                continue
                
            latest_tweet = tweets[0]
            if not hasattr(context.bot_data, 'last_tweets'):
                context.bot_data.last_tweets = {}
            
            if username not in context.bot_data.last_tweets or context.bot_data.last_tweets[username] != latest_tweet.id:
                context.bot_data.last_tweets[username] = latest_tweet.id
                tweet_url = f"https://twitter.com/{username}/status/{latest_tweet.id}"
                message = f"🐦 **Новый твит от @{username}**\n\n{latest_tweet.full_text}\n\n🔗 {tweet_url}"
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        except Exception as e:
            print(f"Ошибка при проверке @{username}: {e}")

# ===== ЗАПУСК БОТА ===== #
def main():
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher
    
    # Добавляем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add_account))
    dp.add_handler(CommandHandler("remove", remove_account))
    dp.add_handler(CommandHandler("list", list_accounts))
    
    # Проверяем твиты каждые 60 секунд
    updater.job_queue.run_repeating(check_new_tweets, interval=60.0, first=0.0)
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()