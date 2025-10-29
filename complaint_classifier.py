import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

class ComplaintClassifier:
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
        """Train the complaint classification model"""
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
    
    def load_model(self):
        """Load the trained model"""
        try:
            model_path = 'ml_models/trained_models/complaint_classifier.pkl'
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                self.is_trained = True
                return True
            return False
        except Exception as e:
            print(f"Error loading complaint classifier: {e}")
            return False
    
    def classify_complaint(self, title, description):
        """Classify complaint and determine priority"""
        if not self.is_trained and not self.load_model():
            return self._fallback_classification(title, description)
        
        try:
            text = f"{title} {description}"
            
            # Predict category
            category = self.model.predict([text])[0]
            probability = np.max(self.model.predict_proba([text]))
            
            # Determine priority based on keywords
            priority_keywords = {
                'high': ['emergency', 'urgent', 'danger', 'fire', 'flood', 'electrocution', 'gas'],
                'medium': ['leak', 'broken', 'not working', 'issue', 'problem'],
                'low': ['clean', 'dust', 'dirty', 'maintenance']
            }
            
            text_lower = text.lower()
            priority = 'low'
            
            for high_word in priority_keywords['high']:
                if high_word in text_lower:
                    priority = 'high'
                    break
            
            if priority == 'low':
                for medium_word in priority_keywords['medium']:
                    if medium_word in text_lower:
                        priority = 'medium'
                        break
            
            return {
                'category': category,
                'priority': priority,
                'confidence': probability
            }
        
        except Exception as e:
            print(f"Error in complaint classification: {e}")
            return self._fallback_classification(title, description)
    
    def _fallback_classification(self, title, description):
        """Fallback classification method"""
        text = f"{title} {description}".lower()
        
        # Simple keyword-based classification
        if any(word in text for word in ['light', 'power', 'electric', 'socket', 'fan', 'ac']):
            category = 'electrical'
        elif any(word in text for word in ['water', 'tap', 'toilet', 'drain', 'pipe', 'bathroom']):
            category = 'plumbing'
        elif any(word in text for word in ['clean', 'dirty', 'dust', 'garbage']):
            category = 'cleaning'
        elif any(word in text for word in ['bed', 'chair', 'table', 'furniture', 'cupboard']):
            category = 'furniture'
        else:
            category = 'other'
        
        # Priority determination
        if any(word in text for word in ['emergency', 'urgent', 'danger', 'fire']):
            priority = 'high'
        elif any(word in text for word in ['broken', 'leak', 'not working']):
            priority = 'medium'
        else:
            priority = 'low'
        
        return {
            'category': category,
            'priority': priority,
            'confidence': 0.7
        }

# Initialize global complaint classifier
complaint_classifier = ComplaintClassifier()