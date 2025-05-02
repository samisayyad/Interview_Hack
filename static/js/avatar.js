// Virtual Avatar Interaction
class VirtualAvatar {
    constructor(containerId) {
        // Container element reference
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error('Avatar container not found:', containerId);
            return;
        }
        
        // Avatar state
        this.isSpeaking = false;
        this.messages = [
            "Hi there! I'm your AI interviewer.",
            "I'll ask you questions that are commonly asked in interviews.",
            "Try to answer as if you're in a real interview!",
            "Remember to maintain good eye contact and posture.",
            "Speak clearly and confidently.",
            "I'm analyzing your responses to provide helpful feedback.",
            "You're doing great so far!",
            "Take your time to think before answering.",
            "Structure your answers with examples.",
            "Don't forget to showcase your strengths.",
            "Let's practice until you feel confident!"
        ];
        
        // Initialize the avatar
        this.initializeAvatar();
        
        // Start interaction behavior
        this.startBehavior();
    }
    
    // Create avatar DOM elements
    initializeAvatar() {
        // Generate avatar HTML
        this.container.innerHTML = `
            <div class="avatar-wrapper">
                <div class="avatar-decoration">
                    <div class="avatar-circle"></div>
                    <div class="avatar-circle"></div>
                    <div class="avatar-circle"></div>
                    <div class="avatar-circle"></div>
                </div>
                
                <div class="avatar-container">
                    <div class="avatar-head">
                        <div class="avatar-ears">
                            <div class="avatar-ear left"></div>
                            <div class="avatar-ear right"></div>
                        </div>
                        <div class="avatar-face">
                            <div class="avatar-eyes">
                                <div class="avatar-eye left"></div>
                                <div class="avatar-eye right"></div>
                            </div>
                            <div class="avatar-mouth"></div>
                        </div>
                        <div class="avatar-neck"></div>
                        <div class="avatar-body"></div>
                    </div>
                </div>
                
                <div class="avatar-message">
                    Welcome to your interview practice!
                </div>
            </div>
        `;
        
        // Get references to avatar elements
        this.head = this.container.querySelector('.avatar-head');
        this.leftEye = this.container.querySelector('.avatar-eye.left');
        this.rightEye = this.container.querySelector('.avatar-eye.right');
        this.mouth = this.container.querySelector('.avatar-mouth');
        this.messageBox = this.container.querySelector('.avatar-message');
    }
    
    // Start avatar's autonomous behavior
    startBehavior() {
        // Activate avatar
        this.container.querySelector('.avatar-wrapper').classList.add('avatar-active');
        
        // Show initial message
        this.showMessage("Welcome to your interview practice!");
        
        // Start random movement
        this.startRandomMovement();
        
        // Start random messages
        this.scheduleRandomMessage();
    }
    
    // Display a message from the avatar
    showMessage(text, duration = 5000) {
        // Set message text
        this.messageBox.textContent = text;
        
        // Show message
        this.messageBox.classList.add('visible');
        
        // Start speaking animation
        this.startSpeaking();
        
        // Hide message after duration
        setTimeout(() => {
            this.messageBox.classList.remove('visible');
            this.stopSpeaking();
        }, duration);
    }
    
    // Start speaking animation
    startSpeaking() {
        if (this.isSpeaking) return;
        
        this.isSpeaking = true;
        this.mouth.classList.add('speaking');
    }
    
    // Stop speaking animation
    stopSpeaking() {
        if (!this.isSpeaking) return;
        
        this.isSpeaking = false;
        this.mouth.classList.remove('speaking');
    }
    
    // Schedule periodic random messages
    scheduleRandomMessage() {
        const delay = Math.random() * 10000 + 10000; // 10-20 seconds
        
        setTimeout(() => {
            // Show random encouraging message
            const randomMessage = this.messages[Math.floor(Math.random() * this.messages.length)];
            this.showMessage(randomMessage);
            
            // Schedule next message
            this.scheduleRandomMessage();
        }, delay);
    }
    
    // Add subtle random movement to the avatar
    startRandomMovement() {
        setInterval(() => {
            // Subtle random head tilt
            const tiltX = (Math.random() - 0.5) * 10;
            const tiltY = (Math.random() - 0.5) * 10;
            
            this.head.style.transform = `rotate(${tiltX}deg) translateY(${tiltY}px)`;
            
            // Reset after a moment
            setTimeout(() => {
                this.head.style.transform = '';
            }, 500);
        }, 5000); // Every 5 seconds
    }
    
    // Call this function when a new question is displayed
    askQuestion(questionText) {
        // Show the question as a message
        this.showMessage(questionText, 8000);
    }
    
    // Call this when providing feedback
    provideFeedback(feedbackText) {
        this.showMessage(feedbackText, 8000);
    }
    
    // React to user starting to answer
    userStartedAnswering() {
        this.stopSpeaking();
        // Add attentive behavior
        this.leftEye.style.transform = 'scale(1.1)';
        this.rightEye.style.transform = 'scale(1.1)';
        
        setTimeout(() => {
            this.leftEye.style.transform = '';
            this.rightEye.style.transform = '';
        }, 1000);
    }
    
    // Call this when the interview is complete
    finishInterview() {
        this.showMessage("Great job! Let's see how you did.", 6000);
    }
}

// Initialize avatar when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Check if avatar container exists
    if (document.getElementById('avatar-container')) {
        window.virtualAvatar = new VirtualAvatar('avatar-container');
    }
});