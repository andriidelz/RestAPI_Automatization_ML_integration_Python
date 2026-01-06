import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
import os

def create_sample_data():
    """Create sample CSV if it doesn't exist"""
    data = [
        ["Fix login bug on website", "high"],
        ["Update user profile page", "low"],
        ["Implement new API endpoint", "high"],
        ["Refactor old code", "low"],
        ["Write unit tests for API", "high"],
        ["Clean up temporary files", "low"],
        ["Optimize database queries", "high"],
        ["Update documentation", "low"],
        ["Security vulnerability fix", "high"],
        ["Add new feature request", "high"],
        ["Update library versions", "low"],
        ["Design new UI component", "low"],
        ["Critical production bug", "high"],
        ["Code review comments", "low"],
        ["Performance optimization", "high"],
        ["Update README file", "low"],
    ]
    
    df = pd.DataFrame(data, columns=["task_description", "priority"])
    df.to_csv("tasks.csv", index=False)
    print("✓ Sample data created: tasks.csv")
    return df

def train_model():
    """Train the classification model"""
    if not os.path.exists("tasks.csv"):
        df = create_sample_data()
    else:
        df = pd.read_csv("tasks.csv")
    
    print(f"Training on {len(df)} samples...")
    
    # Create pipeline
    model = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=100)),
        ('classifier', MultinomialNB())
    ])
    
    # Train the model
    X = df['task_description']
    y = df['priority']
    model.fit(X, y)
    
    joblib.dump(model, 'task3/priority_model.pkl')
    print("✓ Model trained and saved to task3/priority_model.pkl")

    test_tasks = [
        "Fix critical bug",
        "Update documentation",
        "Security patch needed"
    ]

    print("\nTest predictions:")
    for task in test_tasks:
        prediction = model.predict([task])[0]
        print(f"  '{task}' -> {prediction}")

if __name__ == "__main__":
    train_model()