import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download NLTK resources if not already present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Lists of keywords for feature extraction
DIET_KEYWORDS = [
    'salt', 'sodium', 'sugar', 'carb', 'carbohydrate', 'fat', 'saturated', 'unsaturated', 
    'trans', 'protein', 'cholesterol', 'fiber', 'fruit', 'vegetable', 'meat', 'fish',
    'dairy', 'processed', 'junk', 'fast food', 'alcohol', 'wine', 'beer', 'liquor',
    'vitamin', 'mineral', 'supplement', 'calorie', 'portion', 'meal', 'breakfast',
    'lunch', 'dinner', 'snack', 'dessert'
]

MEDICAL_KEYWORDS = [
    'hypertension', 'pressure', 'heart', 'cardiac', 'stroke', 'kidney', 'renal',
    'diabetes', 'insulin', 'glucose', 'cholesterol', 'lipid', 'triglyceride',
    'medication', 'prescription', 'surgery', 'hospitalization', 'emergency',
    'family history', 'genetic', 'hereditary', 'obesity', 'overweight',
    'sleep apnea', 'stress', 'anxiety', 'depression', 'thyroid', 'adrenal',
    'steroid', 'inflammation', 'infection', 'chronic', 'acute'
]

def extract_features_from_text(text):
    """Extract relevant features from text descriptions."""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [w for w in tokens if w not in stop_words]
    
    # Extract features based on keywords
    extracted_features = []
    
    # Check for diet-related terms
    for keyword in DIET_KEYWORDS:
        if keyword in text:
            extracted_features.append(f"diet_{keyword}")
    
    # Check for medical-related terms
    for keyword in MEDICAL_KEYWORDS:
        if keyword in text:
            extracted_features.append(f"medical_{keyword}")
    
    # Additional patterns to look for
    if re.search(r'high.{1,20}salt', text):
        extracted_features.append("high_salt_diet")
    
    if re.search(r'low.{1,20}activity', text) or re.search(r'sedentary', text):
        extracted_features.append("low_physical_activity")
    
    if re.search(r'family.{1,20}hypertension', text) or re.search(r'parent.{1,20}hypertension', text):
        extracted_features.append("family_history_hypertension")
    
    return " ".join(extracted_features)