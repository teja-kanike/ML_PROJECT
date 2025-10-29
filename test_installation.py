#!/usr/bin/env python3
"""Test if all dependencies are installed correctly"""

try:
    import flask
    import flask_sqlalchemy
    import flask_login
    import sklearn
    import pandas as pd
    import numpy as np
    from textblob import TextBlob
    import nltk
    import joblib
    
    print("✅ All core dependencies installed successfully!")
    
    # Test TextBlob
    blob = TextBlob("This is a test")
    print(f"✅ TextBlob working - Sentiment: {blob.sentiment}")
    
    # Test scikit-learn
    from sklearn.ensemble import RandomForestClassifier
    print("✅ scikit-learn working")
    
    # Test pandas and numpy
    df = pd.DataFrame({'col': [1, 2, 3]})
    print("✅ pandas and numpy working")
    
    print("\n🎉 All tests passed! You're ready to run the Hostel Management System.")
    
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
except Exception as e:
    print(f"❌ Error: {e}")