import telebot
from telebot import types
import json
import os
import sqlite3
import secrets
import string
from datetime import datetime, timedelta
from dotenv import load_dotenv 

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)


# ========================================
# КОНФИГУРАЦИЯ
# ========================================
BOT_TOKEN = 'Токен'
DATA_FILE = 'users_data.json'
KEYS_FOLDER = 'keys'
ADMINS_DATA_FILE = 'admins_data.json'
ADMIN_PASSWORD_FILE = 'admin_password.json'
DATABASE_FILE = 'bot_database.db'

DEV_URL = 'https://t.me/Sanya_Bloodsov'
MOD_URL = 'https://t.me/Wezyxsoft'
CHAT_PANEL_URL = 'https://t.me/+1o2hM13sXoQwOGYy'

bot = telebot.TeleBot(BOT_TOKEN)

PRODUCT_MAP = {'1d': 'product1', '3d': 'product2', '7d': 'product3', '14d': 'product4', '30d': 'product5'}
KEY_FILES = {'product1': 'keys_1d.txt', 'product2': 'keys_3d.txt', 'product3': 'keys_7d.txt',
             'product4': 'keys_14d.txt', 'product5': 'keys_30d.txt'}
KEY_CATEGORIES = {k: v for k, v in zip(PRODUCT_MAP.values(), ['1D', '3D', '7D', '14D', '30D'])}
PRODUCT_PRICES = {v: p for v, p in zip(PRODUCT_MAP.values(), [10, 30, 55, 75, 100])}
PRODUCT_DISPLAY = {v: d for v, d in zip(PRODUCT_MAP.values(), ['1 DAY', '3 DAYS', '7 DAYS', '14 DAYS', '30 DAYS'])}

WARNING_LEVELS = {
    1: ('Предупреждение', 'Warning'),
    2: ('Выговор', 'Reprimand'),
    3: ('Строгий выговор', 'Strict Reprimand')
}

user_languages = {}
user_states = {}
admins_db = None
admin_password_cache = {}
db_connection = None


# ========================================
# ТЕКСТЫ ИНТЕРФЕЙСА
# ========================================
LANGUAGES = {
    'ru': {
        'welcome': '👋 Привет! Выберите раздел:',
        'settings': '⚙️ Настройки',
        'support': '🛡️ Чат Панели',
        'products': '🛍 КУПИТЬ PRIMEHACK',
        'profile': '👤 Профиль',
        'back_menu': '🔙 Назад в меню',
        'language': '🏳️ Язык',
        'rules': '📜 Правила Панели',
        'top_up_balance': '💳 Пополнить через разработчика',
        'balance_topup_only_admin': '💰 Баланс пополняется через кнопки ниже.',
        'admin_panel': '🛠️ Админ-панель',
        'admin_menu_title': '<b>🛠️ АДМИН-ПАНЕЛЬ</b>',
        'purchase_success': '✅ <b>ПОКУПКА УСПЕШНА!</b>\n\n🔑 Товар: {}\n🔢 Кол-во: {}\n💵 Списано: {} ₽\n💰 Остаток: {} ₽\n\n🔐 Ваши ключи:\n{}',
        'insufficient_funds': '❌ <b>НЕДОСТАТОЧНО СРЕДСТВ!</b>\n\n💰 Ваш баланс: {} ₽\n💵 Требуется: {} ₽\n📉 Не хватает: {} ₽\n\n<b>Пополните баланс:</b>',
        'no_keys_available': '❌ Подписка закончилась!',
        'unknown_command': '❓ Используйте кнопки.',
        'add_key_instruction': '🔑 <b>Как добавить ключ:</b>\n\nОтправьте сообщение:<code>/addkey ПЕРИОД КЛЮЧ</code>',
        'balance_topup_notification': '✅ <b>Баланс пополнен!</b>\n\n👤 Пользователь: {} \n💰 Добавлено: {}.00 ₽\n💳 Новый баланс: {}.00 ₽',
        'password_generated': '🔒 <b>Пароль сгенерирован:</b>\n\n<code>{}</code>\n\n⚡ Длина: {} символов',
        'limited_access': '❌ Только Супер-Админы могут это делать.',
        'enter_admin_password': '🔐 <b>Требуется пароль администратора!</b>\n\nВведите пароль для доступа к панели:',
        'password_correct': '✅ Пароль верный! Доступ разрешён.',
        'password_incorrect': '❌ Неверный пароль! Попробуйте снова.',
        'password_set': '✅ Пароль администратора установлен.',
        'no_password_set': '⚠️ Пароль ещё не установлен. Установите через /set_admin_password',
        'admin_panel_blocked': '🚫 <b>Доступ закрыт!</b>\n\nВведённый пароль неверен.',
        'chat_panel_title': '🛡️ <b>ЧАТ ПАНЕЛИ</b>',
        'moderator': '🔥 Пополнить через модератора',
        'select_qty_title': '<b>Выберите количество ключей:</b>',
        'confirm_title': '<b>ПОДТВЕРЖДЕНИЕ ПОКУПКИ</b>',
        'confirm_text': '🛍 Товар: {}\n🔢 Количество: {} шт.\n💵 Общая сумма: {} ₽\n\nНажмите кнопку ниже для подтверждения:',
        'rus': '🇷🇺 Русский',
        'eng': '🇬🇧 Английский',
        'current_lang': '🌐 Текущий язык: {}',
        'settings_content': '⚙️ Настройки:',
        'give_warning': '⚖️ Выдать предупреждение',
        'rules_text': '━━━━━━━━━━━━━━━━━━━━\n📜 <b>ПРАВИЛА РАБОТЫ ПАНЕЛИ</b>\n━━━━━━━━━━━━━━━━━━━━\n\n🔹 <b>1. УЧЕТНЫЕ ДАННЫЕ И ИДЕНТИФИКАЦИЯ</b>\n\n<b>1.1.</b> Каждый пользователь привязан к уникальному USER_ID...\n\n(полный текст правил...)'
    },
    'en': {
        'welcome': '👋 Hello! Choose section:',
        'settings': '⚙️ Settings',
        'support': '🛡️ Chat Panel',
        'products': '🛍 BUY PRIMEHACK',
        'profile': '👤 Profile',
        'back_menu': '🔙 Back to menu',
        'language': '🏳️ Language',
        'rules': '📜 Panel Rules',
        'top_up_balance': '💳 Top up via developer',
        'balance_topup_only_admin': '💰 Balance is topped up via buttons below.',
        'admin_panel': '🛠️ Admin Panel',
        'admin_menu_title': '<b>🛠️ ADMIN PANEL</b>',
        'purchase_success': '✅ <b>PURCHASE SUCCESSFUL!</b>\n\n🔑 Product: {}\n🔢 Qty: {}\n💵 Charged: {} ₽\n💰 Remaining: {} ₽\n\n🔐 Your keys:\n{}',
        'insufficient_funds': '❌ <b>INSUFFICIENT FUNDS!</b>\n\n💰 Your balance: {} ₽\n💵 Required: {} ₽\n📉 Missing: {} ₽\n\n<b>Top up balance:</b>',
        'no_keys_available': '❌ Subscription out of stock!',
        'unknown_command': '❓ Please use buttons.',
        'add_key_instruction': '🔑 <b>Add Key:</b>\n\nSend:<code>/addkey PERIOD KEY</code>',
        'balance_topup_notification': '✅ <b>Balance topped up!</b>\n\n👤 User: {} \n💰 Added: {}.00 ₽\n💳 New balance: {}.00 ₽',
        'password_generated': '🔒 <b>Password generated:</b>\n\n<code>{}</code>\n\n⚡ Length: {} chars',
        'limited_access': '❌ Only Super-Admins allowed.',
        'enter_admin_password': '🔐 <b>Admin password required!</b>\n\nEnter password for access:',
        'password_correct': '✅ Password correct! Access granted.',
        'password_incorrect': '❌ Wrong password! Try again.',
        'password_set': '✅ Admin password set.',
        'no_password_set': '⚠️ No password set. Use /set_admin_password',
        'admin_panel_blocked': '🚫 <b>Access Denied!</b>\n\nWrong password.',
        'chat_panel_title': '🛡️ <b>CHAT PANEL</b>',
        'moderator': '🔥 Top up via moderator',
        'select_qty_title': '<b>Select number of keys:</b>',
        'confirm_title': '<b>CONFIRM PURCHASE</b>',
        'confirm_text': '🛍 Product: {}\n🔢 Quantity: {} pcs.\n💵 Total price: {} ₽\n\nPress button to confirm:',
        'rus': '🇷🇺 Russian',
        'eng': '🇬🇧 English',
        'current_lang': '🌐 Current language: {}',
        'settings_content': '⚙️ Settings:',
        'give_warning': '⚖️ Issue Warning',
        'rules_text': '━━━━━━━━━━━━━━━━━━━━\n📜 <b>PANEL RULES</b>\n━━━━━━━━━━━━━━━━━━━━\n\n🔹 <b>1. ACCOUNT & IDENTIFICATION</b>\n\n<b>1.1.</b> Each user has a unique USER_ID...'
    }
}


