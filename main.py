from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, filters
from datetime import datetime

TOKEN = "7806881202:AAFfCJHrhP1KxRf1THDEnN-4kP_Tikh3B1w"

user_states = {}

# Comando /start com botões na tela
async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("📅 Ver Hora", callback_data="hora")],
        [InlineKeyboardButton("ℹ Sobre", callback_data="sobre")],
        [InlineKeyboardButton("🐾 Diga um animal", callback_data="animal")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Escolha uma opção:", reply_markup=reply_markup)

# Responde ao clique nos botões
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == "hora":
        agora = datetime.now().strftime("%H:%M:%S")
        await query.edit_message_text(f"⏰ A hora atual é: {agora}")

    elif query.data == "sobre":
        await query.edit_message_text("🤖 Eu sou um bot criado para demonstração!")
    
    elif query.data == "animal":
        user_states[query.from_user.id] = "waiting_for_animal"
        await query.message.reply_text("Digite o nome de um animal:")


# Captura a resposta do usuário
async def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if user_id in user_states and user_states[user_id] == "waiting_for_animal":
        animal_name = update.message.text.upper()
        await update.message.reply_text(f"Você escolheu: {animal_name}")
        del user_states[user_id]  # Remove o estado do usuário após a resposta

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot está rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()
