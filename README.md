# CarEra daily photo bot

Posts one car per day to Telegram: 3 eras x 3 freely licensed photos from
Wikimedia Commons, each with author and licence, plus a credits message.

Setup (GitHub, free):
1. Telegram: @BotFather -> /newbot -> copy the token. Write any message to your bot.
   Open https://api.telegram.org/bot<TOKEN>/getUpdates and copy "chat":{"id": ...}.
2. GitHub: new PRIVATE repository, upload all files of this folder (keep .github/).
3. Repo -> Settings -> Secrets and variables -> Actions -> New secret:
   TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, CONTACT (an e-mail or URL for Wikimedia).
4. Actions tab -> "CarEra daily photos" -> Run workflow (test). After that it runs every day.

Edit cars.json to add cars (each: name + 3 eras with a Commons search phrase).
Photos are CC BY / CC BY-SA / CC0 / PD only: always credit the author,
link the licence and say the image was edited.
