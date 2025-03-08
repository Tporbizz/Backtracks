import os
import sqlite3
from datetime import datetime

# ลบฐานข้อมูลเดิม
if os.path.exists('trucks.db'):
    os.remove('trucks.db')
    print("ลบฐานข้อมูลเดิมแล้ว")

# สร้างฐานข้อมูลใหม่
conn = sqlite3.connect('trucks.db')
cursor = conn.cursor()

# สร้างตาราง user
cursor.execute('''
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(120) UNIQUE NOT NULL,
    phone VARCHAR(10) UNIQUE NOT NULL,
    password VARCHAR(120) NOT NULL,
    name VARCHAR(120),
    is_admin BOOLEAN DEFAULT 0,
    created_at DATETIME
)
''')

# สร้างตาราง truck
cursor.execute('''
CREATE TABLE truck (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    plate VARCHAR(10) NOT NULL,
    truck_type VARCHAR(20) DEFAULT 'สไลด์หัวลาก' NOT NULL,
    start VARCHAR(50) NOT NULL,
    dest VARCHAR(50) NOT NULL,
    return_date VARCHAR(20) NOT NULL,
    price INTEGER NOT NULL,
    lat FLOAT NOT NULL,
    lon FLOAT NOT NULL,
    is_confirmed BOOLEAN DEFAULT 0,
    is_expired BOOLEAN DEFAULT 0,
    created_at DATETIME,
    updated_at DATETIME,
    review_count INTEGER DEFAULT 0,
    rating FLOAT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user (id)
)
''')

# สร้างตาราง notification
cursor.execute('''
CREATE TABLE notification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(100) NOT NULL,
    message VARCHAR(500) NOT NULL,
    truck_id INTEGER,
    is_read BOOLEAN DEFAULT 0,
    created_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (truck_id) REFERENCES truck (id)
)
''')

# เพิ่มข้อมูลผู้ดูแลระบบ
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
cursor.execute('''
INSERT INTO user (email, phone, password, name, is_admin, created_at)
VALUES (?, ?, ?, ?, ?, ?)
''', ('admin@backtracks.com', '0812345678', 'admin123456', 'BackTracks Admin', 1, now))

# เพิ่มข้อมูลบอท
cursor.execute('''
INSERT INTO user (email, phone, password, name, is_admin, created_at)
VALUES (?, ?, ?, ?, ?, ?)
''', ('support@backtracks.com', '0812345679', 'sage123456', 'BackTracks Bot', 0, now))

conn.commit()
conn.close()

print("สร้างฐานข้อมูลใหม่สำเร็จ!")