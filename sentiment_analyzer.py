import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

class SentimentAnalyzer:
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
            "Reasonable pricing", "Happy with the amenities"
        ]
        
        negative_feedback = [
            "Poor maintenance", "Dirty rooms and bathrooms",
            "Unfriendly staff", "Bad food quality",
            "No proper cleaning", "Issues with electricity",
            "Water problems frequently", "Overpriced for facilities",
            "Poor security measures", "Uncomfortable beds"
        ]
        
        neutral_feedback = [
            "Average facilities", "Room is okay",
            "Food is acceptable", "Standard maintenance",
            "Nothing special", "Could be better",
            "Satisfactory overall", "Meets basic needs"
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
    
    def load_model(self):
        """Load the trained model"""
        try:
            model_path = 'ml_models/trained_models/sentiment_model.pkl'
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                self.is_trained = True
                return True
            return False
        except Exception as e:
            print(f"Error loading sentiment model: {e}")
            return False
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of given text"""
        if not self.is_trained and not self.load_model():
            return self._analyze_with_textblob(text)
        
        try:
            prediction = self.model.predict([text])[0]
            confidence = np.max(self.model.predict_proba([text]))
            
            # Calculate sentiment score
            if TEXTBLOB_AVAILABLE:
                blob = TextBlob(text)
                sentiment_score = blob.sentiment.polarity
            else:
                sentiment_score = 0.0
            
            return {
                'label': prediction,
                'score': sentiment_score,
                'confidence': confidence
            }
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return self._analyze_with_textblob(text)
    
    def _analyze_with_textblob(self, text):
        """Fallback sentiment analysis using TextBlob"""
        if TEXTBLOB_AVAILABLE:
            try:
                blob = TextBlob(text)
                sentiment_score = blob.sentiment.polarity
                
                if sentiment_score > 0.1:
                    label = 'positive'
                elif sentiment_score < -0.1:
                    label = 'negative'
                else:
                    label = 'neutral'
                
                return {
                    'label': label,
                    'score': sentiment_score,
                    'confidence': 0.8
                }
            except:
                pass
        
        # Final fallback
        return {
            'label': 'neutral',
            'score': 0.0,
            'confidence': 0.5
        }

# Initialize global sentiment analyzer
sentiment_analyzer = SentimentAnalyzer()