# ========================================
# БАЗА ДАННЫХ SQLITE
# ========================================
def get_db_connection():
    global db_connection
    if db_connection is None:
        init_database()
    return db_connection


def init_database():
    global db_connection
    db_connection = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
    cursor = db_connection.cursor()

    cursor.execute("PRAGMA table_info(users)")
    columns_info = cursor.fetchall()
    existing_columns = [col[1] for col in columns_info]

    if existing_columns:
        if 'user_id' not in existing_columns:
            print("⚠️  Столбец user_id не найден в таблице users. Выполняется миграция схемы...")
            cursor.execute("ALTER TABLE users RENAME TO users_old")

            cursor.execute('''
                CREATE TABLE users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    balance REAL DEFAULT 0.0,
                    strict_warning_active BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            old_pk = existing_columns[0]
            new_columns = ['user_id', 'username', 'first_name', 'last_name',
                           'balance', 'strict_warning_active', 'created_at']
            select_parts = []
            for col in new_columns:
                if col == 'user_id' and col not in existing_columns:
                    select_parts.append(old_pk)
                elif col in existing_columns:
                    select_parts.append(col)
                else:
                    defaults = {
                        'username': 'NULL',
                        'first_name': 'NULL',
                        'last_name': 'NULL',
                        'balance': '0.0',
                        'strict_warning_active': '0',
                        'created_at': "datetime('now')"
                    }
                    select_parts.append(defaults.get(col, 'NULL'))

            migrate_sql = (
                f"INSERT INTO users ({', '.join(new_columns)}) "
                f"SELECT {', '.join(select_parts)} FROM users_old"
            )
            cursor.execute(migrate_sql)
            cursor.execute("DROP TABLE users_old")
            db_connection.commit()
            print("✅ Миграция таблицы users завершена. Столбец user_id добавлен.")
        else:
            print("✅ Схема таблицы users корректна (столбец user_id присутствует).")
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                balance REAL DEFAULT 0.0,
                strict_warning_active BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            stage INTEGER NOT NULL CHECK (stage IN (1, 2, 3)),
            reason TEXT NOT NULL,
            issued_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            admin_id INTEGER NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            related_warning_id INTEGER,
            executed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (related_warning_id) REFERENCES warnings (id)
        )
    ''')

    db_connection.commit()
    print(f"✅ База данных инициализирована: {DATABASE_FILE}")


def get_user_from_db(user_id):
    conn = get_db_connection()
    if conn is None:
        return None

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute('''
            INSERT INTO users (user_id, username, first_name, last_name, balance)
            VALUES (?, ?, ?, ?, 0.0)
        ''', (user_id, None, None, None))
        conn.commit()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()

    return user


def update_user_balance_db(user_id, new_balance):
    conn = get_db_connection()
    if conn is None:
        return False

    get_user_from_db(user_id)

    cursor = conn.cursor()
    cursor.execute(
        'UPDATE users SET balance = ? WHERE user_id = ?',
        (new_balance, user_id)
    )
    conn.commit()
    return True


def add_transaction(user_id, amount, transaction_type, related_warning_id=None):
    conn = get_db_connection()
    if conn is None:
        return False
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (user_id, amount, type, related_warning_id)
        VALUES (?, ?, ?, ?)
    ''', (user_id, amount, transaction_type, related_warning_id))
    conn.commit()
    return cursor.lastrowid


def get_user_warnings(user_id):
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor()
    cursor.execute('''
        SELECT w.id, w.stage, w.reason, w.issued_at, w.admin_id, u.username as admin_username
        FROM warnings w
        LEFT JOIN users u ON w.admin_id = u.user_id
        WHERE w.user_id = ? AND w.is_active = 1
        ORDER BY w.issued_at DESC
    ''', (user_id,))
    return cursor.fetchall()


def issue_warning(user_id, stage, reason, admin_id):
    conn = get_db_connection()
    if conn is None:
        return None

    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO warnings (user_id, stage, reason, admin_id, is_active)
        VALUES (?, ?, ?, ?, 1)
    ''', (user_id, stage, reason, admin_id))
    warning_id = cursor.lastrowid

    user_before = get_user_from_db(user_id)
    old_balance = user_before[4] if user_before else 0.0
    new_balance = old_balance

    if stage == 2:
        deduction = old_balance * 0.3
        new_balance = old_balance - deduction
        update_user_balance_db(user_id, new_balance)
        add_transaction(user_id, deduction, 'warn_deduction', warning_id)

    elif stage == 3:
        cursor.execute(
            'UPDATE users SET strict_warning_active = 1 WHERE user_id = ?',
            (user_id,)
        )
        conn.commit()

    conn.commit()

    return {
        'warning_id': warning_id,
        'old_balance': old_balance,
        'new_balance': new_balance,
        'deduction': old_balance - new_balance if stage == 2 else 0
    }


