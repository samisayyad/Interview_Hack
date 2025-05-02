import os
import os
import logging
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import json
import uuid
from extensions import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix
from urllib.parse import urlparse

from services.openai_service import get_chatbot_response
from services.speech_service import analyze_speech
from services.body_language_service import analyze_body_language
from dotenv import load_dotenv
load_dotenv()


# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the SQLAlchemy part of the app
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "interview_assistant.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Import models and create tables
with app.app_context():
    from models import User, InterviewResult, CustomerFeedback
    db.create_all()

# Routes
@app.route('/')
def landing():
    """Landing page with animations and introduction"""
    # Initialize session if needed
    if 'user_id' not in session and not current_user.is_authenticated:
        session['user_id'] = str(uuid.uuid4())
        session['chat_history'] = []
    
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    # If already logged in, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    from forms import LoginForm
    form = LoginForm()
    
    # Validate form submission
    if form.validate_on_submit():
        from models import User
        user = User.query.filter_by(username=form.username.data).first()
        
        # Check if user exists and password is correct
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        
        # Log the user in
        login_user(user, remember=form.remember_me.data)
        
        # Redirect to requested page or home
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')
        
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form, title='Sign In')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration page"""
    # If already logged in, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    from forms import SignupForm
    form = SignupForm()
    
    # Validate form submission
    if form.validate_on_submit():
        from models import User
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)
        
        # Save to database
        db.session.add(user)
        db.session.commit()
        
        # Log the user in
        login_user(user)
        
        flash('Account created successfully! Welcome to AI Interview Assistant.', 'success')
        return redirect(url_for('index'))
    
    return render_template('auth/signup.html', form=form, title='Sign Up')

@app.route('/logout')
def logout():
    """Log out the current user"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))

@app.route('/home')
def index():
    """Main application home page"""
    # Initialize session if needed
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        session['chat_history'] = []
    
    return render_template('index.html')

@app.route('/interview')
def interview():
    """Interview page route"""
    return render_template('interview.html')

@app.route('/customer-feedback', methods=['GET'])
@login_required
def customer_feedback():
    """Customer feedback form page"""
    return render_template('customer_feedback.html')

@app.route('/submit-feedback', methods=['POST'])
@login_required
def submit_feedback():
    """Handle customer feedback submission"""
    rating = request.form.get('rating', type=int)
    feedback_text = request.form.get('feedback')
    
    if not rating or not feedback_text:
        flash('Please provide both rating and feedback', 'danger')
        return redirect(url_for('customer_feedback'))
    
    feedback = CustomerFeedback(
        user_id=current_user.id,
        rating=rating,
        feedback_text=feedback_text
    )
    
    db.session.add(feedback)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Thank you for your feedback!'})

@app.route('/feedback')
def feedback():
    """Feedback page route"""
    # Only show feedback if user is authenticated and has interview results
    if not current_user.is_authenticated or 'interview_results' not in session:
        return render_template('feedback.html', results=None)
    
    # In a real app, this would be calculated from actual interview data
    interview_results = {
        'speech': {
            'tone': 75,
            'fluency': 82,
            'pronunciation': 88,
                'overall': 80
            },
            'body_language': {
                'posture': 70,
                'gestures': 65,
                'eye_contact': 80,
                'overall': 72
            },
            'content': {
                'relevance': 85,
                'structure': 78,
                'clarity': 90,
                'overall': 84
            },
            'tips': [
                "Try to vary your tone more to sound more engaging",
                "Maintain a more upright posture during the interview",
                "Your answers are well-structured but could be more concise",
                "Good eye contact, keep it up!"
            ]
        }
    
    return render_template('feedback.html', results=session.get('interview_results'))

@app.route('/chatbot')
def chatbot():
    """Chatbot page route"""
    # Initialize chat history if needed
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    return render_template('chatbot.html', chat_history=session.get('chat_history', []))

