from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length, NumberRange
import math
from datetime import datetime, timedelta
import random
import os

app = Flask(__name__)
app.static_folder = 'static'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trucks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sage-backtracks-2025'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # เมื่อไม่ login ให้กลับไปหน้า login

# Branding และสี
BRAND_NAME = "BackTracks"
BACKGROUND_COLOR = "#1A2B42"
HEADER_COLOR = "#363A51"
TEXT_COLOR = "#5CC59E"
HIGHLIGHT_COLOR = "#67F494"
ACCENT_COLOR = "#FFFFFF"
FONT_SIZE = "20px"
NEW_JOB_COLOR = "#FF6B6B"  # สีแดงอ่อนสำหรับงานใหม่ (ไม่เกิน 1 วัน)

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

# โมเดลฐานข้อมูล
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(10), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=True)
    trucks = db.relationship('Truck', backref='user', lazy=True)

class Truck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plate = db.Column(db.String(10), nullable=False)
    truck_type = db.Column(db.String(20), default="รถบรรทุก", nullable=False)  # เพิ่มประเภทรถ
    start = db.Column(db.String(50), nullable=False)
    dest = db.Column(db.String(50), nullable=False)
    return_date = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False)  # เพิ่มสถานะว่าง/ไม่ว่าง

# ฟังก์ชันคำนวณระยะทาง
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# ฟังก์ชันตรวจสอบงานใหม่ (ไม่เกิน 1 วัน)
def is_new_job(return_date):
    return_date_obj = datetime.strptime(return_date, "%Y-%m-%d")
    now = datetime.now()
    return (return_date_obj - now).days <= 1 and (return_date_obj - now).days >= 0

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
        ('รถพ่วง/หัวลาก', 'รถพ่วง/หัวลาก'), 
        ('รถกระบะ', 'รถกระบะ'), 
        ('รถบรรทุก', 'รถบรรทุก')
    ], validators=[DataRequired()])
    start = SelectField('จุดเริ่มต้น', choices=[(p, p) for p in provinces.keys()], validators=[DataRequired()])
    dest = SelectField('จุดหมายปลายทาง', choices=[(p, p) for p in provinces.keys()], validators=[DataRequired()])
    return_date = DateField('วันที่ว่างกลับ', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('ลงทะเบียนรับงาน')

class SearchForm(FlaskForm):
    start_province = SelectField('จังหวัดต้นทาง', choices=[('', 'เลือกจังหวัด')] + [(p, p) for p in provinces.keys()])
    truck_type = SelectField('ประเภทรถ', choices=[
        ('', 'ทุกประเภท'),
        ('รถพ่วง/หัวลาก', 'รถพ่วง/หัวลาก'), 
        ('รถกระบะ', 'รถกระบะ'), 
        ('รถบรรทุก', 'รถบรรทุก')
    ])
    submit = SubmitField('ค้นหา')


with app.app_context():
    db.create_all()    
    if not User.query.filter_by(email="support@backtracks.com").first():
        bot_user = User(email="support@backtracks.com", phone="0812345678", name="BackTracks Bot", password="sage123456")
        db.session.add(bot_user)
        db.session.commit()

        # เพิ่มข้อมูลตัวอย่าง
        truck_types = ['รถพ่วง/หัวลาก', 'รถกระบะ', 'รถบรรทุก']
        
        for _ in range(10):
            plate = generate_random_plate()
            truck_type = random.choice(truck_types)
            start = random.choice(list(provinces.keys()))
            dest = "กรุงเทพมหานคร"
            return_date = (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
            lat, lon = provinces[start]
            dest_lat, dest_lon = provinces[dest]
            distance = calculate_distance(lat, lon, dest_lat, dest_lon)
            price = int(distance * 12)
            price = (price // 500) * 500 if price % 500 < 250 else ((price // 500) + 1) * 500
            truck = Truck(
                user_id=bot_user.id, 
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

        # เพิ่มข้อมูลตัวอย่าง
        truck_types = ['รถพ่วง/หัวลาก', 'รถกระบะ', 'รถบรรทุก']
        
        for _ in range(10):
            plate = generate_random_plate()
            truck_type = random.choice(truck_types)
            start = random.choice(list(provinces.keys()))
            dest = "กรุงเทพมหานคร"
            return_date = (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
            lat, lon = provinces[start]
            dest_lat, dest_lon = provinces[dest]
            distance = calculate_distance(lat, lon, dest_lat, dest_lon)
            price = int(distance * 12)
            price = (price // 500) * 500 if price % 500 < 250 else ((price // 500) + 1) * 500
            truck = Truck(
                user_id=bot_user.id, 
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

# เส้นทางหน้าแรก (สำหรับสมัครสมาชิก)
@app.route("/", methods=["GET", "POST"])
def home():
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

    return render_template("index.html", register_form=register_form, contact_phone=contact_phone,
                           brand_name=BRAND_NAME, background_color=BACKGROUND_COLOR,
                           header_color=HEADER_COLOR, text_color=TEXT_COLOR, highlight_color=HIGHLIGHT_COLOR,
                           accent_color=ACCENT_COLOR, font_size=FONT_SIZE, new_job_color=NEW_JOB_COLOR)

# เส้นทางสมัครสมาชิก (สำหรับลิงก์ใน login)
@app.route("/register", methods=["GET", "POST"])
def register():
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

    return render_template("index.html", register_form=register_form, contact_phone=contact_phone,
                           brand_name=BRAND_NAME, background_color=BACKGROUND_COLOR,
                           header_color=HEADER_COLOR, text_color=TEXT_COLOR, highlight_color=HIGHLIGHT_COLOR,
                           accent_color=ACCENT_COLOR, font_size=FONT_SIZE, new_job_color=NEW_JOB_COLOR)

# เส้นทางล็อกอิน
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    contact_phone = "08-123-45678"
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data, password=form.password.data).first()
        if user:
            login_user(user)
            flash("เข้าสู่ระบบสำเร็จ!", "success")
            return redirect(url_for("dashboard"))
        flash("อีเมลหรือรหัสผ่านไม่ถูกต้อง", "error")
    return render_template("login.html", form=form, contact_phone=contact_phone, brand_name=BRAND_NAME,
                           background_color=BACKGROUND_COLOR, header_color=HEADER_COLOR,
                           text_color=TEXT_COLOR, highlight_color=HIGHLIGHT_COLOR,
                           accent_color=ACCENT_COLOR, font_size=FONT_SIZE, new_job_color=NEW_JOB_COLOR)

# เส้นทางแดชบอร์ด (หลัง login)
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    trucks = Truck.query.order_by(Truck.id.desc()).all() or []  # งานใหม่ขึ้นบนสุด
    truck_form = TruckForm()
    search_form = SearchForm()
    contact_phone = "08-123-45678"

    if truck_form.validate_on_submit() and "truck" in request.form:
        plate = truck_form.plate.data
        truck_type = truck_form.truck_type.data
        start = truck_form.start.data
        dest = truck_form.dest.data
        return_date = truck_form.return_date.data.strftime("%Y-%m-%d")
        lat, lon = provinces[start]
        dest_lat, dest_lon = provinces[dest]
        distance = calculate_distance(lat, lon, dest_lat, dest_lon)
        price = int(distance * 12)
        price = (price // 500) * 500 if price % 500 < 250 else ((price // 500) + 1) * 500
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

    if search_form.validate_on_submit() and "search" in request.form:
        start_province = search_form.start_province.data
        truck_type = search_form.truck_type.data
        
        if start_province or truck_type:
            filtered_trucks = trucks
            if start_province:
                filtered_trucks = [t for t in filtered_trucks if t.start == start_province]
            if truck_type:
                filtered_trucks = [t for t in filtered_trucks if t.truck_type == truck_type]
            trucks = filtered_trucks

    # ตรวจสอบสถานะงานและงานใหม่
    for truck in trucks:
        truck.is_new = is_new_job(truck.return_date)

    return render_template("dashboard.html", truck_form=truck_form, search_form=search_form, trucks=trucks,
                           provinces=provinces, contact_phone=contact_phone, brand_name=BRAND_NAME,
                           background_color=BACKGROUND_COLOR, header_color=HEADER_COLOR,
                           text_color=TEXT_COLOR, highlight_color=HIGHLIGHT_COLOR,
                           accent_color=ACCENT_COLOR, font_size=FONT_SIZE, new_job_color=NEW_JOB_COLOR)

# API ดึงข้อมูลรถ
@app.route("/trucks")
def get_trucks():
    trucks = Truck.query.all() or []
    return jsonify([{
        "id": t.id, "plate": t.plate, "truck_type": t.truck_type,
        "start": t.start, "dest": t.dest,
        "return_date": t.return_date, "price": t.price, "lat": t.lat, "lon": t.lon,
        "is_confirmed": t.is_confirmed,
        "user": {"email": t.user.email, "phone": t.user.phone if current_user.is_authenticated else None, "name": t.user.name}
    } for t in trucks])

# API แสดงเส้นทางและเวลาเดินทางประมาณ
@app.route("/route/<int:truck_id>")
@login_required
def get_route(truck_id):
    truck = Truck.query.get_or_404(truck_id)
    
    # คำนวณเวลาเดินทางประมาณ (โดยเฉลี่ยรถบรรทุกวิ่ง 60 กม/ชม)
    avg_speed = 60  # km/h
    start_lat, start_lon = provinces[truck.start]
    dest_lat, dest_lon = provinces[truck.dest]
    distance = calculate_distance(start_lat, start_lon, dest_lat, dest_lon)
    travel_time_hours = distance / avg_speed
    
    # แปลงเป็นชั่วโมงและนาที
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
    return redirect(url_for("dashboard"))

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
        db.session.delete(truck)
        db.session.commit()
        flash("ลบข้อมูลรถสำเร็จ!", "success")
    else:
        flash("คุณไม่มีสิทธิ์ลบข้อมูลนี้ หรือรถนี้ถูกยืนยันแล้ว", "error")
    return redirect(url_for("dashboard"))

# แก้ไขข้อมูลรถ
@app.route("/edit_truck/<int:truck_id>", methods=["GET", "POST"])
@login_required
def edit_truck(truck_id):
    truck = Truck.query.get_or_404(truck_id)
    if truck.user_id != current_user.id or truck.is_confirmed:
        flash("คุณไม่มีสิทธิ์แก้ไขข้อมูลนี้ หรือรถนี้ถูกยืนยันแล้ว", "error")
        return redirect(url_for("dashboard"))
    form = TruckForm(obj=truck)
    contact_phone = "08-123-45678"

    if form.validate_on_submit():
        truck.plate = form.plate.data
        truck.truck_type = form.truck_type.data
        truck.start = form.start.data
        truck.dest = form.dest.data
        truck.return_date = form.return_date.data.strftime("%Y-%m-%d")
        truck.lat, truck.lon = provinces[truck.start]
        dest_lat, dest_lon = provinces[truck.dest]
        distance = calculate_distance(truck.lat, truck.lon, dest_lat, dest_lon)
        truck.price = int(distance * 12)
        truck.price = (truck.price // 500) * 500 if truck.price % 500 < 250 else ((truck.price // 500) + 1) * 500
        truck.is_confirmed = False  # รีเซ็ตสถานะเมื่อแก้ไข
        db.session.commit()
        flash("แก้ไขข้อมูลรถสำเร็จ!", "success")
        return redirect(url_for("dashboard"))
# เส้นทางสำหรับค้นหา
@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    search_form = SearchForm()
    trucks = Truck.query.order_by(Truck.id.desc()).all() or []
    
    if search_form.validate_on_submit():
        start_province = search_form.start_province.data
        truck_type = search_form.truck_type.data
        
        if start_province or truck_type:
            if start_province:
                trucks = [t for t in trucks if t.start == start_province]
            if truck_type:
                trucks = [t for t in trucks if t.truck_type == truck_type]
    
    # ตรวจสอบสถานะงานและงานใหม่
    for truck in trucks:
        truck.is_new = is_new_job(truck.return_date)
        
    return render_template("search.html", search_form=search_form, trucks=trucks,
                           provinces=provinces) contact_phone="08-123-45678", brand_name=BRAND_NAME,
                           background_color=BACKGROUND_COLOR, header_color=HEADER_COLOR,
                           text_color=TEXT_COLOR, highlight_color=HIGHLIGHT_COLOR,
                           accent_color=ACCENT_COLOR, font_size=FONT_SIZE, new_job_color=NEW_JOB_COLOR)

# เส้นทางสำหรับเพิ่มรถ
@app.route("/add_truck", methods=["GET", "POST"])
@login_required
def add_truck():
    truck_form = TruckForm()
    
    if truck_form.validate_on_submit():
        plate = truck_form.plate.data
        truck_type = truck_form.truck_type.data
        start = truck_form.start.data
        dest = truck_form.dest.data
        return_date = truck_form.return_date.data.strftime("%Y-%m-%d")
        lat, lon = provinces[start]
        dest_lat, dest_lon = provinces[dest]
        distance = calculate_distance(lat, lon, dest_lat, dest_lon)
        price = int(distance * 12)
        price = (price // 500) * 500 if price % 500 < 250 else ((price // 500) + 1) * 500
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
        
    return render_template("add_truck.html", truck_form=truck_form, provinces=provinces)contact_phone="08-123-45678", brand_name=BRAND_NAME,
                           background_color=BACKGROUND_COLOR, header_color=HEADER_COLOR,
                           text_color=TEXT_COLOR, highlight_color=HIGHLIGHT_COLOR,
                           accent_color=ACCENT_COLOR, font_size=FONT_SIZE, new_job_color=NEW_JOB_COLOR)

# เส้นทางสำหรับงานของฉัน
@app.route("/my_jobs")
@login_required
def my_jobs():
    my_trucks = Truck.query.filter_by(user_id=current_user.id).order_by(Truck.id.desc()).all() or []
    
    # ตรวจสอบสถานะงานและงานใหม่
    for truck in my_trucks:
        truck.is_new = is_new_job(truck.return_date)
        
    return render_template("my_jobs.html", trucks=my_trucks, provinces=provinces)contact_phone="08-123-45678", brand_name=BRAND_NAME,
                           background_color=BACKGROUND_COLOR, header_color=HEADER_COLOR,
                           text_color=TEXT_COLOR, highlight_color=HIGHLIGHT_COLOR,
                           accent_color=ACCENT_COLOR, font_size=FONT_SIZE, new_job_color=NEW_JOB_COLOR)

# เส้นทางสำหรับโปรไฟล์
@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)
                           contact_phone="08-123-45678", brand_name=BRAND_NAME,
                           background_color=BACKGROUND_COLOR, header_color=HEADER_COLOR,
                           text_color=TEXT_COLOR, highlight_color=HIGHLIGHT_COLOR,
                           accent_color=ACCENT_COLOR, font_size=FONT_SIZE, new_job_color=NEW_JOB_COLOR)

    return render_template("edit_truck.html", form=form, truck=truck, provinces=provinces,
                           contact_phone=contact_phone, brand_name=BRAND_NAME,
                           background_color=BACKGROUND_COLOR, header_color=HEADER_COLOR,
                           text_color=TEXT_COLOR, highlight_color=HIGHLIGHT_COLOR,
                           accent_color=ACCENT_COLOR, font_size=FONT_SIZE, new_job_color=NEW_JOB_COLOR)

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)