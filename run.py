from app import app

if __name__ == '__main__':
    print("🚀 Starting Hostel Management System...")
    print("📍 Access the application at: http://localhost:5000")
    print("🔑 Admin Login: admin / admin123")
    app.run(debug=True, host='0.0.0.0', port=5000)