@app.route('/api/chatbot', methods=['POST'])
def chatbot_api():
    """API endpoint for chatbot interaction"""
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Get chat history from session
    chat_history = session.get('chat_history', [])
    
    # Add user message to history
    chat_history.append({'role': 'user', 'content': user_message})
    
    try:
        # Get response from OpenAI
        bot_response = get_chatbot_response(user_message, chat_history)
        
        # Add bot response to history
        chat_history.append({'role': 'assistant', 'content': bot_response})
        
        # Update session
        session['chat_history'] = chat_history
        
        return jsonify({
            'response': bot_response,
            'history': chat_history
        })
    except Exception as e:
        logging.error(f"Error in chatbot API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze_speech', methods=['POST'])
def analyze_speech_api():
    """API endpoint for speech analysis"""
    try:
        # In a real app, we would process audio data here
        # For this MVP, we'll use simplified analysis
        audio_data = request.json.get('audio_data')
        results = analyze_speech(audio_data)
        return jsonify(results)
    except Exception as e:
        logging.error(f"Error in speech analysis API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze_body_language', methods=['POST'])
def analyze_body_language_api():
    """API endpoint for body language analysis"""
    try:
        # In a real app, we would process video/image data here
        # For this MVP, we'll use simplified analysis
        video_data = request.json.get('video_data')
        results = analyze_body_language(video_data)
        return jsonify(results)
    except Exception as e:
        logging.error(f"Error in body language analysis API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/comparison')
@login_required
def comparison():
    """User performance comparison page"""
    # Get query parameters for filtering
    filter_type = request.args.get('type', 'all')
    filter_range = request.args.get('range', 'all')
    
    # Get all public interview results
    query = InterviewResult.query.filter_by(is_public=True)
    
    # Apply filters
    if filter_type != 'all':
        query = query.filter_by(interview_type=filter_type)
    
    if filter_range != 'all':
        if filter_range == 'week':
            cutoff = datetime.utcnow() - timedelta(days=7)
        elif filter_range == 'month':
            cutoff = datetime.utcnow() - timedelta(days=30)
        elif filter_range == 'year':
            cutoff = datetime.utcnow() - timedelta(days=365)
        query = query.filter(InterviewResult.interview_date >= cutoff)
    
    # Get results and group by user
    results = query.order_by(InterviewResult.interview_date.desc()).all()
    user_rankings = []
    processed_users = set()
    
    for result in results:
        if result.user_id not in processed_users:
            user = User.query.get(result.user_id)
            if user:
                # Calculate user's average scores
                user_results = [r for r in results if r.user_id == user.id]
                avg_overall = sum(r.overall_score for r in user_results) // len(user_results)
                avg_speech = sum(r.speech_overall for r in user_results) // len(user_results)
                avg_body = sum(r.body_overall for r in user_results) // len(user_results)
                avg_content = sum(r.content_overall for r in user_results) // len(user_results)
                
                user_rankings.append({
                    'username': user.username,
                    'overall_score': avg_overall,
                    'speech_score': avg_speech,
                    'body_score': avg_body,
                    'content_score': avg_content,
                    'interview_count': len(user_results),
                    'strengths': 'Content & Structure' if avg_content > avg_speech and avg_content > avg_body else 
                                'Speech & Delivery' if avg_speech > avg_body else 'Body Language',
                    'is_current_user': user.id == current_user.id
                })
                processed_users.add(user.id)
    
    # Sort rankings by overall score
    user_rankings.sort(key=lambda x: x['overall_score'], reverse=True)
    
    # Add rank to each user
    for i, ranking in enumerate(user_rankings, 1):
        ranking['rank'] = i
    
    # In a real app, we would query the database for actual comparison data
    # For this demo, we'll generate sample data
    
    # Sample user rankings
    user_rankings = [
        {
            'rank': 1,
            'username': 'interview_master',
            'overall_score': 92,
            'speech_score': 94,
            'body_score': 90,
            'content_score': 93,
            'interview_count': 24,
            'strengths': 'Content & Structure',
            'is_current_user': False
        },
        {
            'rank': 2,
            'username': 'tech_interviewer',
            'overall_score': 89,
            'speech_score': 87,
            'body_score': 86,
            'content_score': 95,
            'interview_count': 18,
            'strengths': 'Technical Knowledge',
            'is_current_user': False
        },
        {
            'rank': 3,
            'username': current_user.username if current_user.is_authenticated else 'you',
            'overall_score': 83,
            'speech_score': 78,
            'body_score': 81,
            'content_score': 89,
            'interview_count': 7,
            'strengths': 'Content Relevance',
            'is_current_user': True
        },
        {
            'rank': 4,
            'username': 'confident_speaker',
            'overall_score': 80,
            'speech_score': 92,
            'body_score': 85,
            'content_score': 74,
            'interview_count': 12,
            'strengths': 'Speech & Delivery',
            'is_current_user': False
        },
        {
            'rank': 5,
            'username': 'body_language_pro',
            'overall_score': 78,
            'speech_score': 75,
            'body_score': 95,
            'content_score': 72,
            'interview_count': 9,
            'strengths': 'Body Language',
            'is_current_user': False
        }
    ]
    
    # Current user's scores for the chart
    current_user_scores = {
        'overall': 83,
        'speech': 78,
        'body': 81,
        'content': 89
    }
    
    # Average scores from all users
    average_scores = {
        'overall': 76,
        'speech': 72,
        'body': 74,
        'content': 78
    }
    
    # Top performers' average scores
    top_scores = {
        'overall': 90,
        'speech': 91,
        'body': 88,
        'content': 94
    }
    
    # Current user's statistics
    current_user_stats = {
        'rank': 3,
        'percentile': 70,
        'improvement': 15,
        'best_area': 'Content',
        'speech_vs_top': 86,
        'body_vs_top': 92,
        'content_vs_top': 95
    }
    
    # Improvement recommendations based on comparison
    improvement_recommendations = [
        {
            'category': 'Speech Clarity',
            'text': 'Practice articulating technical terms more clearly. Record yourself and listen for areas where you mumble or speak too quickly.'
        },
        {
            'category': 'Body Language',
            'text': 'Work on maintaining more consistent eye contact. Top performers maintain eye contact 70% of the time, while you are currently at about 50%.'
        },
        {
            'category': 'Speech Pacing',
            'text': 'Your speaking pace varies too much, sometimes rushing through important points. Practice maintaining a steady, moderate pace.'
        }
    ]
    
    # What top performers do differently
    top_performer_practices = [
        'Practice interviews at least twice a week',
        'Record and review their own performances',
        'Prepare structured answers using the STAR method',
        'Research companies thoroughly before interviews',
        'Use specific metrics and examples in their responses',
        'Maintain consistent eye contact',
        'Speak at a measured, confident pace'
    ]
    
    return render_template(
        'comparison.html',
        filter_type=filter_type,
        filter_range=filter_range,
        user_rankings=user_rankings,
        current_user_scores=current_user_scores,
        average_scores=average_scores,
        top_scores=top_scores,
        current_user_stats=current_user_stats,
        improvement_recommendations=improvement_recommendations,
        top_performer_practices=top_performer_practices
    )

@app.route('/api/save_interview_results', methods=['POST'])
def save_interview_results():
    """API endpoint to save interview results"""
    data = request.json
    session['interview_results'] = data
    
    # If user is logged in, save results to database
    if current_user.is_authenticated:
        try:
            from models import InterviewResult
            # Create new interview result from JSON data
            result = InterviewResult.from_json(data, current_user.id)
            # Save to database
            db.session.add(result)
            db.session.commit()
        except Exception as e:
            logging.error(f"Error saving interview results: {str(e)}")
    
    return jsonify({'success': True})

@app.route('/api/clear_chat_history', methods=['POST'])
def clear_chat_history():
    """API endpoint to clear chat history"""
    session['chat_history'] = []
    return jsonify({'success': True})

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    from forms import ProfileForm
    form = ProfileForm(
        original_username=current_user.username,
        original_email=current_user.email
    )
    
    # Populate form with current user data
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
    
    # Process form submission
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))
    
    # Get user interview data
    user_interviews = []
    strengths = []
    weaknesses = []
    
    # Fetch actual interview data from the database
    interviews = current_user.interview_results.order_by(InterviewResult.interview_date.desc()).all()
    
    if interviews:
        # Process interview data for display
        for interview in interviews:
            user_interviews.append({
                'date': interview.interview_date.strftime('%b %d, %Y'),
                'type': interview.interview_type.capitalize(),
                'score': interview.overall_score
            })
        
        # Calculate stats
        interview_count = len(interviews)
        avg_score = sum(interview.overall_score for interview in interviews) // interview_count if interview_count > 0 else 0
        
        # Mock user rank (in real app, this would be calculated by comparing to other users)
        user_rank = 3
        
        # Prepare chart data
        chart_labels = [interview.interview_date.strftime('%b %d') for interview in reversed(interviews)]
        chart_overall_scores = [interview.overall_score for interview in reversed(interviews)]
        chart_speech_scores = [interview.speech_overall for interview in reversed(interviews)]
        chart_body_scores = [interview.body_overall for interview in reversed(interviews)]
        chart_content_scores = [interview.content_overall for interview in reversed(interviews)]
        
        # Identify strengths and weaknesses
        latest_interview = interviews[0]
        scores = {
            'Speech': latest_interview.speech_overall,
            'Body Language': latest_interview.body_overall,
            'Content': latest_interview.content_overall
        }
        
        # Sort by score (highest first for strengths, lowest first for weaknesses)
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Generate strengths (top 2)
        strengths = [
            f"Strong {sorted_scores[0][0].lower()} skills with a score of {sorted_scores[0][1]}",
            f"Good {sorted_scores[1][0].lower()} with a score of {sorted_scores[1][1]}"
        ]
        
        # Generate weaknesses (lowest score)
        weaknesses = [
            f"Improve your {sorted_scores[2][0].lower()} (currently {sorted_scores[2][1]})",
            "Work on maintaining more consistent eye contact",
            "Practice speaking at a steady, confident pace"
        ]
    else:
        # Default values if no interviews
        interview_count = 0
        avg_score = 0
        user_rank = '-'
        chart_labels = []
        chart_overall_scores = []
        chart_speech_scores = []
        chart_body_scores = []
        chart_content_scores = []
    
    return render_template(
        'profile.html',
        form=form,
        user_interviews=user_interviews,
        interview_count=interview_count,
        avg_score=avg_score,
        user_rank=user_rank,
        chart_labels=chart_labels,
        chart_overall_scores=chart_overall_scores,
        chart_speech_scores=chart_speech_scores,
        chart_body_scores=chart_body_scores,
        chart_content_scores=chart_content_scores,
        strengths=strengths,
        weaknesses=weaknesses
    )

@app.route('/upload_profile_image', methods=['POST'])
@login_required
def upload_profile_image():
    """Upload a new profile image"""
    if 'image' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('profile'))
    
    file = request.files['image']
    
    if file.filename == '':
        flash('No image selected', 'danger')
        return redirect(url_for('profile'))
    
    if file:
        try:
            # In a real app, we would process and save the image
            # For this demo, we'll just update the profile image field
            filename = 'default-profile.svg'  # Would normally be a unique filename
            
            current_user.profile_image = filename
            db.session.commit()
            
            flash('Profile image updated successfully!', 'success')
        except Exception as e:
            logging.error(f"Error updating profile image: {str(e)}")
            flash('Error updating profile image', 'danger')
    
    return redirect(url_for('profile'))

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    """Delete user account and related data"""
    try:
        # Delete all interview results
        current_user.interview_results.delete()
        
        # Delete the user
        db.session.delete(current_user)
        db.session.commit()
        
        # Log the user out
        logout_user()
        
        flash('Your account has been deleted', 'info')
    except Exception as e:
        logging.error(f"Error deleting account: {str(e)}")
        flash('Error deleting account', 'danger')
    
    return redirect(url_for('landing'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
