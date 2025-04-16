import telebot
import os

# Cole o seu Token do Bot aqui!
BOT_TOKEN = '8056808033:AAFWT1jP7F-mPGOAmJBkWqXKiiWVm0asIxY'

bot = telebot.TeleBot(BOT_TOKEN)

# Dicionário para armazenar os IDs dos grupos de origem e destino
grupos = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Olá! Eu sou seu bot de repasse. Use /config para configurar os grupos.")

@bot.message_handler(commands=['config'])
def configurar_grupos(message):
    chat_id = str(message.chat.id)
    bot.send_message(chat_id, "Para configurar o repasse, envie uma mensagem no grupo de ORIGEM e depois envie o comando /origem AQUI nesta conversa privada comigo. Em seguida, envie uma mensagem no grupo de DESTINO e depois envie o comando /destino AQUI nesta conversa privada comigo.")

@bot.message_handler(commands=['origem'])
def definir_origem(message):
    chat_id = str(message.chat.id)
    if message.chat.type == 'private':
        if message.reply_to_message:
            grupo_origem_id = str(message.reply_to_message.forward_from_chat.id)
            grupos[chat_id] = grupos.get(chat_id, {})
            grupos[chat_id]['origem'] = grupo_origem_id
            bot.send_message(chat_id, f"Grupo de origem configurado com ID: {grupo_origem_id}")
        else:
            bot.send_message(chat_id, "Você precisa responder a uma mensagem encaminhada do grupo de ORIGEM para configurar.")
    else:
        bot.send_message(chat_id, "Este comando só pode ser usado em conversa privada comigo.")

@bot.message_handler(commands=['destino'])
def definir_destino(message):
    chat_id = str(message.chat.id)
    if message.chat.type == 'private':
        if message.reply_to_message:
            grupo_destino_id = str(message.reply_to_message.forward_from_chat.id)
            grupos[chat_id] = grupos.get(chat_id, {})
            grupos[chat_id]['destino'] = grupo_destino_id
            bot.send_message(chat_id, f"Grupo de destino configurado com ID: {grupo_destino_id}")
        else:
            bot.send_message(chat_id, "Você precisa responder a uma mensagem encaminhada do grupo de DESTINO para configurar.")
    else:
        bot.send_message(chat_id, "Este comando só pode ser usado em conversa privada comigo.")

@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'audio', 'document', 'sticker'])
def repassar_mensagem(message):
    if message.chat.type in ['group', 'supergroup']:
        chat_id_origem = str(message.chat.id)
        for user_id, config in grupos.items():
            if 'origem' in config and config['origem'] == chat_id_origem and 'destino' in config:
                try:
                    if message.text:
                        bot.send_message(config['destino'], message.text)
                    elif message.photo:
                        bot.send_photo(config['destino'], message.photo[-1].file_id, caption=message.caption)
                    elif message.video:
                        bot.send_video(config['destino'], message.video.file_id, caption=message.caption)
                    elif message.audio:
                        bot.send_audio(config['destino'], message.audio.file_id, caption=message.caption)
                    elif message.document:
                        bot.send_document(config['destino'], message.document.file_id, caption=message.caption)
                    elif message.sticker:
                        bot.send_sticker(config['destino'], message.sticker.file_id)
                except Exception as e:
                    print(f"Erro ao repassar para {config['destino']}: {e}")

# Para que o bot continue rodando no Heroku
if __name__ == "__main__":
    port = int(os.environ.get('PORT', '8443'))
    from telebot import apihelper
    apihelper.ENABLE_MIDDLEWARE = True
    bot.polling(none_stop=True, interval=0, listen='0.0.0.0', port=port)