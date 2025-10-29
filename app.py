from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import config
from models.db_models import db, User, Student, Room, Booking, Complaint, Feedback
from forms import LoginForm, RegistrationForm, StudentProfileForm, RoomForm, BookingForm, ComplaintForm, FeedbackForm
from ml_models.sentiment_analyzer import sentiment_analyzer
from ml_models.occupancy_predictor import occupancy_predictor
from ml_models.complaint_classifier import complaint_classifier
from ml_models.booking_approver import booking_approver
from datetime import datetime, timedelta
import os
from sqlalchemy import text, func
import json

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    config[config_name].init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Initialize database and ML models
    with app.app_context():
        try:
            # Test database connection
            db.session.execute(text('SELECT 1'))
            print("✅ Database connection successful!")
            
            # Create tables if they don't exist
            db.create_all()
            print("✅ Database tables checked/created!")
            
            # Load ML models
            print("📊 Loading ML models...")
            sentiment_analyzer.load_model()
            occupancy_predictor.load_model()
            complaint_classifier.load_model()
            booking_approver.load_model()
            print("✅ ML models loaded!")
            
            # Auto-approve pending bookings on startup
            print("🤖 Checking for pending bookings...")
            approved_count = booking_approver.auto_approve_pending_bookings()
            if approved_count > 0:
                print(f"✅ Auto-approved {approved_count} pending bookings on startup!")
            
        except Exception as e:
            print(f"❌ Startup error: {e}")
    
    # ===== MAIN ROUTES =====
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.is_admin():
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        return render_template('index.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            
            if user and user.check_password(form.password.data) and user.is_active:
                login_user(user, remember=True)
                flash('Login successful!', 'success')
                
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                
                if user.is_admin():
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('student_dashboard'))
            else:
                flash('Login unsuccessful. Please check username and password', 'danger')
        
        return render_template('auth/login.html', form=form)
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            try:
                user = User(
                    username=form.username.data,
                    email=form.email.data,
                    role='student'
                )
                user.set_password(form.password.data)
                
                db.session.add(user)
                db.session.commit()
                
                flash('Registration successful! Please complete your profile.', 'success')
                return redirect(url_for('complete_profile'))
            
            except Exception as e:
                db.session.rollback()
                flash('Registration failed. Please try again.', 'danger')
        
        return render_template('auth/register.html', form=form)
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))
    
    # ===== STUDENT ROUTES =====
    @app.route('/student/dashboard')
    @login_required
    def student_dashboard():
        if current_user.is_admin():
            return redirect(url_for('admin_dashboard'))
        
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student:
            return redirect(url_for('complete_profile'))
        
        # Get REAL statistics from database
        total_bookings = Booking.query.filter_by(student_id=student.id).count()
        active_bookings = Booking.query.filter_by(student_id=student.id, status='confirmed').count()
        pending_complaints = Complaint.query.filter_by(student_id=student.id, status='new').count()
        total_feedback = Feedback.query.filter_by(student_id=student.id).count()
        
        # Get recent complaints and bookings
        recent_complaints = Complaint.query.filter_by(student_id=student.id).order_by(Complaint.created_at.desc()).limit(3).all()
        recent_bookings = Booking.query.filter_by(student_id=student.id).order_by(Booking.booking_date.desc()).limit(3).all()
        
        # Calculate days remaining in current booking
        days_remaining = 0
        current_booking = Booking.query.filter_by(student_id=student.id, status='confirmed').first()
        if current_booking and current_booking.check_out_date:
            days_remaining = (current_booking.check_out_date - datetime.now().date()).days
            days_remaining = max(0, days_remaining)
        
        return render_template('student/dashboard.html', 
                             student=student,
                             total_bookings=total_bookings,
                             active_bookings=active_bookings,
                             pending_complaints=pending_complaints,
                             total_feedback=total_feedback,
                             days_remaining=days_remaining,
                             recent_complaints=recent_complaints,
                             recent_bookings=recent_bookings)
    
    @app.route('/student/profile', methods=['GET', 'POST'])
    @login_required
    def complete_profile():
        student = Student.query.filter_by(user_id=current_user.id).first()
        form = StudentProfileForm()
        
        if form.validate_on_submit():
            try:
                if student:
                    # Update existing profile
                    student.full_name = form.full_name.data
                    student.enrollment_no = form.enrollment_no.data
                    student.phone = form.phone.data
                    student.address = form.address.data
                    student.stream = form.stream.data
                    student.semester = form.semester.data
                    student.date_of_birth = form.date_of_birth.data
                    student.guardian_name = form.guardian_name.data
                    student.guardian_phone = form.guardian_phone.data
                else:
                    # Create new profile
                    student = Student(
                        user_id=current_user.id,
                        full_name=form.full_name.data,
                        enrollment_no=form.enrollment_no.data,
                        phone=form.phone.data,
                        address=form.address.data,
                        stream=form.stream.data,
                        semester=form.semester.data,
                        date_of_birth=form.date_of_birth.data,
                        guardian_name=form.guardian_name.data,
                        guardian_phone=form.guardian_phone.data
                    )
                    db.session.add(student)
                
                db.session.commit()
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('student_dashboard'))
            
            except Exception as e:
                db.session.rollback()
                flash('Error updating profile. Please try again.', 'danger')
        
        elif request.method == 'GET' and student:
            # Populate form with existing data
            form.full_name.data = student.full_name
            form.enrollment_no.data = student.enrollment_no
            form.phone.data = student.phone
            form.address.data = student.address
            form.stream.data = student.stream
            form.semester.data = student.semester
            form.date_of_birth.data = student.date_of_birth
            form.guardian_name.data = student.guardian_name
            form.guardian_phone.data = student.guardian_phone
        
        return render_template('student/profile.html', form=form, student=student)

    @app.route('/student/rooms')
    @login_required
    def student_rooms():
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student:
            flash('Please complete your profile first.', 'warning')
            return redirect(url_for('complete_profile'))
        
        rooms = Room.query.filter_by(is_available=True).all()
        return render_template('student/rooms.html', rooms=rooms)
    
    @app.route('/student/book-room/<int:room_id>', methods=['GET', 'POST'])
    @login_required
    def book_room(room_id):
        room = Room.query.get_or_404(room_id)
        student = Student.query.filter_by(user_id=current_user.id).first()
        
        if not student:
            flash('Please complete your profile first.', 'warning')
            return redirect(url_for('complete_profile'))
        
        form = BookingForm()
        form.room_id.choices = [(room.id, f"Room {room.room_number} - {room.seater_type} seater - ₹{room.monthly_fee}/month")]
        
        if form.validate_on_submit():
            try:
                # Calculate total amount
                check_in = form.check_in_date.data
                check_out = form.check_out_date.data
                days = (check_out - check_in).days
                
                if days <= 0:
                    flash('Check-out date must be after check-in date.', 'danger')
                    return render_template('student/book_room.html', form=form, room=room)
                
                total_amount = (room.monthly_fee / 30) * days
                
                # Create booking with pending status initially
                booking = Booking(
                    student_id=student.id,
                    room_id=room.id,
                    check_in_date=check_in,
                    check_out_date=check_out,
                    food_option=form.food_option.data,
                    total_amount=total_amount,
                    status='pending'  # Start as pending
                )
                
                db.session.add(booking)
                db.session.flush()  # Get booking ID without committing
                
                print(f"📝 Booking created with ID: {booking.id}, Status: {booking.status}")
                
                # Use ML to predict approval
                current_occupancy = occupancy_predictor.predict_occupancy()
                print(f"🏨 Current occupancy: {current_occupancy}%")
                
                approval_prediction = booking_approver.predict_booking_approval(booking, current_occupancy)
                print(f"🤖 ML Prediction - Approved: {approval_prediction['approved']}, Confidence: {approval_prediction['confidence']:.4f}")
                
                # Auto-approve if ML predicts high confidence
                if approval_prediction['approved'] and approval_prediction['confidence'] > 0.7:
                    booking.status = 'confirmed'
                    room.is_available = False  # Mark room as occupied
                    flash_message = f'🎉 Booking confirmed automatically! Your room has been reserved. (ML Confidence: {approval_prediction["confidence"]:.1%})'
                    flash(flash_message, 'success')
                    print(f"✅ Booking {booking.id} auto-approved by ML")
                else:
                    # Keep as pending for manual review
                    flash_message = f'📝 Booking request submitted! It will be reviewed shortly. (ML Suggestion: {"Approve" if approval_prediction["approved"] else "Review"})'
                    flash(flash_message, 'info')
                    print(f"⏳ Booking {booking.id} kept as pending")
                
                db.session.commit()
                print(f"💾 Database committed. Final status: {booking.status}")
                
                return redirect(url_for('student_bookings'))
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error in booking process: {e}")
                flash('Error booking room. Please try again.', 'danger')
        return render_template('student/book_room.html', form=form, room=room)
        
    @app.route('/student/bookings')
    @login_required
    def student_bookings():
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student:
            return redirect(url_for('complete_profile'))
        
        bookings = Booking.query.filter_by(student_id=student.id).order_by(Booking.booking_date.desc()).all()
        return render_template('student/bookings.html', bookings=bookings)
    
    @app.route('/student/complaints', methods=['GET', 'POST'])
    @login_required
    def student_complaints():
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student:
            return redirect(url_for('complete_profile'))
        
        form = ComplaintForm()
        complaints = Complaint.query.filter_by(student_id=student.id).order_by(Complaint.created_at.desc()).all()
        
        if form.validate_on_submit():
            try:
                # 🛠️ USE MANUAL MAPPING INSTEAD OF ML (Temporary Fix)
                category = get_manual_category(form.title.data, form.description.data)
                priority = get_manual_priority(form.title.data, form.description.data)
                
                complaint = Complaint(
                    student_id=student.id,
                    title=form.title.data,
                    description=form.description.data,
                    category=category,    # Correct category
                    priority=priority,    # Correct priority  
                    status='new'
                )
                
                db.session.add(complaint)
                db.session.commit()
                
                flash('Complaint submitted successfully!', 'success')
                return redirect(url_for('student_complaints'))
            
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error in complaint submission: {e}")
                flash('Error submitting complaint. Please try again.', 'danger')
        
        return render_template('student/complaints.html', form=form, complaints=complaints)
    
    @app.route('/student/feedback', methods=['GET', 'POST'])
    @login_required
    def student_feedback():
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student:
            return redirect(url_for('complete_profile'))
        
        form = FeedbackForm()
        
        if form.validate_on_submit():
            try:
                # Use ML to analyze sentiment
                sentiment = sentiment_analyzer.analyze_sentiment(form.comments.data)
                
                feedback = Feedback(
                    student_id=student.id,
                    rating=form.rating.data,
                    comments=form.comments.data,
                    category=form.category.data,
                    sentiment_score=sentiment['score'],
                    sentiment_label=sentiment['label']
                )
                
                db.session.add(feedback)
                db.session.commit()
                
                flash('Feedback submitted successfully! Thank you for your input.', 'success')
                return redirect(url_for('student_dashboard'))
            
            except Exception as e:
                db.session.rollback()
                flash('Error submitting feedback. Please try again.', 'danger')
        
        return render_template('student/feedback.html', form=form)
    
    # ===== ADMIN ROUTES =====
    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        if not current_user.is_admin():
            return redirect(url_for('student_dashboard'))
        
        # Get REAL statistics from database
        total_students = Student.query.count()
        total_rooms = Room.query.count()
        available_rooms = Room.query.filter_by(is_available=True).count()
        total_complaints = Complaint.query.count()
        pending_complaints = Complaint.query.filter_by(status='new').count()
        total_feedback = Feedback.query.count()
        
        # Get ML predictions - REAL DATA
        current_occupancy = occupancy_predictor.predict_occupancy()
        occupancy_trend = occupancy_predictor.get_occupancy_trend(7)
        
        # Get sentiment analysis from ML - REAL DATA
        feedback_stats = db.session.query(
            Feedback.sentiment_label,
            func.count(Feedback.id)
        ).group_by(Feedback.sentiment_label).all()
        
        # Convert to dictionary
        sentiment_data = {label: count for label, count in feedback_stats}
        
        # Get recent complaints
        recent_complaints = Complaint.query.order_by(Complaint.created_at.desc()).limit(5).all()
        
        # Calculate revenue (simplified)
        monthly_revenue = db.session.query(func.sum(Booking.total_amount)).filter(
            Booking.status.in_(['confirmed', 'completed'])
        ).scalar() or 0
        
        # Get complaint statistics by category and find top category - FIXED SECTION
        complaint_categories_data = db.session.query(
            Complaint.category,
            func.count(Complaint.id)
        ).group_by(Complaint.category).all()
        
        # Convert to dictionary and find top category
        complaint_categories_dict = dict(complaint_categories_data)
        top_category = None
        if complaint_categories_dict:
            top_category = max(complaint_categories_dict.items(), key=lambda x: x[1])[0]
        
        # Get complaint statistics by priority
        complaint_priorities = db.session.query(
            Complaint.priority,
            func.count(Complaint.id)
        ).group_by(Complaint.priority).all()
        
        return render_template('admin/dashboard.html',
                            total_students=total_students,
                            total_rooms=total_rooms,
                            available_rooms=available_rooms,
                            total_complaints=total_complaints,
                            pending_complaints=pending_complaints,
                            total_feedback=total_feedback,
                            monthly_revenue=monthly_revenue,
                            current_occupancy=current_occupancy,
                            occupancy_trend=occupancy_trend,
                            feedback_stats=sentiment_data,
                            recent_complaints=recent_complaints,
                            complaint_categories=complaint_categories_dict,  # Use the new variable
                            top_category=top_category,  # Added
                            complaint_priorities=dict(complaint_priorities))
    
    @app.route('/admin/students')
    @login_required
    def admin_students():
        if not current_user.is_admin():
            return redirect(url_for('student_dashboard'))
        
        students = Student.query.all()
        return render_template('admin/students.html', students=students)
    
    @app.route('/admin/rooms', methods=['GET', 'POST'])
    @login_required
    def admin_rooms():
        if not current_user.is_admin():
            return redirect(url_for('student_dashboard'))
        
        form = RoomForm()
        rooms = Room.query.all()
        
        if form.validate_on_submit():
            try:
                room = Room(
                    room_number=form.room_number.data,
                    seater_type=form.seater_type.data,
                    monthly_fee=form.monthly_fee.data,
                    amenities=form.amenities.data
                )
                
                db.session.add(room)
                db.session.commit()
                
                flash('Room added successfully!', 'success')
                return redirect(url_for('admin_rooms'))
            
            except Exception as e:
                db.session.rollback()
                flash('Error adding room. Please try again.', 'danger')
        
        return render_template('admin/rooms.html', form=form, rooms=rooms)
    
    @app.route('/admin/complaints')
    @login_required
    def admin_complaints():
        if not current_user.is_admin():
            return redirect(url_for('student_dashboard'))
        
        complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()
        bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
        current_occupancy = occupancy_predictor.predict_occupancy()
        
        return render_template('admin/complaints.html', 
                             complaints=complaints, 
                             bookings=bookings,
                             current_occupancy=current_occupancy,
                             booking_approver=booking_approver)
    
    @app.route('/admin/update-complaint/<int:complaint_id>', methods=['POST'])
    @login_required
    def update_complaint_status(complaint_id):
        if not current_user.is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        complaint = Complaint.query.get_or_404(complaint_id)
        new_status = request.json.get('status')
        admin_notes = request.json.get('admin_notes', '')
        
        if new_status in ['new', 'in_progress', 'resolved', 'closed']:
            complaint.status = new_status
            complaint.admin_notes = admin_notes
            
            if new_status in ['resolved', 'closed']:
                complaint.resolved_at = datetime.utcnow()
            
            db.session.commit()
            return jsonify({'message': 'Complaint status updated successfully'})
        
        return jsonify({'error': 'Invalid status'}), 400
    
    # Admin booking management routes
    @app.route('/admin/auto-approve-bookings', methods=['POST'])
    @login_required
    def auto_approve_bookings():
        if not current_user.is_admin():
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        try:
            approved_count = booking_approver.auto_approve_pending_bookings()
            return jsonify({
                'success': True,
                'approved_count': approved_count,
                'message': f'Auto-approved {approved_count} bookings'
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/admin/approve-booking/<int:booking_id>', methods=['POST'])
    @login_required
    def approve_booking(booking_id):
        if not current_user.is_admin():
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        try:
            booking = Booking.query.get_or_404(booking_id)
            booking.status = 'confirmed'
            booking.room.is_available = False
            
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Booking approved'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/admin/reject-booking/<int:booking_id>', methods=['POST'])
    @login_required
    def reject_booking(booking_id):
        if not current_user.is_admin():
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        try:
            booking = Booking.query.get_or_404(booking_id)
            booking.status = 'cancelled'
            
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Booking rejected'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/admin/feedback-analysis')
    @login_required
    def feedback_analysis():
        if not current_user.is_admin():
            return redirect(url_for('student_dashboard'))
        
        feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
        
        # Analyze feedback statistics
        total_feedback = len(feedbacks)
        positive_feedback = len([f for f in feedbacks if f.sentiment_label == 'positive'])
        negative_feedback = len([f for f in feedbacks if f.sentiment_label == 'negative'])
        neutral_feedback = len([f for f in feedbacks if f.sentiment_label == 'neutral'])
        
        # Average rating
        avg_rating = sum([f.rating for f in feedbacks]) / total_feedback if total_feedback > 0 else 0
        
        return render_template('admin/feedback_analysis.html',
                             feedbacks=feedbacks,
                             total_feedback=total_feedback,
                             positive_feedback=positive_feedback,
                             negative_feedback=negative_feedback,
                             neutral_feedback=neutral_feedback,
                             avg_rating=round(avg_rating, 2))
    
    @app.route('/admin/ml-insights')
    @login_required
    def ml_insights():
        if not current_user.is_admin():
            return redirect(url_for('student_dashboard'))
        
        # Get occupancy predictions
        occupancy_trend = occupancy_predictor.get_occupancy_trend(30)
        
        # Get complaint statistics by category and priority
        complaint_stats = db.session.query(
            Complaint.category,
            Complaint.priority,
            func.count(Complaint.id)
        ).group_by(Complaint.category, Complaint.priority).all()
        
        # Get sentiment trends
        sentiment_trends = db.session.query(
            func.date(Feedback.created_at),
            Feedback.sentiment_label,
            func.count(Feedback.id)
        ).group_by(func.date(Feedback.created_at), Feedback.sentiment_label).all()
        
        # Get ML model performance info
        ml_models_info = {
            'sentiment_analyzer': sentiment_analyzer.is_trained,
            'occupancy_predictor': occupancy_predictor.is_trained,
            'complaint_classifier': complaint_classifier.is_trained,
            'booking_approver': booking_approver.is_trained
        }
        
        return render_template('admin/ml_insights.html',
                             occupancy_trend=occupancy_trend,
                             complaint_stats=complaint_stats,
                             sentiment_trends=sentiment_trends,
                             ml_models_info=ml_models_info)
    
    @app.route('/admin/reports', methods=['GET', 'POST'])
    @login_required
    def admin_reports():
        if not current_user.is_admin():
            return redirect(url_for('student_dashboard'))
        
        # Handle report generation requests
        report_type = request.args.get('type', 'all')
        
        # Generate report data
        total_students = Student.query.count()
        total_rooms = Room.query.count()
        total_complaints = Complaint.query.count()
        total_feedback = Feedback.query.count()
        
        # Recent activities
        recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(10).all()
        recent_complaints = Complaint.query.order_by(Complaint.created_at.desc()).limit(10).all()
        
        # Financial data
        total_revenue = db.session.query(func.sum(Booking.total_amount)).filter(
            Booking.status.in_(['confirmed', 'completed'])
        ).scalar() or 0
        
        # Handle PDF generation
        if request.method == 'POST':
            if 'generate_pdf' in request.form:
                return generate_pdf_report(report_type)
            elif 'generate_excel' in request.form:
                return generate_excel_report(report_type)
        
        return render_template('admin/reports.html',
                            total_students=total_students,
                            total_rooms=total_rooms,
                            total_complaints=total_complaints,
                            total_feedback=total_feedback,
                            total_revenue=total_revenue,
                            recent_bookings=recent_bookings,
                            recent_complaints=recent_complaints,
                            report_type=report_type)

    def generate_pdf_report(report_type):
        """Generate PDF report (placeholder - you'll need to implement this)"""
        flash('PDF report generation will be implemented soon!', 'info')
        return redirect(url_for('admin_reports'))

    def generate_excel_report(report_type):
        """Generate Excel report (placeholder - you'll need to implement this)"""
        flash('Excel report generation will be implemented soon!', 'info')
        return redirect(url_for('admin_reports'))
    
    @app.route('/admin/settings')
    @login_required
    def admin_settings():
        if not current_user.is_admin():
            return redirect(url_for('student_dashboard'))
        
        return render_template('admin/settings.html')
    
    # ===== API ROUTES =====
    @app.route('/api/occupancy-data')
    @login_required
    def api_occupancy_data():
        if not current_user.is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        trend = occupancy_predictor.get_occupancy_trend(30)
        return jsonify(trend)
    
    @app.route('/api/sentiment-data')
    @login_required
    def api_sentiment_data():
        if not current_user.is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        sentiment_data = db.session.query(
            Feedback.sentiment_label,
            func.count(Feedback.id).label('count')
        ).group_by(Feedback.sentiment_label).all()
        
        data = {label: count for label, count in sentiment_data}
        return jsonify(data)
    
    @app.route('/api/complaint-stats')
    @login_required
    def api_complaint_stats():
        if not current_user.is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Category stats
        category_stats = db.session.query(
            Complaint.category,
            func.count(Complaint.id).label('count')
        ).group_by(Complaint.category).all()
        
        # Priority stats
        priority_stats = db.session.query(
            Complaint.priority,
            func.count(Complaint.id).label('count')
        ).group_by(Complaint.priority).all()
        
        return jsonify({
            'categories': dict(category_stats),
            'priorities': dict(priority_stats)
        })
    
    return app

