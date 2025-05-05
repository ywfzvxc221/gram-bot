import telebot
import time
import json
import random
from datetime import datetime

# إعدادات البوت
TOKEN = '7866801308:AAHFso2PDuZVyXXOaO09TK9sadcdHeG07Xw'
ADMIN_ID = 5475256932
bot = telebot.TeleBot(TOKEN)

# قاعدة البيانات
users = {}
ads = [
    {"text": "شاهد إعلان 1 واربح 100 TON", "url": "https://example.com", "reward": 100},
    {"text": "شاهد إعلان 2 واربح 150 TON", "url": "https://example2.com", "reward": 150}
]

def load_data():
    global users
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except:
        users = {}

def save_data():
    with open("users.json", "w") as f:
        json.dump(users, f)

def get_user(user_id):
    if str(user_id) not in users:
        users[str(user_id)] = {"balance": 0, "referrals": 0, "last_claim": "1970-01-01"}
    return users[str(user_id)]

@bot.message_handler(commands=["start"])
def start(message):
    user = get_user(message.from_user.id)
    args = message.text.split()
    if len(args) > 1:
        ref_id = args[1]
        if ref_id != str(message.from_user.id):
            ref_user = get_user(ref_id)
            ref_user["referrals"] += 1
            ref_user["balance"] += 250
    save_data()
    bot.send_message(message.chat.id, "مرحباً بك في بوت ربح TON!", reply_markup=main_menu())

def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("مشاهدة الإعلانات", "المكافأة اليومية")
    markup.row("رصيدي", "سحب الأرباح")
    markup.row("رابط الإحالة", "لوحة الإدارة")
    return markup

@bot.message_handler(func=lambda m: m.text == "مشاهدة الإعلانات")
def view_ads(message):
    ad = random.choice(ads)
    bot.send_message(message.chat.id, f"{ad['text']}\nرابط الإعلان: {ad['url']}")
    time.sleep(10)
    user = get_user(message.from_user.id)
    user["balance"] += ad["reward"]
    save_data()
    bot.send_message(message.chat.id, f"تم إضافة {ad['reward']} TON إلى رصيدك.")

@bot.message_handler(func=lambda m: m.text == "المكافأة اليومية")
def daily_bonus(message):
    user = get_user(message.from_user.id)
    last = datetime.strptime(user["last_claim"], "%Y-%m-%d")
    today = datetime.utcnow().date()
    if last.date() < today:
        user["balance"] += 200
        user["last_claim"] = str(today)
        save_data()
        bot.send_message(message.chat.id, "تم إضافة 200 TON إلى رصيدك كمكافأة يومية!")
    else:
        bot.send_message(message.chat.id, "لقد استلمت مكافأتك اليومية بالفعل، عُد غداً!")

@bot.message_handler(func=lambda m: m.text == "رصيدي")
def check_balance(message):
    user = get_user(message.from_user.id)
    bot.send_message(message.chat.id, f"رصيدك الحالي: {user['balance']} TON")

@bot.message_handler(func=lambda m: m.text == "رابط الإحالة")
def referral_link(message):
    link = f"https://t.me/YOUR_BOT_USERNAME?start={message.from_user.id}"
    bot.send_message(message.chat.id, f"رابط الإحالة الخاص بك:\n{link}\nعدد الإحالات: {get_user(message.from_user.id)['referrals']}")

@bot.message_handler(func=lambda m: m.text == "سحب الأرباح")
def withdraw(message):
    bot.send_message(message.chat.id, "أرسل عنوان محفظتك على FaucetPay (عملة TON):")
    bot.register_next_step_handler(message, process_withdraw)

def process_withdraw(message):
    address = message.text
    user = get_user(message.from_user.id)
    if user["balance"] < 1000:
        bot.send_message(message.chat.id, "الحد الأدنى للسحب هو 1000 TON.")
        return
    user["balance"] -= 1000
    save_data()
    bot.send_message(message.chat.id, f"تم إرسال 1000 TON إلى محفظتك: {address}")
    bot.send_message("@YourProofChannel", f"تم دفع 1000 TON إلى {address} من المستخدم @{message.from_user.username or message.from_user.id}")

# لوحة تحكم للإدمن
@bot.message_handler(func=lambda m: m.text == "لوحة الإدارة")
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("عدد المستخدمين", "رصيد مستخدم")
    markup.row("إرسال رسالة جماعية")
    bot.send_message(message.chat.id, "لوحة التحكم:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "عدد المستخدمين")
def count_users(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, f"عدد المستخدمين: {len(users)}")

@bot.message_handler(func=lambda m: m.text == "رصيد مستخدم")
def ask_user_id(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, "أرسل ID المستخدم:")
    bot.register_next_step_handler(message, show_user_balance)

def show_user_balance(message):
    if message.from_user.id != ADMIN_ID:
        return
    uid = str(message.text)
    if uid in users:
        bot.send_message(message.chat.id, f"رصيد المستخدم {uid}: {users[uid]['balance']} TON")
    else:
        bot.send_message(message.chat.id, "المستخدم غير موجود.")

@bot.message_handler(func=lambda m: m.text == "إرسال رسالة جماعية")
def broadcast_ask(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, "أرسل الرسالة التي تريد إرسالها لكل المستخدمين:")
    bot.register_next_step_handler(message, broadcast_message)

def broadcast_message(message):
    if message.from_user.id != ADMIN_ID:
        return
    for uid in users:
        try:
            bot.send_message(uid, message.text)
        except:
            pass
    bot.send_message(message.chat.id, "تم إرسال الرسالة.")

# تشغيل البوت
load_data()
print("Bot is running...")
bot.infinity_polling()
