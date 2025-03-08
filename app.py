from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, DateField, BooleanField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional
import math
from datetime import datetime, timedelta
import random
import os
from functools import wraps

app = Flask(__name__)
app.static_folder = 'static'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///backtracks_new.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sage-backtracks-2025'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ข้อมูลจังหวัดทั้งหมดของประเทศไทย
provinces = {
    "กรุงเทพมหานคร": (13.75, 100.50), "เชียงใหม่": (18.79, 98.98), "เชียงราย": (19.91, 99.83),
    "ขอนแก่น": (16.44, 102.83), "อุดรธานี": (17.41, 102.80), "นครราชสีมา": (14.98, 102.10),
    "สงขลา": (7.19, 100.59), "สุราษฎร์ธานี": (9.14, 99.32), "ภูเก็ต": (7.89, 98.39),
    "พิษณุโลก": (16.82, 100.26), "นครสวรรค์": (15.70, 100.12), "กระบี่": (8.09, 98.91),
    "กาญจนบุรี": (14.02, 99.53), "กาฬสินธุ์": (16.43, 103.50), "กำแพงเพชร": (16.47, 99.52),
    "จันทบุรี": (12.61, 102.10), "ฉะเชิงเทรา": (13.69, 101.07), "ชลบุรี": (13.36, 100.99),
    "ชัยนาท": (15.19, 100.12), "ชัยภูมิ": (15.80, 102.03), "ชุมพร": (10.49, 99.18),
    "ตรัง": (7.57, 99.61), "ตราด": (12.24, 102.51), "ตาก": (16.88, 99.13), "นครนายก": (14.21, 101.21),
    "นครปฐม": (13.82, 100.04), "นครพนม": (17.39, 104.77), "นครศรีธรรมราช": (8.43, 99.97),
    "นนทบุรี": (13.86, 100.51), "นราธิวาส": (6.42, 101.82), "น่าน": (18.78, 100.77), "บึงกาฬ": (18.34, 103.63),
    "บุรีรัมย์": (14.99, 103.10), "ปทุมธานี": (14.01, 100.53), "ประจวบคีรีขันธ์": (11.82, 99.79),
    "ปราจีนบุรี": (14.05, 101.37), "ปัตตานี": (6.87, 101.25), "พะเยา": (19.15, 99.89),
    "พังงา": (8.45, 98.53), "พัทลุง": (7.62, 100.07), "พิจิตร": (16.44, 100.35),
    "เพชรบุรี": (13.11, 99.94), "เพชรบูรณ์": (16.44, 101.15), "แพร่": (18.14, 100.14),
    "มหาสารคาม": (16.19, 103.30), "มุกดาหาร": (16.54, 104.72), "แม่ฮ่องสอน": (19.30, 97.96),
    "ยโสธร": (15.79, 104.15), "ร้อยเอ็ด": (16.05, 103.65), "ระนอง": (9.96, 98.63), "ระยอง": (12.68, 101.28),
    "ราชบุรี": (13.53, 99.82), "ลพบุรี": (14.80, 100.65), "ลำปาง": (18.29, 99.50),
    "ลำพูน": (18.58, 99.01), "เลย": (17.49, 101.72), "ศรีสะเกษ": (15.12, 104.33),
    "สกลนคร": (17.15, 104.15), "สตูล": (6.63, 100.07), "สมุทรปราการ": (13.60, 100.60),
    "สมุทรสงคราม": (13.41, 100.00), "สมุทรสาคร": (13.55, 100.28), "สระบุรี": (14.53, 100.92),
    "สระแก้ว": (13.82, 102.08), "สิงห์บุรี": (14.89, 100.40), "สุโขทัย": (17.01, 99.82),
    "สุพรรณบุรี": (14.47, 100.12), "หนองคาย": (17.88, 102.74), "หนองบัวลำภู": (17.20, 102.44),
    "อ่างทอง": (14.59, 100.45), "อำนาจเจริญ": (15.80, 104.63), "อุตรดิตถ์": (17.62, 100.10),
    "อุทัยธานี": (15.38, 100.02), "อุบลราชธานี": (15.23, 104.86)
}
bangkok_zones = {
    "เขตพระนคร": (13.7520, 100.4940),
    "เขตดุสิต": (13.7700, 100.5090),
    "เขตหนองจอก": (13.8560, 100.8530),
    "เขตบางรัก": (13.7270, 100.5270),
    "เขตบางเขน": (13.8360, 100.6100),
    "เขตบางกะปิ": (13.7630, 100.6380),
    "เขตปทุมวัน": (13.7450, 100.5340),
    "เขตป้อมปราบศัตรูพ่าย": (13.7520, 100.5090),
    "เขตพระโขนง": (13.7020, 100.6010),
    "เขตมีนบุรี": (13.8110, 100.7310),
    "เขตลาดกระบัง": (13.7280, 100.7780),
    "เขตยานนาวา": (13.6950, 100.5450),
    "เขตสัมพันธวงศ์": (13.7370, 100.5140),
    "เขตพญาไท": (13.7560, 100.5380),
    "เขตธนบุรี": (13.7190, 100.4840),
    "เขตบางกอกใหญ่": (13.7240, 100.4760),
    "เขตห้วยขวาง": (13.7690, 100.5810),
    "เขตคลองสาน": (13.7230, 100.5050),
    "เขตตลิ่งชัน": (13.7890, 100.4340),
    "เขตบางกอกน้อย": (13.7610, 100.4720),
    "เขตบางขุนเทียน": (13.6360, 100.4410),
    "เขตภาษีเจริญ": (13.7150, 100.4390),
    "เขตหนองแขม": (13.6823, 100.3553),
    "เขตราษฎร์บูรณะ": (13.6790, 100.5140),
    "เขตบางพลัด": (13.7860, 100.4840),
    "เขตดินแดง": (13.7580, 100.5550),
    "เขตบึงกุ่ม": (13.8040, 100.6450),
    "เขตสาทร": (13.7140, 100.5340),
    "เขตบางซื่อ": (13.8150, 100.5260),
    "เขตจตุจักร": (13.8217, 100.5413),
    "เขตบางคอแหลม": (13.6940, 100.5140),
    "เขตประเวศ": (13.7130, 100.6970),
    "เขตคลองเตย": (13.7100, 100.5840),
    "เขตสวนหลวง": (13.7380, 100.6450),
    "เขตจอมทอง": (13.6810, 100.4600),
    "เขตดอนเมือง": (13.9115, 100.5835),
    "เขตราชเทวี": (13.7537, 100.5354),
    "เขตลาดพร้าว": (13.8260, 100.5970),
    "เขตวัฒนา": (13.7200, 100.5680),
    "เขตบางแค": (13.7130, 100.4050),
    "เขตหลักสี่": (13.8746, 100.5675),
    "เขตสายไหม": (13.8980, 100.6560),
    "เขตคันนายาว": (13.8300, 100.6790),
    "เขตสะพานสูง": (13.7620, 100.6920),
    "เขตวังทองหลาง": (13.7800, 100.6090),
    "เขตคลองสามวา": (13.8810, 100.7380),
    "เขตบางนา": (13.6670, 100.6040),
    "เขตทวีวัฒนา": (13.7770, 100.3730),
    "เขตทุ่งครุ": (13.6447, 100.5070),
    "เขตบางบอน": (13.6824, 100.3965)
}

