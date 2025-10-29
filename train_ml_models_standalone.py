#!/usr/bin/env python3
"""
Standalone ML Models Training Script
This script trains ML models without requiring the full Flask app
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingRegressor
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error, r2_score
import joblib
import nltk

# Download NLTK data
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Downloading NLTK stopwords...")
    nltk.download('stopwords')

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    print("TextBlob not available. Using fallback methods.")
    TEXTBLOB_AVAILABLE = False

class StandaloneSentimentAnalyzer:
    def __init__(self):
        self.model = None
        self.is_trained = False
        
    def generate_training_data(self):
        """Generate training data for sentiment analysis"""
        positive_feedback = [
            "Great facilities and clean rooms", "Excellent staff service",
            "Very comfortable living environment", "Good food quality",
            "Well maintained hostel", "Friendly wardens",
            "Clean bathrooms and common areas", "Good security",
            "Reasonable pricing", "Happy with the amenities",
            "Outstanding maintenance service", "Perfect location and environment",
            "Wonderful experience overall", "Staff is very helpful",
            "Rooms are spacious and clean", "Excellent Wi-Fi connection"
        ]
        
        negative_feedback = [
            "Poor maintenance", "Dirty rooms and bathrooms",
            "Unfriendly staff", "Bad food quality",
            "No proper cleaning", "Issues with electricity",
            "Water problems frequently", "Overpriced for facilities",
            "Poor security measures", "Uncomfortable beds",
            "Terrible internet connection", "No hot water available",
            "Broken furniture everywhere", "Noise pollution issues"
        ]
        
        neutral_feedback = [
            "Average facilities", "Room is okay",
            "Food is acceptable", "Standard maintenance",
            "Nothing special", "Could be better",
            "Satisfactory overall", "Meets basic needs",
            "Neither good nor bad", "Room is average size",
            "Facilities are standard", "Acceptable for price"
        ]
        
        texts = positive_feedback + negative_feedback + neutral_feedback
        labels = (['positive'] * len(positive_feedback) + 
                 ['negative'] * len(negative_feedback) + 
                 ['neutral'] * len(neutral_feedback))
        
        return texts, labels
    
    def train_model(self):
        """Train the sentiment analysis model"""
        try:
            texts, labels = self.generate_training_data()
            
            X_train, X_test, y_train, y_test = train_test_split(
                texts, labels, test_size=0.2, random_state=42, stratify=labels
            )
            
            self.model = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=1000, stop_words='english')),
                ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
            ])
            
            self.model.fit(X_train, y_train)
            self.is_trained = True
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            print(f"✅ Sentiment Analyzer trained! Accuracy: {accuracy:.4f}")
            
            # Save model
            os.makedirs('ml_models/trained_models', exist_ok=True)
            joblib.dump(self.model, 'ml_models/trained_models/sentiment_model.pkl')
            
        except Exception as e:
            print(f"❌ Error training sentiment model: {e}")

class StandaloneComplaintClassifier:
    def __init__(self):
        self.model = None
        self.is_trained = False
        
    def generate_training_data(self):
        """Generate training data for complaint classification"""
        electrical_complaints = [
            "Lights not working in room", "Power socket not functioning",
            "Fan not working properly", "AC not cooling",
            "Electrical wiring issue", "Switch board problem",
            "Power cut in room", "Bulb needs replacement"
        ]
        
        plumbing_complaints = [
            "Water tap leaking", "Toilet not flushing",
            "Drainage blockage", "No water supply",
            "Bathroom pipe leakage", "Hot water not available",
            "Water pressure low", "Sink clogged"
        ]
        
        cleaning_complaints = [
            "Room needs cleaning", "Bathroom is dirty",
            "Common area not cleaned", "Garbage not collected",
            "Bed sheets need changing", "Dust accumulation",
            "Floor needs mopping", "Windows are dirty"
        ]
        
        furniture_complaints = [
            "Bed broken needs repair", "Chair is damaged",
            "Study table wobbling", "Cupboard lock not working",
            "Mattress needs replacement", "Wardrobe door broken",
            "Desk drawer stuck", "Bookshelf unstable"
        ]
        
        texts = (electrical_complaints + plumbing_complaints + 
                cleaning_complaints + furniture_complaints)
        
        categories = (['electrical'] * len(electrical_complaints) +
                     ['plumbing'] * len(plumbing_complaints) +
                     ['cleaning'] * len(cleaning_complaints) +
                     ['furniture'] * len(furniture_complaints))
        
        return texts, categories
    
    def train_model(self):
        """Train the complaint classifier"""
        try:
            texts, categories = self.generate_training_data()
            
            X_train, X_test, y_train, y_test = train_test_split(
                texts, categories, test_size=0.2, random_state=42, stratify=categories
            )
            
            self.model = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=500, stop_words='english')),
                ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
            ])
            
            self.model.fit(X_train, y_train)
            self.is_trained = True
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            print(f"✅ Complaint Classifier trained! Accuracy: {accuracy:.4f}")
            
            # Save model
            os.makedirs('ml_models/trained_models', exist_ok=True)
            joblib.dump(self.model, 'ml_models/trained_models/complaint_classifier.pkl')
            
        except Exception as e:
            print(f"❌ Error training complaint classifier: {e}")

class StandaloneOccupancyPredictor:
    def __init__(self):
        self.model = None
        self.is_trained = False
        
    def generate_training_data(self):
        """Generate training data for occupancy prediction"""
        np.random.seed(42)
        
        # Generate data for the past year
        dates = pd.date_range(start='2022-01-01', end='2023-12-31', freq='D')
        
        data = []
        for date in dates:
            month = date.month
            day_of_week = date.weekday()
            
            # Seasonal patterns
            if month in [8, 9, 10, 11, 1, 2, 3, 4]:
                base_occupancy = np.random.randint(70, 95)
            else:
                base_occupancy = np.random.randint(30, 60)
            
            # Weekend effect
            if day_of_week >= 5:
                base_occupancy -= np.random.randint(5, 15)
            
            noise = np.random.randint(-5, 5)
            occupancy_rate = max(10, min(100, base_occupancy + noise))
            
            data.append({
                'month': month,
                'day_of_week': day_of_week,
                'is_weekend': 1 if day_of_week >= 5 else 0,
                'is_academic_month': 1 if month in [8, 9, 10, 11, 1, 2, 3, 4] else 0,
                'occupancy_rate': occupancy_rate
            })
        
        return pd.DataFrame(data)
    
    def train_model(self):
        """Train the occupancy predictor"""
        try:
            df = self.generate_training_data()
            
            X = df[['month', 'day_of_week', 'is_weekend', 'is_academic_month']]
            y = df['occupancy_rate']
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)
            self.is_trained = True
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            print(f"✅ Occupancy Predictor trained! MAE: {mae:.4f}, R²: {r2:.4f}")
            
            # Save model
            os.makedirs('ml_models/trained_models', exist_ok=True)
            joblib.dump(self.model, 'ml_models/trained_models/occupancy_model.pkl')
            
        except Exception as e:
            print(f"❌ Error training occupancy predictor: {e}")

def main():
    """Main training function"""
    print("🚀 Starting Standalone ML Models Training...")
    
    # Create directories
    os.makedirs('ml_models/trained_models', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Train models
    print("\n📊 Training Sentiment Analyzer...")
    sentiment_analyzer = StandaloneSentimentAnalyzer()
    sentiment_analyzer.train_model()
    
    print("\n📋 Training Complaint Classifier...")
    complaint_classifier = StandaloneComplaintClassifier()
    complaint_classifier.train_model()
    
    print("\n🏨 Training Occupancy Predictor...")
    occupancy_predictor = StandaloneOccupancyPredictor()
    occupancy_predictor.train_model()
    
    print("\n🎉 All ML models trained successfully!")
    print("\n📁 Models saved in: ml_models/trained_models/")
    print("   - sentiment_model.pkl")
    print("   - complaint_classifier.pkl") 
    print("   - occupancy_model.pkl")

if __name__ == '__main__':
    main()