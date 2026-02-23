import os
import asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- APNA TOKEN YAHAN DALEIN ---
TOKEN = '8680749656:AAGnUw4wryTeZY9lytEnWy3BDVkGgV2I80I'

user_data = {}

# --- MAIN KEYBOARD MENU (Keyboard ki jagah dikhega) ---
def main_menu_keyboard():
    keyboard = [
        [KeyboardButton("📂 Merge Numbers (1:1)"), KeyboardButton("➕ Add Plus (+) Mode")],
        [KeyboardButton("📊 Statistics"), KeyboardButton("👨‍💻 Developer")]
    ]
    # resize_keyboard=True se buttons keyboard ke size ke hisab se set ho jayenge
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- START COMMAND ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    text = (
        f"🌟 **Hello {user_name}!**\n\n"
        "Niche diye gaye keyboard buttons ka use karein apna kaam select karne ke liye:"
    )
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=main_menu_keyboard())

# --- MESSAGE HANDLER (Buttons click handle karne ke liye) ---
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    msg_text = update.message.text

    if msg_text == "📂 Merge Numbers (1:1)":
        user_data[user_id] = {'mode': 'merge', 'files': []}
        await update.message.reply_text("📂 **Mode: Split/Merge (1:1)** Active.\n\nAb pehli `.txt` file bhejein.", reply_markup=main_menu_keyboard())
    
    elif msg_text == "➕ Add Plus (+) Mode":
        user_data[user_id] = {'mode': 'plus'}
        await update.message.reply_text("➕ **Mode: Add Plus (+)** Active.\n\nAb `.txt` file bhejein, main sabke aage + laga dunga.", reply_markup=main_menu_keyboard())
    
    elif msg_text == "📊 Statistics":
        await update.message.reply_text("📊 **Bot Status:** Online 🟢\n🚀 **Speed:** Premium Fast\n✨ **Dev:** @ngxgod1")
    
    elif msg_text == "👨‍💻 Developer":
        await update.message.reply_text("👨‍💻 **Developer Contact:**\n\nUsername: @ngxgod1\n\nClick karke message karein!", parse_mode='Markdown')

# --- DOCUMENT HANDLING ---
async def handle_docs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    doc = update.message.document

    if user_id not in user_data:
        await update.message.reply_text("❌ Pehle niche buttons se mode select karein!", reply_markup=main_menu_keyboard())
        return

    if not doc.file_name.endswith('.txt'):
        await update.message.reply_text("❌ Error: Sirf `.txt` file bhejein.")
        return

    mode = user_data[user_id].get('mode')
    file = await doc.get_file()

    # --- MERGE LOGIC ---
    if mode == 'merge':
        path = f"f_{len(user_data[user_id]['files'])}_{user_id}.txt"
        await file.download_to_drive(path)
        user_data[user_id]['files'].append(path)

        if len(user_data[user_id]['files']) == 1:
            await update.message.reply_text("✅ Pehli file mil gayi! Ab **dusri file** bhejिये.")
        else:
            status = await update.message.reply_text("⚙️ **Processing...**\n`[▓▓▓▓▓▓▓▓░░]`")
            f1, f2 = user_data[user_id]['files']
            out_path = f"Merged_{user_id}.txt"

            with open(f1, 'r') as file1, open(f2, 'r') as file2, open(out_path, 'w') as out:
                for l1, l2 in zip(file1, file2):
                    out.write(f"{l1.strip()}\n{l2.strip()}\n")

            await status.delete()
            await update.message.reply_document(document=open(out_path, 'rb'), filename="Merged_List.txt", caption="💎 **Merge Done!**")
            
            for p in [f1, f2, out_path]: 
                if os.path.exists(p): os.remove(p)
            user_data.pop(user_id)

    # --- PLUS (+) LOGIC ---
    elif mode == 'plus':
        status = await update.message.reply_text("⚡ **Adding Plus (+)...**")
        in_p = f"plus_in_{user_id}.txt"
        out_p = f"plus_out_{user_id}.txt"
        await file.download_to_drive(in_p)

        with open(in_p, 'r') as fin, open(out_p, 'w') as fout:
            for line in fin:
                num = line.strip()
                if num:
                    fout.write(f"+{num}\n" if not num.startswith('+') else f"{num}\n")

        await status.delete()
        await update.message.reply_document(document=open(out_p, 'rb'), filename="Plus_Added.txt", caption="➕ **Added Plus!**")
        
        for p in [in_p, out_p]:
            if os.path.exists(p): os.remove(p)
        user_data.pop(user_id)

def main():
    print("🚀 Keyboard Button Bot Running...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_docs))
    
    app.run_polling()

if __name__ == '__main__':
    main()
