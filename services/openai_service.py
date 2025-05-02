import os
import logging
from openai import OpenAI
from services.fallback_service import get_fallback_response

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
MODEL = "gpt-4o"

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Flag to track if we should use fallback mode after API errors
USE_FALLBACK_MODE = False

# Create a function to get or create the OpenAI client
def get_openai_client():
    """Get the OpenAI client if API key is available, otherwise return None"""
    if OPENAI_API_KEY:
        return OpenAI(api_key=OPENAI_API_KEY)
    return None

def get_chatbot_response(user_message, chat_history=None):
    """
    Get a response from the OpenAI chatbot for interview preparation
    
    Args:
        user_message (str): The user's message
        chat_history (list): Previous chat messages
        
    Returns:
        str: The chatbot's response
    """
    global USE_FALLBACK_MODE
    
    # First, check if we should use fallback mode due to previous API errors
    if USE_FALLBACK_MODE:
        logging.info("Using fallback mode for chatbot response")
        return get_fallback_response(user_message) + " (Fallback Mode)"
    
    try:
        # Check if OpenAI API key is available
        client = get_openai_client()
        if not client:
            # Switch to fallback mode and return a response from it
            USE_FALLBACK_MODE = True
            logging.warning("No API key found, switching to fallback mode")
            fallback_msg = get_fallback_response(user_message)
            return "I'm sorry, but the OpenAI service is currently unavailable. I'll switch to basic mode to help you with interview preparation.\n\n" + fallback_msg + " (Fallback Mode)"
        
        # Prepare the system message
        system_message = """
        You are an AI Interview Preparation Assistant. Your role is to help users prepare for job interviews by:
        
        1. Answering questions about interview best practices
        2. Providing tips on how to handle difficult interview questions
        3. Giving feedback on interview responses
        4. Helping with resume and cover letter tips
        5. Offering advice on body language, tone, and presentation
        
        Keep your responses concise, practical, and encouraging. Focus on providing actionable advice that candidates can immediately apply to their interview preparation.
        """
        
        # Prepare messages for the API
        messages = [{"role": "system", "content": system_message}]
        
        # Add relevant chat history if available (limit to last 10 messages for context)
        if chat_history:
            for message in chat_history[-10:]:
                messages.append({
                    "role": message["role"],
                    "content": message["content"]
                })
        else:
            # If no chat history, just add the user's message
            messages.append({"role": "user", "content": user_message})
        
        # Make the API call
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        # Extract and return the response text
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        error_str = str(e)
        logging.error(f"Error in OpenAI API call: {error_str}")
        
        # Switch to fallback mode for future requests
        USE_FALLBACK_MODE = True
        fallback_msg = get_fallback_response(user_message)
        
        # Check if this is a quota exceeded error
        if "insufficient_quota" in error_str or "exceeded your current quota" in error_str:
            return "I'm sorry, the OpenAI API key has exceeded its quota. I'll switch to basic mode to help you with interview preparation.\n\n" + fallback_msg + " (Fallback Mode)"
        
        # Check if it's a rate limit error
        elif "rate limit" in error_str.lower() or "429" in error_str:
            return "I'm sorry, we're experiencing too many requests to the OpenAI service. I'll switch to basic mode to help you with interview preparation.\n\n" + fallback_msg + " (Fallback Mode)"
            
        # General error handler
        else:
            return "I'm sorry, I encountered an error with the AI service. I'll switch to basic mode to help you with interview preparation.\n\n" + fallback_msg + " (Fallback Mode)"
