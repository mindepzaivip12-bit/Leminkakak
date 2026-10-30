import logging
import time
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Import từ các file khác
from keep_alive import keep_alive
from algorithm import predict_hash
from database import generate_key, activate_key, check_auth

# --- CẤU HÌNH ADMIN ---
BOT_TOKEN = "8627314570:AAG8L2vxe8u-4uDGdnip8gzoW8BlDQ_bg3E"
ADMIN_ID = 8627314570
ADMIN_USERNAME = "@cskhleminh"

# Bật log
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- CÁC LỆNH CƠ BẢN ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = (
        f"👋 Chào {user_name} đến với BOT TOOL MINHLE!\n\n"
        "🤖 **Chức năng:** Nhập mã MD5 (32 ký tự) hoặc Hash (64 ký tự) để dự đoán Tài/Xỉu.\n"
        "🔥 **Thuật toán:** Phân tích chuyên sâu, cam kết không random.\n\n"
        "💳 **Bảng giá Key:**\n"
        "├ 12k / 1 Giờ\n"
        "├ 20k / 1 Ngày\n"
        "└ 36k / 3 Ngày\n\n"
        f"👉 Liên hệ Admin để mua key: {ADMIN_USERNAME}\n"
        "👉 Nhập key: `/key LC79-XXXXXX`\n\n"
        "👇 **Hãy dán MD5 hoặc Hash vào đây để bắt đầu!**"
    )
    
    keyboard = [
        [InlineKeyboardButton("💬 Liên hệ Admin mua Key", url="https://t.me/cskhleminh")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

# --- LỆNH ADMIN TẠO KEY ---
async def create_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Chỉ Admin mới có quyền tạo
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Bạn không phải Admin!")
        return
        
    try:
        args = context.args
        if not args:
            await update.message.reply_text("Cú pháp: `/taokey 1h` (1 giờ), `/taokey 1d` (1 ngày), `/taokey 3d` (3 ngày)", parse_mode='Markdown')
            return
            
        duration = args[0].lower()
        hours = 0
        if duration == '1h': hours = 1
        elif duration == '1d': hours = 24
        elif duration == '3d': hours = 72
        else:
            await update.message.reply_text("❌ Sai định dạng. Chỉ nhận 1h, 1d, 3d")
            return
            
        new_key = generate_key(hours)
        await update.message.reply_text(
            f"✅ **Đã tạo key thành công!**\n\n"
            f"🔑 Key: `{new_key}`\n"
            f"⏳ Hạn dùng: {duration}\n\n"
            f"*(Hãy gửi key này cho khách hàng)*", 
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(f"Lỗi: {e}")

# --- LỆNH NHẬP KEY ---
async def enter_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        key_input = context.args[0]
    except IndexError:
        await update.message.reply_text("Cú pháp: `/key LC79-XXXXXX`")
        return
        
    success, result = activate_key(user_id, key_input)
    
    if success:
        expire_time = datetime.fromtimestamp(result).strftime('%H:%M:%S - %d/%m/%Y')
        await update.message.reply_text(
            f"✅ **Kích hoạt Key thành công!**\n\n"
            f"⏳ Hạn sử dụng đến: `{expire_time}`\n\n"
            f"👇 Bây giờ bạn có thể dán MD5 hoặc Hash vào để dự đoán!", 
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(f"{result}")

# --- NHẬN MD5/HASH VÀ DỰ ĐOÁN ---
async def handle_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # 1. Kiểm tra xem có phải MD5/Hash không
    if len(text) not in [32, 64]:
        # Nếu không phải lệnh và không phải hash, nhắc nhở
        if not text.startswith('/'):
            await update.message.reply_text("⚠️ Vui lòng nhập chuẩn MD5 (32 ký tự) hoặc Hash (64 ký tự).")
        return
        
    # 2. Kiểm tra xem đã nhập Key chưa (Check Auth)
    is_authed, expire_time = check_auth(user_id)
    
    # Nếu là ADMIN thì auto cho qua
    if user_id == ADMIN_ID:
        is_authed = True
        
    if not is_authed:
        await update.message.reply_text(
            "🔒 **Bạn chưa có Key hoặc Key đã hết hạn!**\n\n"
            f" Vui lòng liên hệ Admin {ADMIN_USERNAME} để mua key.\n"
            "💳 Bảng giá: 12k/1h - 20k/1d - 36k/3d\n"
            "🔑 Sau khi mua, nhập: `/key LC79-XXXXXX`",
            parse_mode='Markdown'
        )
        return
        
    # 3. Xử lý thuật toán dự đoán
    ket_qua, tai_percent, xiu_percent = predict_hash(text)
    
    if ket_qua:
        # Tạo hiệu ứng chờ cho ngầu
        msg = await update.message.reply_text("⏳ Đang phân tích thuật toán...")
        time.sleep(1.5) # Đợi 1.5s tạo cảm giác đang giải mã
        
        # Format kết quả
        result_text = (
            f"🎯 **KẾT QUẢ PHÂN TÍCH THUẬT TOÁN**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔗 **Mã Hash:** `{text[:10]}...{text[-10:]}` ({len(text)} ký tự)\n\n"
            f"🔮 **Dự đoán:** **{ket_qua}**\n"
            f"📊 **Tỷ lệ:**\n"
            f"┣ TÀI: **{tai_percent}%** ❄️\n"
            f"┗ XỈU: **{xiu_percent}%** ❄️\n\n"
            f"*(Lưu ý: Kết quả dựa trên thuật toán phân tích chuỗi MD5, không sử dụng Random)*"
        )
        
        # Cập nhật lại tin nhắn đang chờ
        await msg.edit_text(result_text, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Mã không hợp lệ. Vui lòng kiểm tra lại.")

# --- HÀM MAIN KHỞI CHẠY BOT ---
def main():
    # 1. Giữ Render luôn thức
    keep_alive()
    
    # 2. Khởi tạo Bot
    application = Application.builder().token(BOT_TOKEN).build()
    
    # 3. Thêm các lệnh
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("taokey", create_key)) # Lệnh của Admin
    application.add_handler(CommandHandler("key", enter_key))     # Lệnh nhập key của User
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_hash)) # Nhận MD5/Hash
    
    # 4. Chạy Bot
    print("Bot đã khởi động thành công!")
    application.run_polling()

if __name__ == '__main__':
    main()
