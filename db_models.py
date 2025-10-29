from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('student', 'admin', 'warden'), default='student')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    student_profile = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_student(self):
        return self.role == 'student'
    
    def is_warden(self):
        return self.role == 'warden'

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    enrollment_no = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    address = db.Column(db.Text)
    stream = db.Column(db.String(50))
    semester = db.Column(db.Integer)
    date_of_birth = db.Column(db.Date)
    guardian_name = db.Column(db.String(100))
    guardian_phone = db.Column(db.String(15))
    
    # Relationships
    bookings = db.relationship('Booking', backref='student', lazy='dynamic')
    complaints = db.relationship('Complaint', backref='student', lazy='dynamic')
    feedback = db.relationship('Feedback', backref='student', lazy='dynamic')

class Room(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(10), unique=True, nullable=False)
    seater_type = db.Column(db.Enum('1', '2', '3', '4'), nullable=False)
    monthly_fee = db.Column(db.Numeric(10, 2), nullable=False)
    amenities = db.Column(db.Text)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='room', lazy='dynamic')

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    food_option = db.Column(db.Enum('veg', 'non-veg'), default='veg')
    total_amount = db.Column(db.Numeric(10, 2))
    status = db.Column(db.Enum('pending', 'confirmed', 'cancelled', 'completed'), default='pending')
    
    # Relationships
    payments = db.relationship('Payment', backref='booking', lazy='dynamic')

class Complaint(db.Model):
    __tablename__ = 'complaints'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.Enum('electrical', 'plumbing', 'cleaning', 'furniture', 'other'), default='other')
    priority = db.Column(db.Enum('low', 'medium', 'high'), default='medium')
    status = db.Column(db.Enum('new', 'in_progress', 'resolved', 'closed'), default='new')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    admin_notes = db.Column(db.Text)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text)
    category = db.Column(db.Enum('facilities', 'food', 'staff', 'cleanliness', 'overall'), nullable=False)
    sentiment_score = db.Column(db.Float)
    sentiment_label = db.Column(db.Enum('positive', 'negative', 'neutral'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.Enum('cash', 'online', 'card'), default='cash')
    transaction_id = db.Column(db.String(100))
    status = db.Column(db.Enum('pending', 'completed', 'failed'), default='pending')