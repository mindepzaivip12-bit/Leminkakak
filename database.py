import time
import random
import string

# Lưu trữ tạm thời trên RAM
VALID_KEYS = {} # key: {time_expired: timestamp}
AUTHORIZED_USERS = {} # user_id: timestamp_het_han

def generate_key(duration_hours):
    # Tạo key dạng LC79-XXXXXX
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    key = f"LC79-{random_str}"
    
    # Thời gian hết hạn
    expire_time = time.time() + (duration_hours * 3600)
    VALID_KEYS[key] = expire_time
    return key

def activate_key(user_id, key):
    key = key.upper().strip()
    if key not in VALID_KEYS:
        return False, "❌ Key không tồn tại!"
        
    expire_time = VALID_KEYS[key]
    if time.time() > expire_time:
        return False, "❌ Key đã hết hạn!"
        
    # Kích hoạt cho user
    AUTHORIZED_USERS[user_id] = expire_time
    
    # Xóa key sau khi dùng (1 key dùng 1 lần)
    del VALID_KEYS[key] 
    
    return True, expire_time

def check_auth(user_id):
    if user_id not in AUTHORIZED_USERS:
        return False, 0
    expire_time = AUTHORIZED_USERS[user_id]
    if time.time() > expire_time:
        del AUTHORIZED_USERS[user_id]
        return False, 0
    return True, expire_time
