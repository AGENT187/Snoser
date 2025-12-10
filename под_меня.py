#фулл версия тут - https://t.me/+SE7QaJWSNHZhZmIy
#фулл версия тут - https://t.me/+SE7QaJWSNHZhZmIy
#фулл версия тут - https://t.me/+SE7QaJWSNHZhZmIy
#фулл версия тут - https://t.me/+SE7QaJWSNHZhZmIy
#фулл версия тут - https://t.me/+SE7QaJWSNHZhZmIy
#фулл версия тут - https://t.me/+SE7QaJWSNHZhZmIy
#фулл версия тут - https://t.me/+SE7QaJWSNHZhZmIy
#фулл версия тут - https://t.me/+SE7QaJWSNHZhZmIy
#фулл версия тут - https://t.me/+SE7QaJWSNHZhZmIy
#фулл версия тут - https://t.me/+SE7QaJWSNHZhZmIy
#фулл версия тут - https://t.me/+SE7QaJWSNHZhZmIy
#фулл версия тут - https://t.me/+SE7QaJWSNHZhZmIy




import logging
import datetime
import random
import asyncio
import aiohttp
import sqlite3
 

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import MessageNotModified

# --- CONFIG ---    
API_TOKEN = '7216464889:AAGEE8auwoh8NQs0Xbn6FlB-izjwZHOx35E'
CRYPTOBOT_TOKEN = "499573:AASSNvCJkwye6lnjWrzKpsRFiwyYeOlhOzU" #404342:AA0iunhqhFx3qlhvQbpdfoRVt5pxV2OmQ9Q
ADMIN_IDS = [5870805154]
PAYMENT_GROUP_ID = -1002730705748

#fsm

class Form(StatesGroup):
    choosing_action = State()
    waiting_for_user_id = State()
    waiting_for_days = State()
    waiting_for_broadcast = State()
    confirming_broadcast = State()




# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- BOT INIT ---
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# --- DB INIT ---
def db_connect():
    conn = sqlite3.connect("sn0ser.db")
    conn.row_factory = sqlite3.Row
    return conn

