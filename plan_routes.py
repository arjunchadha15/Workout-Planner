"""
Plan generation API endpoint.
POST /plans/generate - Generate a workout plan using OpenAI
"""
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
import logging

from ai_plan_generation_service import AIPlanGenerationService
from app.database import get_db  # Adjust import based on your DB setup

logger = logging.getLogger(__name__)

# Create blueprint
plan_routes = Blueprint('plan_routes', __name__, url_prefix='/plans')


@plan_routes.route('/generate', methods=['POST'])
def generate_plan():
    """
    Generate a workout plan using AI.
    
    Request Body:
    {
        "user_id": "string",
        "user_profile": {
            "goal": "strength|hypertrophy|weight_loss|general_fitness",
            "days_per_week": 4,
            "experience": "beginner|intermediate|advanced",
            "gender": "male|female",
            "bodyweight_lb": 150.0
        },
        "constraints": {
            "session_length_minutes": 60,
            "equipment_access": "full_gym|dumbbells_only|home_gym|bodyweight_only"
        }
    }
    
    Response:
    {
        "success": true,
        "plan": { ... },
        "message": "Plan generated successfully"
    }
    """
    try:
        # Parse request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Extract fields
        user_id = data.get('user_id')
        user_profile = data.get('user_profile', {})
        constraints = data.get('constraints', {})
        
        # Validate user_id
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        # Get database session
        db: Session = next(get_db())
        
        try:
            # Initialize service
            service = AIPlanGenerationService(db)
            
            # Generate plan
            result = service.generate_plan(
                user_id=user_id,
                user_profile=user_profile,
                constraints=constraints
            )
            
            # Return success response
            return jsonify({
                'success': True,
                'plan': result['plan'],
                'metadata': result.get('metadata', {}),
                'message': 'Plan generated successfully'
            }), 200
            
        finally:
            db.close()
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"Plan generation failed: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Failed to generate plan',
            'details': str(e)
        }), 500


# Health check endpoint
@plan_routes.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'plan_generation'
    }), 200
