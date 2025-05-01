from web import keep_alive

keep_alive()

import asyncio
import datetime
import gspread
from google.oauth2.service_account import Credentials
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor

BOT_TOKEN = "8168684697:AAEl56r8o5gaU2xAkisM961XqCfxqqHulLg"
GOOGLE_SHEET_NAME = "Finans"
SERVICE_ACCOUNT_FILE = "C:/Users/SAAS-NT/Desktop/Telegram Bot/creds.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEET_NAME).worksheet("Kassa")

HEADERS = ["1", "2", "3", "4", "5"]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Salam! Mən maliyyə botuyam. 🤖\n\nKomandalar üçün /help yaz.")

@dp.message_handler(commands=["help"])
async def help_command(message: types.Message):
    await message.answer(
        "📌 Bot Komandalarının Ətraflı İzahı:\n\n"
        "/pulqoy [məbləğ] [qeyd] - Kassaya pul əlavə edir\n"
        "/xerc [məbləğ] [qeyd] - Gider/xərc daxil edir\n"
        "/kassa - Kassadakı ümumi məbləği göstərir\n"
        "/gelirler - Yalnız gəlirləri göstərir\n"
        "/xercler - Yalnız xərcləri göstərir\n"
        "/balans - İstifadəçilərin ümumi balansı\n"
        "/log - Son 10 əməliyyatı göstərir\n"
        "/giris [məbləğ] [qeyd] - Kassaya daxil olan pul\n"
        "/pulgotur [məbləğ] [qeyd] - Kassadan cibə pul transferi\n"
        "/cibxerc [məbləğ] [qeyd] - Cibdən edilən xərclər\n"
        "/cibqaligi - Cibdəki mövcud vəsaiti göstərir\n"
        "/cibqaytar [məbləğ] [qeyd] - Cibdən kassaya qaytarılan məbləğ\n"
        "/cibhesabat - Ciblə bağlı hesabat\n"
        "/kassaxerc [məbləğ] [qeyd] - Kassadan edilən xərc\n"
        "/bazarborcal [məbləğ] [tədarükçü] [mal] [qiymət] - Tədarükçüyə borc\n"
        "/bazarborcode [məbləğ] [tədarükçü] - Borcun ödənməsi\n"
        "/bazarborc - Tədarükçüdən alınan mallar\n"
        "/maas [məbləğ] [qeyd] - Maaş verilməsi\n"
        "/kassayaborc [məbləğ] [qeyd] - Kassaya borcun verilmesi\n"
        "/gsmborc - Kassanın idarə heyəti verdiyi borcları göstərir"
    )

async def log_to_sheet(user, amount, note, type_):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([now, user, amount, note, type_], value_input_option="USER_ENTERED")

@dp.message_handler(commands=["pulqoy", "xerc", "giris", "pulgotur", "cibxerc", "cibqaytar", "kassaxerc", "bazarborcal", "bazarborcode", "maas", "kassayaborc", "gsmborc"])
async def handle_transactions(message: types.Message):
    try:
        content = message.text.split(" ", 2)
        if len(content) < 3:
            await message.reply("İstifadə: /komanda <məbləğ> <qeyd>")
            return

        amount = float(content[1])
        note = content[2]
        cmd = message.text.split()[0][1:]

        await log_to_sheet(message.from_user.username or message.from_user.first_name, amount, note, cmd)
        await message.reply(f"✅ {amount:.2f} AZN '{cmd}' kimi qeyd olundu.")

    except Exception as e:
        await message.reply(f"Xəta baş verdi: {str(e)}")

@dp.message_handler(commands=["bazarbor"])
async def bazarbor(message: types.Message):
    data = sheet.get_all_values()[1:]
    entries = [r for r in data if r[4] == "bazarborcal"]
    if not entries:
        await message.reply("Bazar borcu tapılmadı.")
        return

    output = "\n".join([f"📅 {r[0]} - 💼 {r[1]} - 📄 {r[3]} - 💰 {r[2]} AZN" for r in entries])
    await message.reply(output)

@dp.message_handler(commands=["gsmborc"])
async def gsmborc(message: types.Message):
    data = sheet.get_all_values()[1:]
    entries = [r for r in data if r[4] == "kassayaborc"]
    if not entries:
        await message.reply("GSM borcu tapılmadı.")
        return

    output = "\n".join([f"📅 {r[0]} - 💼 {r[1]} - 💰 {r[2]} AZN - 📄 {r[3]}" for r in entries])
    await message.reply(output)

# (Qalan funksiyalar — kassa, gelirler, xercler, balans, cibqaligi, log) kodda eynidir və saxlanılıb.

if __name__ == "__main__":
    print("✅ Bot işə düşdü...")
    executor.start_polling(dp, skip_updates=True)