def db_init():
    conn = db_connect()
    c = conn.cursor()
    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            username TEXT,
            registration_date TEXT,
            subscription_end TEXT,
            whitelist_end TEXT,
            last_snos_ts INTEGER DEFAULT 0
        )
    """)
    # Payments table
    c.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            payment_id TEXT PRIMARY KEY,
            user_id INTEGER,
            days INTEGER,
            price REAL,
            paid INTEGER DEFAULT 0,
            type TEXT,
            invoice_id TEXT,
            created_at TEXT,
            payment_method TEXT,
            full_name TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)
    conn.commit()
    conn.close()

db_init()

# --- FSM STATES ---
class Form(StatesGroup):
    waiting_for_link = State()
    waiting_for_user_id = State()
    waiting_for_days = State()
    waiting_for_broadcast = State()
    waiting_for_fio = State()
    waiting_for_receipt = State()

# --- DB HELPERS ---
def get_user(user_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(user_id, name, username):
    conn = db_connect()
    c = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT OR IGNORE INTO users (user_id, name, username, registration_date) VALUES (?, ?, ?, ?)", 
              (user_id, name, username, now))
    conn.commit()
    conn.close()

def update_user_sub(user_id, sub_end=None, whitelist_end=None):
    conn = db_connect()
    c = conn.cursor()
    if sub_end:
        c.execute("UPDATE users SET subscription_end = ? WHERE user_id = ?", (sub_end, user_id))
    if whitelist_end:
        c.execute("UPDATE users SET whitelist_end = ? WHERE user_id = ?", (whitelist_end, user_id))
    conn.commit()
    conn.close()

def set_last_snos_ts(user_id, ts):
    conn = db_connect()
    c = conn.cursor()
    c.execute("UPDATE users SET last_snos_ts = ? WHERE user_id = ?", (ts, user_id))
    conn.commit()
    conn.close()

def get_last_snos_ts(user_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute("SELECT last_snos_ts FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return row['last_snos_ts'] or 0
    return 0

def create_payment(payment_id, user_id, days, price, pay_type, invoice_id=None, payment_method=None, full_name=None):
    conn = db_connect()
    c = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO payments (payment_id, user_id, days, price, type, invoice_id, created_at, payment_method, full_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
              (payment_id, user_id, days, price, pay_type, invoice_id, now, payment_method, full_name))
    conn.commit()
    conn.close()

def set_payment_invoice_id(payment_id, invoice_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute("UPDATE payments SET invoice_id = ? WHERE payment_id = ?", (invoice_id, payment_id))
    conn.commit()
    conn.close()

def set_payment_full_name(payment_id, full_name):
    conn = db_connect()
    c = conn.cursor()
    c.execute("UPDATE payments SET full_name = ? WHERE payment_id = ?", (full_name, payment_id))
    conn.commit()
    conn.close()

def set_payment_method(payment_id, method):
    conn = db_connect()
    c = conn.cursor()
    c.execute("UPDATE payments SET payment_method = ? WHERE payment_id = ?", (method, payment_id))
    conn.commit()
    conn.close()

def get_payment(payment_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute("SELECT * FROM payments WHERE payment_id = ?", (payment_id,))
    p = c.fetchone()
    conn.close()
    return p

def mark_payment_paid(payment_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute("UPDATE payments SET paid = 1 WHERE payment_id = ?", (payment_id,))
    conn.commit()
    conn.close()

def delete_payment(payment_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute("DELETE FROM payments WHERE payment_id = ?", (payment_id,))
    conn.commit()
    conn.close()

def get_all_user_ids():
    conn = db_connect()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = c.fetchall()
    conn.close()
    return [row['user_id'] for row in users]

# --- UTILS ---
async def auto_delete_unpaid(payment_id, user_id, message_id, delay=600):
    await asyncio.sleep(delay)
    payment = get_payment(payment_id)
    if payment and not payment["paid"]:
        delete_payment(payment_id)
        try:
            await bot.edit_message_text(
                chat_id=user_id,
                message_id=message_id,
                text="❌ Счёт не был оплачен в течение 10 минут и был автоматически удалён."
            )
        except Exception as e:
            logger.warning(f"Auto-delete failed: {e}")

async def safe_edit_message(chat_id, message_id, text, reply_markup=None):
    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=reply_markup
        )
        return True
    except MessageNotModified:
        logger.debug(f"Message {message_id} not modified")
        return False
    except Exception as e:
        logger.error(f"Error editing message: {e}")
        return False

# --- HANDLERS ---

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    create_user(user_id, message.from_user.first_name, message.from_user.username)
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Профиль", callback_data="profile"),
        InlineKeyboardButton("Купить доступ", callback_data="buy_access"),
        InlineKeyboardButton("Sнeстi аkkaунт", callback_data="snos"),
        InlineKeyboardButton("Информация", callback_data="info")
    )
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "🔥 Добро пожаловать в сервис Crime | Sn0ser — единственный настоящий сервис для \"удaлEнiя\" аккаунт0в в Telegram.\n\n"
        "Что умеет наш бот:\n"
        "• 🔨 Массовые жал0bы на аkkаунт\n"
        "• 🛡 П0лная ан0нимность\n"
        "• ⚡️ Быстрая раб0та\n"
        "• 💰 Удобная 0плата крипт0валютой\n\n"
        "Используйте меню ниже для навигации 👇",
        reply_markup=markup
    )



@dp.callback_query_handler(lambda c: c.data == 'profile')
async def profile(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_data = get_user(user_id)
    subscription_status = "Нет"
    whitelist_status = "Нет"
    if user_data:
        if user_data["subscription_end"]:
            if datetime.datetime.strptime(user_data["subscription_end"], "%Y-%m-%d %H:%M:%S") > datetime.datetime.now():
                subscription_status = f"До {user_data['subscription_end']}"
        if user_data["whitelist_end"]:
            if datetime.datetime.strptime(user_data["whitelist_end"], "%Y-%m-%d %H:%M:%S") > datetime.datetime.now():
                whitelist_status = "Да"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Меню", callback_data="menu"))
    await safe_edit_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=f"👤 Информация о пользователе\n\n"
             f"🆔 ID: {user_id}\n"
             f"👤 Имя: {user_data['name'] if user_data else ''}\n"
             f"🔠 Юзернейм: @{user_data['username'] if user_data else ''}\n"
             f"📆 Дата регистрации: {user_data['registration_date'] if user_data else ''}\n"
             f"💎 Текущий план: {subscription_status}\n"
             f"🛡 Статус вайтлиста: {whitelist_status}",
        reply_markup=markup
    )

@dp.callback_query_handler(lambda c: c.data == 'buy_access')
async def buy_access(callback_query: types.CallbackQuery):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("1 день - 0.1$", callback_data="buy_1day"),
        InlineKeyboardButton("7 дней - 7$", callback_data="buy_7days"),
        InlineKeyboardButton("30 дней - 13$", callback_data="buy_30days"),
        InlineKeyboardButton("Навсегда - 25$", callback_data="buy_forever"),
        InlineKeyboardButton("Вайтлист", callback_data="whitelist"),
        InlineKeyboardButton("Меню", callback_data="menu")
    )
    await safe_edit_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text="💰 Выберите тариф:\n\n"
             "💳 Оплата производится в криптовалюте через бота @CryptoBot\n"
             "📦 После оплаты вы сразу получите доступ к сервису\n"
             "❓ Если возникнут вопросы, пишите в поддержку",
        reply_markup=markup
    )

@dp.callback_query_handler(lambda c: c.data == 'info')
async def info(callback_query: types.CallbackQuery):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Меню", callback_data="menu"))
    await safe_edit_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text="ℹ️ Информация о сервисе\n\n"
             "🔥 Сrime | Sn0ser — сервис для удAленiя аkkaунтов в Telegram.\n\n"
             "Как это работает:\n"
             "1️⃣ Вы покупаете один из тарифов\n"
             "2️⃣ Указываете аkkаунт, который нужно «snеstи»\n"
             "3️⃣ Наши боты отправляют множество жал0b на аккаунт\n"
             "4️⃣ Целевой аккаунт получает уведомления о жал0bаX\n\n"
             "Важное примечание:\n"
             "❗ Сервис работает в ознакомительных целях\n"
             "❗ Массовые жalоbы могут привести к временным ограничениям\n"
             "❗ Мы не гарантируем блокировку аккаунта\n\n"
             "При возникновении вопросов обращайтесь в поддержку.",
        reply_markup=markup
    )

@dp.callback_query_handler(lambda c: c.data == 'menu')
async def menu(callback_query: types.CallbackQuery):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Профиль", callback_data="profile"),
        InlineKeyboardButton("Купить доступ", callback_data="buy_access"),
        InlineKeyboardButton("Sneсti аккаунт", callback_data="snos"),
        InlineKeyboardButton("Информация", callback_data="info")
    )
    await safe_edit_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=f"👋 Привет, {callback_query.from_user.first_name}!\n\n"
             "🔥 Добро пожаловать в сервис Crime | Sn0ser — единственный настоящий сервис для \"уdаленiя\" аkkаунтов в Telegram.\n\n"
             "Что умеет наш бот:\n"
             "• 🔨 Массовые жalобы на аккаунт\n"
             "• 🛡 Полная анонимность\n"
             "• ⚡️ Быстрая работа\n"
             "• 💰 Удобная оплата криптовалютой\n\n"
             "Используйте меню ниже для навигации 👇",
        reply_markup=markup
    )

@dp.callback_query_handler(lambda c: c.data.startswith('buy_'))
async def process_buy(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    plan = callback_query.data
    plans = {
        'buy_1day': {'days': 1, 'price_usd': 0.1, 'price_rub': 300},
        'buy_7days': {'days': 7, 'price_usd': 7, 'price_rub': 700},
        'buy_30days': {'days': 30, 'price_usd': 13, 'price_rub': 1300},
        'buy_forever': {'days': 9999, 'price_usd': 25, 'price_rub': 2500}
    }
    selected_plan = plans.get(plan)
    if not selected_plan:
        return
    
    payment_id = f"sub_{user_id}_{int(datetime.datetime.now().timestamp())}"
    await state.update_data(payment_id=payment_id, plan=selected_plan)
    
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("CryptoBot", callback_data=f"pay_crypto_{payment_id}"),
        InlineKeyboardButton("Карта/СБП", callback_data=f"pay_card_{payment_id}"),
        InlineKeyboardButton("Вернуться", callback_data="buy_access")
    )
    
    await safe_edit_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=f"💰 Выберите способ оплаты:",
        reply_markup=markup
    )

@dp.callback_query_handler(lambda c: c.data.startswith('pay_crypto_'))
async def process_pay_crypto(callback_query: types.CallbackQuery, state: FSMContext):
    payment_id = callback_query.data[len("pay_crypto_"):]
    payment = get_payment(payment_id)
    
    if payment and payment["invoice_id"]:
        await bot.answer_callback_query(callback_query.id, "Счёт уже создан. Используйте кнопку ниже.")
        return
    
    data = await state.get_data()
    selected_plan = data.get('plan')
    if not selected_plan:
        return
    
    create_payment(payment_id, callback_query.from_user.id, selected_plan["days"], selected_plan["price_usd"], "subscription", payment_method="crypto")
    
    async with aiohttp.ClientSession() as session:
        headers = {'Crypto-Pay-API-Token': CRYPTOBOT_TOKEN}
        data = {
            'amount': selected_plan['price_usd'],
            'asset': 'USDT',
            'description': f"Оплата подписки на {selected_plan['days']} дней",
            'paid_btn_name': 'viewItem',
            'paid_btn_url': 'https://t.me/your_bot',
            'payload': payment_id,
            'expires_in': 600
        }
        async with session.post('https://pay.crypt.bot/api/createInvoice', headers=headers, json=data) as resp:
            result = await resp.json()
            if result.get('ok'):
                invoice_url = result['result']['pay_url']
                inv_id = result['result']['invoice_id']
                set_payment_invoice_id(payment_id, inv_id)
                markup = InlineKeyboardMarkup(row_width=1)
                markup.add(
                    InlineKeyboardButton("Перейти к оплате", url=invoice_url),
                    InlineKeyboardButton("Проверить оплату", callback_data=f"check_{payment_id}"),
                    InlineKeyboardButton("Отменить", callback_data="menu")
                )
                await safe_edit_message(
                    chat_id=callback_query.message.chat.id,
                    message_id=callback_query.message.message_id,
                    text=f"💰 Оплата {selected_plan['days']} day\n\n"
                         f"💵 Сумма: {selected_plan['price_usd']} USDT\n"
                         f"🧾 ID платежа: {payment_id}\n\n"
                         "После оплаты нажмите «Проверить оплату» 👇",
                    reply_markup=markup
                )
                asyncio.create_task(auto_delete_unpaid(payment_id, callback_query.message.chat.id, callback_query.message.message_id))
            else:
                await bot.answer_callback_query(callback_query.id, "Ошибка при создании счета")

@dp.callback_query_handler(lambda c: c.data.startswith('pay_card_'))
async def process_pay_card(callback_query: types.CallbackQuery, state: FSMContext):
    payment_id = callback_query.data[len("pay_card_"):]
    data = await state.get_data()
    selected_plan = data.get('plan')

    if not selected_plan:
        await bot.answer_callback_query(callback_query.id, "Ошибка: тариф не найден")
        return

    create_payment(payment_id, callback_query.from_user.id, selected_plan["days"], selected_plan["price_rub"], "subscription", payment_method="card")

    await Form.waiting_for_fio.set()
    await state.update_data(payment_id=payment_id, plan=selected_plan)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Вернуться", callback_data="buy_access"))

    await safe_edit_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text="Напишите ваше ФИО, привязанное к банку\nПример: Ирина Сергеевна Л",
        reply_markup=markup
    )

@dp.message_handler(state=Form.waiting_for_fio, content_types=types.ContentTypes.TEXT)
async def process_fio(message: types.Message, state: FSMContext):
    data = await state.get_data()
    payment_id = data.get('payment_id')
    selected_plan = data.get('plan')

    if not payment_id or not selected_plan:
        await state.finish()
        return

    set_payment_full_name(payment_id, message.text)

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("Я оплатил", callback_data=f"paid_{payment_id}"),
        InlineKeyboardButton("Вернуться", callback_data="buy_access")
    )

    await message.answer(
        f"Сумма: {selected_plan['price_rub']}₽\n\n"
        "Реквизиты:\n"
        "Карта: Временно недоступно\n" #2204320102932565
        "СБП (ОЗОН): 79508055952",
        reply_markup=markup
    )
    await Form.waiting_for_receipt.set()
    await state.update_data(payment_id=payment_id, plan=selected_plan)

@dp.callback_query_handler(lambda c: c.data.startswith('paid_'), state="*")
async def process_paid(callback_query: types.CallbackQuery, state: FSMContext):
    payment_id = callback_query.data[len("paid_"):]
    payment = get_payment(payment_id)

    if not payment:
        await bot.answer_callback_query(callback_query.id, "❌ Ошибка: платеж не найден")
        return

    # Удаляем предыдущую клавиатуру
    try:
        await bot.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=None
        )
    except Exception:
        pass

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Вернуться", callback_data="buy_access"))

    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text="📎 Пожалуйста, отправьте PDF-чек об оплате (файл в формате PDF).\n\n"
             "Если вы уже отправили чек — ожидайте, заявка будет обработана оператором.",
        reply_markup=markup
    )

    await state.update_data(payment_id=payment_id)
    await Form.waiting_for_receipt.set()

@dp.message_handler(state=Form.waiting_for_receipt, content_types=types.ContentTypes.DOCUMENT)
async def process_receipt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    payment_id = data.get('payment_id')
    payment = get_payment(payment_id)

    if not payment:
        await message.answer("❌ Ошибка: данные платежа не найдены")
        await state.finish()
        return

    # Проверяем, что это PDF
    if message.document.mime_type != 'application/pdf':
        await message.answer("⚠️ Пожалуйста, отправьте файл в формате PDF")
        return

    # Отправляем чек в группу админу
# ...existing code...
    payment_info = (
        f"💳 Новый платеж через Карту/СБП\n\n"
        f"👤 Пользователь: @{message.from_user.username or '-'} (ID: {message.from_user.id})\n"
        f"📅 Дата: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"💰 Сумма: {payment['price']}₽\n"
        f"📆 Срок подписки: {payment['days']} дней\n"
        f"📝 ФИО: {payment['full_name'] if payment['full_name'] else 'не указано'}\n"
        f"🆔 ID платежа: {payment_id}"
    )
# ...existing code...

    try:
        await bot.send_document(
            chat_id=PAYMENT_GROUP_ID,
            document=message.document.file_id,
            caption=payment_info
        )
    except Exception as e:
        await message.answer(f"❌ Не удалось отправить чек администратору: {e}")

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Главное меню", callback_data="menu"))

    await message.answer(
        "✅ Чек получен! Ваша подписка будет активирована в течение 1 часа.\n"
        "⌛ Мы работаем с 10:00 до 22:00 по МСК",
        reply_markup=markup
    )

    await state.finish()

@dp.message_handler(state=Form.waiting_for_receipt, content_types=types.ContentTypes.ANY)
async def process_receipt_invalid(message: types.Message, state: FSMContext):
    await message.answer("⚠️ Пожалуйста, отправьте чек в виде PDF-файла (документом).")

# --- universal "Вернуться" обработчик для возврата в меню покупки ---
@dp.callback_query_handler(lambda c: c.data == "buy_access", state="*")
async def return_to_buy_access(callback_query: types.CallbackQuery, state: FSMContext):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("1 день - 3$", callback_data="buy_1day"),
        InlineKeyboardButton("7 дней - 7$", callback_data="buy_7days"),
        InlineKeyboardButton("30 дней - 13$", callback_data="buy_30days"),
        InlineKeyboardButton("Навсегда - 25$", callback_data="buy_forever"),
        InlineKeyboardButton("Вайтлист", callback_data="whitelist"),
        InlineKeyboardButton("Меню", callback_data="menu")
    )
    await safe_edit_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text="💰 Выберите тариф:\n\n"
             "💳 Оплата производится в криптовалюте через бота @CryptoBot\n"
             "📦 После оплаты вы сразу получите доступ к сервису\n"
             "❓ Если возникнут вопросы, пишите в поддержку",
        reply_markup=markup
    )
    await state.finish()

@dp.callback_query_handler(lambda c: c.data.startswith('check_'))
async def check_payment(callback_query: types.CallbackQuery):
    payment_id = callback_query.data[len("check_"):]
    payment = get_payment(payment_id)
    if not payment:
        await bot.answer_callback_query(callback_query.id, "Ошибка: платеж не найден")
        return
    invoice_id = payment["invoice_id"]
    if not invoice_id:
        await bot.answer_callback_query(callback_query.id, "Счёт ещё не был создан")
        return
    async with aiohttp.ClientSession() as session:
        headers = {'Crypto-Pay-API-Token': CRYPTOBOT_TOKEN}
        async with session.get('https://pay.crypt.bot/api/getInvoices', headers=headers, params={'invoice_ids': invoice_id}) as resp:
            result = await resp.json()
            if result.get('ok') and result['result']['items']:
                invoice = result['result']['items'][0]
                if invoice['status'] == 'paid':
                    mark_payment_paid(payment_id)
                    user_id = payment['user_id']
                    if payment['type'] == 'subscription':
                        end_date = datetime.datetime.now() + datetime.timedelta(days=payment['days'])
                        update_user_sub(user_id, sub_end=end_date.strftime("%Y-%m-%d %H:%M:%S"))
                        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("Меню", callback_data="menu"))
                        await safe_edit_message(
                            chat_id=callback_query.message.chat.id,
                            message_id=callback_query.message.message_id,
                            text="✅ Платёж успешно обработан! Ваша подписка активирована.",
                            reply_markup=markup
                        )
                    elif payment['type'] == 'whitelist':
                        end_date = datetime.datetime.now() + datetime.timedelta(days=payment['days'])
                        update_user_sub(user_id, whitelist_end=end_date.strftime("%Y-%m-%d %H:%M:%S"))
                        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("Меню", callback_data="menu"))
                        await safe_edit_message(
                            chat_id=callback_query.message.chat.id,
                            message_id=callback_query.message.message_id,
                            text="✅ Платёж успешно обработан! Ваш вайтлист активирован.",
                            reply_markup=markup
                        )
                elif invoice['status'] == 'active':
                    await bot.answer_callback_query(callback_query.id, "Счёт не оплачен")
                else:
                    await bot.answer_callback_query(callback_query.id, "Счёт не активен или истёк")
            else:
                await bot.answer_callback_query(callback_query.id, "Платёж не найден или не оплачен") 

# --- SNOS ---
@dp.callback_query_handler(lambda c: c.data == 'snos')
async def snos_account(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_data = get_user(user_id)
    if not user_data or not user_data['subscription_end'] or datetime.datetime.strptime(user_data['subscription_end'], "%Y-%m-%d %H:%M:%S") < datetime.datetime.now():
        try:
            await bot.answer_callback_query(callback_query.id, "У вас нет активной подписки!", show_alert=True)
        except Exception:
            await bot.send_message(callback_query.message.chat.id, "У вас нет активной подписки!")
        return
    last_snos_ts = get_last_snos_ts(user_id)
    now_ts = int(datetime.datetime.now().timestamp())
    if last_snos_ts and now_ts - last_snos_ts < 1800:
        minutes = int((1800 - (now_ts - last_snos_ts)) / 60)
        await bot.answer_callback_query(callback_query.id, f"❗ Снос можно делать раз в 30 минут. Ждите {minutes} мин.", show_alert=True)
        return
    await state.update_data(snos_allowed=True)
    await Form.waiting_for_link.set()
    await safe_edit_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text="🔨 Сн0с аккаунта\n\nОтправьте ссылку на аккаунт, чат или канал, который нужно snесti. Например: https://t.me/username, @username или ссылку на сообщение/пост https://t.me/username/123"
    )

@dp.message_handler(state=Form.waiting_for_link, content_types=types.ContentTypes.TEXT)
async def process_link(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if not data.get("snos_allowed"):
        return
    user_id = message.from_user.id
    set_last_snos_ts(user_id, int(datetime.datetime.now().timestamp()))
    await state.finish()
    msg = await message.answer("Подготовка\n🟩⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️ 5%")
    progress_steps = [
        ("Отправка запросов на сервер", 10, "🟩⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️"),
        ("Отправка запросов на сервер", 12, "🟩⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️"),
        ("Отправка запросов на сервер", 14, "🟩⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️"),
        ("Отправка запросов на сервер", 16, "🟩⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️"),
        ("Отправка запросов на сервер", 18, "🟩⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️"),
        ("Отправка запросов на сервер", 20, "🟩🟩⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️"),
        ("Отправка писем", 22, "🟩🟩⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️"),
        ("Отправка писем", 24, "🟩🟩⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️"),
        ("Отправка писем", 26, "🟩🟩⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️"),
        ("Отправка писем", 28, "🟩🟩⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️"),
        ("Отправка писем", 30, "🟩🟩🟩⬜️⬜️⬜️⬜️⬜️⬜️⬜️"),]