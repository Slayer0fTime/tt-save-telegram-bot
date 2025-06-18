from dotenv import load_dotenv
import telebot
import requests
import os


def get_tiktok_media(tiktok_url: str) -> dict:
    api_url = "https://tikwm.com/api/"
    params = {"url": tiktok_url}
    response = requests.get(api_url, params=params)

    data = response.json()
    if data.get("code") != 0:
        raise Exception("API error: " + data.get("msg", "Unknown"))

    media = data["data"]
    if media.get('images'):
        return {"type": "images", "urls": media["images"]}
    return {"type": "video", "url": media["play"]}


def main() -> None:
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start'])
    def handle_start(message):
        start_message = (
            f"👋 Welcome, <b>{message.from_user.first_name}</b>\n"
            "Send me a TikTok link and I’ll return the media\n\n"
            "🔗 Just paste a TikTok URL here and I’ll do the rest"
        )
        bot.send_message(message.chat.id, start_message, parse_mode="HTML")

    @bot.message_handler(commands=['help'])
    def handle_help(message):
        help_message = (
            "📌 <b>How to use this bot:</b>\n\n"
            "➊ Copy a link to any TikTok video or photo post\n"
            "➋ Send it here\n"
            "➌ Get the video or photo gallery with no watermark"
        )
        bot.send_message(message.chat.id, help_message, parse_mode="HTML")

    @bot.message_handler(func=lambda msg: "https://" in msg.text and "tiktok.com/" in msg.text)
    def handle_tiktok_link(message) -> None:
        try:
            media = get_tiktok_media(message.text.strip())

            if media["type"] == "video":
                bot.send_chat_action(message.chat.id, 'upload_video')
                bot.send_video(message.chat.id, media["url"], reply_to_message_id=message.message_id)
            elif media["type"] == "images":
                send_photo_gallery(message.chat.id, media["urls"], message.message_id)
        except Exception as e:
            bot.reply_to(message, f"❌ Unexpected error:\n{e}")

    def send_photo_gallery(chat_id: int, photos: str, reply_to: int) -> None:
        CHUNK_SIZE = 10
        for i in range(0, len(photos), CHUNK_SIZE):
            chunk = photos[i:i + CHUNK_SIZE]
            media_group = [telebot.types.InputMediaPhoto(url) for url in chunk]
            bot.send_chat_action(chat_id, 'upload_photo', 10)
            bot.send_media_group(chat_id, media_group, reply_to_message_id=reply_to)

    @bot.message_handler(func=lambda message: True)
    def handle_other(message):
        bot.reply_to(message, "This is not a valid TikTok video link")

    bot.infinity_polling()


if __name__ == '__main__':
    main()
