from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db

class User(UserMixin, db.Model):
    """User model for authentication and profile information"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    profile_image = db.Column(db.String(256), default='default-profile.svg')
    
    # Relationships
    interview_results = db.relationship('InterviewResult', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.get_full_name(),
            'profile_image': self.profile_image,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CustomerFeedback(db.Model):
    """Model for storing customer feedback and ratings"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    feedback_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CustomerFeedback {self.id} - Rating {self.rating}>'

class InterviewResult(db.Model):
    """Model for storing interview results and analysis"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    interview_date = db.Column(db.DateTime, default=datetime.utcnow)
    interview_type = db.Column(db.String(64), default='general')
    is_public = db.Column(db.Boolean, default=True)  # Controls visibility in comparisons
    
    # Performance scores (0-100)
    speech_tone = db.Column(db.Integer)
    speech_fluency = db.Column(db.Integer)
    speech_pronunciation = db.Column(db.Integer)
    speech_overall = db.Column(db.Integer)
    
    body_posture = db.Column(db.Integer)
    body_gestures = db.Column(db.Integer)
    body_eye_contact = db.Column(db.Integer)
    body_overall = db.Column(db.Integer)
    
    content_relevance = db.Column(db.Integer)
    content_structure = db.Column(db.Integer)
    content_clarity = db.Column(db.Integer)
    content_overall = db.Column(db.Integer)
    
    overall_score = db.Column(db.Integer)
    
    # Feedback and tips
    speech_feedback = db.Column(db.Text)
    body_feedback = db.Column(db.Text)
    content_feedback = db.Column(db.Text)
    general_tips = db.Column(db.Text)
    areas_to_improve = db.Column(db.Text)
    
    def __repr__(self):
        return f'<InterviewResult {self.id} - User {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'interview_date': self.interview_date.isoformat() if self.interview_date else None,
            'interview_type': self.interview_type,
            'speech': {
                'tone': self.speech_tone,
                'fluency': self.speech_fluency,
                'pronunciation': self.speech_pronunciation,
                'overall': self.speech_overall
            },
            'body_language': {
                'posture': self.body_posture,
                'gestures': self.body_gestures,
                'eye_contact': self.body_eye_contact,
                'overall': self.body_overall
            },
            'content': {
                'relevance': self.content_relevance,
                'structure': self.content_structure,
                'clarity': self.content_clarity,
                'overall': self.content_overall
            },
            'overall_score': self.overall_score,
            'feedback': {
                'speech': self.speech_feedback,
                'body': self.body_feedback,
                'content': self.content_feedback,
                'tips': self.general_tips,
                'improvement_areas': self.areas_to_improve
            }
        }
    
    @staticmethod
    def from_json(data, user_id):
        """Create or update InterviewResult from json data"""
        result = InterviewResult(user_id=user_id)
        
        # Speech scores
        speech = data.get('speech', {})
        result.speech_tone = speech.get('tone')
        result.speech_fluency = speech.get('fluency')
        result.speech_pronunciation = speech.get('pronunciation')
        result.speech_overall = speech.get('overall')
        
        # Body language scores
        body = data.get('body_language', {})
        result.body_posture = body.get('posture')
        result.body_gestures = body.get('gestures')
        result.body_eye_contact = body.get('eye_contact')
        result.body_overall = body.get('overall')
        
        # Content scores
        content = data.get('content', {})
        result.content_relevance = content.get('relevance')
        result.content_structure = content.get('structure')
        result.content_clarity = content.get('clarity')
        result.content_overall = content.get('overall')
        
        # Calculate overall score
        speech_weight = 0.3
        body_weight = 0.3
        content_weight = 0.4
        
        if all([result.speech_overall, result.body_overall, result.content_overall]):
            result.overall_score = int(
                result.speech_overall * speech_weight +
                result.body_overall * body_weight +
                result.content_overall * content_weight
            )
        
        # Feedback and tips
        tips = data.get('tips', [])
        result.general_tips = '\n'.join(tips) if isinstance(tips, list) else tips
        
        # Generate feedback based on scores
        result.speech_feedback = InterviewResult.generate_speech_feedback(speech)
        result.body_feedback = InterviewResult.generate_body_feedback(body)
        result.content_feedback = InterviewResult.generate_content_feedback(content)
        
        # Generate areas to improve
        result.areas_to_improve = InterviewResult.generate_improvement_areas(
            result.speech_overall, 
            result.body_overall, 
            result.content_overall
        )
        
        return result
    
    @staticmethod
    def generate_speech_feedback(speech_data):
        """Generate feedback based on speech scores"""
        feedback = []
        
        tone = speech_data.get('tone', 0)
        fluency = speech_data.get('fluency', 0)
        pronunciation = speech_data.get('pronunciation', 0)
        
        if tone < 70:
            feedback.append("Your tone could be more dynamic. Try varying your pitch and volume to emphasize key points.")
        elif tone < 85:
            feedback.append("Your tone is good but could be more engaging with additional variation.")
        else:
            feedback.append("Your tone is excellent - dynamic and engaging.")
            
        if fluency < 70:
            feedback.append("Your fluency needs improvement. Practice speaking without pauses and filler words.")
        elif fluency < 85:
            feedback.append("Your fluency is good. Continue reducing filler words like 'um' and 'uh'.")
        else:
            feedback.append("Your fluency is excellent - smooth and natural.")
            
        if pronunciation < 70:
            feedback.append("Focus on clearer pronunciation of technical terms and difficult words.")
        elif pronunciation < 85:
            feedback.append("Your pronunciation is good. Continue working on clarity of specific terms.")
        else:
            feedback.append("Your pronunciation is excellent - clear and articulate.")
            
        return "\n".join(feedback)
    
    @staticmethod
    def generate_body_feedback(body_data):
        """Generate feedback based on body language scores"""
        feedback = []
        
        posture = body_data.get('posture', 0)
        gestures = body_data.get('gestures', 0)
        eye_contact = body_data.get('eye_contact', 0)
        
        if posture < 70:
            feedback.append("Improve your posture. Sit or stand straight with shoulders back to project confidence.")
        elif posture < 85:
            feedback.append("Your posture is good. Continue being mindful of maintaining an upright position.")
        else:
            feedback.append("Your posture is excellent - confident and professional.")
            
        if gestures < 70:
            feedback.append("Use more natural hand gestures to emphasize points and appear engaged.")
        elif gestures < 85:
            feedback.append("Your gestures are good. Work on making them more purposeful and less nervous.")
        else:
            feedback.append("Your gestures are excellent - natural and reinforcing your message.")
            
        if eye_contact < 70:
            feedback.append("Improve your eye contact. Look at the interviewer directly to build trust.")
        elif eye_contact < 85:
            feedback.append("Your eye contact is good. Try to maintain it more consistently during responses.")
        else:
            feedback.append("Your eye contact is excellent - engaged and confident.")
            
        return "\n".join(feedback)
    
    @staticmethod
    def generate_content_feedback(content_data):
        """Generate feedback based on content scores"""
        feedback = []
        
        relevance = content_data.get('relevance', 0)
        structure = content_data.get('structure', 0)
        clarity = content_data.get('clarity', 0)
        
        if relevance < 70:
            feedback.append("Focus more on directly answering the question asked and providing relevant examples.")
        elif relevance < 85:
            feedback.append("Your answers are generally relevant. Work on tying examples more closely to the question.")
        else:
            feedback.append("Your answers are highly relevant and directly address the questions.")
            
        if structure < 70:
            feedback.append("Structure your answers better using the STAR method (Situation, Task, Action, Result).")
        elif structure < 85:
            feedback.append("Your answer structure is good. Work on smoother transitions between points.")
        else:
            feedback.append("Your answers are excellently structured - clear, logical, and well-organized.")
            
        if clarity < 70:
            feedback.append("Improve the clarity of your answers by avoiding jargon and being more concise.")
        elif clarity < 85:
            feedback.append("Your answers are clear. Continue working on conciseness and precision.")
        else:
            feedback.append("Your answers are exceptionally clear and easy to understand.")
            
        return "\n".join(feedback)
    
    @staticmethod
    def generate_improvement_areas(speech_score, body_score, content_score):
        """Identify areas most needing improvement"""
        areas = []
        scores = {
            "speech": speech_score or 0,
            "body language": body_score or 0,
            "content": content_score or 0
        }
        
        # Sort by score (lowest first)
        sorted_areas = sorted(scores.items(), key=lambda x: x[1])
        
        if sorted_areas[0][1] < 75:
            areas.append(f"Focus primarily on improving your {sorted_areas[0][0]}.")
            
            if sorted_areas[1][1] < 80:
                areas.append(f"Also work on enhancing your {sorted_areas[1][0]}.")
                
            # Add specific advice for the weakest area
            if sorted_areas[0][0] == "speech":
                areas.append("Practice speaking exercises daily. Record yourself answering questions and review the recordings.")
                areas.append("Try tongue twisters to improve articulation and join a speaking club like Toastmasters.")
            elif sorted_areas[0][0] == "body language":
                areas.append("Practice interviews in front of a mirror to be aware of your posture and gestures.")
                areas.append("Record yourself on video to identify unconscious habits and work on eliminating them.")
            else:  # content
                areas.append("Prepare answers for common interview questions using the STAR method.")
                areas.append("Ask a friend to critique your answers for clarity, relevance, and structure.")
        else:
            areas.append("All aspects of your interview skills are strong, but there's always room for improvement.")
            areas.append(f"For optimal results, continue refining your {sorted_areas[0][0]} to reach excellence.")
            
        return "\n".join(areas)