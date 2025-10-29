import mysql.connector
import os
import sys

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

def create_database():
    """Create database and tables for XAMPP"""
    try:
        # Connect to MySQL server (XAMPP default has no password)
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            port=Config.MYSQL_PORT
        )
        cursor = conn.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB}")
        cursor.execute(f"USE {Config.MYSQL_DB}")
        
        print("✅ Database created successfully!")
        
        # Create tables
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('student', 'admin', 'warden') DEFAULT 'student',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                full_name VARCHAR(100) NOT NULL,
                enrollment_no VARCHAR(20) UNIQUE NOT NULL,
                phone VARCHAR(15),
                address TEXT,
                stream VARCHAR(50),
                semester INT,
                date_of_birth DATE,
                guardian_name VARCHAR(100),
                guardian_phone VARCHAR(15),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS rooms (
                id INT AUTO_INCREMENT PRIMARY KEY,
                room_number VARCHAR(10) UNIQUE NOT NULL,
                seater_type ENUM('1', '2', '3', '4') NOT NULL,
                monthly_fee DECIMAL(10,2) NOT NULL,
                amenities TEXT,
                is_available BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS bookings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                room_id INT,
                booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                check_in_date DATE,
                check_out_date DATE,
                food_option ENUM('veg', 'non-veg') DEFAULT 'veg',
                total_amount DECIMAL(10,2),
                status ENUM('pending', 'confirmed', 'cancelled', 'completed') DEFAULT 'pending',
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS complaints (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                title VARCHAR(200) NOT NULL,
                description TEXT NOT NULL,
                category ENUM('electrical', 'plumbing', 'cleaning', 'furniture', 'other') DEFAULT 'other',
                priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
                status ENUM('new', 'in_progress', 'resolved', 'closed') DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP NULL,
                admin_notes TEXT,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                rating INT CHECK (rating >= 1 AND rating <= 5),
                comments TEXT,
                category ENUM('facilities', 'food', 'staff', 'cleanliness', 'overall'),
                sentiment_score FLOAT,
                sentiment_label ENUM('positive', 'negative', 'neutral'),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS payments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                booking_id INT,
                amount DECIMAL(10,2) NOT NULL,
                payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                payment_method ENUM('cash', 'online', 'card') DEFAULT 'cash',
                transaction_id VARCHAR(100),
                status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
                FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
            )
            """
        ]
        
        for i, table in enumerate(tables):
            try:
                cursor.execute(table)
                print(f"✅ Table {i+1} created successfully!")
            except mysql.connector.Error as e:
                print(f"❌ Error creating table {i+1}: {e}")
        
        # Insert default admin user
        from werkzeug.security import generate_password_hash
        admin_password = generate_password_hash('admin123')
        
        cursor.execute("""
            INSERT IGNORE INTO users (username, email, password_hash, role) 
            VALUES ('admin', 'admin@hostel.com', %s, 'admin')
        """, (admin_password,))
        
        # Insert sample rooms
        sample_rooms = [
            ('101', '1', 5000.00, 'AC, Attached Bathroom, Wi-Fi'),
            ('102', '2', 4000.00, 'Non-AC, Attached Bathroom, Wi-Fi'),
            ('103', '3', 3000.00, 'Non-AC, Common Bathroom'),
            ('104', '4', 2500.00, 'Non-AC, Common Bathroom'),
            ('201', '1', 5500.00, 'AC, Attached Bathroom, Wi-Fi, TV'),
            ('202', '2', 4500.00, 'Non-AC, Attached Bathroom, Wi-Fi'),
            ('203', '3', 3500.00, 'Non-AC, Common Bathroom, Study Table'),
            ('204', '4', 2800.00, 'Non-AC, Common Bathroom'),
        ]
        
        cursor.executemany("""
            INSERT IGNORE INTO rooms (room_number, seater_type, monthly_fee, amenities) 
            VALUES (%s, %s, %s, %s)
        """, sample_rooms)
        
        conn.commit()
        print("✅ Sample data inserted successfully!")
        print("\n🔑 Default Admin Login:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n🎉 Database setup completed successfully!")
        
    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
        print("\n💡 Make sure:")
        print("   1. XAMPP is running")
        print("   2. MySQL is started in XAMPP Control Panel")
        print("   3. MySQL password is correct (default is empty)")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    create_database()