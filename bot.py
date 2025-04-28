
import json
import asyncio
import logging
from telethon import TelegramClient, events
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# تنظیمات
API_ID = 'YOUR_API_ID'  # از my.telegram.org
API_HASH = 'YOUR_API_HASH'  # از my.telegram.org
PHONE = 'YOUR_PHONE_NUMBER'  # شماره اکانت تلگرام
BOT_TOKEN = 'YOUR_BOT_TOKEN'  # توکن از BotFather
CONFIG_FILE = 'forwards.json'
ERROR_LOG = 'errors.json'

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# فیلتر کلمات
WORD_FILTERS = {
    'عضوشو': 'سلام',
    'عضوکن': 'خداحافظ'
}

# بارگذاری یا ایجاد فایل تنظیمات
def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'forwards': [], 'users': []}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# مدیریت خطاها
def log_error(error_message):
    try:
        with open(ERROR_LOG, 'r') as f:
            errors = json.load(f)
    except FileNotFoundError:
        errors = []
    errors.append({'time': str(asyncio.get_event_loop().time()), 'message': error_message})
    with open(ERROR_LOG, 'w') as f:
        json.dump(errors, f, indent=4)

# بررسی کاربر مجاز
def is_authorized_user(user_id):
    config = load_config()
    return user_id in config['users']

# فیلتر و جایگزینی کلمات در متن
def filter_text(text):
    if not text:
        return text
    for old_word, new_word in WORD_FILTERS.items():
        text = text.replace(old_word, new_word)
    return text

# منوی اصلی
def main_menu():
    keyboard = [
        [InlineKeyboardButton("افزودن هدایت جدید", callback_data='add_forward')],
        [InlineKeyboardButton("لیست هدایت‌ها", callback_data='list_forwards')],
        [InlineKeyboardButton("لیست چت‌ها", callback_data='list_chats')],
        [INLINEKeyboardButton("لیست خطاها", callback_data='errors')],
    ]
    return InlineKeyboardMarkup(keyboard)

# دستور شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    config = load_config()
    if not config['users']:
        config['users'].append(user_id)
        save_config(config)
    if not is_authorized_user(user_id):
        await update.message.reply_text("شما مجاز به استفاده از این ربات نیستید!")
        return
    await update.message.reply_text("به ربات فوروارد پیشرفته خوش آمدید!", reply_markup=main_menu())