# ========================================
# ТЕЛЕГРАМ ФУНКЦИИ
# ========================================
def format_timestamp(timestamp=None):
    if timestamp is None:
        return datetime.now().strftime("%d.%m.%Y %H:%M")
    if isinstance(timestamp, str):
        # FIX: обработка разных форматов timestamp из SQLite и ISO
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            try:
                dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                dt = datetime.now()
    else:
        dt = timestamp
    return dt.strftime("%d.%m.%Y %H:%M")


def notify_admins_about_new_user(user_id, first_name, last_name, username, registration_time=None):
    global admins_db
    if admins_db is None:
        admins_db = load_admins_data()
    all_admin_ids = get_all_admins()
    full_name = first_name + (f" {last_name}" if last_name else "")
    display_username = username if username else "не указан"
    reg_time_str = format_timestamp(registration_time) if registration_time else format_timestamp()

    notification_text = (
        f'🔔 <b>Новый пользователь!</b>\n\n'
        f'👤 Имя: {full_name}\n'
        f'🆔 @username: {display_username}\n'
        f'🔢 ID: {user_id}\n'
        f'⏰ Время: {reg_time_str}'
    )

    for admin_id in all_admin_ids:
        try:
            bot.send_message(admin_id, notification_text, parse_mode='HTML')
        except Exception:
            pass


def notify_admins_about_warning(user_id, stage, reason, admin_id):
    global admins_db
    if admins_db is None:
        admins_db = load_admins_data()
    all_admin_ids = get_all_admins()

    user_db = get_user_from_db(user_id)
    target_username = user_db[1] if user_db else f"ID {user_id}"

    admin_db = get_user_from_db(admin_id)
    admin_username = admin_db[1] if admin_db else f"ID {admin_id}"

    stage_name = WARNING_LEVELS[stage][0] if stage in WARNING_LEVELS else str(stage)

    notification_text = (
        f'🚨 ВЫДАНО ПРЕДУПРЕЖДЕНИЕ\n\n'
        f'Пользователь: {target_username} (ID: {user_id})\n'
        f'Уровень: {stage} ({stage_name})\n'
        f'Причина: {reason}\n'
        f'Выдал: {admin_username} (ID: {admin_id})\n'
        f'Дата: {datetime.now().strftime("%d.%m.%Y %H:%M")}'
    )

    for admin_id_notify in all_admin_ids:
        try:
            bot.send_message(admin_id_notify, notification_text, parse_mode='HTML')
        except Exception:
            pass


def log_new_user(user_id, first_name, last_name, username):
    full_name = first_name + (f" {last_name}" if last_name else "")
    display_username = username if username else "не указан"
    print(f"\n{'📝' * 40}\n🆔 ID: {user_id}\n👤 Имя: {full_name}\n✏️ Username: {display_username}\n{'📝' * 40}\n")


# === ФУНКЦИИ АДМИНОВ ===
def load_admins_data():
    global admins_db
    if os.path.exists(ADMINS_DATA_FILE):
        try:
            with open(ADMINS_DATA_FILE, 'r', encoding='utf-8') as f:
                admins_db = json.load(f)
                return admins_db
        except Exception:
            pass
    return {'super_admins': [], 'admins': []}


def save_admins_data(data):
    global admins_db
    admins_db = data
    with open(ADMINS_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def init_admins_database():
    global admins_db
    admins_db = load_admins_data()
    if not admins_db.get('super_admins'):
        owner_id = int(input("👑 Введите ваш Telegram ID для Супер-Админа: "))
        admins_db['super_admins'].append(owner_id)
        admins_db['admins'].append(owner_id)
        save_admins_data(admins_db)
        print(f"✅ Супер-Админ установлен: {owner_id}")
    return admins_db


def get_super_admins():
    global admins_db
    if admins_db is None:
        admins_db = load_admins_data()
    return admins_db.get('super_admins', [])


def get_all_admins():
    global admins_db
    if admins_db is None:
        admins_db = load_admins_data()
    return list(set(admins_db.get('admins', []) + admins_db.get('super_admins', [])))


def is_super_admin(user_id):
    return user_id in get_super_admins()


def is_regular_admin(user_id):
    return user_id in get_all_admins() and not is_super_admin(user_id)


def is_admin(user_id):
    return is_super_admin(user_id) or is_regular_admin(user_id)


def add_to_admin(role, user_id):
    global admins_db
    admins_db = load_admins_data()
    if role == 'super':
        if user_id not in admins_db['super_admins']:
            admins_db['super_admins'].append(user_id)
            if user_id not in admins_db['admins']:
                admins_db['admins'].append(user_id)
            save_admins_data(admins_db)
            return True
    else:
        if user_id not in admins_db['admins'] and user_id not in admins_db['super_admins']:
            admins_db['admins'].append(user_id)
            save_admins_data(admins_db)
            return True
    return False


def remove_from_admin(user_id):
    global admins_db
    admins_db = load_admins_data()
    admins_db['admins'] = [x for x in admins_db.get('admins', []) if x != user_id]
    admins_db['super_admins'] = [x for x in admins_db.get('super_admins', []) if x != user_id]
    save_admins_data(admins_db)


# === ПАРОЛИ И КЭШ ===
def load_admin_password():
    if os.path.exists(ADMIN_PASSWORD_FILE):
        try:
            with open(ADMIN_PASSWORD_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('password', '')
        except Exception:
            pass
    return ''


def save_admin_password(password):
    with open(ADMIN_PASSWORD_FILE, 'w', encoding='utf-8') as f:
        json.dump({'password': password}, f)


def check_admin_password(password):
    stored_password = load_admin_password()
    if not stored_password:
        return False
    return password == stored_password


def is_admin_password_cached(user_id):
    if user_id in admin_password_cache:
        last_login = admin_password_cache[user_id]
        if datetime.now() - last_login < timedelta(days=1):
            return True
        else:
            del admin_password_cache[user_id]
    return False


def cache_admin_password(user_id):
    admin_password_cache[user_id] = datetime.now()


# === ДРУГИЕ ФУНКЦИИ ===
def get_lang(user_id):
    return user_languages.get(user_id, 'ru')


def format_balance(amount):
    try:
        return '{:,.0f}'.format(float(amount)).replace(',', ' ')
    except Exception:
        return '0'


def generate_password(length=16):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    pwd = ''.join(secrets.choice(alphabet) for _ in range(length))
    while not (
            any(c.islower() for c in pwd) and
            any(c.isupper() for c in pwd) and
            any(c.isdigit() for c in pwd) and
            any(c in "!@#$%^&*()-_=+" for c in pwd)
    ):
        pwd = ''.join(secrets.choice(alphabet) for _ in range(length))
    return pwd


def init_keys_folder():
    if not os.path.exists(KEYS_FOLDER):
        os.makedirs(KEYS_FOLDER)
    for f in KEY_FILES.values():
        path = os.path.join(KEYS_FOLDER, f)
        if not os.path.exists(path):
            open(path, 'w', encoding='utf-8').close()


def load_users_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_users_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user_data(user_id):
    data = load_users_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            'balance': 0.0,
            'username': None,
            'purchases': [],
            'created_at': datetime.now().isoformat()
        }
        save_users_data(data)
        return data[uid]
    return data[uid]


def update_user_info(user_id, first_name, last_name, username):
    data = load_users_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            'balance': 0.0,
            'first_name': first_name,
            'last_name': last_name if last_name else None,
            'username': username,
            'purchases': [],
            'created_at': datetime.now().isoformat()
        }
        log_new_user(user_id, first_name, last_name, username)
        notify_admins_about_new_user(user_id, first_name, last_name, username)
        get_user_from_db(user_id)
    else:
        data[uid]['first_name'] = first_name
        data[uid]['last_name'] = last_name if last_name else data[uid].get('last_name')
        data[uid]['username'] = username
    save_users_data(data)


