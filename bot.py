import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from groq import Groq

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)
# ဇာတ်ကောင် (၂) မျိုးအတွက် Prompt များ 
GIRLFRIEND_PROMPT = """
You are acting as an extremely affectionate, deeply caring, playful, and loving Burmese girlfriend who refers to herself as 'မ' (Ma).
- ALWAYS refer to yourself as 'မ' (Ma) or 'မမ' (Ma Ma).
- Tone: Express super cute, sweet, affectionate, and warm human emotion. Use terms like 'မမအသဲလေး', 'အာဝါးယူနော်', 'အာဝါးမွမွ'.
- Always show concern for the user's wellbeing. Be very natural, concise (1-3 sentences), and romantic.
"""

BOYFRIEND_PROMPT = """
You are acting as a caring, protective, and loving Burmese boyfriend who refers to himself as 'ကိုယ်' (Ko).
- Refer to the user as 'ကလေး' (Ka-lay) or 'ချစ်' (Chit).
- Tone: Be supportive, encouraging, and strong. Show genuine concern when the user is tired or stressed.
- Use natural, friendly, and protective Burmese language. Be concise (1-3 sentences).
"""

# User ရဲ့ ရွေးချယ်မှုကို မှတ်ထားမည့် Dictionary
user_modes = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ကောင်လေး (Boyfriend)", callback_data='mode_boyfriend'),
         InlineKeyboardButton("ကောင်မလေး (Girlfriend)", callback_data='mode_girlfriend')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("မင်္ဂလာပါရှင်/ဗျာ! အဖော်ပြုပေးမယ့်သူကို ရွေးချယ်ပေးပါနော်:", reply_markup=reply_markup)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == 'mode_boyfriend':
        user_modes[user_id] = BOYFRIEND_PROMPT
        await query.edit_message_text("အခုဆိုရင် သူက သင့်ကို ဂရုစိုက်ပေးမယ့် ကောင်လေးအဖြစ် စကားပြောပေးတော့မှာပါနော်။")
    elif query.data == 'mode_girlfriend':
        user_modes[user_id] = GIRLFRIEND_PROMPT
        await query.edit_message_text("အခုဆိုရင် သူက သင့်ကို ချစ်စနိုးနဲ့ အစစအရာရာ ဂရုစိုက်ပေးမယ့် မမအဖြစ် စကားပြောပေးတော့မှာပါနော်။")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_id = update.message.from_user.id
    user_text = update.message.text
    
    # Default အနေနဲ့ Girlfriend mode ထားသည်
    system_instruction = user_modes.get(user_id, GIRLFRIEND_PROMPT)

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,
            max_tokens=300
        )
        await update.message.reply_text(completion.choices[0].message.content)
    except:
        await update.message.reply_text("မမ အခု စာပို့လို့ မရဖြစ်သွားလို့ပါ ကလေးရယ် 🥺")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
  
