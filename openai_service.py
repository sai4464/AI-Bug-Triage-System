import re
from collections import Counter

# Simple rule-based classification without external dependencies
CATEGORIES = {
    'UI': ['ui', 'interface', 'button', 'display', 'visual', 'layout', 'css', 'style', 'responsive', 'mobile', 'desktop', 'color', 'font', 'menu', 'navigation', 'modal', 'popup', 'dropdown', 'form', 'input', 'checkbox', 'radio'],
    'Backend': ['server', 'api', 'endpoint', 'database', 'sql', 'query', 'backend', 'service', 'microservice', 'rest', 'graphql', 'json', 'xml', 'response', 'request', 'timeout', 'error 500', '500 error', 'internal server'],
    'Authentication': ['login', 'logout', 'password', 'auth', 'authentication', 'authorization', 'session', 'token', 'jwt', 'oauth', 'sso', 'user', 'account', 'permission', 'role', 'access', 'forbidden', 'unauthorized', '401', '403'],
    'Performance': ['slow', 'performance', 'speed', 'lag', 'latency', 'memory', 'cpu', 'loading', 'timeout', 'optimization', 'cache', 'heavy', 'bottleneck', 'scalability', 'response time', 'page load', 'rendering'],
    'Security': ['security', 'vulnerability', 'xss', 'csrf', 'injection', 'sql injection', 'malware', 'phishing', 'breach', 'exploit', 'attack', 'hacking', 'encryption', 'ssl', 'tls', 'certificate', 'privacy', 'gdpr', 'pii']
}

URGENCY_KEYWORDS = {
    'Critical': ['critical', 'urgent', 'emergency', 'down', 'crash', 'broken', 'not working', 'data loss', 'security breach', 'vulnerability', 'exploit', 'production down', 'system failure'],
    'High': ['high', 'important', 'major', 'significant', 'affecting users', 'blocking', 'cannot', 'error', 'failed', 'bug', 'issue', 'problem'],
    'Medium': ['medium', 'moderate', 'minor', 'sometimes', 'occasionally', 'inconsistent', 'improvement', 'enhancement'],
    'Low': ['low', 'cosmetic', 'suggestion', 'nice to have', 'feature request', 'documentation', 'typo', 'minor']
}

def analyze_bug_report(title, description):
    """
    Analyze a bug report using rule-based classification to determine category and urgency
    
    Args:
        title (str): Bug report title
        description (str): Bug report description
    
    Returns:
        dict: Contains 'category' and 'urgency' classifications
    
    Raises:
        Exception: If analysis fails
    """
    
    try:
        # Combine title and description for analysis
        text = f"{title} {description}".lower()
        
        # Clean and tokenize the text
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        
        # Calculate category scores
        category_scores = {}
        for category, keywords in CATEGORIES.items():
            score = 0
            for keyword in keywords:
                # Count exact matches and partial matches
                if keyword in text:
                    score += text.count(keyword) * 2  # Exact phrase matches get double points
                
                # Count individual word matches
                keyword_words = keyword.split()
                if len(keyword_words) == 1:
                    score += words.count(keyword)
            
            category_scores[category] = score
        
        # Determine the category with highest score
        max_score = max(category_scores.values()) if category_scores else 0
        if max_score == 0:
            category = "Backend"  # Default category
        else:
            # Find category with highest score
            best_category = "Backend"
            best_score = 0
            for cat, score in category_scores.items():
                if score > best_score:
                    best_score = score
                    best_category = cat
            category = best_category
        
        # Calculate urgency scores
        urgency_scores = {}
        for urgency, keywords in URGENCY_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += text.count(keyword) * 2
                
                keyword_words = keyword.split()
                if len(keyword_words) == 1:
                    score += words.count(keyword)
            
            urgency_scores[urgency] = score
        
        # Determine urgency with highest score
        max_urgency_score = max(urgency_scores.values()) if urgency_scores else 0
        if max_urgency_score == 0:
            urgency = "Medium"  # Default urgency
        else:
            # Find urgency with highest score
            best_urgency = "Medium"
            best_urgency_score = 0
            for urg, score in urgency_scores.items():
                if score > best_urgency_score:
                    best_urgency_score = score
                    best_urgency = urg
            urgency = best_urgency
        
        # Apply additional rules for better classification
        # Security-related bugs are always high priority
        security_indicators = ['security', 'vulnerability', 'breach', 'exploit', 'xss', 'injection']
        if any(indicator in text for indicator in security_indicators):
            if urgency in ['Low', 'Medium']:
                urgency = 'High'
        
        # Critical system failures
        critical_indicators = ['crash', 'down', 'not working', 'broken', 'data loss', 'production']
        if any(indicator in text for indicator in critical_indicators):
            urgency = 'Critical'
        
        # Performance issues are typically medium unless severe
        if category == 'Performance' and urgency == 'Low':
            urgency = 'Medium'
        
        return {
            'category': category,
            'urgency': urgency
        }
        
    except Exception as e:
        raise Exception(f"Failed to analyze bug report: {str(e)}")

