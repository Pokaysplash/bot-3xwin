import logging
import gspread
import asyncio
import os
import json
from keep_alive import keep_alive
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 🔐 Configuraciones
SHEET_ID = '1bntOQ6pR2-ynu4KO9s8rpESnW4-TcN_3U_cdNWazz2A'
BOT_TOKEN = os.environ["BOT_TOKEN"]

# 🔐 Conexión segura con Google Sheets desde variable de entorno
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]
json_keyfile_dict = json.loads(os.environ["GOOGLE_SERVICE_JSON"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(json_keyfile_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet("Respuestas")

# 🧾 Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 📩 Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.send_message(
        chat_id=chat_id,
        text="👋 Hola, por favor escribe tu código de usuario (Ej: XWIN001)"
    )

# ✅ Validar código
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_input = update.message.text.strip().upper()

    try:
        codigos = sheet.col_values(10)[1:]  # Columna J desde fila 2
        if user_input in codigos:
            await context.bot.send_message(
                chat_id=chat_id,
                text="✅ ¡Código válido! Aquí está tu enlace: https://t.me/Fases_3xWinBot"
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ No encontramos tu código. Por favor regístrate aquí: https://www.3xwin.top/formulario.html"
            )
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ Error al validar tu código."
        )
        logging.error(f"Error: {e}")

# 🧠 Función principal
async def main():
    keep_alive()  # Mantiene vivo el bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot en ejecución...")
    await app.run_polling()  # ✅ Este es el método correcto para ptb >= 20

# 🚀 Ejecutar
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "event loop is running" in str(e):
            loop = asyncio.get_event_loop()
            loop.create_task(main())
        else:
            raise
