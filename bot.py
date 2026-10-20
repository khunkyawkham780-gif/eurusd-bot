import logging
import yfinance as yf
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ *EUR/USD Real-Market AI Bot* မှ ကြိုဆိုပါတယ်ဗျာ!\n\n"
        "Yahoo Finance မှ တကယ့် Live Data ဖြင့် Signal ရယူရန် /signal ဟု ရိုက်ပါ၊",
        parse_mode="Markdown"
    )

# Yahoo Finance မှ တကယ့် Data အစစ်အမှန်ကို ယူ၍ တွက်ချက်ခြင်း
async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer("Yahoo Finance မှ တကယ့် Market Data ကို ဆွဲထုတ်နေပါသည်...")

    try:
        # EUR/USD (EURUSD=X) ၏ တကယ့် Live Data များကို တိုက်ရိုက်ဆွဲထုတ်ခြင်း
        data = yf.download(tickers="EURUSD=X", period="5d", interval="1m", progress=False)
        
        if data.empty:
            raise Exception("Data မရှိသေးပါ။")

        current_price = float(data['Close'].iloc[-1])
        prev_price = float(data['Close'].iloc[-2])

        # RSI Indicator တွက်ချက်ခြင်း
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = float(rsi.iloc[-1])

        # Moving Average (MA) တွက်ချက်ခြင်း
        ma_50 = data['Close'].rolling(window=50).mean().iloc[-1]

        # Trend ဆုံးဖြတ်ချက်
        if current_rsi < 45 and current_price > ma_50:
            chosen_dir = "🟢 CALL (BUY) - Oversold Zone"
        elif current_rsi > 55 and current_price < ma_50:
            chosen_dir = "🔴 PUT (SELL) - Overbought Zone"
        else:
            chosen_dir = "🟢 CALL (BUY)" if current_price >= prev_price else "🔴 PUT (SELL)"

        signal_text = (
            f"📈 **REAL MARKET EUR/USD SIGNAL** 📈\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"💱 **Asset:** `EUR/USD` (Yahoo Finance Live)\n"
            f"💲 **Live Price:** `{current_price:.5f}`\n"
            f"📊 **RSI (14):** `{current_rsi:.2f}`\n"
            f"📉 **MA (50):** `{ma_50:.5f}`\n"
            f"⏱ **Expiry Time:** `5 Seconds / 1 Min`\n"
            f"🎯 **Prediction:** **{chosen_dir}**\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ *တကယ့် Live Market Data အစစ်အမှန်ဖြင့် တွက်ချက်ထားပါသည်။*"
        )

    except Exception as e:
        signal_text = (
            f"⏳ **Market Data ကို ချိတ်ဆက်နေဆဲဖြစ်ပါသည်...**\n\n"
            f"အသေးစိတ် Error: `{str(e)}`\n\n"
            f"ခဏစောင့်ပြီး ခလုတ်ကို (သို့မဟုတ်) /signal ကို ထပ်မံကြိုးစားပေးပါ။"
        )

    keyboard = [
        [InlineKeyboardButton("🔄 Get Next Real Signal", callback_data="get_real_signal")],
        [InlineKeyboardButton("🌐 Pocket Option", url="https://pocketoption.com")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(signal_text, parse_mode="Markdown", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text=signal_text, parse_mode="Markdown", reply_markup=reply_markup)

if __name__ == '__main__':
    TOKEN = "8925749724:AAGDqKUUZ396lcZds9GVUxMXKSZpZhkjD_A"
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('signal', signal))
    application.add_handler(CallbackQueryHandler(signal, pattern="get_real_signal"))

    print("Real-Data Signal Bot အလုပ်လုပ်နေပါပြီ...")
    application.
run_polling()
