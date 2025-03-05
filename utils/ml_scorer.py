import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
import pickle
import os

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

class MLScorer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        self.scaler = MinMaxScaler()
        
    def preprocess_text(self, text):
        """Preprocess resume text for ML analysis"""
        # Tokenize
        tokens = nltk.word_tokenize(text.lower())
        # Remove stopwords
        stop_words = set(nltk.corpus.stopwords.words('english'))
        tokens = [t for t in tokens if t not in stop_words]
        # Get parts of speech
        pos_tags = nltk.pos_tag(tokens)
        
        # Extract features
        features = {
            'word_count': len(tokens),
            'avg_word_length': np.mean([len(t) for t in tokens]),
            'noun_count': len([t for t, pos in pos_tags if pos.startswith('NN')]),
            'verb_count': len([t for t, pos in pos_tags if pos.startswith('VB')]),
            'number_count': len([t for t in tokens if t.isdigit()]),
        }
        
        return ' '.join(tokens), features

    def extract_features(self, text):
        """Extract TF-IDF and statistical features"""
        processed_text, stat_features = self.preprocess_text(text)
        
        # TF-IDF features
        tfidf_features = self.vectorizer.transform([processed_text])
        
        # Combine with statistical features
        stat_features_array = np.array([[
            stat_features['word_count'],
            stat_features['avg_word_length'],
            stat_features['noun_count'],
            stat_features['verb_count'],
            stat_features['number_count']
        ]])
        
        return tfidf_features, stat_features_array

    def predict_score(self, text):
        """Predict resume score using ML model"""
        try:
            # Extract features
            tfidf_features, stat_features = self.extract_features(text)
            
            # Make prediction
            tfidf_score = self.model.predict_proba(tfidf_features)[0][1]
            
            # Scale statistical features
            scaled_stats = self.scaler.transform(stat_features)
            
            # Combine scores (70% TF-IDF, 30% statistical)
            final_score = (0.7 * tfidf_score + 0.3 * np.mean(scaled_stats)) * 100
            
            return min(max(final_score, 0), 100)  # Ensure score is between 0 and 100
            
        except Exception as e:
            print(f"Error in ML scoring: {str(e)}")
            return 50  # Return neutral score on error
    
    def save_model(self, path='models'):
        """Save the trained model and vectorizer"""
        os.makedirs(path, exist_ok=True)
        with open(f'{path}/vectorizer.pkl', 'wb') as f:
            pickle.dump(self.vectorizer, f)
        with open(f'{path}/model.pkl', 'wb') as f:
            pickle.dump(self.model, f)
        with open(f'{path}/scaler.pkl', 'wb') as f:
            pickle.dump(self.scaler, f)
    
    def load_model(self, path='models'):
        """Load the trained model and vectorizer"""
        try:
            with open(f'{path}/vectorizer.pkl', 'rb') as f:
                self.vectorizer = pickle.load(f)
            with open(f'{path}/model.pkl', 'rb') as f:
                self.model = pickle.load(f)
            with open(f'{path}/scaler.pkl', 'rb') as f:
                self.scaler = pickle.load(f)
            return True
        except:
            return False
