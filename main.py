from telebot import TeleBot
from telebot_token import TOKEN
import requests


def get_tiktok_video_url(tiktok_url: str) -> str:
    api_url = "https://tikwm.com/api/"
    params = {
        "url": tiktok_url
    }

    response = requests.get(api_url, params=params)
    data = response.json()

    if data.get("code") == 0:
        return data["data"]["play"]
    else:
        raise Exception(data.get("msg", "Unknown error"))


def main():
    bot = TeleBot(TOKEN)

    @bot.message_handler(commands=['test'])
    def handle_test(message):
        pass

    @bot.message_handler(commands=['start', 'help'])
    def handle_start_help(message):
        start_message = f"Hi, {message.from_user.first_name}.\n" \
                        "I can convert audio or video into a voice message.\n" \
                        "Send audio or video.\n"
        bot.send_message(message.chat.id, start_message)

    @bot.message_handler(func=lambda message: 'tiktok.com/' in message.text)
    def handle_tiktok(message):
        # bot.reply_to(message, "🔄 Downloading...")
        video_url = get_tiktok_video_url(message.text.strip())
        bot.send_video(message.chat.id, video=video_url, reply_to_message_id=message.message_id)

    bot.infinity_polling()


if __name__ == '__main__':
    main()
