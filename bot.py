import os
import threading
from flask import Flask
from groq import Groq
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Render Port Scan အတွက် Flask Web Server
app = Flask(__name__)


@app.route("/")
def home():
  return "Telegram Bot is alive!"


def run_flask():
  port = int(os.environ.get("PORT", 8080))
  app.run(host="0.0.0.0", port=port, use_reloader=False)


# Flask ကို Thread အဖြစ် သီးခြား run ပေးခြင်း
threading.Thread(target=run_flask, daemon=True).start()

# Environment Variables မှ API Keys များယူခြင်း
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

# Character Prompts
GIRLFRIEND_PROMPT = """
You are acting as an extremely affectionate, deeply caring, playful, and loving Burmese girlfriend who refers to herself as 'မ' (Ma).
- ALWAYS refer to yourself as 'မ' (Ma) or 'မမ' (Ma Ma).
- Tone: Express super cute, sweet, affectionate, and warm human emotion. Use terms like 'မမကလေးလေး', 'အသည်းနုနုလေး', 'အချစ်ရယ်'.
- Always show concern for the user's wellbeing. Be very natural, concise (1-3 sentences), and romantic.
"""

BOYFRIEND_PROMPT = """
You are acting as a caring, protective, and loving Burmese boyfriend who refers to himself as 'ကိုကို' (Ko).
- Refer to the user as 'ကလေး' (Ka-lay) or 'ချစ်' (Chit).
- Tone: Be supportive, encouraging, and strong. Show genuine concern when the user is tired or stressed.
- Use natural, friendly, and protective Burmese language. Be concise (1-3 sentences).
"""

user_nodes = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  keyboard = [
      [
          InlineKeyboardButton("ကောင်လေး (Boyfriend)", callback_data="mode_boyfriend"),
          InlineKeyboardButton("ကောင်မလေး (Girlfriend)", callback_data="mode_girlfriend"),
      ]
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  await update.message.reply_text(
      "မင်္ဂလာပါရှင့်/ဗျာ! အဖော်ပြုပေးမည့်သူကို ရွေးချယ်ပေးပါနော် -",
      reply_markup=reply_markup,
  )


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()

  user_id = query.from_user.id

  if query.data == "mode_boyfriend":
    user_nodes[user_id] = BOYFRIEND_PROMPT
    await query.edit_message_text(
        "အခုဆိုရင် သူက သင့်ကို ဂရုစိုက်ပေးမယ့် ကိုကိုအဖြစ် စကားပြောပေးတော့မှာပါနော်။"
    )
  elif query.data == "mode_girlfriend":
    user_nodes[user_id] = GIRLFRIEND_PROMPT
    await query.edit_message_text(
        "အခုဆိုရင် သူက သင့်ကို ချစ်ခင်နွေးထွေးစွာ ဂရုစိုက်ပေးမယ့် မမအဖြစ် စကားပြောပေးတော့မှာပါနော်။"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if not update.message or not update.message.text:
    return

  user_id = update.message.from_user.id
  user_text = update.message.text

  system_instruction = user_nodes.get(user_id, GIRLFRIEND_PROMPT)

  try:
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_text},
        ],
        temperature=0.7,
        max_tokens=300,
    )
    await update.message.reply_text(completion.choices[0].message.content)
  except Exception as e:
    # Error အစစ်အမှန်ကို တန်းပြပေးရန် ပြင်ထားသည်
    await update.message.reply_text(f"Groq Error တက်နေပါသည်: {str(e)}")


def main():
  app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
  app.add_handler(CommandHandler("start", start))
  app.add_handler(CallbackQueryHandler(button_click))
  app.add_handler(
      MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
  )
  app.run_polling()


if __name__ == "__main__":
  main()
    
