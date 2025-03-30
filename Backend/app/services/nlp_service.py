# import re
# import nltk
# from nltk.tokenize import word_tokenize
# from nltk.corpus import stopwords
# import spacy
# from typing import Dict, List, Set, Tuple, Any

# # Download necessary NLTK data
# nltk.download('punkt')
# nltk.download('stopwords')

# class NLPService:
#     def __init__(self):
#         self.nlp = spacy.load("en_core_web_sm")
#         self.stop_words = set(stopwords.words('english'))
        
#         # Medical terms and conditions related to hypertension
#         self.hypertension_terms = {
#             'hypertension', 'high blood pressure', 'elevated blood pressure', 
#             'htn', 'hbp', 'high bp'
#         }
        
#         self.risk_factor_terms = {
#             'obesity', 'overweight', 'smoking', 'alcohol', 'stress', 'anxiety',
#             'diabetes', 'kidney disease', 'renal disease', 'heart disease',
#             'cardiac disease', 'cardiovascular disease', 'cholesterol', 'high cholesterol',
#             'hypercholesterolemia', 'family history', 'genetic', 'hereditary',
#             'diet', 'exercise', 'sedentary', 'salt', 'sodium', 'fat', 'saturated fat',
#             'trans fat', 'sleep apnea', 'insomnia', 'sleep disorder'
#         }
        
#         self.medication_terms = {
#             'diuretic', 'beta blocker', 'ace inhibitor', 'calcium channel blocker',
#             'angiotensin receptor blocker', 'arb', 'lisinopril', 'hydrochlorothiazide',
#             'hctz', 'amlodipine', 'metoprolol', 'losartan', 'valsartan', 'medication',
#             'pill', 'prescription', 'medicine'
#         }
        
#     def preprocess_text(self, text: str) -> str:
#         """Clean and preprocess text data."""
#         if not text:
#             return ""
            
#         # Convert to lowercase
#         text = text.lower()
        
#         # Remove special characters and digits
#         text = re.sub(r'[^\w\s]', ' ', text)
#         text = re.sub(r'\d+', ' ', text)
        
#         # Remove extra whitespace
#         text = re.sub(r'\s+', ' ', text).strip()
        
#         return text
    
#     def extract_medical_entities(self, text: str) -> Dict[str, List[str]]:
#         """Extract medical entities from text using SpaCy."""
#         if not text:
#             return {
#                 'conditions': [],
#                 'medications': [],
#                 'symptoms': []
#             }
            
#         doc = self.nlp(text)
        
#         entities = {
#             'conditions': [],
#             'medications': [],
#             'symptoms': []
#         }
        
#         # Extract entities
#         for ent in doc.ents:
#             if ent.label_ == 'CONDITION' or ent.label_ == 'DISEASE':
#                 entities['conditions'].append(ent.text)
#             elif ent.label_ == 'MEDICINE' or ent.label_ == 'TREATMENT':
#                 entities['medications'].append(ent.text)
#             elif ent.label_ == 'SYMPTOM':
#                 entities['symptoms'].append(ent.text)
        
#         return entities
    
#     def analyze_medical_text(self, text: str) -> Dict[str, Any]:
#         """Analyze medical text and extract relevant features for hypertension prediction."""
#         # Preprocess text
#         processed_text = self.preprocess_text(text)
        
#         if not processed_text:
#             return {
#                 'has_hypertension_mention': False,
#                 'has_risk_factors': False,
#                 'has_medication_mention': False,
#                 'risk_factors': [],
#                 'medications': [],
#                 'hypertension_terms': []
#             }
        
#         # Tokenize
#         tokens = word_tokenize(processed_text)
#         tokens = [token for token in tokens if token not in self.stop_words]
        
#         # Find relevant terms
#         found_hypertension_terms = []
#         found_risk_factors = []
#         found_medications = []
        
#         # Check for hypertension terms
#         for term in self.hypertension_terms:
#             if term in processed_text:
#                 found_hypertension_terms.append(term)
        
