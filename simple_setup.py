import mysql.connector
from werkzeug.security import generate_password_hash

def setup_database_simple():
    """Simple database setup without complex imports"""
    
    # Database configuration
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'hostel_management',
        'port': 3306
    }
    
    try:
        # Connect to MySQL server
        conn = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            port=config['port']
        )
        cursor = conn.cursor()
        
        # Drop database if exists
        cursor.execute(f"DROP DATABASE IF EXISTS {config['database']}")
        print("✅ Dropped existing database")
        
        # Create database
        cursor.execute(f"CREATE DATABASE {config['database']}")
        cursor.execute(f"USE {config['database']}")
        print("✅ Created new database")
        
        # Create tables
        tables = [
            # Users table
            """
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('student', 'admin', 'warden') DEFAULT 'student',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Students table
            """
            CREATE TABLE students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
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
            
            # Rooms table
            """
            CREATE TABLE rooms (
                id INT AUTO_INCREMENT PRIMARY KEY,
                room_number VARCHAR(10) UNIQUE NOT NULL,
                seater_type ENUM('1', '2', '3', '4') NOT NULL,
                monthly_fee DECIMAL(10,2) NOT NULL,
                amenities TEXT,
                is_available BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Bookings table
            """
            CREATE TABLE bookings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                room_id INT NOT NULL,
                booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                check_in_date DATE NOT NULL,
                check_out_date DATE NOT NULL,
                food_option ENUM('veg', 'non-veg') DEFAULT 'veg',
                total_amount DECIMAL(10,2),
                status ENUM('pending', 'confirmed', 'cancelled', 'completed') DEFAULT 'pending',
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
            """,
            
            # Complaints table
            """
            CREATE TABLE complaints (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
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
            
            # Feedback table
            """
            CREATE TABLE feedback (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
                comments TEXT,
                category ENUM('facilities', 'food', 'staff', 'cleanliness', 'overall') NOT NULL,
                sentiment_score FLOAT,
                sentiment_label ENUM('positive', 'negative', 'neutral'),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
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
        admin_password = generate_password_hash('admin123')
        
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role) 
            VALUES ('admin', 'admin@hostel.com', %s, 'admin')
        """, (admin_password,))
        print("✅ Admin user created")
        
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
            INSERT INTO rooms (room_number, seater_type, monthly_fee, amenities) 
            VALUES (%s, %s, %s, %s)
        """, sample_rooms)
        print("✅ Sample rooms inserted")
        
        conn.commit()
        print("\n🎉 Database setup completed successfully!")
        print("\n🔑 Default Admin Login:")
        print("   Username: admin")
        print("   Password: admin123")
        
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
    print("🚀 Setting up Hostel Management Database...")
    print("⚠️  This will DELETE all existing data!")
    confirmation = input("Type 'YES' to continue: ")
    
    if confirmation == 'YES':
        setup_database_simple()
    else:
        print("❌ Operation cancelled.")