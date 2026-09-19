import os
import re
import hashlib
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# ============================================================
#   MINH TOOL VIP BOT
#   Zalo hỗ trợ: 0372834763
# ============================================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "DÁN_TOKEN_BOT_VÀO_ĐÂY")
ZALO_PHONE = "0372834763"
ZALO_URL = f"https://zalo.me/{ZALO_PHONE}"
SECRET_TOKEN = os.getenv("SECRET_TOKEN", "MINH_TOOL_VIP_2026_SECRET_KEY")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ============================================================
#   THUẬT TOÁN DỰ ĐOÁN VIP
# ============================================================
def detect_hash_type(h: str):
    h = h.strip()
    if re.fullmatch(r"[a-fA-F0-9]{32}", h):
        return "MD5 (32 ký tự)"
    if re.fullmatch(r"[a-fA-F0-9]{64}", h):
        return "SHA-256 (64 ký tự)"
    return None


def hash_to_score(h: str) -> int:
    h = h.lower()
    mixed = f"{h}::{SECRET_TOKEN}".encode()
    for i in range(7):
        mixed = hashlib.sha512(mixed + str(i).encode()).digest()
    score = 0
    for i in range(0, len(mixed), 4):
        chunk = int.from_bytes(mixed[i:i+4], "big")
        score = (score * 37 + chunk) % 100
    return score


def predict(h: str) -> dict:
    htype = detect_hash_type(h)
    if not htype:
        return {"error": "❌ Sai định dạng! Cần 32 ký tự (MD5) hoặc 64 ký tự (SHA-256) hex."}
    score = hash_to_score(h)
    result = "XỈU" if score < 50 else "TÀI"
    return {
        "hash": h,
        "type": htype,
        "result": result,
        "tai": score,
        "xiu": 100 - score,
        "confidence": abs(score - 50) * 2,
    }


# ============================================================
#   KEYBOARD
# ============================================================
def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 Zalo Hỗ Trợ", url=ZALO_URL)],
        [
            InlineKeyboardButton("📘 /32kitu", callback_data="guide32"),
            InlineKeyboardButton("📗 /64kitu", callback_data="guide64"),
        ],
        [InlineKeyboardButton("ℹ️ Hướng dẫn", callback_data="help")],
    ])


# ============================================================
#   HANDLERS
# ============================================================
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = (
        "★ **MINH TOOL VIP** ★\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🎯 Dự đoán **TÀI / XỈU** từ hash 32 & 64 ký tự\n\n"
        f"📞 Zalo hỗ trợ: `{ZALO_PHONE}`\n"
        f"🔗 {ZALO_URL}\n\n"
        "**Lệnh:**\n"
        "• `/32kitu` – Hướng dẫn 32 ký tự (MD5)\n"
        "• `/64kitu` – Hướng dẫn 64 ký tự (SHA-256)\n"
        "• `/zalo` – Mở Zalo admin\n"
        "• `/help` – Trợ giúp\n\n"
        "👉 Gửi hash để dự đoán ngay!"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_keyboard())


async def cmd_zalo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📞 **Zalo hỗ trợ:** `{ZALO_PHONE}`\n🔗 {ZALO_URL}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("👉 Mở Zalo", url=ZALO_URL)]]
        ),
    )


async def cmd_32(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📘 **HƯỚNG DẪN 32 KÝ TỰ (MD5)**\n"
        "• Chuỗi đúng 32 ký tự hex (0-9, a-f)\n"
        "• Ví dụ: `d41d8cd98f00b204e9800998ecf8427e`",
        parse_mode="Markdown",
    )


async def cmd_64(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📗 **HƯỚNG DẪN 64 KÝ TỰ (SHA-256)**\n"
        "• Chuỗi đúng 64 ký tự hex (0-9, a-f)\n"
        "• Ví dụ:\n`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`",
        parse_mode="Markdown",
    )


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await start(update, ctx)


async def handle_hash(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    res = predict(text)

    if "error" in res:
        await update.message.reply_text(
            res["error"] + "\n\n👉 Gõ /32kitu hoặc /64kitu để xem hướng dẫn.",
            reply_markup=main_keyboard(),
        )
        return

    emoji = "🔴" if res["result"] == "TÀI" else "🔵"
    msg = (
        "★ **MINH TOOL VIP** ★\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔎 `{res['hash']}`\n"
        f"🧩 Loại: {res['type']}\n\n"
        f"{emoji} **KẾT QUẢ: {res['result']}**\n"
        f"📊 TÀI: `{res['tai']}%`\n"
        f"📊 XỈU: `{res['xiu']}%`\n"
        f"⚡ Tin cậy: `{res['confidence']}%`\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"📞 Zalo: `{ZALO_PHONE}`"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=main_keyboard())


async def button_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "guide32":
        await q.message.reply_text(
            "📘 **32 KÝ TỰ (MD5)**\nVí dụ: `d41d8cd98f00b204e9800998ecf8427e`",
            parse_mode="Markdown",
        )
    elif q.data == "guide64":
        await q.message.reply_text(
            "📗 **64 KÝ TỰ (SHA-256)**\nVí dụ:\n`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`",
            parse_mode="Markdown",
        )
    elif q.data == "help":
        await q.message.reply_text(
            "Gửi hash 32 hoặc 64 ký tự để dự đoán.\nGõ /zalo để liên hệ admin.",
        )


# ============================================================
#   MAIN
# ============================================================
def main():
    if BOT_TOKEN == "DÁN_TOKEN_BOT_VÀO_ĐÂY":
        raise SystemExit("⚠️ Chưa cấu hình BOT_TOKEN!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("zalo", cmd_zalo))
    app.add_handler(CommandHandler("32kitu", cmd_32))
    app.add_handler(CommandHandler("64kitu", cmd_64))
    app.add_handler(CallbackQueryHandler(button_cb))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_hash))

    logger.info("🚀 MINH TOOL VIP BOT đang chạy...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
