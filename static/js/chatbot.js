document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const chatContainer = document.getElementById('chat-container');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const typingIndicator = document.getElementById('typing-indicator');
    const clearChatBtn = document.getElementById('clear-chat');
    const suggestionBtns = document.querySelectorAll('.suggestion-btn');
    
    // Check if we're coming from the feedback page
    const fromFeedback = localStorage.getItem('from_feedback') === 'true';
    if (fromFeedback) {
        // Clear the flag
        localStorage.removeItem('from_feedback');
        
        // Add a suggestion about the feedback
        setTimeout(() => {
            userInput.value = "Can you help me understand my interview feedback?";
            sendMessage();
        }, 1000);
    }
    
    // Scroll to the bottom of the chat container
    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Add a message to the chat container
    function addMessage(content, isUser = false) {
        const messageRow = document.createElement('div');
        messageRow.className = isUser ? 'message-row justify-content-end' : 'message-row';
        
        const avatar = document.createElement('div');
        avatar.className = isUser ? 'avatar user-avatar' : 'avatar bot-avatar';
        avatar.innerHTML = isUser ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const messageDiv = document.createElement('div');
        messageDiv.className = isUser ? 'user-message' : 'bot-message';
        messageDiv.textContent = content;
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = isUser ? 'You' : 'Assistant';
        
        messageContent.appendChild(messageDiv);
        messageContent.appendChild(timeDiv);
        
        if (isUser) {
            messageRow.appendChild(messageContent);
            messageRow.appendChild(avatar);
        } else {
            messageRow.appendChild(avatar);
            messageRow.appendChild(messageContent);
        }
        
        chatContainer.appendChild(messageRow);
        scrollToBottom();
    }
    
    // Show typing indicator
    function showTypingIndicator() {
        typingIndicator.style.display = 'block';
        scrollToBottom();
    }
    
    // Hide typing indicator
    function hideTypingIndicator() {
        typingIndicator.style.display = 'none';
    }
    
    // Send a message to the chatbot
    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addMessage(message, true);
        
        // Clear input
        userInput.value = '';
        
        // Show typing indicator
        showTypingIndicator();
        
        // Send message to server
        fetch('/api/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        })
        .then(response => response.json())
        .then(data => {
            // Hide typing indicator
            hideTypingIndicator();
            
            // Check for error
            if (data.error) {
                addMessage('Sorry, I encountered an error. Please try again later.', false);
                console.error('Error:', data.error);
                return;
            }
            
            // Check if the response indicates missing API key
            if (data.response && data.response.includes('API key is missing')) {
                addMessage(data.response, false);
                // Add a special message about how to get set up
                setTimeout(() => {
                    addMessage('To use this chatbot feature, an OpenAI API key is required. Please contact the administrator to set up the API key.', false);
                }, 1000);
                return;
            }
            
            // Check if response indicates quota exceeded or fallback mode activated
            if (data.response && (data.response.includes('exceeded its quota') || data.response.includes('switch to basic mode'))) {
                addMessage(data.response, false);
                // Add a helpful message if not already in fallback mode
                if (!data.response.includes('Fallback Mode')) {
                    setTimeout(() => {
                        addMessage('This happens when using a free OpenAI account that has used up its credits. You\'ll need to upgrade your OpenAI account or get a new API key with available credits.', false);
                    }, 1000);
                }
                return;
            }
            
            // Check if response indicates rate limiting
            if (data.response && data.response.includes('too many requests')) {
                addMessage(data.response, false);
                // Add a helpful message
                setTimeout(() => {
                    addMessage('Please wait a minute before trying again. The API has rate limits on how quickly you can send requests.', false);
                }, 1000);
                return;
            }
            
            // Special styling for fallback mode responses
            if (data.response && data.response.includes('(Fallback Mode)')) {
                const responseWithoutTag = data.response.replace(' (Fallback Mode)', '');
                addMessage(responseWithoutTag, false);
                
                // Only show this message once per session
                if (!sessionStorage.getItem('fallback_mode_explained')) {
                    setTimeout(() => {
                        addMessage('Note: I\'m currently in basic mode, using pre-defined responses instead of the OpenAI API. My capabilities are limited in this mode, but I can still provide helpful interview advice.', false);
                        sessionStorage.setItem('fallback_mode_explained', 'true');
                    }, 1000);
                }
                return;
            }
            
            // Add bot response to chat
            addMessage(data.response, false);
        })
        .catch(error => {
            // Hide typing indicator
            hideTypingIndicator();
            
            // Show error message
            addMessage('Sorry, I encountered an error. Please try again later.', false);
            console.error('Error:', error);
        });
    }
    
    // Clear chat history
    function clearChat() {
        // Confirm before clearing
        if (confirm('Are you sure you want to clear the chat history?')) {
            // Send request to clear chat history
            fetch('/api/clear_chat_history', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                // Remove all messages except the first one (welcome message)
                const messages = chatContainer.querySelectorAll('.message-row');
                for (let i = 1; i < messages.length; i++) {
                    messages[i].remove();
                }
                
                // Also remove typing indicator if visible
                hideTypingIndicator();
                
                // Show success message
                addMessage('Chat history has been cleared. How can I help you with interview preparation today?', false);
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('Sorry, I encountered an error clearing the chat history.', false);
            });
        }
    }
    
    // Event listeners
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        sendMessage();
    });
    
    clearChatBtn.addEventListener('click', clearChat);
    
    // Add event listeners to suggestion buttons
    suggestionBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            userInput.value = btn.getAttribute('data-question');
            sendMessage();
        });
    });
    
    // Focus on input field when page loads
    userInput.focus();
    
    // Initial scroll to bottom
    scrollToBottom();
});
