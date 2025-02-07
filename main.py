import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, filters
from datetime import datetime
import requests

from mtgsdk import Card


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


TOKEN = "7806881202:AAFfCJHrhP1KxRf1THDEnN-4kP_Tikh3B1w"


BUTTON_HORA = "hora"
BUTTON_SOBRE = "sobre"
BUTTON_ANIMAL = "animal"

user_states = {}

url = "https://api.magicthegathering.io/v1/cards"
headers = {
    "Authorization": "Bearer SEU_TOKEN_AQUI",
    "Content-Type": "application/json"
}


async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("📅 Ver Hora", callback_data=BUTTON_HORA)],
        [InlineKeyboardButton("ℹ Sobre", callback_data=BUTTON_SOBRE)],
        [InlineKeyboardButton("Digite sua carta", callback_data=BUTTON_ANIMAL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Escolha uma opção:", reply_markup=reply_markup)


async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == BUTTON_HORA:
        agora = datetime.now().strftime("%H:%M:%S")
        await query.edit_message_text(f"⏰ A hora atual é: {agora}")

    elif query.data == BUTTON_SOBRE:
        await query.edit_message_text("🤖 Eu sou um bot criado para demonstração!")
    
    elif query.data == BUTTON_ANIMAL:
        user_states[query.from_user.id] = "waiting_for_animal"
        await query.message.reply_text("Digite o nome de uma carta:")


async def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    message_text = update.message.text

    def buscar_cartas(nome):
        payload = {
            "name": nome,
            "language": "Portuguese (Brazil)"
        }
        response = requests.get(url, headers=headers, params=payload)
        if response.status_code == 200:
            resposta = response.json()
            try:
                resposta= resposta['cards'][0]['foreignNames']
            except Exception:
                resposta = None
            # resposta= resposta['cards'][0]

            return resposta
        else:
            raise Exception(f"Erro na API: {response.status_code}")
    
    def criar_resposta(cartas):
        resposta = ""
        for card in cartas:
            print(card)
            resposta += f"Nome: {card}"
            # resposta += f"Nome: {card.get('name', 'Desconhecido')}\nTipo: {card.get('type', 'Desconhecido')}\nCusto: {card.get('mana_cost', 'Desconhecido')}\nArtista: {card.get('artist', 'Desconhecido')}\n{image}\n\n"
        return resposta

    if user_id in user_states and user_states[user_id] == "waiting_for_animal":
        # try:
        resposta = ''
        cartas = buscar_cartas(message_text)
        if cartas:
            for carta in cartas:
                if carta['language'] == 'Portuguese (Brazil)':
                    resposta += f'Nome: {carta['name']}\nTipo: {carta['type']}\n{carta['imageUrl']}'
                    # resposta += f'{carta['name']}\n\n'
            await update.message.reply_text(f"Você escolheu:\n\n{resposta}")
        else:
            await update.message.reply_text("Nenhuma carta encontrada com esse nome.")
        # except Exception as e:
        #     await update.message.reply_text(f"Ocorreu um erro: {str(e)}")
        # cards = Card.where(name=update.message.text).all()
        # await update.message.reply_text(f"Você escolheu: {cards}")
        # if cards:
        #     resposta = ""
        #     for card in cards:
        #         # image = card.imageUrl
        #         image = card.image_url if hasattr(card, 'image_url') else 'Sem imagem disponível'                    
        #         resposta += f"Nome: {card.name}\nTipo: {card.type}\nCusto: {card.mana_cost}\n{card.artist}\n{image}\n\n"
        #     await update.message.reply_text(f"Você escolheu:\n\n{resposta}")
        # else:
        #     await update.message.reply_text("Nenhuma carta encontrada com esse nome.")
        del user_states[user_id]


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("Bot está rodando...")
    app.run_polling()


if __name__ == "__main__":
    main()
