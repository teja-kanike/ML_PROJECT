import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
from datetime import datetime, timedelta

class OccupancyPredictor:
    def __init__(self):
        self.model = None
        self.is_trained = False
    
    def generate_training_data(self):
        """Generate training data for occupancy prediction"""
        np.random.seed(42)
        
        # Generate data for the past year
        start_date = datetime.now() - timedelta(days=365)
        dates = [start_date + timedelta(days=x) for x in range(365)]
        
        data = []
        for date in dates:
            # Seasonal patterns
            month = date.month
            day_of_week = date.weekday()
            
            # Higher occupancy during academic months
            if month in [8, 9, 10, 11, 1, 2, 3, 4]:
                base_occupancy = np.random.randint(70, 95)
            else:
                base_occupancy = np.random.randint(30, 60)
            
            # Weekend effect
            if day_of_week >= 5:
                base_occupancy -= np.random.randint(5, 15)
            
            # Random noise
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
        """Train the occupancy prediction model"""
        try:
            # Generate training data
            df = self.generate_training_data()
            
            # Prepare features and target
            X = df[['month', 'day_of_week', 'is_weekend', 'is_academic_month']]
            y = df['occupancy_rate']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train model
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
            print(f"❌ Error training occupancy model: {e}")
    
    def load_model(self):
        """Load the trained model"""
        try:
            model_path = 'ml_models/trained_models/occupancy_model.pkl'
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                self.is_trained = True
                return True
            return False
        except Exception as e:
            print(f"Error loading occupancy model: {e}")
            return False
    
    def predict_occupancy(self, date=None):
        """Predict occupancy rate for a given date"""
        if date is None:
            date = datetime.now()
        
        if not self.is_trained and not self.load_model():
            return self._calculate_current_occupancy()
        
        try:
            # Prepare features for prediction
            features = np.array([[
                date.month,
                date.weekday(),
                1 if date.weekday() >= 5 else 0,
                1 if date.month in [8, 9, 10, 11, 1, 2, 3, 4] else 0
            ]])
            
            prediction = self.model.predict(features)[0]
            return max(0, min(100, prediction))
        
        except Exception as e:
            print(f"Error in occupancy prediction: {e}")
            return self._calculate_current_occupancy()
    
    def _calculate_current_occupancy(self):
        """Calculate current actual occupancy rate"""
        # For now, return a default value since we don't have database access
        return 75.0  # Default occupancy rate
    
    def get_occupancy_trend(self, days=30):
        """Get occupancy trend for next days"""
        trend = []
        current_date = datetime.now()
        
        for i in range(days):
            date = current_date + timedelta(days=i)
            predicted_occupancy = self.predict_occupancy(date)
            trend.append({
                'date': date.strftime('%Y-%m-%d'),
                'occupancy_rate': round(predicted_occupancy, 2)
            })
        
        return trend

# Initialize global occupancy predictor
occupancy_predictor = OccupancyPredictor()