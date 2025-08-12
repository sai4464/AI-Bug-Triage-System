import torch
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIBugTriageService:
    def __init__(self):
        """Initialize the AI-powered bug triage service with Hugging Face models"""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        # Initialize models
        self._load_models()
        
        # Define bug categories with example descriptions
        self.categories = {
            'UI': [
                "User interface issues, visual problems, layout issues, responsive design problems",
                "Button not working, form validation errors, display glitches, CSS styling issues",
                "Mobile responsiveness, navigation problems, modal popup issues, color scheme problems"
            ],
            'Backend': [
                "Server errors, API failures, database connection issues, backend service problems",
                "500 errors, timeout issues, database query failures, microservice communication problems",
                "Server crashes, API endpoint failures, database performance issues, backend logic errors"
            ],
            'Authentication': [
                "Login problems, password issues, user authentication failures, session management",
                "User access denied, permission errors, token validation failures, OAuth problems",
                "Account lockout, password reset issues, user registration problems, security access"
            ],
            'Performance': [
                "Slow loading, performance degradation, memory leaks, CPU usage problems",
                "Page load time issues, response time delays, optimization problems, scalability issues",
                "Resource consumption, bottleneck identification, performance monitoring, speed issues"
            ],
            'Security': [
                "Security vulnerabilities, data breaches, injection attacks, access control issues",
                "XSS vulnerabilities, SQL injection, CSRF attacks, authentication bypass",
                "Data privacy issues, encryption problems, security compliance, threat detection"
            ]
        }
        
        # Define urgency levels with example descriptions
        self.urgency_levels = {
            'Critical': [
                "System completely down, production outage, data loss, security breach",
                "Critical functionality broken, users cannot access system, emergency situation",
                "System crash, complete failure, urgent security vulnerability, blocking all users"
            ],
            'High': [
                "Major functionality broken, affecting many users, significant impact on operations",
                "Important feature not working, blocking user workflow, significant performance degradation",
                "Security concern, data integrity issue, affecting production environment"
            ],
            'Medium': [
                "Minor functionality issues, affecting some users, moderate impact on operations",
                "Feature partially working, occasional errors, performance degradation",
                "UI inconsistencies, minor bugs, non-critical functionality problems"
            ],
            'Low': [
                "Cosmetic issues, minor UI improvements, documentation updates, nice-to-have features",
                "Minor visual glitches, typo corrections, enhancement suggestions, optimization opportunities",
                "Non-critical improvements, user experience enhancements, minor bug fixes"
            ]
        }
        
        # Generate embeddings for categories and urgency levels
        self._generate_reference_embeddings()
    
    def _load_models(self):
        """Load Hugging Face models for text processing"""
        try:
            logger.info("Loading sentence transformer model...")
            # Use a lightweight but effective model for sentence embeddings
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            logger.info("Loading text classification model...")
            # Use a model fine-tuned for text classification
            self.tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-medium')
            self.classifier_model = AutoModel.from_pretrained('microsoft/DialoGPT-medium')
            
            logger.info("Models loaded successfully!")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise Exception(f"Failed to load AI models: {str(e)}")
    
    def _generate_reference_embeddings(self):
        """Generate embeddings for category and urgency reference texts"""
        try:
            logger.info("Generating reference embeddings...")
            
            # Generate embeddings for categories
            self.category_embeddings = {}
            for category, descriptions in self.categories.items():
                embeddings = []
                for desc in descriptions:
                    embedding = self.sentence_model.encode(desc)
                    embeddings.append(embedding)
                self.category_embeddings[category] = np.mean(embeddings, axis=0)
            
            # Generate embeddings for urgency levels
            self.urgency_embeddings = {}
            for urgency, descriptions in self.urgency_levels.items():
                embeddings = []
                for desc in descriptions:
                    embedding = self.sentence_model.encode(desc)
                    embeddings.append(embedding)
                self.urgency_embeddings[urgency] = np.mean(embeddings, axis=0)
            
            logger.info("Reference embeddings generated successfully!")
            
        except Exception as e:
            logger.error(f"Error generating reference embeddings: {str(e)}")
            raise Exception(f"Failed to generate reference embeddings: {str(e)}")
    
    def analyze_bug_report(self, title, description):
        """
        Analyze a bug report using AI to determine category and urgency
        
        Args:
            title (str): Bug report title
            description (str): Bug report description
        
        Returns:
            dict: Contains 'category' and 'urgency' classifications with confidence scores
        """
        try:
            # Combine title and description for analysis
            text = f"{title} {description}".strip()
            
            if not text:
                raise ValueError("Bug report text cannot be empty")
            
            logger.info(f"Analyzing bug report: {title[:50]}...")
            
            # Generate embedding for the bug report
            bug_embedding = self.sentence_model.encode(text)
            
            # Classify category using semantic similarity
            category_result = self._classify_category(bug_embedding)
            
            # Classify urgency using semantic similarity
            urgency_result = self._classify_urgency(bug_embedding)
            
            # Apply AI-powered rules for better classification
            final_result = self._apply_ai_rules(category_result, urgency_result, text)
            
            logger.info(f"Analysis complete - Category: {final_result['category']}, Urgency: {final_result['urgency']}")
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error analyzing bug report: {str(e)}")
            raise Exception(f"Failed to analyze bug report: {str(e)}")
    
    def _classify_category(self, bug_embedding):
        """Classify bug into category using semantic similarity"""
        similarities = {}
        
        for category, ref_embedding in self.category_embeddings.items():
            similarity = float(cosine_similarity([bug_embedding], [ref_embedding])[0][0])
            similarities[category] = similarity
        
        # Find the category with highest similarity
        best_category = max(similarities, key=similarities.get)
        confidence = similarities[best_category]
        
        return {
            'category': best_category,
            'confidence': confidence,
            'all_scores': similarities
        }
    
    def _classify_urgency(self, bug_embedding):
        """Classify bug urgency using semantic similarity"""
        similarities = {}
        
        for urgency, ref_embedding in self.urgency_embeddings.items():
            similarity = float(cosine_similarity([bug_embedding], [ref_embedding])[0][0])
            similarities[urgency] = similarity
        
        # Find the urgency with highest similarity
        best_urgency = max(similarities, key=similarities.get)
        confidence = similarities[best_urgency]
        
        return {
            'urgency': best_urgency,
            'confidence': confidence,
            'all_scores': similarities
        }
    
    def _apply_ai_rules(self, category_result, urgency_result, text):
        """Apply intelligent rules to improve classification"""
        text_lower = text.lower()
        
        # Security-related bugs are always high priority
        security_indicators = ['security', 'vulnerability', 'breach', 'exploit', 'xss', 'injection', 'hack', 'attack']
        if any(indicator in text_lower for indicator in security_indicators):
            if urgency_result['urgency'] in ['Low', 'Medium']:
                urgency_result['urgency'] = 'High'
                urgency_result['confidence'] = min(urgency_result['confidence'] + 0.2, 1.0)
        
        # Critical system failures
        critical_indicators = ['crash', 'down', 'not working', 'broken', 'data loss', 'production', 'outage', 'emergency']
        if any(indicator in text_lower for indicator in critical_indicators):
            urgency_result['urgency'] = 'Critical'
            urgency_result['confidence'] = min(urgency_result['confidence'] + 0.3, 1.0)
        
        # Performance issues are typically medium unless severe
        if category_result['category'] == 'Performance' and urgency_result['urgency'] == 'Low':
            urgency_result['urgency'] = 'Medium'
            urgency_result['confidence'] = min(urgency_result['confidence'] + 0.1, 1.0)
        
        # Authentication issues affecting many users are high priority
        if (category_result['category'] == 'Authentication' and 
            any(word in text_lower for word in ['all users', 'everyone', 'cannot login', 'blocked'])):
            if urgency_result['urgency'] in ['Low', 'Medium']:
                urgency_result['urgency'] = 'High'
                urgency_result['confidence'] = min(urgency_result['confidence'] + 0.2, 1.0)
        
        return {
            'category': category_result['category'],
            'urgency': urgency_result['urgency'],
            'category_confidence': float(round(category_result['confidence'], 3)),
            'urgency_confidence': float(round(urgency_result['confidence'], 3)),
            'category_scores': {k: float(round(v, 3)) for k, v in category_result['all_scores'].items()},
            'urgency_scores': {k: float(round(v, 3)) for k, v in urgency_result['all_scores'].items()}
        }
    
    def get_model_info(self):
        """Get information about the loaded models"""
        return {
            'sentence_model': 'all-MiniLM-L6-v2',
            'classifier_model': 'microsoft/DialoGPT-medium',
            'device': str(self.device),
            'categories': list(self.categories.keys()),
            'urgency_levels': list(self.urgency_levels.keys())
        }

# Create a global instance
ai_triage_service = None

def get_ai_triage_service():
    """Get or create the AI triage service instance"""
    global ai_triage_service
    if ai_triage_service is None:
        ai_triage_service = AIBugTriageService()
    return ai_triage_service

def analyze_bug_report(title, description):
    """
    Wrapper function to maintain compatibility with existing code
    """
    service = get_ai_triage_service()
    return service.analyze_bug_report(title, description) 