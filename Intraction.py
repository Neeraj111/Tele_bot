import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler

# Stages of conversation for credentials and cookies
REQUEST_COOKIES, REQUEST_CREDENTIALS, APPLY_JOB = range(3)

# Store user session data (in production use encrypted storage)
user_data = {}

# LinkedIn login or job apply logic using cookies
def linkedin_apply(cookies, job_url):
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Cookie': cookies
    }
    # For example purposes, assume job_url is a LinkedIn job link
    response = requests.get(job_url, headers=headers)
    if response.status_code == 200:
        # Logic to apply for job (example)
        return True
    return False

# Internshala login or job apply logic using cookies
def internshala_apply(cookies, job_url):
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Cookie': cookies
    }
    # Example of applying for a job in Internshala
    response = requests.get(job_url, headers=headers)
    if response.status_code == 200:
        # Logic to apply for job (example)
        return True
    return False

async def start(update: Update, context):
    await update.message.reply_text("Welcome! Please choose:\n1. /apply_linkedin\n2. /apply_internshala")

async def request_cookies(update: Update, context):
    await update.message.reply_text("Please provide your LinkedIn/Internshala cookies as JSON.")
    return REQUEST_COOKIES

async def request_credentials(update: Update, context):
    await update.message.reply_text("Cookies not provided. Please provide LinkedIn/Internshala credentials.")
    return REQUEST_CREDENTIALS

async def receive_cookies(update: Update, context):
    cookies = update.message.text
    user_id = update.message.from_user.id
    user_data[user_id] = {'cookies': cookies}
    await update.message.reply_text("Cookies saved! Now send me a job URL to apply.")
    return APPLY_JOB

async def receive_credentials(update: Update, context):
    credentials = update.message.text
    user_id = update.message.from_user.id
    user_data[user_id] = {'credentials': credentials}
    await update.message.reply_text("Credentials saved! Now send me a job URL to apply.")
    return APPLY_JOB

async def apply_job(update: Update, context):
    job_url = update.message.text
    user_id = update.message.from_user.id

    # Check if the user has provided cookies or credentials
    if 'cookies' in user_data[user_id]:
        cookies = user_data[user_id]['cookies']
        if 'linkedin' in job_url:
            if linkedin_apply(cookies, job_url):
                await update.message.reply_text(f"Successfully applied for job on LinkedIn: {job_url}")
            else:
                await update.message.reply_text(f"Failed to apply for job on LinkedIn: {job_url}")
        elif 'internshala' in job_url:
            if internshala_apply(cookies, job_url):
                await update.message.reply_text(f"Successfully applied for job on Internshala: {job_url}")
            else:
                await update.message.reply_text(f"Failed to apply for job on Internshala: {job_url}")
        else:
            await update.message.reply_text("Invalid job URL.")
    else:
        await update.message.reply_text("Please provide cookies or credentials first.")
    
    return ConversationHandler.END

async def cancel(update: Update, context):
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token('8189699500:AAG2-BV8XNW2elFyZ8dK1NczrAESU8wnHHI').build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('apply_linkedin', request_cookies), CommandHandler('apply_internshala', request_cookies)],
        states={
            REQUEST_COOKIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_cookies)],
            REQUEST_CREDENTIALS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_credentials)],
            APPLY_JOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, apply_job)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.run_polling()
