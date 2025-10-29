from .sentiment_analyzer import sentiment_analyzer
from .occupancy_predictor import occupancy_predictor
from .complaint_classifier import complaint_classifier

# Initialize all ML models
def initialize_ml_models():
    """Initialize and train all ML models"""
    print("Initializing ML Models...")
    
    try:
        # Train sentiment analyzer
        print("Training Sentiment Analyzer...")
        sentiment_analyzer.train_model()
        
        # Train occupancy predictor
        print("Training Occupancy Predictor...")
        occupancy_predictor.train_model()
        
        # Train complaint classifier
        print("Training Complaint Classifier...")
        complaint_classifier.train_model()
        
        print("All ML models trained successfully!")
        
    except Exception as e:
        print(f"Error initializing ML models: {e}")

def load_ml_models():
    """Load pre-trained ML models"""
    print("Loading ML Models...")
    
    try:
        sentiment_loaded = sentiment_analyzer.load_model()
        occupancy_loaded = occupancy_predictor.load_model()
        complaint_loaded = complaint_classifier.load_model()
        
        loaded_count = sum([sentiment_loaded, occupancy_loaded, complaint_loaded])
        print(f"Loaded {loaded_count}/3 ML models")
        
        return loaded_count == 3
        
    except Exception as e:
        print(f"Error loading ML models: {e}")
        return False

# Export models
__all__ = ['sentiment_analyzer', 'occupancy_predictor', 'complaint_classifier', 
           'initialize_ml_models', 'load_ml_models']