def update_user_balance(user_id, amount):
    data = load_users_data()
    uid = str(user_id)

    if uid not in data:
        data[uid] = {'balance': 0.0, 'username': None, 'purchases': []}
    if 'balance' not in data[uid]:
        data[uid]['balance'] = 0.0

    data[uid]['balance'] = round(data[uid]['balance'] + amount, 2)
    save_users_data(data)

    update_user_balance_db(int(user_id), data[uid]['balance'])
    return data[uid]['balance']


def add_purchase_record(user_id, product, price, key):
    data = load_users_data()
    uid = str(user_id)
    if uid in data:
        data[uid].setdefault('purchases', []).append({
            'product': product,
            'price': price,
            'key': key,
            'date': datetime.now().isoformat()
        })
        save_users_data(data)


def get_keys_count(short_key):
    prod_id = PRODUCT_MAP.get(short_key)
    if not prod_id:
        return 0
    path = os.path.join(KEYS_FOLDER, KEY_FILES.get(prod_id, ''))
    if not os.path.exists(path):
        return 0
    with open(path, 'r', encoding='utf-8') as f:
        return len([l.strip() for l in f if l.strip()])


def get_multiple_keys_from_file(short_key, quantity):
    prod_id = PRODUCT_MAP.get(short_key)
    if not prod_id or prod_id not in KEY_FILES:
        return None
    path = os.path.join(KEYS_FOLDER, KEY_FILES[prod_id])
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip()]
    if len(lines) < quantity:
        return None
    taken_keys = lines[:quantity]
    remaining_keys = lines[quantity:]
    with open(path, 'w', encoding='utf-8') as f:
        # FIX: добавляем перевод строки в конце, чтобы не склеивать последний ключ
        if remaining_keys:
            f.write('\n'.join(remaining_keys) + '\n')
    return taken_keys


def add_key_to_file(short_key, key):
    prod_id = PRODUCT_MAP.get(short_key)
    if not prod_id:
        return False
    path = os.path.join(KEYS_FOLDER, KEY_FILES.get(prod_id, ''))
    with open(path, 'a', encoding='utf-8') as f:
        f.write(key.strip() + '\n')
    return True


def send_balance_notification(target_user_id, amount, new_balance):
    target_lang = get_lang(target_user_id)
    template = LANGUAGES[target_lang]['balance_topup_notification']
    text = template.format(target_user_id, amount, new_balance)
    try:
        bot.send_message(target_user_id, text, parse_mode='HTML')
    except Exception:
        pass


# === КЛАВИАТУРЫ ===
def get_main_keyboard(user_id):
    lang = get_lang(user_id)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(LANGUAGES[lang]['products'], LANGUAGES[lang]['profile'])
    kb.row(LANGUAGES[lang]['settings'], LANGUAGES[lang]['support'])
    kb.row(LANGUAGES[lang]['rules'])
    if is_admin(user_id):
        kb.row(LANGUAGES[lang]['admin_panel'])
    return kb


def get_subscription_keyboard(lang):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for short_key, prod_id in PRODUCT_MAP.items():
        display_name = PRODUCT_DISPLAY[prod_id]
        price = PRODUCT_PRICES[prod_id]
        btn_text = f"🤍 PRIMEHACK • {display_name} — {price}₽"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"select_qty_menu_{short_key}"))
    back_text = "← Назад" if lang == "ru" else "← Back"
    markup.add(types.InlineKeyboardButton(back_text, callback_data="back_to_menu"))
    return markup


