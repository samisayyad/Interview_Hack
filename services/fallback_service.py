"""
Fallback service for the chatbot when OpenAI API is unavailable.
This provides basic interview advice responses without requiring an API key.
"""

import random

# Common interview questions and predefined answers
INTERVIEW_QA = {
    "tell me about yourself": "When answering 'Tell me about yourself', focus on your professional background, relevant skills, and brief career highlights. Keep it under 2 minutes, be enthusiastic, and tailor it to the specific job. Avoid personal details and practice until it feels natural.",
    
    "why should we hire you": "To answer 'Why should we hire you?', highlight your specific skills and experience that match the job requirements. Use concrete examples of past achievements, show enthusiasm for the company, and explain how you can solve their problems or add value.",
    
    "what is your greatest weakness": "When discussing weaknesses, choose something non-essential to the job, explain how you're working to improve it, and focus on your growth mindset. Be honest but strategic - avoid clichés like 'I'm a perfectionist' and never mention critical flaws.",
    
    "why do you want to work here": "When answering why you want to work somewhere, research the company thoroughly and mention specific aspects of their culture, mission, or products that align with your values and career goals. Show enthusiasm and explain how you can contribute to their success.",
    
    "where do you see yourself in 5 years": "When discussing your 5-year plan, show ambition that's realistic and relevant to the company. Focus on skill development and growing in ways that benefit the organization. Demonstrate commitment without seeming like you'll outgrow the position too quickly.",
    
    "tell me about a challenge you faced": "When describing a challenge you faced, use the STAR method (Situation, Task, Action, Result). Choose a relevant example, focus on your problem-solving process, highlight the positive outcome, and share what you learned from the experience.",
    
    "what are your salary expectations": "For salary questions, research industry standards beforehand. Give a range rather than a specific number, emphasize that you're flexible, and focus on the value you bring. Consider the total compensation package, not just the base salary.",
    
    "do you have any questions for me": "Always prepare thoughtful questions for the interviewer about the role, team dynamics, company culture, or professional development opportunities. This shows genuine interest and helps determine if the position is right for you.",
    
    "what is your greatest achievement": "When discussing your greatest achievement, choose something relevant to the job, use specific metrics to show impact, explain your process, and connect it to how you'll succeed in this new role. Keep it professional and focused on results.",
    
    "how do you handle stress": "Explain your specific stress management techniques like prioritization, exercise, or time management. Provide a brief example of handling pressure successfully, emphasize your resilience, and show you maintain productivity during challenging times."
}

# General interview advice categories
GENERAL_ADVICE = {
    "preparation": [
        "Research the company thoroughly before your interview. Understand their products, services, mission, and recent news.",
        "Practice common interview questions with a friend or in front of a mirror.",
        "Prepare concise examples of your achievements and challenges using the STAR method (Situation, Task, Action, Result).",
        "Have questions prepared to ask the interviewer about the role and company.",
        "Review the job description and align your responses to highlight relevant skills and experience."
    ],
    
    "appearance": [
        "Dress one level above the company's everyday dress code. When in doubt, business professional is safest.",
        "Ensure your clothes are clean, pressed, and fit well.",
        "Keep accessories minimal and professional.",
        "Check your appearance before the interview - hair neat, shoes clean, overall polished look.",
        "For virtual interviews, wear professional attire and check your background is tidy and appropriate."
    ],
    
    "body_language": [
        "Maintain good posture throughout the interview - sit straight with shoulders back.",
        "Make appropriate eye contact to show confidence and engagement.",
        "Offer a firm handshake at the beginning and end (when in-person).",
        "Avoid nervous habits like pen-clicking or hair-twirling.",
        "Use natural hand gestures when speaking, but avoid excessive movements."
    ],
    
    "communication": [
        "Speak clearly and at a moderate pace - neither too fast nor too slow.",
        "Listen carefully to questions before answering.",
        "Use professional language and avoid slang or filler words like 'um' and 'like'.",
        "Structure your answers with a clear beginning, middle, and end.",
        "Be concise - aim for 1-2 minute responses to most questions."
    ],
    
    "follow_up": [
        "Send a personalized thank-you email within 24 hours of your interview.",
        "Reference specific points from your conversation to show engagement.",
        "Reaffirm your interest in the position and briefly summarize why you're a good fit.",
        "If you don't hear back within the timeframe they specified, a polite follow-up is appropriate.",
        "Regardless of outcome, maintain a professional relationship as networking opportunities can arise later."
    ]
}

def get_fallback_response(user_message):
    """
    Get a fallback response when OpenAI is unavailable
    
    Args:
        user_message (str): The user's message
        
    Returns:
        str: The fallback response
    """
    # Convert user message to lowercase for better matching
    user_message_lower = user_message.lower()
    
    # Check if the message contains a common interview question
    for key_phrase, response in INTERVIEW_QA.items():
        if key_phrase in user_message_lower:
            return response
    
    # Check if the message is asking about a specific advice category
    for category, advice_list in GENERAL_ADVICE.items():
        if category in user_message_lower:
            return random.choice(advice_list)
    
    # If no specific match, provide a general response
    general_responses = [
        "For successful interviews, preparation is key. Research the company, practice common questions, and prepare examples of your achievements using the STAR method.",
        "Body language matters in interviews. Maintain good eye contact, have good posture, and offer a firm handshake. These nonverbal cues significantly impact the interviewer's perception.",
        "When answering behavioral questions, use the STAR method: describe the Situation, Task you were assigned, Action you took, and Results you achieved.",
        "To make a good impression, arrive 10-15 minutes early, dress professionally, bring extra copies of your resume, and turn off your phone before the interview.",
        "After your interview, send a thank-you email within 24 hours that reinforces your interest and briefly mentions why you're a good fit for the role."
    ]
    
    return random.choice(general_responses)