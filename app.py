import os
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
try:
    from ai_triage_service import analyze_bug_report, get_ai_triage_service
    AI_AVAILABLE = True
except ImportError:
    from openai_service import analyze_bug_report
    AI_AVAILABLE = False

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Enable CORS for API access
CORS(app)

@app.route('/')
def index():
    """Serve the main testing interface"""
    return render_template('index.html')

@app.route('/triage', methods=['POST'])
def triage_bug():
    """
    POST endpoint to analyze and categorize bug reports
    Supports both single bug and batch processing (10-20 bugs)
    
    Single bug format:
    {
        "title": "Bug title",
        "description": "Bug description"
    }
    
    Batch format:
    {
        "bugs": [
            {"title": "Bug 1", "description": "Description 1"},
            {"title": "Bug 2", "description": "Description 2"},
            ...
        ]
    }
    
    Returns JSON with 'category' and 'urgency' classification(s)
    """
    try:
        # Validate request content type
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({
                'error': 'Request body must contain JSON data'
            }), 400
        
        # Check if this is a batch request
        if 'bugs' in data:
            return process_batch_triage(data)
        
        # Single bug processing (existing functionality)
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        
        if not title:
            return jsonify({
                'error': 'Bug title is required'
            }), 400
        
        if not description:
            return jsonify({
                'error': 'Bug description is required'
            }), 400
        
        # Log the incoming request
        app.logger.info(f"Processing single bug triage for: {title[:50]}...")
        
        # Analyze the bug report
        result = analyze_bug_report(title, description)
        
        app.logger.info(f"Analysis complete - Category: {result['category']}, Urgency: {result['urgency']}")
        
        # Ensure all values are JSON serializable
        try:
            return jsonify(result), 200
        except TypeError as e:
            app.logger.error(f"JSON serialization error: {str(e)}")
            # Fallback to basic result without confidence scores
            basic_result = {
                'category': result.get('category', 'Unknown'),
                'urgency': result.get('urgency', 'Medium')
            }
            return jsonify(basic_result), 200
        
    except ValueError as e:
        app.logger.error(f"Validation error: {str(e)}")
        return jsonify({
            'error': f'Invalid input: {str(e)}'
        }), 400
        
    except Exception as e:
        app.logger.error(f"Unexpected error in triage endpoint: {str(e)}")
        return jsonify({
            'error': 'An unexpected error occurred while processing the bug report. Please try again.'
        }), 500

def process_batch_triage(data):
    """
    Process multiple bug reports in a single request
    """
    try:
        bugs = data.get('bugs', [])
        
        # Validate batch size
        if not bugs:
            return jsonify({
                'error': 'Bugs array is required and cannot be empty'
            }), 400
        
        if len(bugs) < 1 or len(bugs) > 20:
            return jsonify({
                'error': 'Batch size must be between 1 and 20 bugs'
            }), 400
        
        app.logger.info(f"Processing batch triage for {len(bugs)} bugs...")
        
        results = []
        processed_count = 0
        
        for i, bug in enumerate(bugs):
            try:
                # Validate each bug entry
                if not isinstance(bug, dict):
                    results.append({
                        'index': i,
                        'error': 'Bug entry must be an object with title and description'
                    })
                    continue
                
                title = bug.get('title', '').strip()
                description = bug.get('description', '').strip()
                
                if not title:
                    results.append({
                        'index': i,
                        'error': 'Bug title is required'
                    })
                    continue
                
                if not description:
                    results.append({
                        'index': i,
                        'error': 'Bug description is required'
                    })
                    continue
                
                # Analyze the bug report
                result = analyze_bug_report(title, description)
                
                # Add the result with original data for reference
                try:
                    results.append({
                        'index': i,
                        'title': title,
                        'description': description,
                        'category': result['category'],
                        'urgency': result['urgency'],
                        'category_confidence': result.get('category_confidence'),
                        'urgency_confidence': result.get('urgency_confidence')
                    })
                except (KeyError, TypeError) as e:
                    app.logger.warning(f"Using basic result for bug {i}: {str(e)}")
                    results.append({
                        'index': i,
                        'title': title,
                        'description': description,
                        'category': result.get('category', 'Unknown'),
                        'urgency': result.get('urgency', 'Medium')
                    })
                
                processed_count += 1
                
            except Exception as bug_error:
                app.logger.error(f"Error processing bug {i}: {str(bug_error)}")
                results.append({
                    'index': i,
                    'error': f'Failed to process bug: {str(bug_error)}'
                })
        
        app.logger.info(f"Batch analysis complete - Processed {processed_count}/{len(bugs)} bugs successfully")
        
        # Return batch results with summary
        return jsonify({
            'total_bugs': len(bugs),
            'processed_successfully': processed_count,
            'failed': len(bugs) - processed_count,
            'results': results
        }), 200
        
    except Exception as e:
        app.logger.error(f"Unexpected error in batch triage: {str(e)}")
        return jsonify({
            'error': 'An unexpected error occurred while processing the batch request.'
        }), 500

@app.route('/batch-triage', methods=['POST'])
def batch_triage_dedicated():
    """
    Dedicated endpoint for batch processing 10-20 bug reports
    Expects JSON with 'bugs' array containing bug objects
    Returns JSON array with all results for dashboard display
    """
    try:
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        if not data or 'bugs' not in data:
            return jsonify({
                'error': 'Request must contain a "bugs" array'
            }), 400
        
        return process_batch_triage(data)
        
    except Exception as e:
        app.logger.error(f"Error in batch triage endpoint: {str(e)}")
        return jsonify({
            'error': 'Failed to process batch request'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Bug Triage API',
        'version': '1.0.0',
        'ai_available': AI_AVAILABLE
    }), 200

@app.route('/ai-status', methods=['GET'])
def ai_status():
    """Get AI service status and model information"""
    try:
        if AI_AVAILABLE:
            service = get_ai_triage_service()
            model_info = service.get_model_info()
            return jsonify({
                'ai_available': True,
                'models': model_info,
                'status': 'AI models loaded and ready'
            }), 200
        else:
            return jsonify({
                'ai_available': False,
                'status': 'Using rule-based fallback system',
                'message': 'Install AI dependencies to enable AI-powered triage'
            }), 200
    except Exception as e:
        return jsonify({
            'ai_available': False,
            'status': 'Error loading AI models',
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'Method not allowed'
    }), 405

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))  # Use PORT env var or default to 8080
    app.run(host='0.0.0.0', port=port, debug=True)