def get_profile_keyboard(user_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(LANGUAGES[get_lang(user_id)]['top_up_balance'], url=DEV_URL))
    markup.add(types.InlineKeyboardButton(LANGUAGES[get_lang(user_id)]['moderator'], url=MOD_URL))
    markup.add(types.InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_menu"))
    return markup


def get_settings_keyboard(user_id):
    lang = get_lang(user_id)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(LANGUAGES[lang]['language'])
    kb.row(LANGUAGES[lang]['back_menu'])
    return kb


def get_language_keyboard(user_id):
    lang = get_lang(user_id)
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(LANGUAGES[lang]['rus'], LANGUAGES[lang]['eng'])
    kb.row(LANGUAGES[lang]['back_menu'])
    return kb


def get_support_inline_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💬 Войти в чат", url=CHAT_PANEL_URL))
    markup.add(types.InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_menu"))
    return markup


def get_chat_join_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📲 ВОЙТИ В ЧАТ", url=CHAT_PANEL_URL))
    markup.add(types.InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_menu"))
    return markup


def get_rules_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_menu"))
    return markup


def get_insufficient_funds_keyboard(user_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(LANGUAGES[get_lang(user_id)]['top_up_balance'], url=DEV_URL))
    markup.add(types.InlineKeyboardButton(LANGUAGES[get_lang(user_id)]['moderator'], url=MOD_URL))
    markup.add(types.InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_menu"))
    return markup


def get_admin_keyboard(user_id):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row('📊 Наличие', '💸 Пополнить', '🧯 Обнулить')
    kb.row('🔒 Пароль', '⚖️ Выдать варн')
    if is_super_admin(user_id):
        kb.row('🔑 Добавить ключ', '➕ Добавить админа')
        kb.row('👑 Супер-админ', '❌ Снять с админки')
        kb.row('🔐 Установить пароль админа')
    kb.row('🔙 Назад')
    return kb


def get_subscription_text(lang):
    title = "Категория: 🤍 PRIMEHACK" if lang == "ru" else "Category: 🤍 PRIMEHACK"
    choose = "Выберите период подписки:" if lang == "ru" else "Choose subscription period:"
    text = f"<b>{title}</b>\n\n"
    for short_key, prod_id in PRODUCT_MAP.items():
        price = PRODUCT_PRICES[prod_id]
        display = PRODUCT_DISPLAY[prod_id]
        stock = get_keys_count(short_key)
        status = f"⚡ Мало ({stock})" if stock < 5 else f"✅ ({stock}+)"
        text += f"♦️ 🤍 PRIMEHACK • {display} — {price}₽ {status}\n"
    return f"{text}\n<b>{choose}</b>"


# === ОБРАБОТКА КНОПОК ===
def handle_button_press(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text
    lang = get_lang(user_id)

    current_state = user_states.get(user_id)

    # FIX: обработка состояния ввода варна (ID + причина)
    if current_state and current_state.startswith('awaiting_warn_reason_'):
        stage = int(current_state.split('_')[-1])
        # Ожидаем формат: ID причина_текст
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            bot.send_message(chat_id, "❌ Формат: <ID> <причина (мин. 10 символов)>")
            return True
        try:
            target_id = int(parts[0])
        except ValueError:
            bot.send_message(chat_id, "❌ ID должен быть числом!")
            return True
        reason = parts[1].strip()
        if len(reason) < 10:
            bot.send_message(chat_id, "❌ Причина минимум 10 символов!")
            return True

        user_db = get_user_from_db(target_id)
        if not user_db:
            bot.send_message(chat_id, "❌ Пользователь не найден в БД!")
            user_states[user_id] = None
            return True

        result = issue_warning(target_id, stage, reason, user_id)
        user_states[user_id] = None

        if not result:
            bot.send_message(chat_id, "❌ Не удалось выдать предупреждение")
            return True

        stage_name = WARNING_LEVELS[stage][0] if stage in WARNING_LEVELS else str(stage)
        username_target = user_db[1] if user_db[1] else f"ID {target_id}"

        if stage == 1:
            notif_text = f'🔔 Вам выдано <b>предупреждение</b>.\nПричина: {reason}'
        elif stage == 2:
            notif_text = (
                f'⚠️ Вам выдан <b>ВЫГОВОР</b>.\nПричина: {reason}\n'
                f'Списано 30%: {format_balance(result["old_balance"])} → {format_balance(result["new_balance"])} ₽'
            )
        else:
            notif_text = f'🚨 Вам выдан <b>СТРОГИЙ ВЫГОВОР</b>.\nПричина: {reason}'

        try:
            bot.send_message(target_id, notif_text, parse_mode='HTML')
        except Exception:
            pass

        notify_admins_about_warning(target_id, stage, reason, user_id)
        bot.send_message(chat_id, f"✅ Предупреждение (ур. {stage}) выдано: {username_target}",
                         reply_markup=get_admin_keyboard(user_id))
        return True

    if current_state == 'awaiting_admin_password':
        if check_admin_password(text):
            user_states[user_id] = None
            cache_admin_password(user_id)
            bot.send_message(chat_id, LANGUAGES[lang]['password_correct'], parse_mode='HTML',
                             reply_markup=get_admin_keyboard(user_id))
            return True
        else:
            user_states[user_id] = None
            bot.send_message(chat_id, LANGUAGES[lang]['admin_panel_blocked'], parse_mode='HTML',
                             reply_markup=get_main_keyboard(user_id))
            return True

    if text == LANGUAGES[lang]['products']:
        bot.send_message(chat_id, get_subscription_text(lang), parse_mode='HTML',
                         reply_markup=get_subscription_keyboard(lang))
        return True
    elif text == LANGUAGES[lang]['profile']:
        user_data = get_user_data(user_id)
        username = message.from_user.username or message.from_user.first_name
        profile = f"🆔 ID: {user_id}\n👤 Имя: {username}\n💰 Баланс: {format_balance(user_data['balance'])} ₽"
        bot.send_message(chat_id, profile, reply_markup=get_profile_keyboard(user_id))
        return True
    elif text == LANGUAGES[lang]['settings']:
        bot.send_message(chat_id, LANGUAGES[lang]['settings_content'], reply_markup=get_settings_keyboard(user_id))
        return True
    elif text == LANGUAGES[lang]['support']:
        bot.send_message(chat_id, LANGUAGES[lang]['chat_panel_title'], parse_mode='HTML',
                         reply_markup=get_chat_join_keyboard())
        return True
    elif text == LANGUAGES[lang]['rules']:
        bot.send_message(chat_id, LANGUAGES[lang]['rules_text'], parse_mode='HTML', reply_markup=get_rules_keyboard())
        return True
    elif text == LANGUAGES[lang]['language']:
        current = LANGUAGES[lang]['rus'] if lang == 'ru' else LANGUAGES[lang]['eng']
        bot.send_message(chat_id, LANGUAGES[lang]['current_lang'].format(current),
                         reply_markup=get_language_keyboard(user_id))
        return True
    elif text == LANGUAGES[lang]['rus']:
        user_languages[user_id] = 'ru'
        bot.send_message(chat_id, "✅ Русский", reply_markup=get_main_keyboard(user_id))
        return True
    elif text == LANGUAGES[lang]['eng']:
        user_languages[user_id] = 'en'
        bot.send_message(chat_id, "✅ English", reply_markup=get_main_keyboard(user_id))
        return True
    elif text == LANGUAGES[lang]['back_menu']:
        bot.send_message(chat_id, LANGUAGES[lang]['welcome'], reply_markup=get_main_keyboard(user_id))
        return True

    if text == LANGUAGES[lang]['admin_panel'] and is_admin(user_id):
        password = load_admin_password()
        if not password:
            bot.send_message(chat_id, LANGUAGES[lang]['no_password_set'], parse_mode='HTML',
                             reply_markup=get_admin_keyboard(user_id))
            return True
        elif is_admin_password_cached(user_id):
            bot.send_message(chat_id, LANGUAGES[lang]['admin_menu_title'], parse_mode='HTML',
                             reply_markup=get_admin_keyboard(user_id))
            return True
        else:
            user_states[user_id] = 'awaiting_admin_password'
            bot.send_message(chat_id, LANGUAGES[lang]['enter_admin_password'], parse_mode='HTML')
            return True
    elif text == '⚖️ Выдать варн' and is_super_admin(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("Уровень 1 - Предупреждение", callback_data="warn_level_1"))
        markup.row(types.InlineKeyboardButton("Уровень 2 - Выговор", callback_data="warn_level_2"))
        markup.row(types.InlineKeyboardButton("Уровень 3 - Строгий выговор", callback_data="warn_level_3"))
        markup.row(types.InlineKeyboardButton("🔙 Отмена", callback_data="back_to_menu"))
        bot.send_message(chat_id, "🛡️ <b>Выберите уровень предупреждения:</b>", parse_mode='HTML',
                         reply_markup=markup)
        return True
    elif text == '🔙 Назад':
        bot.send_message(chat_id, LANGUAGES[lang]['welcome'], reply_markup=get_main_keyboard(user_id))
        return True
    elif text == '🔑 Добавить ключ' and is_super_admin(user_id):
        bot.send_message(chat_id, LANGUAGES[lang]['add_key_instruction'], parse_mode='HTML')
        return True
    elif text == '➕ Добавить админа' and is_super_admin(user_id):
        bot.send_message(chat_id, "📌 /add_admin <ID>")
        return True
    elif text == '👑 Супер-админ' and is_super_admin(user_id):
        bot.send_message(chat_id, "📌 /add_super_admin <ID>")
        return True
    elif text == '❌ Снять с админки' and is_super_admin(user_id):
        bot.send_message(chat_id, "📌 /remove_admin <ID>")
        return True
    elif text == '🔐 Установить пароль админа' and is_super_admin(user_id):
        bot.send_message(chat_id, "📌 /set_admin_password ВАШ_ПАРОЛЬ")
        return True
    elif text == '📊 Наличие' and is_admin(user_id):
        lines = []
        for k in PRODUCT_MAP:
            lines.append(f"{KEY_CATEGORIES[PRODUCT_MAP[k]]}: {get_keys_count(k)} шт")
        bot.send_message(chat_id, '\n'.join(lines))
        return True
    elif text == '🧯 Обнулить' and is_admin(user_id):
        bot.send_message(chat_id, "📌 /reset_balances <ID>")
        return True
    elif text == '💸 Пополнить' and is_admin(user_id):
        bot.send_message(chat_id, "📌 /add_balance <ID> <сумма>")
        return True
    elif text == '🔒 Пароль' and is_admin(user_id):
        password = generate_password(16)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔄 Ещё", callback_data="regen_password"))
        markup.add(types.InlineKeyboardButton("🔙 Меню", callback_data="back_to_menu"))
        bot.send_message(chat_id, LANGUAGES[lang]['password_generated'].format(password, len(password)),
                         parse_mode='HTML', reply_markup=markup)
        return True
    return False


# === КОМАНДЫ ===
@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name if message.from_user.last_name else None
    username = message.from_user.username if message.from_user.username else None
    user_languages.setdefault(user_id, 'ru')
    update_user_info(user_id, first_name, last_name, username)
    bot.send_message(message.chat.id, LANGUAGES['ru']['welcome'], reply_markup=get_main_keyboard(user_id))


@bot.message_handler(commands=['my_warn'])
def cmd_my_warn(message):
    user_id = message.from_user.id
    warnings = get_user_warnings(user_id)

    if not warnings:
        bot.reply_to(message, "📋 <b>У вас нет действующих предупреждений</b>", parse_mode='HTML')
        return

    text = "<b>📋 ВАШИ ПРЕДУПРЕЖДЕНИЯ:</b>\n\n"
    for idx, warning in enumerate(warnings, 1):
        warning_id, stage, reason, issued_at, admin_id, admin_username = warning
        stage_name = WARNING_LEVELS[stage][0] if stage in WARNING_LEVELS else str(stage)
        time_formatted = format_timestamp(issued_at)
        text += f"#{idx}. №{warning_id} | {time_formatted}\n"
        text += f"   Уровень: {stage} ({stage_name})\n"
        text += f"   Причина: {reason}\n"
        text += f"   Статус: Активно\n\n"

    bot.reply_to(message, text, parse_mode='HTML')


@bot.message_handler(commands=['warn'])
def cmd_warn(message):
    if not is_super_admin(message.from_user.id):
        bot.reply_to(message, LANGUAGES[get_lang(message.from_user.id)]['limited_access'])
        return
    try:
        parts = message.text.split(maxsplit=3)
        if len(parts) < 4:
            bot.reply_to(message, "Ошибка: /warn <user_id> <stage 1-3> <reason>")
            return
        target_id = int(parts[1])
        stage = int(parts[2])
        reason = parts[3].strip()
        if stage not in [1, 2, 3]:
            bot.reply_to(message, "Ошибка: уровень 1, 2 или 3")
            return
        if len(reason) < 10:
            bot.reply_to(message, "Ошибка: причина минимум 10 символов")
            return
        user_db = get_user_from_db(target_id)
        if not user_db:
            bot.reply_to(message, "Ошибка: пользователь не найден")
            return
        result = issue_warning(target_id, stage, reason, message.from_user.id)
        if not result:
            bot.reply_to(message, "Ошибка: не удалось выдать предупреждение")
            return
        stage_name = WARNING_LEVELS[stage][0] if stage in WARNING_LEVELS else str(stage)
        username_target = user_db[1] if user_db[1] else f"ID {target_id}"
        if stage == 1:
            notif_text = f'🔔 Вам выдано <b>предупреждение</b>.\nПричина: {reason}'
        elif stage == 2:
            notif_text = (
                f'⚠️ Вам выдан <b>ВЫГОВОР</b>.\nПричина: {reason}\n'
                f'Списано 30%: {format_balance(result["old_balance"])} → {format_balance(result["new_balance"])} ₽'
            )
        elif stage == 3:
            notif_text = f'🚨 Вам выдан <b>СТРОГИЙ ВЫГОВОР</b>.\nПричина: {reason}'
        try:
            bot.send_message(target_id, notif_text, parse_mode='HTML')
        except Exception:
            pass
        notify_admins_about_warning(target_id, stage, reason, message.from_user.id)
        bot.reply_to(message, f"✅ Предупреждение выдано: {username_target}")
    except ValueError:
        bot.reply_to(message, "Ошибка: ID и уровень должны быть числами")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")


@bot.message_handler(commands=['admin'])
def cmd_admin(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    lang = get_lang(user_id)
    password = load_admin_password()
    if not password:
        bot.send_message(message.chat.id, LANGUAGES[lang]['no_password_set'], reply_markup=get_admin_keyboard(user_id))
    elif is_admin_password_cached(user_id):
        bot.send_message(message.chat.id, LANGUAGES[lang]['admin_menu_title'], parse_mode='HTML',
                         reply_markup=get_admin_keyboard(user_id))
    else:
        user_states[user_id] = 'awaiting_admin_password'
        bot.send_message(message.chat.id, LANGUAGES[lang]['enter_admin_password'], parse_mode='HTML')


@bot.message_handler(commands=['set_admin_password'])
def cmd_set_admin_password(message):
    if not is_super_admin(message.from_user.id):
        return bot.reply_to(message, LANGUAGES[get_lang(message.from_user.id)]['limited_access'])
    try:
        args = message.text.split(maxsplit=1)
        if len(args) != 2:
            bot.reply_to(message, "❌ /set_admin_password ВАШ_ПАРОЛЬ")
            return
        new_password = args[1].strip()
        if len(new_password) < 4:
            bot.reply_to(message, "❌ Минимум 4 символа!")
            return
        save_admin_password(new_password)
        bot.reply_to(message, LANGUAGES[get_lang(message.from_user.id)]['password_set'])
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")


@bot.message_handler(commands=['admin_refresh'])
def cmd_admin_refresh(message):
    if is_admin(message.from_user.id):
        bot.reply_to(message, "✅ Клавиатура обновлена!", reply_markup=get_main_keyboard(message.from_user.id))
    else:
        bot.reply_to(message, "❌ Нет прав.")


@bot.message_handler(commands=['add_balance'])
def cmd_add_balance(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target, amt = message.text.split()
        target_id = int(target.lstrip('@'))
        amount = int(amt)
        if target_id == message.from_user.id:
            bot.reply_to(message, "❌ Нельзя пополнять себе!")
            return
        new_bal = update_user_balance(target_id, amount)
        bot.reply_to(message, f"✅ Пополнено {amount}₽, баланс: {new_bal}₽")
        send_balance_notification(target_id, amount, new_bal)
    except ValueError:
        bot.reply_to(message, "❌ /add_balance <ID> <сумма>")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")


@bot.message_handler(commands=['reset_balances'])
def cmd_reset_balance(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, target = message.text.split()
        target_id = int(target.lstrip('@'))
        user_data = get_user_data(target_id)
        old_balance = user_data['balance']
        update_user_balance(target_id, -old_balance)
        bot.reply_to(message, f"✅ Баланс {target_id} обнулён.")
    except Exception:
        bot.reply_to(message, "❌ /reset_balances <ID>")


@bot.message_handler(commands=['remove_admin'])
def cmd_remove_admin(message):
    if not is_super_admin(message.from_user.id):
        return bot.reply_to(message, LANGUAGES[get_lang(message.from_user.id)]['limited_access'])
    try:
        _, target = message.text.split()
        target_id = int(target.lstrip('@'))
        if target_id == message.from_user.id:
            return bot.reply_to(message, "❌ Нельзя удалить себя!")
        remove_from_admin(target_id)
        bot.reply_to(message, f"✅ {target_id} удалён из админов.")
    except Exception:
        bot.reply_to(message, "❌ /remove_admin <ID>")


@bot.message_handler(commands=['add_super_admin'])
def cmd_add_super_admin(message):
    if not is_super_admin(message.from_user.id):
        return bot.reply_to(message, LANGUAGES[get_lang(message.from_user.id)]['limited_access'])
    try:
        _, target = message.text.split()
        new_id = int(target.lstrip('@'))
        if new_id in get_super_admins():
            return bot.reply_to(message, "⚠️ Уже супер-админ.")
        if add_to_admin('super', new_id):
            bot.reply_to(message, f"✅ {new_id} назначен Супер-Админом!")
            try:
                bot.send_message(new_id, "👑 Вы назначены СУПЕР-АДМИНОМ!", parse_mode='HTML')
            except Exception:
                pass
    except Exception:
        bot.reply_to(message, "❌ /add_super_admin <ID>")


# FIX: убран висящий pass и битый try/except
@bot.message_handler(commands=['add_admin'])
def cmd_add_admin(message):
    if not is_super_admin(message.from_user.id):
        return bot.reply_to(message, LANGUAGES[get_lang(message.from_user.id)]['limited_access'])
    try:
        _, target = message.text.split()
        new_id = int(target.lstrip('@'))
        if new_id in get_all_admins():
            return bot.reply_to(message, "⚠️ Уже админ.")
        if add_to_admin('regular', new_id):
            bot.reply_to(message, f"✅ {new_id} добавлен как админ.")
            try:
                bot.send_message(new_id, "🛠️ Вы назначены администратором!", parse_mode='HTML')
            except Exception:
                pass
    except Exception:
        bot.reply_to(message, "❌ /add_admin <ID>")


@bot.message_handler(commands=['list_admins'])
def cmd_list_admins(message):
    if not is_super_admin(message.from_user.id):
        return bot.reply_to(message, LANGUAGES[get_lang(message.from_user.id)]['limited_access'])
    super_admins = get_super_admins()
    admins = get_all_admins()
    text = "<b>📋 Список админов:</b>\n\n👑 Супер-Админы:\n"
    for aid in super_admins:
        text += f"   • {aid} ✅\n"
    text += "\n👤 Все админы:\n"
    for aid in admins:
        level = "👑 Супер" if aid in super_admins else "👤 Админ"
        text += f"   • {aid} [{level}]\n"
    bot.reply_to(message, text, parse_mode='HTML')


@bot.message_handler(commands=['addkey'])
def cmd_addkey(message):
    if not is_super_admin(message.from_user.id):
        return bot.reply_to(message, LANGUAGES[get_lang(message.from_user.id)]['limited_access'])
    try:
        args = message.text.split(maxsplit=2)
        if len(args) != 3:
            return bot.reply_to(message, LANGUAGES[get_lang(message.from_user.id)]['add_key_instruction'],
                                parse_mode='HTML')
        _, short_key, key = args
        if short_key not in PRODUCT_MAP:
            return bot.reply_to(message, "❌ Неверный период")
        if add_key_to_file(short_key, key):
            bot.reply_to(message, "✅ Ключ добавлен")
        else:
            bot.reply_to(message, "❌ Ошибка")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")


@bot.message_handler(commands=['genpassword'])
def cmd_genpassword(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "❌ Нет доступа")
    lang = get_lang(message.from_user.id)
    password = generate_password(16)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 Ещё", callback_data="regen_password"))
    markup.add(types.InlineKeyboardButton("🔙 Меню", callback_data="back_to_menu"))
    bot.send_message(message.chat.id, LANGUAGES[lang]['password_generated'].format(password, len(password)),
                     parse_mode='HTML', reply_markup=markup)


@bot.message_handler(commands=['help'])
def cmd_help(message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    help_text = "📋 Команды:\n/start | /help | /my_warn\n"
    if is_super_admin(user_id):
        help_text += "\n👑 /add_admin | /add_super_admin | /remove_admin | /list_admins | /addkey | /set_admin_password | /warn\n"
    elif is_admin(user_id):
        help_text += "\n👤 /add_balance | /reset_balances | /genpassword\n"
    bot.send_message(message.chat.id, help_text, parse_mode='HTML')


@bot.message_handler(commands=['myid'])
def cmd_myid(message):
    bot.send_message(message.chat.id, f"🆔 ID: {message.from_user.id}")


@bot.message_handler(commands=['cancel'])
def cmd_cancel(message):
    user_states[message.from_user.id] = None
    bot.send_message(message.chat.id, "❌ Отмена", reply_markup=get_main_keyboard(message.from_user.id))


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if not handle_button_press(message):
        bot.send_message(message.chat.id, LANGUAGES[get_lang(message.from_user.id)]['unknown_command'],
                         reply_markup=get_main_keyboard(message.from_user.id))


# === CALLBACK ===
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    msg_id = call.message.message_id
    chat_id = call.message.chat.id
    lang = get_lang(user_id)

    if call.data.startswith("warn_level_"):
        if not is_super_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Нет прав")
            return
        stage = int(call.data.split("_")[-1])
        user_states[user_id] = f"awaiting_warn_reason_{stage}"
        # FIX: используем send_message вместо edit_message_text,
        # чтобы пользователь мог ответить текстом
        bot.send_message(
            chat_id,
            f"⚠️ <b>Уровень {stage} выбран.</b>\n\n"
            f"Отправьте сообщение в формате:\n<code>ID_пользователя причина</code>\n\n"
            f"Пример: <code>123456789 Нарушение правил панели</code>\n\n"
            f"Для отмены: /cancel",
            parse_mode='HTML')
        bot.answer_callback_query(call.id)
        return

    # FIX: back_to_menu — нельзя использовать edit_message_text с ReplyKeyboardMarkup
    # Удаляем inline-сообщение и отправляем новое с reply-клавиатурой
    if call.data == "back_to_menu":
        try:
            bot.delete_message(chat_id, msg_id)
        except Exception:
            pass
        bot.send_message(chat_id, LANGUAGES[lang]['welcome'],
                         reply_markup=get_main_keyboard(user_id))
        bot.answer_callback_query(call.id)
        return

    if call.data == "regen_password":
        password = generate_password(16)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔄 Ещё", callback_data="regen_password"))
        markup.add(types.InlineKeyboardButton("🔙 Меню", callback_data="back_to_menu"))
        bot.edit_message_text(LANGUAGES[lang]['password_generated'].format(password, len(password)),
                              chat_id, msg_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("select_qty_menu_"):
        short_key = call.data.replace("select_qty_menu_", "")
        prod_id = PRODUCT_MAP.get(short_key)
        if not prod_id:
            bot.answer_callback_query(call.id, "❌ Ошибка")
            return
        price = PRODUCT_PRICES[prod_id]
        display = PRODUCT_DISPLAY[prod_id]
        stock = get_keys_count(short_key)
        text = (f"<b>🛍 {display}</b>\n💵 Цена за 1 шт: {price}₽\n"
                f"📦 В наличии: {stock} шт.\n\n{LANGUAGES[lang]['select_qty_title']}")
        markup = types.InlineKeyboardMarkup(row_width=2)
        for i in range(1, 6):
            markup.add(types.InlineKeyboardButton(
                f"{i} шт. ({i * price}₽)", callback_data=f"confirm_qty_{short_key}_{i}"))
        markup.add(types.InlineKeyboardButton("🔙 Назад к товарам", callback_data="back_to_products"))
        bot.edit_message_text(text, chat_id, msg_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if call.data == "back_to_products":
        bot.edit_message_text(get_subscription_text(lang), chat_id, msg_id, parse_mode='HTML',
                              reply_markup=get_subscription_keyboard(lang))
        bot.answer_callback_query(call.id)
        return

    # FIX: корректный парсинг callback_data для confirm_qty и final_buy
    # Формат: confirm_qty_<short_key>_<quantity>
    # short_key может содержать цифры (14d, 30d), поэтому split("_") ненадёжен
    # Используем rsplit для отделения количества с конца
    if call.data.startswith("confirm_qty_"):
        suffix = call.data[len("confirm_qty_"):]  # например "14d_3"
        # Отделяем последнее значение (quantity) от short_key
        last_underscore = suffix.rfind("_")
        if last_underscore == -1:
            bot.answer_callback_query(call.id, "❌ Ошибка данных")
            return
        short_key = suffix[:last_underscore]
        try:
            quantity = int(suffix[last_underscore + 1:])
        except ValueError:
            bot.answer_callback_query(call.id, "❌ Ошибка данных")
            return

        prod_id = PRODUCT_MAP.get(short_key)
        if not prod_id:
            bot.answer_callback_query(call.id, "❌ Ошибка")
            return
        price_per_unit = PRODUCT_PRICES[prod_id]
        total_price = price_per_unit * quantity
        display = PRODUCT_DISPLAY[prod_id]
        product_name = f"🤍 PRIMEHACK • {display}"
        stock = get_keys_count(short_key)
        if stock < quantity:
            text = f"❌ Недостаточно ключей!\nВ наличии только {stock} шт."
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_products"))
            bot.edit_message_text(text, chat_id, msg_id, reply_markup=markup)
            bot.answer_callback_query(call.id)
            return
        confirm_text = (LANGUAGES[lang]['confirm_title'] + '\n' +
                        LANGUAGES[lang]['confirm_text'].format(product_name, quantity, total_price))
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Купить", callback_data=f"final_buy_{short_key}_{quantity}"))
        markup.add(
            types.InlineKeyboardButton("🔙 Изменить кол-во", callback_data=f"select_qty_menu_{short_key}"))
        markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data="back_to_menu"))
        bot.edit_message_text(confirm_text, chat_id, msg_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("final_buy_"):
        suffix = call.data[len("final_buy_"):]  # например "30d_2"
        last_underscore = suffix.rfind("_")
        if last_underscore == -1:
            bot.answer_callback_query(call.id, "❌ Ошибка данных")
            return
        short_key = suffix[:last_underscore]
        try:
            quantity = int(suffix[last_underscore + 1:])
        except ValueError:
            bot.answer_callback_query(call.id, "❌ Ошибка данных")
            return

        prod_id = PRODUCT_MAP.get(short_key)
        if not prod_id:
            bot.answer_callback_query(call.id, "❌ Ошибка")
            return
        price_per_unit = PRODUCT_PRICES[prod_id]
        total_price = price_per_unit * quantity
        display = PRODUCT_DISPLAY[prod_id]
        product_name = f"🤍 PRIMEHACK • {display}"

        user_data = get_user_data(user_id)
        balance = user_data.get('balance', 0.0)

        if balance < total_price:
            missing = total_price - balance
            text = LANGUAGES[lang]['insufficient_funds'].format(
                format_balance(balance), format_balance(total_price), format_balance(missing))
            bot.edit_message_text(text, chat_id, msg_id, parse_mode='HTML',
                                  reply_markup=get_insufficient_funds_keyboard(user_id))
            bot.answer_callback_query(call.id)
            return

        keys = get_multiple_keys_from_file(short_key, quantity)
        if not keys:
            bot.edit_message_text("❌ Ошибка выдачи ключей!", chat_id, msg_id)
            bot.answer_callback_query(call.id)
            return

        new_balance = update_user_balance(user_id, -total_price)
        for key in keys:
            add_purchase_record(user_id, product_name, price_per_unit, key)

        keys_text = "\n".join(keys)
        success_text = LANGUAGES[lang]['purchase_success'].format(
            product_name, quantity, format_balance(total_price), format_balance(new_balance), keys_text)
        bot.edit_message_text(success_text, chat_id, msg_id, parse_mode='HTML')
        bot.answer_callback_query(call.id, "✅ Успешно!")
        return

    bot.answer_callback_query(call.id)


# === ЗАПУСК ===
def main():
    init_keys_folder()
    init_database()
    global admins_db
    admins_db = load_admins_data()
    if not admins_db.get('super_admins'):
        try:
            owner_id = int(input("👑 Введите ваш Telegram ID: "))
            admins_db['super_admins'] = [owner_id]
            admins_db['admins'] = [owner_id]
            save_admins_data(admins_db)
        except Exception:
            print("❌ Ошибка настройки")
    print("=" * 60)
    print("✅ БОТ ЗАПУЩЕН | СИСТЕМА ПРЕДУПРЕЖДЕНИЙ АКТИВНА")
    print(f"👑 Супер-админы: {len(get_super_admins())}")
    print(f"👤 Всего админов: {len(get_all_admins())}")
    print(f"🗄️ База данных: {DATABASE_FILE}")
    print("=" * 60)
    bot.infinity_polling()


# FIX: правильная проверка __name__ и убран дублирующий bot.polling()
if __name__ == '__main__':
    main()
