import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
import pickle
import os

# Define and download all required NLTK data
required_nltk_data = [
    'punkt',
    'averaged_perceptron_tagger',
    'stopwords',
    'maxent_ne_chunker',
    'words'
]

# Create NLTK data directory if it doesn't exist
nltk_data_dir = os.path.expanduser('~/nltk_data')
os.makedirs(nltk_data_dir, exist_ok=True)

# Download required NLTK data
for resource in required_nltk_data:
    try:
        nltk.download(resource, quiet=True, download_dir=nltk_data_dir)
    except Exception as e:
        print(f"Warning: Could not download {resource}: {str(e)}")

class MLScorer:
    def __init__(self):
        # Initialize with some basic training data
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.model = RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )
        self.scaler = MinMaxScaler()

        # Fit vectorizer with some sample text to avoid "not fitted" errors
        sample_texts = [
            "experienced software engineer with python java",
            "project manager with agile methodology",
            "data scientist machine learning expert",
            "marketing specialist with digital expertise",
            "sales representative with customer service"
        ]
        self.vectorizer.fit(sample_texts)

        # Initialize model with sample data
        sample_features = self.vectorizer.transform(sample_texts)
        sample_scores = np.array([75.0, 80.0, 85.0, 70.0, 75.0])  # Sample scores
        self.model.fit(sample_features, sample_scores)

        # Initialize scaler
        self.scaler.fit([[0, 0, 0, 0, 0], [100, 20, 50, 30, 20]])

    def preprocess_text(self, text):
        """Preprocess resume text for ML analysis"""
        try:
            # Basic text cleaning
            text = text.lower().strip()

            # Tokenize with error handling
            try:
                tokens = nltk.word_tokenize(text)
            except Exception as e:
                print(f"Tokenization error: {str(e)}")
                tokens = text.split()

            # Remove stopwords with error handling
            try:
                stop_words = set(nltk.corpus.stopwords.words('english'))
                tokens = [t for t in tokens if t not in stop_words]
            except Exception as e:
                print(f"Stopwords error: {str(e)}")
                tokens = [t for t in tokens if len(t) > 2]

            # Get parts of speech with error handling
            try:
                pos_tags = nltk.pos_tag(tokens)
            except Exception as e:
                print(f"POS tagging error: {str(e)}")
                pos_tags = [(token, 'NN') for token in tokens]  # Default to nouns

            # Extract features with error handling
            features = {
                'word_count': len(tokens),
                'avg_word_length': np.mean([len(t) for t in tokens]) if tokens else 5.0,
                'noun_count': len([t for t, pos in pos_tags if pos.startswith('NN')]),
                'verb_count': len([t for t, pos in pos_tags if pos.startswith('VB')]),
                'number_count': len([t for t in tokens if any(c.isdigit() for c in t)])
            }

            return ' '.join(tokens), features

        except Exception as e:
            print(f"Error in text preprocessing: {str(e)}")
            # Return safe defaults
            return text.lower(), {
                'word_count': len(text.split()),
                'avg_word_length': 5.0,
                'noun_count': 0,
                'verb_count': 0,
                'number_count': 0
            }

    def extract_features(self, text):
        """Extract TF-IDF and statistical features"""
        processed_text, stat_features = self.preprocess_text(text)

        try:
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
        except Exception as e:
            print(f"Error in feature extraction: {str(e)}")
            # Return safe defaults
            return self.vectorizer.transform([""]), np.zeros((1, 5))

    def predict_score(self, text):
        """Predict resume score using ML model"""
        try:
            # Extract features
            tfidf_features, stat_features = self.extract_features(text)

            # Make prediction using regression model
            tfidf_score = self.model.predict(tfidf_features)[0]

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