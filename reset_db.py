from app import app, db
import os

# ลบฐานข้อมูลเดิม
if os.path.exists('trucks.db'):
    os.remove('trucks.db')
    print("ลบฐานข้อมูลเดิมแล้ว")

# สร้างฐานข้อมูลใหม่
with app.app_context():
    db.create_all()
    print("สร้างฐานข้อมูลใหม่แล้ว")
    
print("รีเซ็ตฐานข้อมูลสำเร็จ!")