# افزودن هدایت جدید
async def add_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_authorized_user(user_id):
        await query.message.reply_text("شما مجاز به استفاده از این ربات نیستید!")
        return
    await query.message.delete()
    context.user_data['add_forward_step'] = 'source'
    client = TelegramClient('forwarder', API_ID, API_HASH)
    await client.start(phone=PHONE)
    chats = []
    async for dialog in client.iter_dialogs():
        chats.append({'id': dialog.id, 'title': dialog.title})
    await client.disconnect()
    keyboard = [
        [InlineKeyboardButton(chat['title'], callback_data=f"source_{chat['id']}")]
        for chat in chats
    ]
    keyboard.append([InlineKeyboardButton("لغو", callback_data='cancel')])
    await query.message.reply_text("لطفاً چت مبدا را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))

# انتخاب چت مقصد
async def select_destination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_authorized_user(user_id):
        await query.message.reply_text("شما مجاز به استفاده از این ربات نیستید!")
        return
    source_chat = query.data.split('_')[1]
    context.user_data['source_chat'] = source_chat
    context.user_data['add_forward_step'] = 'destination'
    client = TelegramClient('forwarder', API_ID, API_HASH)
    await client.start(phone=PHONE)
    chats = []
    async for dialog in client.iter_dialogs():
        chats.append({'id': dialog.id, 'title': dialog.title})
    await client.disconnect()
    keyboard = [
        [InlineKeyboardButton(chat['title'], callback_data=f"dest_{chat['id']}")]
        for chat in chats
    ]
    keyboard.append([InlineKeyboardButton("لغو", callback_data='cancel')])
    await query.message.edit_text("لطفاً چت مقصد را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))

# دریافت کلمات کلیدی
async def get_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_authorized_user(user_id):
        await query.message.reply_text("شما مجاز به استفاده از این ربات نیستید!")
        return
    dest_chat = query.data.split('_')[1]
    context.user_data['dest_chat'] = dest_chat
    context.user_data['add_forward_step'] = 'keywords'
    await query.message.edit_text("لطفاً کلمات کلیدی را وارد کنید (با کاما جدا شده) یا برای فوروارد همه پیام‌ها، خالی بگذارید:")
    keyboard = [[InlineKeyboardButton("لغو", callback_data='cancel')]]
    await query.message.reply_text("کلمات کلیدی:", reply_markup=InlineKeyboardMarkup _

# ذخیره هدایت
async def save_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not is_authorized_user(user_id):
        await update.message.reply_text("شما مجاز به استفاده از این ربات نیستید!")
        return
    if context.user_data.get('add_forward_step') != 'keywords':
        await update.message.reply_text("لطفاً فرآیند را از ابتدا شروع کنید!", reply_markup=main_menu())
        return
    keywords = update.message.text.strip()
    keywords = [k.strip() for k in keywords.split(',')] if keywords else []
    config = load_config()
    config['forwards'].append({
        'user_id': user_id,
        'source_chat': context.user_data['source_chat'],
        'dest_chat': context.user_data['dest_chat'],
        'keywords': keywords
    })
    save_config(config)
    await update.message.reply_text("هدایت با موفقیت اضافه شد!", reply_markup=main_menu())
    context.user_data.clear()

# نمایش هدایت‌ها
async def list_forwards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_authorized_user(user_id):
        await query.message.reply_text("شما مجاز به استفاده از این ربات نیستید!")
        return
    await query.message.delete()
    config = load_config()
    forwards = [f for f in config['forwards'] if f['user_id'] == user_id]
    if not forwards:
        await query.message.reply_text("هیچ هدایتی وجود ندارد.", reply_markup=main_menu())
        return
    response = "هدایت‌های فعال:\n"
    keyboard = []
    for i, f in enumerate(forwards):
        response += f"{i+1}. مبدا: {f['source_chat']}, مقصد: {f['dest_chat']}, کلمات: {', '.join(f['keywords'])}\n"
        keyboard.append([InlineKeyboardButton(f"حذف هدایت {i+1}", callback_data=f"delete_{i}")])
    keyboard.append([InlineKeyboardButton("بازگشت", callback_data='home')])
    await query.message.reply_text(response, reply_markup=InlineKeyboardMarkup(keyboard))

# حذف هدایت
async def delete_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_authorized_user(user_id):
        await query.message.reply_text("شما مجاز به استفاده از این ربات نیستید!")
        return
    index = int(query.data.split('_')[1])
    config = load_config()
    forwards = [f for f in config['forwards'] if f['user_id'] == user_id]
    if index < 0 or index >= len(forwards):
        await query.message.edit_text("هدایت نامعتبر!", reply_markup=main_menu())
        return
    config['forwards'].remove(forwards[index])
    save_config(config)
    await query.message.edit_text("هدایت حذف شد!", reply_markup=main_menu())

# نمایش چت‌ها
async def list_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_authorized_user(user_id):
        await query.message.reply_text("شما مجاز به استفاده از این ربات نیستید!")
        return
    await query.message.delete()
    client = TelegramClient('forwarder', API_ID, API_HASH)
    await client.start(phone=PHONE)
    chats = []
    async for dialog in client.iter_dialogs():
        chats.append({'id': dialog.id, 'title': dialog.title})
    await client.disconnect()
    if not chats:
        await query.message.reply_text("هیچ گروه یا کانالی یافت نشد.", reply_markup=main_menu())
        return
    keyboard = [
        [InlineKeyboardButton(chat['title'], callback_data=f"chat_{chat['id']}")]
        for chat in chats
    ]
    keyboard.append([InlineKeyboardButton("بازگشت", callback_data='home')])
    await query.message.reply_text("لیست چت‌ها:", reply_markup=InlineKeyboardMarkup(keyboard))

# نمایش جزئیات چت
async def chat_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_authorized_user(user_id):
        await query.message.reply_text("شما مجاز به استفاده از این ربات نیستید!")
        return
    chat_id = query.data.split('_')[1]
    await query.message.edit_text(f"ID چت: {chat_id}", reply_markup=main_menu())

# نمایش خطاها
async def errors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_authorized_user(user_id):
        await query.message.reply_text("شما مجاز به استفاده از این ربات نیستید!")
        return
    await query.message.delete()
    try:
        with open(ERROR_LOG, 'r') as f:
            errors = json.load(f)
    except FileNotFoundError:
        await query.message.reply_text("هیچ خطایی ثبت نشده است.", reply_markup=main_menu())
        return
    response = "لیست خطاها:\n"
    for error in errors:
        response += f"زمان: {error['time']}, پیام: {error['message']}\n"
    await query.message.reply_text(response, reply_markup=main_menu())

# لغو دستور
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_authorized_user(user_id):
        await query.message.reply_text("شما مجاز به استفاده از این ربات نیستید!")
        return
    await query.message.delete()
    context.user_data.clear()
    await query.message.reply_text("دستور لغو شد!", reply_markup=main_menu())

# بازگشت به خانه
async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_authorized_user(user_id):
        await query.message.reply_text("شما مجاز به استفاده از این ربات نیستید!")
        return
    await query.message.delete()
    await query.message.reply_text("منوی اصلی:", reply_markup=main_menu())

# کلاینت Telethon برای فوروارد
async def start_telethon():
    client = TelegramClient('forwarder', API_ID, API_HASH)
    await client.start(phone=PHONE)

    @client.on(events.NewMessage)
    async def handler(event):
        try:
            config = load_config()
            for f in config['forwards']:
                if str(event.chat_id) == f['source_chat']:
                    # بررسی کلمات کلیدی
                    message_text = event.message.text or ""
                    if not f['keywords'] or any(keyword.lower() in message_text.lower() for keyword in f['keywords']):
                        # اگر پیام متنی است، فیلتر کلمات اعمال می‌شود
                        if message_text:
                            filtered_text = filter_text(message_text)
                            await client.send_message(int(f['dest_chat']), filtered_text)
                        # فوروارد رسانه‌ها (عکس، ویدئو، استیکر و غیره)
                        if event.message.media or event.message.sticker or event.message.emoji:
                            await client.forward_messages(int(f['dest_chat']), event.message)
                        logger.info(f"Message forwarded from {f['source_chat']} to {f['dest_chat']}")
        except Exception as e:
            log_error(str(e))
            logger.error(f"Error in forwarding: {str(e)}")
        await asyncio.sleep(1)  # تأخیر برای جلوگیری از بن شدن

    await client.run_until_disconnected()

# مدیریت callback‌ها
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == 'add_forward':
        await add_forward(update, context)
    elif data.startswith('source_'):
        await select_destination(update, context)
    elif data.startswith('dest_'):
        await get_keywords(update, context)
    elif data == 'list_forwards':
        await list_forwards(update, context)
    elif data.startswith('delete_'):
        await delete_forward(update, context)
    elif data == 'list_chats':
        await list_chats(update, context)
    elif data.startswith('chat_'):
        await chat_details(update, context)
    elif data == 'errors':
        await errors(update, context)
    elif data == 'cancel':
        await cancel(update, context)
    elif data == 'home':
        await home(update, context)

# اجرای ربات
def main():
    config = load_config()
    if 'users' not in config:
        config['users'] = []
        save_config(config)

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_forward))

    # اجرای Telethon در یک حلقه جدا
    loop = asyncio.get_event_loop()
    loop.create_task(start_telethon())

    # اجرای ربات تلگرام
    app.run_polling()

if __name__ == '__main__':
    main()