#         # Check for risk factor terms
#         for term in self.risk_factor_terms:
#             if term in processed_text:
#                 found_risk_factors.append(term)
        
#         # Check for medication terms
#         for term in self.medication_terms:
#             if term in processed_text:
#                 found_medications.append(term)
        
#         # Get additional medical entities
#         entities = self.extract_medical_entities(text)
#         found_risk_factors.extend(entities['conditions'])
#         found_medications.extend(entities['medications'])
        
#         # Remove duplicates
#         found_hypertension_terms = list(set(found_hypertension_terms))
#         found_risk_factors = list(set(found_risk_factors))
#         found_medications = list(set(found_medications))
        
#         return {
#             'has_hypertension_mention': len(found_hypertension_terms) > 0,
#             'has_risk_factors': len(found_risk_factors) > 0,
#             'has_medication_mention': len(found_medications) > 0,
#             'risk_factors': found_risk_factors,
#             'medications': found_medications,
#             'hypertension_terms': found_hypertension_terms
#         }
    
#     def analyze_diet_description(self, text: str) -> Dict[str, Any]:
#         """Analyze diet description for hypertension risk factors."""
#         # Preprocess text
#         processed_text = self.preprocess_text(text)
        
#         if not processed_text:
#             return {
#                 'has_risk_factors': False,
#                 'diet_risk_score': 0,
#                 'risk_factors': []
#             }
        
#         # Diet risk factors for hypertension
#         high_risk_terms = {
#             'salt', 'sodium', 'processed food', 'fast food', 'fried', 
#             'junk food', 'red meat', 'saturated fat', 'trans fat'
#         }
        
#         medium_risk_terms = {
#             'sugar', 'sweet', 'dessert', 'cake', 'cookie', 'candy',
#             'alcohol', 'beer', 'wine', 'liquor', 'drink'
#         }
        
#         low_risk_terms = {
#             'moderate', 'occasional', 'sometimes'
#         }
        
#         protective_terms = {
#             'vegetable', 'fruit', 'whole grain', 'fish', 'olive oil',
#             'nut', 'seed', 'legume', 'bean', 'dash diet', 'mediterranean'
#         }
        
#         # Count occurrences
#         high_risk_count = sum(1 for term in high_risk_terms if term in processed_text)
#         medium_risk_count = sum(1 for term in medium_risk_terms if term in processed_text)
#         low_risk_count = sum(1 for term in low_risk_terms if term in processed_text)
#         protective_count = sum(1 for term in protective_terms if term in processed_text)
        
#         # Compile risk factors
#         risk_factors = []
#         for term in high_risk_terms:
#             if term in processed_text:
#                 risk_factors.append(term)
                
#         for term in medium_risk_terms:
#             if term in processed_text:
#                 risk_factors.append(term)
        
#         # Calculate diet risk score (0-10)
#         risk_score = min(10, (high_risk_count * 2) + medium_risk_count - protective_count)
#         if low_risk_count > 0:
#             risk_score = max(0, risk_score - 1)
        
#         risk_score = max(0, risk_score)
        
#         return {
#             'has_risk_factors': risk_score > 3,
#             'diet_risk_score': risk_score,
#             'risk_factors': risk_factors
#         }
    
#     def extract_features_from_text(self, medical_history_text: str, diet_description: str) -> Dict[str, Any]:
#         """Extract features from text data for the ML model."""
#         medical_analysis = self.analyze_medical_text(medical_history_text)
#         diet_analysis = self.analyze_diet_description(diet_description)
        
#         # Combine features
#         nlp_features = {
#             'has_hypertension_history': medical_analysis['has_hypertension_mention'],
#             'has_medications': medical_analysis['has_medication_mention'],
#             'diet_risk_score': diet_analysis['diet_risk_score'],
#             'medical_risk_factors_count': len(medical_analysis['risk_factors']),
#             'diet_risk_factors_count': len(diet_analysis['risk_factors'])
#         }
        
#         return nlp_features

# # Singleton instance
# nlp_service = NLPService()