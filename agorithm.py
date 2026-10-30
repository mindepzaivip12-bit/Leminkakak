import hashlib

def predict_hash(hash_str):
    # Kiểm tra độ dài hợp lệ
    if len(hash_str) not in [32, 64]:
        return None, None, None
        
    # Thuật toán phân tích Hash (Không dùng Random)
    # Sử dụng chính mã hash để băm ra 1 kết quả cố định
    h = hashlib.sha256(hash_str.encode()).hexdigest()
    num = int(h[:8], 16) # Lấy 8 ký tự đầu chuyển thành số
    
    # Tính phần trăm
    val = num % 100
    if val == 0: val = 1
    if val == 100: val = 99

    if val >= 50:
        ket_qua = "TÀI"
        tai_percent = 50 + ((val - 50) * 0.9) # Kéo dãn % cho đẹp
        xiu_percent = 100 - tai_percent
    else:
        ket_qua = "XỈU"
        xiu_percent = 50 + ((50 - val) * 0.9)
        tai_percent = 100 - xiu_percent
        
    return ket_qua, round(tai_percent, 2), round(xiu_percent, 2)
