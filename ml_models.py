import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, mean_squared_error
import joblib
import mysql.connector
from database import get_db_connection

class MLModels:
    def __init__(self):
        self.complaint_classifier = None
        self.room_occupancy_predictor = None
        self.feedback_analyzer = None
        self.load_models()
    
    def load_models(self):
        try:
            self.complaint_classifier = joblib.load('models/complaint_classifier.pkl')
            self.room_occupancy_predictor = joblib.load('models/room_predictor.pkl')
            self.feedback_analyzer = joblib.load('models/feedback_analyzer.pkl')
        except:
            print("Models not found, will train new ones")
    
    def train_complaint_classifier(self):
        """Train ML model to predict complaint categories"""
        connection = get_db_connection()
        if connection:
            query = """
            SELECT title, description, category, status 
            FROM complaints 
            WHERE category IS NOT NULL
            """
            df = pd.read_sql(query, connection)
            connection.close()
            
            if len(df) > 10:
                # Feature engineering
                df['text_length'] = df['description'].str.len()
                df['title_length'] = df['title'].str.len()
                df['has_urgent'] = df['title'].str.contains('urgent|emergency', case=False).astype(int)
                
                # Encode categorical variables
                le_category = LabelEncoder()
                df['category_encoded'] = le_category.fit_transform(df['category'])
                
                # Features and target
                X = df[['text_length', 'title_length', 'has_urgent']]
                y = df['category_encoded']
                
                # Train model
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                self.complaint_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
                self.complaint_classifier.fit(X_train, y_train)
                
                # Save model
                joblib.dump(self.complaint_classifier, 'models/complaint_classifier.pkl')
                joblib.dump(le_category, 'models/category_encoder.pkl')
                
                accuracy = accuracy_score(y_test, self.complaint_classifier.predict(X_test))
                return f"Complaint classifier trained with accuracy: {accuracy:.2f}"
            else:
                return "Not enough data to train complaint classifier"
        return "Database connection failed"
    
    def predict_complaint_category(self, title, description):
        """Predict complaint category using ML"""
        if self.complaint_classifier is None:
            return "maintenance"  # Default category
        
        try:
            features = pd.DataFrame([{
                'text_length': len(description),
                'title_length': len(title),
                'has_urgent': 1 if any(word in title.lower() for word in ['urgent', 'emergency', 'immediate']) else 0
            }])
            
            le_category = joblib.load('models/category_encoder.pkl')
            prediction = self.complaint_classifier.predict(features)[0]
            return le_category.inverse_transform([prediction])[0]
        except:
            return "maintenance"
    
    def train_room_occupancy_predictor(self):
        """Train ML model to predict room occupancy patterns"""
        connection = get_db_connection()
        if connection:
            query = """
            SELECT 
                MONTH(booking_date) as month,
                seater_type,
                COUNT(*) as bookings_count
            FROM bookings b
            JOIN rooms r ON b.room_id = r.id
            WHERE YEAR(booking_date) = YEAR(CURDATE())
            GROUP BY MONTH(booking_date), seater_type
            """
            df = pd.read_sql(query, connection)
            connection.close()
            
            if len(df) > 5:
                X = df[['month', 'seater_type']]
                y = df['bookings_count']
                
                self.room_occupancy_predictor = RandomForestRegressor(n_estimators=50, random_state=42)
                self.room_occupancy_predictor.fit(X, y)
                
                joblib.dump(self.room_occupancy_predictor, 'models/room_predictor.pkl')
                
                return "Room occupancy predictor trained successfully"
            else:
                return "Not enough data for room occupancy prediction"
        return "Database connection failed"
    
    def predict_room_demand(self, month, seater_type):
        """Predict room demand for given month and seater type"""
        if self.room_occupancy_predictor is None:
            return 5  # Default prediction
        
        try:
            features = pd.DataFrame([{'month': month, 'seater_type': seater_type}])
            return int(self.room_occupancy_predictor.predict(features)[0])
        except:
            return 5
    
    def analyze_feedback_sentiment(self, comments):
        """Simple sentiment analysis based on keyword matching"""
        positive_words = ['good', 'excellent', 'happy', 'satisfied', 'great', 'nice', 'comfortable', 'clean']
        negative_words = ['bad', 'poor', 'terrible', 'unhappy', 'dissatisfied', 'dirty', 'broken', 'issue']
        
        comment_lower = comments.lower()
        positive_count = sum(1 for word in positive_words if word in comment_lower)
        negative_count = sum(1 for word in negative_words if word in comment_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'

# Create models directory
import os
os.makedirs('models', exist_ok=True)