# ===== TEMPORARY FIX FOR COMPLAINT CATEGORIZATION =====

    @app.route('/debug/ml-status')
    def debug_ml_status():
        """Check if ML classification is working"""
        print("🔍 Checking ML Model Status...")
        
        # Test the complaint classifier
        test_complaints = [
            "WiFi not working in my room",
            "Room is very dirty and needs cleaning", 
            "Water leakage in bathroom",
            "Bed is broken and needs repair",
            "Light not working in room"
        ]
        
        results = []
        for complaint in test_complaints:
            try:
                classification = complaint_classifier.classify_complaint(complaint, "")
                results.append({
                    'complaint': complaint,
                    'category': classification['category'],
                    'priority': classification['priority']
                })
                print(f"📝 '{complaint}' → Category: {classification['category']}, Priority: {classification['priority']}")
            except Exception as e:
                print(f"❌ Error classifying '{complaint}': {e}")
        
        return jsonify({
            'model_trained': complaint_classifier.is_trained,
            'test_results': results
        })

    @app.route('/fix-complaints-categories')
    def fix_complaints_categories():
        """FIX ALL EXISTING COMPLAINTS - Run this once"""
        try:
            complaints = Complaint.query.all()
            fixed_count = 0
            
            for complaint in complaints:
                old_category = complaint.category
                old_priority = complaint.priority
                
                # Get correct category and priority
                new_category = get_manual_category(complaint.title, complaint.description)
                new_priority = get_manual_priority(complaint.title, complaint.description)
                
                if old_category != new_category or old_priority != new_priority:
                    complaint.category = new_category
                    complaint.priority = new_priority
                    fixed_count += 1
                    print(f"🔄 Fixed: '{complaint.title}' → {old_category}→{new_category}, {old_priority}→{new_priority}")
            
            db.session.commit()
            return f"✅ SUCCESS: Fixed {fixed_count} complaints! Categories are now correct."
        
        except Exception as e:
            db.session.rollback()
            return f"❌ ERROR: {e}"

    def get_manual_category(title, description):
        """Manual mapping for categories"""
        text = (title + " " + description).lower()
        
        if any(word in text for word in ['wifi', 'internet', 'network', 'online', 'connection']):
            return 'internet'
        elif any(word in text for word in ['clean', 'dirty', 'dust', 'sweep', 'mop', 'hygiene']):
            return 'cleaning' 
        elif any(word in text for word in ['water', 'leak', 'pipe', 'bathroom', 'tap', 'drain']):
            return 'plumbing'
        elif any(word in text for word in ['bed', 'chair', 'table', 'furniture', 'cupboard', 'almirah']):
            return 'furniture'
        elif any(word in text for word in ['light', 'fan', 'switch', 'electrical', 'power', 'socket']):
            return 'electrical'
        else:
            return 'other'

    def get_manual_priority(title, description):
        """Manual mapping for priorities"""
        text = (title + " " + description).lower()
        
        if any(word in text for word in ['emergency', 'urgent', 'immediately', 'critical', 'flood', 'fire', 'wifi', 'internet', 'exam', 'study']):
            return 'high'
        elif any(word in text for word in ['not working', 'broken', 'issue', 'problem', 'leak']):
            return 'medium'
        else:
            return 'low'
# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)