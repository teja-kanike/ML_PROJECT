# ML_PROJECT
Smart Hostel Management
#template
hostel_management/
│
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── run.py                          # Application runner
│
├── database/                       # Database related files
│   ├── _init_.py
│   ├── setup_database.py          # Database setup script
│   ├── fix_database.py            # Database fix script
│   ├── fix_passwords.py           # Password reset script
│   └── recreate_database.py       # Complete DB recreation
│
├── ml_models/                      # Machine Learning models
│   ├── _init_.py
│   ├── sentiment_analyzer.py      # Feedback sentiment analysis
│   ├── occupancy_predictor.py     # Room occupancy prediction
│   ├── complaint_classifier.py    # Complaint priority classification
│   ├── student_behavior.py        # Student behavior analysis (future)
│   └── trained_models/            # Saved ML models
│       ├── sentiment_model.pkl
│       ├── occupancy_model.pkl
│       └── complaint_classifier.pkl
│
├── static/                         # Static files (CSS, JS, Images)
│   ├── css/
│   │   ├── style.css
│   │   ├── dashboard.css
│   │   └── responsive.css
│   ├── js/
│   │   ├── main.js
│   │   ├── dashboard.js
│   │   ├── charts.js
│   │   └── forms.js
│   ├── images/
│   │   ├── logo.png
│   │   ├── favicon.ico
│   │   ├── hostel-building.jpg
│   │   └── default-avatar.png
│   └── vendors/                   # Third-party libraries
│       ├── bootstrap/
│       ├── fontawesome/
│       └── chartjs/
│
├── templates/                      # HTML templates
│   ├── base.html                  # Base template
│   ├── index.html                 # Homepage
│   │
│   ├── auth/                      # Authentication templates
│   │   ├── login.html
│   │   ├── register.html
│   │   └── forgot_password.html
│   │
│   ├── student/                   # Student dashboard templates
│   │   ├── dashboard.html
│   │   ├── profile.html
│   │   ├── rooms.html
│   │   ├── book_room.html
│   │   ├── bookings.html
│   │   ├── complaints.html
│   │   ├── feedback.html
│   │   └── payment.html
│   │
│   ├── admin/                     # Admin dashboard templates
│   │   ├── dashboard.html
│   │   ├── students.html
│   │   ├── rooms.html
│   │   ├── complaints.html
│   │   ├── feedback_analysis.html
│   │   ├── ml_insights.html      # ML analytics dashboard
│   │   ├── reports.html
│   │   └── settings.html
│   │
│   └── warden/                    # Warden templates (future)
│       ├── dashboard.html
│       └── complaints.html
│
├── utils/                         # Utility functions
│   ├── _init_.py
│   ├── helpers.py                 # Helper functions
│   ├── validators.py              # Form validators
│   ├── email_service.py           # Email notifications
│   └── report_generator.py        # PDF report generation
│
├── models/                        # Database models (alternative structure)
│   ├── _init_.py
│   ├── user.py
│   ├── student.py
│   ├── room.py
│   ├── booking.py
│   ├── complaint.py
│   └── feedback.py
│
├── routes/                        # Route handlers (alternative structure)
│   ├── _init_.py
│   ├── auth.py
│   ├── student.py
│   ├── admin.py
│   └── api.py                    # API endpoints
│
├── forms/                         # WTForms classes
│   ├── _init_.py
│   ├── auth_forms.py
│   ├── student_forms.py
│   └── admin_forms.py
│
├── tests/                         # Test cases
│   ├── _init_.py
│   ├── test_models.py
│   ├── test_routes.py
│   ├── test_forms.py
│   └── test_ml_models.py
│
├── logs/                          # Application logs
│   ├── app.log
│   ├── error.log
│   └── access.log
│
├── uploads/                       # File uploads
│   ├── student_documents/
│   ├── complaint_photos/
│   └── reports/
│
├── docs/                          # Documentation
│   ├── README.md
│   ├── INSTALLATION.md
│   ├── API_DOCUMENTATION.md
│   └── USER_GUIDE.md
│
└── .env                          # Environment variables (gitignored)