# เพิ่มเขตในกรุงเทพฯ เข้าไปในข้อมูลจังหวัด
provinces.update(bangkok_zones)

# โมเดลฐานข้อมูล
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(10), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    trucks = db.relationship('Truck', backref='user', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

class Truck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plate = db.Column(db.String(10), nullable=False)
    truck_type = db.Column(db.String(20), default="สไลด์หัวลาก", nullable=False)
    start = db.Column(db.String(50), nullable=False)
    dest = db.Column(db.String(50), nullable=False)
    return_date = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False)
    is_expired = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    review_count = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    truck_id = db.Column(db.Integer, db.ForeignKey('truck.id'), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    user = db.relationship('User', backref='notifications')
    truck = db.relationship('Truck', backref='notifications')

    

# ฟังก์ชันคำนวณระยะทาง
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# ตรวจสอบว่าเป็นพื้นที่กรุงเทพฯ หรือไม่
def is_bangkok_area(location):
    return location == "กรุงเทพมหานคร" or location.startswith("เขต")

# ฟังก์ชันคำนวณราคา
def calculate_price_with_location(start, dest, distance):
    # อัตราค่าขนส่งภายในกรุงเทพฯ: 25 บาท/กม.
    # อัตราค่าขนส่งจังหวัดอื่น: 12 บาท/กม.
    
    is_bkk_start = is_bangkok_area(start)
    is_bkk_dest = is_bangkok_area(dest)
    
    # ถ้าทั้งต้นทางและปลายทางอยู่ในกรุงเทพฯ
    if is_bkk_start and is_bkk_dest:
        rate = 25
        price = int(distance * rate)
    # ถ้ามีจุดหนึ่งอยู่ในกรุงเทพฯ
    elif is_bkk_start or is_bkk_dest:
        # คำนวณส่วนที่อยู่ในกรุงเทพฯ 25 บาท/กม. และส่วนที่อยู่นอกกรุงเทพฯ 12 บาท/กม.
        # ประมาณการว่า 20% ของระยะทางอยู่ในเขตกรุงเทพฯ
        bkk_distance = distance * 0.2
        other_distance = distance * 0.8
        price = int((bkk_distance * 25) + (other_distance * 12))
    else:
        rate = 12
        price = int(distance * rate)
    
    # ปัดเป็นหลัก 500
    price = (price // 500) * 500 if price % 500 < 250 else ((price // 500) + 1) * 500
    
    # ป้องกันราคาเป็น 0
    if price <= 0:
        price = 500
        
    return price

# ฟังก์ชันแปลงวันที่เป็นรูปแบบภาษาไทย
def format_thai_date(date_str):
    thai_months = {
        1: "มกราคม", 2: "กุมภาพันธ์", 3: "มีนาคม", 4: "เมษายน", 5: "พฤษภาคม", 6: "มิถุนายน",
        7: "กรกฎาคม", 8: "สิงหาคม", 9: "กันยายน", 10: "ตุลาคม", 11: "พฤศจิกายน", 12: "ธันวาคม"
    }
    
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{date_obj.day} {thai_months[date_obj.month]}"

# เพิ่ม filter สำหรับใช้ในไฟล์ template
@app.template_filter('thai_date')
def thai_date_filter(date_str):
    return format_thai_date(date_str)
# เพิ่ม filter สำหรับตรวจสอบพื้นที่กรุงเทพฯ
@app.template_filter('is_bangkok_area')
def is_bangkok_area_filter(location):
    return is_bangkok_area(location)
# ฟังก์ชันตรวจสอบงานใหม่ (ไม่เกิน 1 วัน)
def is_new_job(return_date):
    try:
        return_date_obj = datetime.strptime(return_date, "%Y-%m-%d")
        now = datetime.now()
        days_diff = (return_date_obj - now).days
        
        # เป็นงานใหม่ถ้าวันที่ว่างอยู่ภายใน 24 ชั่วโมง หรือเป็นวันนี้หรือพรุ่งนี้
        return 0 <= days_diff <= 1
    except:
        return False

# ฟังก์ชันตรวจสอบงานหมดอายุ
def is_expired_job(return_date):
    return_date_obj = datetime.strptime(return_date, "%Y-%m-%d")
    now = datetime.now()
    return (return_date_obj - now).days < 0

# ฟังก์ชัน admin required
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# สร้างป้ายทะเบียนรถแบบสุ่ม
def generate_random_plate():
    province = random.choice(['ก', 'ข', 'ค', 'ง', 'จ', 'ช', 'ซ', 'ญ', 'ฎ', 'ฐ'])
    number = f"{random.randint(1, 9999):04d}"
    return f"{province}{number}"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# แบบฟอร์ม
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('รหัสผ่าน', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('เข้าสู่ระบบ')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = IntegerField('หมายเลขโทรศัพท์ (10 หลัก)', validators=[DataRequired(), NumberRange(min=100000000, max=9999999999)])
    name = StringField('ชื่อคนขับ', validators=[DataRequired()])
    password = PasswordField('รหัสผ่าน', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('สมัครสมาชิก')

class TruckForm(FlaskForm):
    plate = StringField('ป้ายทะเบียน', validators=[DataRequired(), Length(max=10)])
    truck_type = SelectField('ประเภทรถ', choices=[
        ('สไลด์หัวลาก', 'สไลด์หัวลาก'), 
        ('สไลด์กระบะ', 'สไลด์กระบะ'), 
        ('สไลด์ 2 ชั้น', 'สไลด์ 2 ชั้น')
    ], validators=[DataRequired()])
    start = SelectField('จุดเริ่มต้น', choices=[(p, p) for p in provinces.keys()], validators=[DataRequired()])
    dest = SelectField('จุดหมายปลายทาง', choices=[(p, p) for p in provinces.keys()], validators=[DataRequired()])
    return_date = DateField('วันที่ว่างกลับ', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('ลงทะเบียนรับงาน')

class SearchForm(FlaskForm):
    start_province = SelectField('จังหวัดปลายทาง', choices=[('', 'เลือกจังหวัด')] + [(p, p) for p in provinces.keys()])
    submit = SubmitField('ค้นหา')

class AdminUserEditForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('หมายเลขโทรศัพท์', validators=[DataRequired(), Length(min=10, max=10)])
    name = StringField('ชื่อผู้ใช้', validators=[DataRequired()])
    is_admin = BooleanField('เป็นแอดมิน')
    submit = SubmitField('บันทึกข้อมูล')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('รหัสผ่านปัจจุบัน', validators=[DataRequired(), Length(min=6)])
    new_password = PasswordField('รหัสผ่านใหม่', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('ยืนยันรหัสผ่านใหม่', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('เปลี่ยนรหัสผ่าน')

# สร้างและอัพเกรดฐานข้อมูล
with app.app_context():
    db.create_all()
    print("สร้างฐานข้อมูลสำเร็จ!")
    
    db_exists = os.path.exists('backtracks_new.db')
    
    if db_exists:
        try:
            User.query.first()
        except Exception as e:
            if "no such column: user.is_admin" in str(e):
                print("พบปัญหาโครงสร้างฐานข้อมูล กำลังสร้างใหม่...")
                os.remove('backtracks_new.db')
                db_exists = False
    
    db.create_all()
    
    admin = User.query.filter_by(email="admin@backtracks.com").first()
    if not admin:
        admin_user = User(email="admin@backtracks.com", phone="0812345678", 
                         name="BackTracks Admin", password="admin123456", is_admin=True)
        db.session.add(admin_user)
        db.session.commit()
        print("เพิ่มผู้ดูแลระบบแล้ว")

# ลบข้อมูล bot
def remove_bot_data():
    with app.app_context():
        try:
            db.session.execute("DELETE FROM notification WHERE user_id = (SELECT id FROM user WHERE email = 'support@backtracks.com')")
            db.session.execute("DELETE FROM truck WHERE user_id = (SELECT id FROM user WHERE email = 'support@backtracks.com')")
            db.session.execute("DELETE FROM user WHERE email = 'support@backtracks.com'")
            db.session.commit()
            print("ลบข้อมูล bot สำเร็จ")
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการลบข้อมูล bot: {e}")
            db.session.rollback()

# ตรวจสอบและสร้างการแจ้งเตือนสำหรับรถที่หมดอายุ
def check_expired_trucks():
    trucks = Truck.query.filter_by(is_confirmed=False, is_expired=False).all()
    now = datetime.now()
    
    for truck in trucks:
        return_date_obj = datetime.strptime(truck.return_date, "%Y-%m-%d")
        days_until_expiry = (return_date_obj - now).days
        
        if days_until_expiry < 0:
            truck.is_expired = True
            
            notification = Notification(
                user_id=truck.user_id,
                title="รถของคุณหมดเวลาประกาศแล้ว",
                message=f"รถทะเบียน {truck.plate} เส้นทาง {truck.start} → {truck.dest} หมดเวลาประกาศแล้ว คุณต้องการขยายเวลาหรือลบประกาศนี้?",
                truck_id=truck.id
            )
            db.session.add(notification)
        
        elif days_until_expiry == 1:
            existing_notification = Notification.query.filter_by(
                truck_id=truck.id, 
                title="รถของคุณใกล้หมดเวลาประกาศ", 
                is_read=False
            ).first()
            
            if not existing_notification:
                notification = Notification(
                    user_id=truck.user_id,
                    title="รถของคุณใกล้หมดเวลาประกาศ",
                    message=f"รถทะเบียน {truck.plate} เส้นทาง {truck.start} → {truck.dest} จะหมดเวลาประกาศในวันพรุ่งนี้ คุณต้องการขยายเวลาหรือไม่?",
                    truck_id=truck.id
                )
                db.session.add(notification)
    
    db.session.commit()

# เส้นทางหน้าแรก (หน้า login)
@app.route("/", methods=["GET", "POST"])
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
        
    form = LoginForm()
    contact_phone = "08-123-45678"

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data, password=form.password.data).first()
        if user:
            login_user(user)
            flash("เข้าสู่ระบบสำเร็จ!", "success")
            
            if user.is_admin:
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("dashboard"))
        flash("อีเมลหรือรหัสผ่านไม่ถูกต้อง", "error")
    
    return render_template("login.html", form=form, contact_phone=contact_phone)

# เส้นทางสมัครสมาชิก
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
        
    register_form = RegisterForm()
    contact_phone = "08-123-45678"

    if register_form.validate_on_submit():
        email = register_form.email.data
        phone = str(register_form.phone.data)
        name = register_form.name.data
        password = register_form.password.data
        
        if User.query.filter_by(email=email).first() or User.query.filter_by(phone=phone).first():
            flash("อีเมลหรือหมายเลขโทรศัพท์นี้มีผู้ใช้แล้ว", "error")
        else:
            user = User(email=email, phone=phone, name=name, password=password)
            db.session.add(user)
            db.session.commit()
            flash("สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ", "success")
            return redirect(url_for("login"))

    return render_template("register.html", register_form=register_form, contact_phone=contact_phone)

# เส้นทางล็อกอิน
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
        
    form = LoginForm()
    contact_phone = "08-123-45678"
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data, password=form.password.data).first()
        if user:
            login_user(user)
            flash("เข้าสู่ระบบสำเร็จ!", "success")
            
            if user.is_admin:
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("dashboard"))
        flash("อีเมลหรือรหัสผ่านไม่ถูกต้อง", "error")
    
    return render_template("login.html", form=form, contact_phone=contact_phone)

# เส้นทางแดชบอร์ด (หลัง login)
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    # ตรวจสอบรถที่หมดอายุและสร้างการแจ้งเตือน
    check_expired_trucks()
    
    # ดึงข้อมูลรถทั้งหมด (เฉพาะที่ยังไม่หมดอายุและยังไม่ถูกยืนยัน)
    trucks = Truck.query.filter_by(is_confirmed=False, is_expired=False).order_by(Truck.id.desc()).all() or []
    truck_form = TruckForm()
    contact_phone = "08-123-45678"

    # ตรวจสอบการแจ้งเตือนที่ยังไม่ได้อ่าน
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).all()
    unread_count = len(notifications)

    # หากมีการส่งฟอร์มลงทะเบียนรถ
    if request.method == "POST" and "truck_submit" in request.form:
        if truck_form.validate_on_submit():
            plate = truck_form.plate.data
            truck_type = truck_form.truck_type.data
            start = truck_form.start.data
            dest = truck_form.dest.data
            return_date = truck_form.return_date.data.strftime("%Y-%m-%d")
            
            # ตรวจสอบว่ามีการเลือกเขตใน กทม. หรือไม่
            actual_start = request.form.get('actual_start', start)
            actual_dest = request.form.get('actual_dest', dest)
            
            # ใช้เขตถ้ามีการเลือก
            if actual_start and start == 'กรุงเทพมหานคร':
                start = actual_start
            if actual_dest and dest == 'กรุงเทพมหานคร':
                dest = actual_dest
            
            # ดึงข้อมูลพิกัดจากจุดเริ่มต้นและปลายทาง
            if start in provinces:
                lat, lon = provinces[start]
            else:
                lat, lon = provinces["กรุงเทพมหานคร"]
                
            if dest in provinces:
                dest_lat, dest_lon = provinces[dest]
            else:
                dest_lat, dest_lon = provinces["กรุงเทพมหานคร"]
                
            # คำนวณระยะทาง
            distance = calculate_distance(lat, lon, dest_lat, dest_lon)
            
            # คำนวณราคาตามโซน
            price = calculate_price_with_location(start, dest, distance)
            
            truck = Truck(
                user_id=current_user.id, 
                plate=plate, 
                truck_type=truck_type,
                start=start, 
                dest=dest,
                return_date=return_date, 
                price=price, 
                lat=lat, 
                lon=lon, 
                is_confirmed=False
            )
            db.session.add(truck)
            db.session.commit()
            flash("ลงข้อมูลรถสำเร็จ!", "success")
            return redirect(url_for("dashboard"))

    # ตรวจสอบสถานะ "งานใหม่" สำหรับแต่ละรถ
    for truck in trucks:
        truck.is_new = is_new_job(truck.return_date)

    return render_template(
        "dashboard.html", 
        truck_form=truck_form, 
        trucks=trucks, 
        provinces=provinces, 
        contact_phone=contact_phone,
        notifications=notifications,
        unread_count=unread_count
    )

@app.route("/truck/<int:truck_id>/partial")
def truck_detail_partial(truck_id):
    truck = Truck.query.get_or_404(truck_id)
    
    # คำนวณระยะทางและเวลาเดินทาง
    if truck.start in provinces:
        start_lat, start_lon = provinces[truck.start]
    else:
        start_lat, start_lon = provinces["กรุงเทพมหานคร"]
        
    if truck.dest in provinces:
        dest_lat, dest_lon = provinces[truck.dest]
    else:
        dest_lat, dest_lon = provinces["กรุงเทพมหานคร"]
        
    distance = calculate_distance(start_lat, start_lon, dest_lat, dest_lon)
    travel_time_hours = distance / 60
    hours = int(travel_time_hours)
    minutes = int((travel_time_hours - hours) * 60)
    
    return render_template(
        "truck_detail_partial.html", 
        truck=truck, 
        distance=round(distance, 2),
        travel_time=f"{hours} ชั่วโมง {minutes} นาที",
        provinces=provinces
    )

# เส้นทางสำหรับค้นหา
@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    search_form = SearchForm()
    # เรียงลำดับให้งานใหม่แสดงก่อน
    trucks = Truck.query.filter_by(is_confirmed=False, is_expired=False).order_by(Truck.id.desc()).all() or []
    
    if request.method == "POST":
        dest_province = search_form.start_province.data
        
        if dest_province:
            # ค้นหาเฉพาะจังหวัดปลายทาง (แทนที่จะเป็นต้นทาง)
            if dest_province == "กรุงเทพมหานคร":
                # ถ้าค้นหากรุงเทพฯ ให้แสดงรถที่มีปลายทางในกรุงเทพฯ และเขตต่างๆ
                trucks = Truck.query.filter(
                    (Truck.dest == "กรุงเทพมหานคร") | 
                    (Truck.dest.startswith("เขต")), 
                    Truck.is_confirmed == False, 
                    Truck.is_expired == False
                ).order_by(Truck.id.desc()).all() or []
            else:
                trucks = Truck.query.filter_by(dest=dest_province, is_confirmed=False, is_expired=False).order_by(Truck.id.desc()).all() or []
            
            # ถ้าไม่พบรถที่ตรงเงื่อนไข
            if not trucks:
                flash(f"ไม่พบรถที่มีปลายทางจังหวัด{dest_province}", "info")
    
    # ตรวจสอบสถานะงานและงานใหม่
    for truck in trucks:
        truck.is_new = is_new_job(truck.return_date)
        
    return render_template("search.html", search_form=search_form, trucks=trucks, provinces=provinces)


# เส้นทางสำหรับเพิ่มรถ
@app.route("/add_truck", methods=["GET", "POST"])
@login_required
def add_truck():
    truck_form = TruckForm()
    
    if request.method == "POST" and truck_form.validate_on_submit():
        plate = truck_form.plate.data
        truck_type = truck_form.truck_type.data
        start = truck_form.start.data
        dest = truck_form.dest.data
        return_date = truck_form.return_date.data.strftime("%Y-%m-%d")
        
        # ตรวจสอบว่ามีการเลือกเขตใน กทม. หรือไม่
        actual_start = request.form.get('actual_start', start)
        actual_dest = request.form.get('actual_dest', dest)
        
        # ใช้เขตถ้ามีการเลือก
        if actual_start and start == 'กรุงเทพมหานคร':
            start = actual_start
        if actual_dest and dest == 'กรุงเทพมหานคร':
            dest = actual_dest
        
        # ดึงข้อมูลพิกัดจากจุดเริ่มต้นและปลายทาง
        if start in provinces:
            lat, lon = provinces[start]
        else:
            lat, lon = provinces["กรุงเทพมหานคร"]
            
        if dest in provinces:
            dest_lat, dest_lon = provinces[dest]
        else:
            dest_lat, dest_lon = provinces["กรุงเทพมหานคร"]
            
        # คำนวณระยะทาง
        distance = calculate_distance(lat, lon, dest_lat, dest_lon)
        
        # คำนวณราคาตามโซน
        price = calculate_price_with_location(start, dest, distance)
        
        truck = Truck(
            user_id=current_user.id, 
            plate=plate,
            truck_type=truck_type,
            start=start, 
            dest=dest,
            return_date=return_date, 
            price=price, 
            lat=lat, 
            lon=lon, 
            is_confirmed=False
        )
        db.session.add(truck)
        db.session.commit()
        flash("ลงข้อมูลรถสำเร็จ!", "success")
        return redirect(url_for("dashboard"))
    
    return render_template("add_truck.html", truck_form=truck_form, provinces=provinces)

# เส้นทางสำหรับงานของฉัน
@app.route("/my_jobs")
@login_required
def my_jobs():
    my_trucks = Truck.query.filter_by(user_id=current_user.id).order_by(Truck.id.desc()).all() or []
    
    for truck in my_trucks:
        truck.is_new = is_new_job(truck.return_date)
        truck.is_expired = is_expired_job(truck.return_date)
        
    return render_template("my_jobs.html", trucks=my_trucks, provinces=provinces)

# เส้นทางสำหรับโปรไฟล์
@app.route("/profile")
@login_required
def profile():
    # นับจำนวนรถที่ confirm, expired และทั้งหมด
    total_trucks = Truck.query.filter_by(user_id=current_user.id).count()
    confirmed_trucks = Truck.query.filter_by(user_id=current_user.id, is_confirmed=True).count()
    expired_trucks = Truck.query.filter_by(user_id=current_user.id, is_expired=True).count()
    
    return render_template(
        "profile.html", 
        user=current_user, 
        stats={
            'total': total_trucks,
            'confirmed': confirmed_trucks,
            'expired': expired_trucks
        }
    )

# เส้นทางสำหรับเปลี่ยนรหัสผ่าน
@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data
        
        # ตรวจสอบรหัสผ่านปัจจุบัน
        if current_user.password != current_password:
            flash("รหัสผ่านปัจจุบันไม่ถูกต้อง", "error")
            return redirect(url_for("change_password"))
        
        # ตรวจสอบว่ารหัสผ่านใหม่ตรงกัน
        if new_password != confirm_password:
            flash("รหัสผ่านใหม่ไม่ตรงกัน", "error")
            return redirect(url_for("change_password"))
        
        # อัพเดทรหัสผ่าน
        current_user.password = new_password
        db.session.commit()
        
        flash("เปลี่ยนรหัสผ่านสำเร็จ!", "success")
        return redirect(url_for("profile"))
    
    return render_template("change_password.html", form=form)

# เส้นทางสำหรับแจ้งเตือน
@app.route("/notifications/read/<int:notification_id>")
@login_required
def read_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != current_user.id:
        abort(403)
    
    notification.is_read = True
    db.session.commit()
    
    # ถ้ามี truck_id ให้ redirect ไปที่ truck นั้น แต่ต้องตรวจสอบว่า truck ยังมีอยู่หรือไม่
    if notification.truck_id:
        truck = Truck.query.get(notification.truck_id)
        if truck:
            return redirect(url_for("truck_detail", truck_id=notification.truck_id))
        else:
            flash("ไม่พบข้อมูลรถที่ต้องการ อาจถูกลบไปแล้ว", "error")
            return redirect(url_for("notifications"))
    
    return redirect(url_for("notifications"))

# API ดึงข้อมูลรถ
@app.route("/trucks")
def get_trucks():
    trucks = Truck.query.filter_by(is_confirmed=False, is_expired=False).all() or []
    return jsonify([{
        "id": t.id, "plate": t.plate, "truck_type": t.truck_type,
        "start": t.start, "dest": t.dest,
        "return_date": t.return_date, "price": t.price, "lat": t.lat, "lon": t.lon,
        "is_confirmed": t.is_confirmed,
        "user": {
            "email": t.user.email, 
            "phone": t.user.phone if current_user.is_authenticated else None, 
            "name": t.user.name,
            "rating": t.rating,
            "review_count": t.review_count
        }
    } for t in trucks])

# API แสดงเส้นทางและเวลาเดินทางประมาณ
@app.route("/route/<int:truck_id>")
@login_required
def get_route(truck_id):
    truck = Truck.query.get_or_404(truck_id)
    
    avg_speed = 60
    if truck.start in provinces:
        start_lat, start_lon = provinces[truck.start]
    else:
        start_lat, start_lon = provinces["กรุงเทพมหานคร"]
        
    if truck.dest in provinces:
        dest_lat, dest_lon = provinces[truck.dest]
    else:
        dest_lat, dest_lon = provinces["กรุงเทพมหานคร"]
        
    distance = calculate_distance(start_lat, start_lon, dest_lat, dest_lon)
    travel_time_hours = distance / avg_speed
    
    hours = int(travel_time_hours)
    minutes = int((travel_time_hours - hours) * 60)
    
    return jsonify({
        "truck_id": truck.id,
        "start": {"name": truck.start, "lat": start_lat, "lon": start_lon},
        "destination": {"name": truck.dest, "lat": dest_lat, "lon": dest_lon},
        "distance": round(distance, 2),
        "estimated_time": f"{hours} ชั่วโมง {minutes} นาที",
        "price": truck.price
    })

# API สำหรับคำนวณราคา
@app.route("/calculate_price", methods=["POST"])
def calculate_price():
    data = request.json
    start = data.get("start")
    dest = data.get("dest")
    
    # ตรวจสอบว่ามีพิกัดของจังหวัดหรือเขต
    has_start_coords = start in provinces
    has_dest_coords = dest in provinces
    
    if has_start_coords and has_dest_coords:
        start_lat, start_lon = provinces[start]
        dest_lat, dest_lon = provinces[dest]
        distance = calculate_distance(start_lat, start_lon, dest_lat, dest_lon)
        
        # คำนวณราคาตามโซน
        price = calculate_price_with_location(start, dest, distance)
        
        # ตรวจสอบว่าเป็นโซนกรุงเทพฯ หรือไม่
        is_special_zone = is_bangkok_area(start) or is_bangkok_area(dest)
        
        # คำนวณเวลาเดินทางโดยประมาณ (ความเร็วเฉลี่ย 60 กม./ชม.)
        travel_time_hours = distance / 60
        hours = int(travel_time_hours)
        minutes = int((travel_time_hours - hours) * 60)
        
        return jsonify({
            "distance": round(distance, 2),
            "price": price,
            "travel_time": f"{hours} ชั่วโมง {minutes} นาที",
            "is_special_zone": is_special_zone
        })
    elif not has_start_coords and start.startswith('เขต'):
        # ถ้าเป็นเขตที่ไม่มีในข้อมูล ให้ใช้พิกัดของกรุงเทพฯ แทน
        start_lat, start_lon = provinces["กรุงเทพมหานคร"]
        
        if has_dest_coords:
            dest_lat, dest_lon = provinces[dest]
        else:
            dest_lat, dest_lon = provinces["กรุงเทพมหานคร"]
            
        distance = calculate_distance(start_lat, start_lon, dest_lat, dest_lon)
        price = calculate_price_with_location(start, dest, distance)
        
        # เขตในกรุงเทพฯ = โซนพิเศษ
        is_special_zone = True
        
        travel_time_hours = distance / 60
        hours = int(travel_time_hours)
        minutes = int((travel_time_hours - hours) * 60)
        
        return jsonify({
            "distance": round(distance, 2),
            "price": price,
            "travel_time": f"{hours} ชั่วโมง {minutes} นาที",
            "is_special_zone": is_special_zone
        })
    else:
        return jsonify({"error": "ไม่พบข้อมูลจังหวัด"}), 400
        
@app.context_processor
def utility_processor():
    return {
        'is_bangkok_area': is_bangkok_area
    }
# รายละเอียดรถ
@app.route("/truck/<int:truck_id>")
def truck_detail(truck_id):
    truck = Truck.query.get_or_404(truck_id)
    
    # คำนวณระยะทางและเวลาเดินทาง
    if truck.start in provinces:
        start_lat, start_lon = provinces[truck.start]
    else:
        start_lat, start_lon = provinces["กรุงเทพมหานคร"]
        
    if truck.dest in provinces:
        dest_lat, dest_lon = provinces[truck.dest]
    else:
        dest_lat, dest_lon = provinces["กรุงเทพมหานคร"]
        
    distance = calculate_distance(start_lat, start_lon, dest_lat, dest_lon)
    travel_time_hours = distance / 60
    hours = int(travel_time_hours)
    minutes = int((travel_time_hours - hours) * 60)
    
    return render_template(
        "truck_detail.html", 
        truck=truck, 
        distance=round(distance, 2),
        travel_time=f"{hours} ชั่วโมง {minutes} นาที",
        provinces=provinces
    )

# เส้นทางยืนยันงาน
@app.route("/confirm_truck/<int:truck_id>", methods=["POST"])
@login_required
def confirm_truck(truck_id):
    truck = Truck.query.get_or_404(truck_id)
    if truck.user_id == current_user.id and not truck.is_confirmed:
        truck.is_confirmed = True
        db.session.commit()
        flash("ยืนยันงานสำเร็จ! รถคันนี้ไม่ว่างแล้ว", "success")
    else:
        flash("ไม่สามารถยืนยันงานนี้ได้", "error")
    return redirect(url_for("my_jobs"))

# ขยายเวลาประกาศรถ
@app.route("/extend_truck/<int:truck_id>", methods=["POST"])
@login_required
def extend_truck(truck_id):
    truck = Truck.query.get_or_404(truck_id)
    
    if truck.user_id != current_user.id:
        flash("คุณไม่มีสิทธิ์ขยายเวลาประกาศนี้", "error")
        return redirect(url_for("my_jobs"))
    
    # ขยายเวลาไปอีก 7 วัน
    new_return_date = datetime.now() + timedelta(days=7)
    truck.return_date = new_return_date.strftime("%Y-%m-%d")
    truck.is_expired = False
    
    # อัพเดทเวลาแก้ไข
    truck.updated_at = datetime.now()
    
    db.session.commit()
    
    # อัพเดทสถานะการอ่านแจ้งเตือน
    notifications = Notification.query.filter_by(truck_id=truck.id, is_read=False).all()
    for notification in notifications:
        notification.is_read = True
    db.session.commit()
    
    flash("ขยายเวลาประกาศสำเร็จ! รถคันนี้จะแสดงอีก 7 วัน", "success")
    return redirect(url_for("my_jobs"))

# เส้นทางออกจากระบบ
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("ออกจากระบบสำเร็จ!", "success")
    return redirect(url_for("home"))

# ลบข้อมูลรถ
@app.route("/delete_truck/<int:truck_id>", methods=["POST"])
@login_required
def delete_truck(truck_id):
    truck = Truck.query.get_or_404(truck_id)
    if truck.user_id == current_user.id and not truck.is_confirmed:
        # ลบการแจ้งเตือนที่เกี่ยวข้องกับรถคันนี้
        Notification.query.filter_by(truck_id=truck.id).delete()
        
        db.session.delete(truck)
        db.session.commit()
        flash("ลบข้อมูลรถสำเร็จ!", "success")
    else:
        flash("คุณไม่มีสิทธิ์ลบข้อมูลนี้ หรือรถนี้ถูกยืนยันแล้ว", "error")
    return redirect(url_for("my_jobs"))

# แก้ไขข้อมูลรถ
@app.route("/edit_truck/<int:truck_id>", methods=["GET", "POST"])
@login_required
def edit_truck(truck_id):
    truck = Truck.query.get_or_404(truck_id)
    if truck.user_id != current_user.id or truck.is_confirmed:
        flash("คุณไม่มีสิทธิ์แก้ไขข้อมูลนี้ หรือรถนี้ถูกยืนยันแล้ว", "error")
        return redirect(url_for("my_jobs"))
    
    # แก้ตรงนี้: สร้าง form ก่อนแล้วค่อยใส่ค่าแต่ละฟิลด์
    form = TruckForm()
    
    # ไม่ต้องส่ง obj=truck เพราะมีปัญหากับ return_date ที่เป็น string
    form.plate.data = truck.plate
    form.truck_type.data = truck.truck_type
    form.start.data = truck.start
    form.dest.data = truck.dest
    
    # แปลง string เป็น datetime object
    if request.method == "GET":
        form.return_date.data = datetime.strptime(truck.return_date, "%Y-%m-%d")
    
    if form.validate_on_submit():
        # ส่วนที่เหลือไม่ต้องแก้
        truck.plate = form.plate.data
        truck.truck_type = form.truck_type.data
        
        # ตรวจสอบว่ามีการเลือกเขตใน กทม. หรือไม่
        start = form.start.data
        dest = form.dest.data
        actual_start = request.form.get('actual_start')
        actual_dest = request.form.get('actual_dest')
        
        # ใช้เขตถ้ามีการเลือก
        if actual_start and start == 'กรุงเทพมหานคร':
            start = actual_start
        if actual_dest and dest == 'กรุงเทพมหานคร':
            dest = actual_dest

        truck.start = start
        truck.dest = dest
        truck.return_date = form.return_date.data.strftime("%Y-%m-%d")
        
        # ดึงพิกัดจากข้อมูลจังหวัด/เขต
        if start in provinces:
            truck.lat, truck.lon = provinces[start]
        else:
            truck.lat, truck.lon = provinces["กรุงเทพมหานคร"]
            
        if dest in provinces:
            dest_lat, dest_lon = provinces[dest]
        else:
            dest_lat, dest_lon = provinces["กรุงเทพมหานคร"]
            
        distance = calculate_distance(truck.lat, truck.lon, dest_lat, dest_lon)
        
        # คำนวณราคาตามโซน
        truck.price = calculate_price_with_location(truck.start, truck.dest, distance)
        
        truck.is_confirmed = False
        truck.is_expired = False
        truck.updated_at = datetime.now()
        db.session.commit()
        flash("แก้ไขข้อมูลรถสำเร็จ!", "success")
        return redirect(url_for("my_jobs"))

    return render_template("edit_truck.html", form=form, truck=truck, provinces=provinces)

# ส่วนของแอดมิน
@app.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    # จำนวนผู้ใช้ทั้งหมด (ไม่รวมบอท)
    total_users = User.query.filter(User.email != "support@backtracks.com").count()
    
    # จำนวนรถทั้งหมด
    total_trucks = Truck.query.count()
    
    # จำนวนรถที่ยืนยันแล้ว
    confirmed_trucks = Truck.query.filter_by(is_confirmed=True).count()
    
    # จำนวนรถที่หมดอายุ
    expired_trucks = Truck.query.filter_by(is_expired=True).count()
    
    # จำนวนรถที่ว่างอยู่
    available_trucks = Truck.query.filter_by(is_confirmed=False, is_expired=False).count()
    
    # ผู้ใช้ล่าสุด
    latest_users = User.query.filter(User.email != "support@backtracks.com").order_by(User.created_at.desc()).limit(5).all()
    
    # รถล่าสุด
    latest_trucks = Truck.query.order_by(Truck.created_at.desc()).limit(5).all()
    
    return render_template(
        "admin/dashboard.html",
        stats={
            "total_users": total_users,
            "total_trucks": total_trucks,
            "confirmed_trucks": confirmed_trucks,
            "expired_trucks": expired_trucks,
            "available_trucks": available_trucks
        },
        latest_users=latest_users,
        latest_trucks=latest_trucks
    )

@app.route("/admin/users")
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    
    # เพิ่มข้อมูลกิจกรรมของผู้ใช้แต่ละคน
    for user in users:
        user.total_trucks = Truck.query.filter_by(user_id=user.id).count()
        user.active_trucks = Truck.query.filter_by(user_id=user.id, is_confirmed=False, is_expired=False).count()
        user.confirmed_trucks = Truck.query.filter_by(user_id=user.id, is_confirmed=True).count()
        user.expired_trucks = Truck.query.filter_by(user_id=user.id, is_expired=True).count()
        
    return render_template("admin/users.html", users=users)

@app.route("/admin/trucks")
@login_required
@admin_required
def admin_trucks():
    trucks = Truck.query.all()
    return render_template("admin/trucks.html", trucks=trucks)

@app.route("/admin/user/<int:user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminUserEditForm(obj=user)
    
    if form.validate_on_submit():
        # ตรวจสอบว่าอีเมลซ้ำกับผู้ใช้อื่นหรือไม่
        existing_user = User.query.filter(User.email == form.email.data, User.id != user_id).first()
        if existing_user:
            flash("อีเมลนี้มีผู้ใช้แล้ว", "error")
            return redirect(url_for("admin_edit_user", user_id=user_id))
        
        # ตรวจสอบเบอร์โทรซ้ำ
        existing_phone = User.query.filter(User.phone == form.phone.data, User.id != user_id).first()
        if existing_phone:
            flash("เบอร์โทรศัพท์นี้มีผู้ใช้แล้ว", "error")
            return redirect(url_for("admin_edit_user", user_id=user_id))
        
        user.email = form.email.data
        user.phone = form.phone.data
        user.name = form.name.data
        user.is_admin = form.is_admin.data
        
        db.session.commit()
        flash("แก้ไขข้อมูลผู้ใช้สำเร็จ!", "success")
        return redirect(url_for("admin_users"))
    
    return render_template("admin/edit_user.html", form=form, user=user)

@app.route("/admin/user/<int:user_id>/reset_password", methods=["POST"])
@login_required
@admin_required
def admin_reset_password(user_id):
    user = User.query.get_or_404(user_id)
    
    # รีเซ็ตรหัสผ่านเป็น "123456"
    user.password = "123456"
    db.session.commit()
    
    flash(f"รีเซ็ตรหัสผ่านของ {user.name} สำเร็จ! รหัสผ่านใหม่คือ 123456", "success")
    return redirect(url_for("admin_edit_user", user_id=user_id))

@app.route("/admin/truck/<int:truck_id>", methods=["GET", "POST"])
@login_required
@admin_required
def admin_edit_truck(truck_id):
    truck = Truck.query.get_or_404(truck_id)
    form = TruckForm(obj=truck)
    
    if form.validate_on_submit():
        truck.plate = form.plate.data
        truck.truck_type = form.truck_type.data
        
        # ตรวจสอบว่ามีการเลือกเขตใน กทม. หรือไม่
        start = form.start.data
        dest = form.dest.data
        actual_start = request.form.get('actual_start')
        actual_dest = request.form.get('actual_dest')
        
        # ใช้เขตถ้ามีการเลือก
        if actual_start and start == 'กรุงเทพมหานคร':
            start = actual_start
        if actual_dest and dest == 'กรุงเทพมหานคร':
            dest = actual_dest
            
        truck.start = start
        truck.dest = dest
        truck.return_date = form.return_date.data.strftime("%Y-%m-%d")
        
        # ดึงพิกัดจากข้อมูลจังหวัด/เขต
        if start in provinces:
            truck.lat, truck.lon = provinces[start]
        else:
            truck.lat, truck.lon = provinces["กรุงเทพมหานคร"]
            
        if dest in provinces:
            dest_lat, dest_lon = provinces[dest]
        else:
            dest_lat, dest_lon = provinces["กรุงเทพมหานคร"]
            
        distance = calculate_distance(truck.lat, truck.lon, dest_lat, dest_lon)
        
        # คำนวณราคาตามโซน
        truck.price = calculate_price_with_location(truck.start, truck.dest, distance)
        
        db.session.commit()
        flash("แก้ไขข้อมูลรถสำเร็จ!", "success")
        return redirect(url_for("admin_trucks"))
    
    return render_template("admin/edit_truck.html", form=form, truck=truck)

@app.route("/admin/truck/<int:truck_id>/toggle_status", methods=["POST"])
@login_required
@admin_required
def admin_toggle_truck_status(truck_id):
    truck = Truck.query.get_or_404(truck_id)
    
    truck.is_confirmed = not truck.is_confirmed
    db.session.commit()
    
    status = "ยืนยัน" if truck.is_confirmed else "ยกเลิกการยืนยัน"
    flash(f"{status}สถานะรถสำเร็จ!", "success")
    return redirect(url_for("admin_trucks"))

@app.route("/admin/truck/<int:truck_id>/delete", methods=["POST"])
@login_required
@admin_required
def admin_delete_truck(truck_id):
    truck = Truck.query.get_or_404(truck_id)
    
    # ลบการแจ้งเตือนที่เกี่ยวข้องกับรถคันนี้
    Notification.query.filter_by(truck_id=truck.id).delete()
    
    db.session.delete(truck)
    db.session.commit()
    
    flash("ลบข้อมูลรถสำเร็จ!", "success")
    return redirect(url_for("admin_trucks"))

@app.route("/setup_admin")
def setup_admin():
    with app.app_context():
        try:
            admin = User.query.filter_by(email="admin@backtracks.com").first()
            if not admin:
                admin_user = User(email="admin@backtracks.com", phone="0812345678", 
                                name="BackTracks Admin", password="admin123456", is_admin=True)
                db.session.add(admin_user)
                db.session.commit()
                return "เพิ่มผู้ดูแลระบบสำเร็จ!"
            else:
                admin.is_admin = True
                db.session.commit()
                return "อัปเดตสถานะผู้ดูแลระบบสำเร็จ!"
        except Exception as e:
            return f"เกิดข้อผิดพลาด: {str(e)}"
# รันแอป
if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)