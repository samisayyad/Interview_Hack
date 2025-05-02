document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const startBtn = document.getElementById('start-btn');
    const recordBtn = document.getElementById('record-btn');
    const nextBtn = document.getElementById('next-btn');
    const finishBtn = document.getElementById('finish-btn');
    const userVideo = document.getElementById('user-video');
    const questionContainer = document.getElementById('question-container');
    const questionNumber = document.getElementById('question-number');
    const timerElement = document.getElementById('timer');
    const progressBar = document.getElementById('progress-bar');
    const loadingIndicator = document.getElementById('loading-indicator');
    const cameraStatus = document.getElementById('camera-status');
    const questionStatus = document.getElementById('question-status');
    const cameraMessage = document.getElementById('camera-message');

    // State variables
    let mediaStream = null;
    let mediaRecorder = null;
    let audioChunks = [];
    let isRecording = false;
    let currentQuestionIndex = 0;
    let timerInterval = null;
    let secondsElapsed = 0;
    let videoFrames = [];
    let videoCapturing = false;
    let videoCapturingInterval = null;

    // Sample interview questions
    const interviewQuestions = [
        "Tell me about yourself and your background.",
        "What are your greatest strengths and how do they help you succeed?",
        "Describe a challenging situation you faced at work and how you handled it.",
        "Why are you interested in this position and our company?",
        "Where do you see yourself professionally in five years?"
    ];

    // Initialize camera
    async function initializeCamera() {
        try {
            // Check if getUserMedia is supported
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('Your browser does not support camera/microphone access');
            }

            // First request video only to check camera
            const videoStream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: false
            });

            // Then request audio
            const audioStream = await navigator.mediaDevices.getUserMedia({
                video: false,
                audio: true
            });

            // Combine both streams
            mediaStream = new MediaStream([
                ...videoStream.getVideoTracks(),
                ...audioStream.getAudioTracks()
            ]);

            // Set the video source
            userVideo.srcObject = mediaStream;
            await userVideo.play();

            // Update status
            cameraStatus.classList.remove('bg-danger');
            cameraStatus.classList.add('bg-success');
            cameraMessage.classList.remove('alert-info');
            cameraMessage.classList.add('alert-success');
            cameraMessage.innerHTML = '<i class="fas fa-check-circle me-2"></i> Camera and microphone are ready! Click "Start Interview" to begin.';

            // Enable start button
            startBtn.disabled = false;
        } catch (error) {
            console.error('Error accessing media devices:', error);
            cameraMessage.classList.remove('alert-info');
            cameraMessage.classList.add('alert-danger');
            cameraMessage.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i> Error accessing camera or microphone: ${error.message}. Please ensure you have granted permission.`;
        }
    }

    // Start interview
    function startInterview() {
        // Update UI
        startBtn.disabled = true;
        startBtn.innerHTML = '<i class="fas fa-check-circle me-2"></i> Interview Started';
        recordBtn.disabled = false;
        questionStatus.classList.remove('bg-warning');
        questionStatus.classList.add('bg-success');

        // Welcome message from virtual avatar
        if (window.virtualAvatar) {
            window.virtualAvatar.showMessage("Welcome to your interview practice! I'll ask you some questions. Take your time to think and answer clearly.");
        }

        // Show first question after a short delay
        setTimeout(() => {
            // Show first question
            currentQuestionIndex = 0;
            displayQuestion(currentQuestionIndex);

            // Update progress
            updateProgress();
        }, 4000); // Delay to let the welcome message be read
    }

    // Display question
    function displayQuestion(index) {
        if (index < interviewQuestions.length) {
            const questionText = interviewQuestions[index];
            questionContainer.innerHTML = `<p class="mb-0">${questionText}</p>`;
            questionNumber.textContent = `Question ${index + 1} of ${interviewQuestions.length}`;

            // Enable record button for new question
            recordBtn.disabled = false;
            recordBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            recordBtn.classList.remove('btn-danger');
            recordBtn.classList.add('btn-danger');

            // Use the virtual avatar to ask the question
            if (window.virtualAvatar) {
                window.virtualAvatar.askQuestion(questionText);
            }
        } else {
            // All questions completed
            questionContainer.innerHTML = '<p class="mb-0">All questions completed! Click "Finish Interview" to view your feedback.</p>';
            questionNumber.textContent = `Completed`;
            recordBtn.disabled = true;
            nextBtn.disabled = true;
            finishBtn.disabled = false;

            // Use the virtual avatar to provide completion message
            if (window.virtualAvatar) {
                window.virtualAvatar.showMessage("Great job! You've completed all the questions. Let's review your performance.");
            }
        }
    }

    // Update progress bar
    function updateProgress() {
        const progress = (currentQuestionIndex / interviewQuestions.length) * 100;
        progressBar.style.width = `${progress}%`;
    }

    // Start recording
    function startRecording() {
        // Reset audio chunks
        audioChunks = [];
        videoFrames = [];

        // Create media recorder
        mediaRecorder = new MediaRecorder(mediaStream);

        // Add data handler
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        // Start recording
        mediaRecorder.start();
        isRecording = true;

        // Start timer
        startTimer();

        // Start capturing video frames
        startVideoCapture();

        // Update UI
        recordBtn.innerHTML = '<i class="fas fa-stop"></i>';
        recordBtn.classList.add('recording');
        nextBtn.disabled = true;

        // Notify avatar that user is speaking (makes it pay attention)
        if (window.virtualAvatar) {
            window.virtualAvatar.userStartedAnswering();
        }
    }

    // Stop recording
    function stopRecording() {
        if (mediaRecorder && isRecording) {
            // Stop media recorder
            mediaRecorder.stop();
            isRecording = false;

            // Stop timer
            stopTimer();

            // Stop capturing video frames
            stopVideoCapture();

            // Update UI
            recordBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            recordBtn.classList.remove('recording');
            recordBtn.disabled = true;

            // Show loading indicator
            loadingIndicator.style.display = 'block';

            // Process recording after a short delay
            setTimeout(() => {
                processRecording();
            }, 1000);
        }
    }

    // Start timer
    function startTimer() {
        secondsElapsed = 0;
        timerElement.textContent = '00:00';
        timerInterval = setInterval(() => {
            secondsElapsed++;
            timerElement.textContent = formatTime(secondsElapsed);
        }, 1000);
    }

    // Stop timer
    function stopTimer() {
        clearInterval(timerInterval);
    }

    // Start capturing video frames at intervals
    function startVideoCapture() {
        videoCapturing = true;
        // Capture a frame every second
        videoCapturingInterval = setInterval(() => {
            captureVideoFrame();
        }, 1000);
    }

    // Stop capturing video frames
    function stopVideoCapture() {
        videoCapturing = false;
        clearInterval(videoCapturingInterval);
    }

    // Capture a single video frame
    function captureVideoFrame() {
        if (videoCapturing && userVideo) {
            const canvas = document.createElement('canvas');
            canvas.width = userVideo.videoWidth;
            canvas.height = userVideo.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(userVideo, 0, 0, canvas.width, canvas.height);

            // In a real app, we would store the image data
            // For this MVP, we'll just store a placeholder
            videoFrames.push({
                timestamp: secondsElapsed,
                // In a real app: canvas.toDataURL('image/jpeg')
                placeholder: 'frame_data'
            });
        }
    }

    // Process recording
    function processRecording() {
        // In a real app, we would send the audio and video data to the server
        // For this MVP, we'll simulate analysis

        // Simulate API calls for speech and body language analysis
        Promise.all([
            simulateSpeechAnalysis(),
            simulateBodyLanguageAnalysis()
        ]).then(([speechResults, bodyLanguageResults]) => {
            // Hide loading indicator
            loadingIndicator.style.display = 'none';

            // Enable next button
            nextBtn.disabled = false;

            // Show feedback in an alert
            const overallScore = (speechResults.overall + bodyLanguageResults.overall) / 2;
            const message = `
                <strong>Quick Feedback:</strong><br>
                Speech: ${speechResults.overall}%<br>
                Body Language: ${bodyLanguageResults.overall}%<br>
                Overall: ${Math.round(overallScore)}%
            `;
            showAlert(message, 'info', 5000);

            // Have the avatar provide feedback
            if (window.virtualAvatar) {
                let feedbackMessage = "";

                // Create personalized feedback message based on results
                if (overallScore >= 85) {
                    feedbackMessage = "Excellent answer! Your delivery was clear and your body language was confident.";
                } else if (overallScore >= 75) {
                    feedbackMessage = "Good answer! " + (speechResults.feedback[0] || bodyLanguageResults.feedback[0] || "Try to be a bit more confident next time.");
                } else {
                    feedbackMessage = "You're making progress. " + (speechResults.feedback[0] || bodyLanguageResults.feedback[0] || "Keep practicing and you'll improve!");
                }

                // Slight delay so the alert appears first
                setTimeout(() => {
                    window.virtualAvatar.provideFeedback(feedbackMessage);
                }, 1000);
            }
        }).catch(error => {
            console.error('Error processing recording:', error);
            loadingIndicator.style.display = 'none';
            showAlert('Analysis complete. You may continue.', 'info');
            recordBtn.disabled = true;
            nextBtn.disabled = false;
        });
    }

    // Simulate speech analysis API call
    function simulateSpeechAnalysis() {
        return new Promise((resolve) => {
            // In a real app, we would send the audio data to the server
            setTimeout(() => {
                // Simulate response from the speech analysis service
                fetch('/api/analyze_speech', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        audio_data: 'simulated_audio_data',
                        duration: secondsElapsed
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    resolve(data);
                })
                .catch(error => {
                    console.error('Error:', error);
                    resolve({
                        tone: 75,
                        fluency: 80,
                        pronunciation: 85,
                        overall: 80,
                        feedback: ['Your tone was good, but could be more varied.']
                    });
                });
            }, 1000);
        });
    }

    // Simulate body language analysis API call
    function simulateBodyLanguageAnalysis() {
        return new Promise((resolve) => {
            // In a real app, we would send the video data to the server
            setTimeout(() => {
                // Simulate response from the body language analysis service
                fetch('/api/analyze_body_language', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        video_data: 'simulated_video_data',
                        frames: videoFrames.length
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    resolve(data);
                })
                .catch(error => {
                    console.error('Error:', error);
                    resolve({
                        posture: 70,
                        gestures: 65,
                        eye_contact: 80,
                        overall: 72,
                        feedback: ['Try to maintain better posture during the interview.']
                    });
                });
            }, 1500);
        });
    }

    // Go to next question
    function nextQuestion() {
        currentQuestionIndex++;
        displayQuestion(currentQuestionIndex);
        updateProgress();

        // If all questions are completed, enable finish button
        if (currentQuestionIndex >= interviewQuestions.length) {
            finishBtn.disabled = false;
        }
    }

    // Finish interview and go to feedback page
    function finishInterview() {
        // Let the avatar say goodbye
        if (window.virtualAvatar) {
            window.virtualAvatar.finishInterview();
        }

        // Simulate interview results for demo purposes
        const simulatedResults = {
            speech: {
                tone: Math.floor(Math.random() * 30) + 65,
                fluency: Math.floor(Math.random() * 30) + 65,
                pronunciation: Math.floor(Math.random() * 30) + 65,
                overall: Math.floor(Math.random() * 15) + 70
            },
            body_language: {
                posture: Math.floor(Math.random() * 30) + 65,
                gestures: Math.floor(Math.random() * 30) + 65,
                eye_contact: Math.floor(Math.random() * 30) + 65,
                overall: Math.floor(Math.random() * 15) + 70
            },
            content: {
                relevance: Math.floor(Math.random() * 20) + 75,
                structure: Math.floor(Math.random() * 20) + 75,
                clarity: Math.floor(Math.random() * 20) + 75,
                overall: Math.floor(Math.random() * 15) + 80
            },
            tips: [
                "Try to vary your tone more to sound more engaging",
                "Maintain a more upright posture during the interview",
                "Your answers are well-structured but could be more concise",
                "Good eye contact, keep it up!"
            ]
        };

        // Short delay to let avatar finish speaking
        setTimeout(() => {
            // Save the results
            fetch('/api/save_interview_results', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(simulatedResults),
            })
            .then(response => response.json())
            .then(data => {
                // Redirect to feedback page
                window.location.href = '/feedback';
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Error saving results. Please try again.', 'danger');
            });
        }, 3000);
    }

    // Clean up
    function cleanUp() {
        // Stop all media tracks
        if (mediaStream) {
            mediaStream.getTracks().forEach(track => track.stop());
        }

        // Stop recording
        if (isRecording) {
            stopRecording();
        }

        // Stop timer
        stopTimer();

        // Stop video capture
        stopVideoCapture();
    }

    // Event listeners
    startBtn.addEventListener('click', startInterview);

    recordBtn.addEventListener('click', function() {
        if (!isRecording) {
            startRecording();
        } else {
            stopRecording();
        }
    });

    nextBtn.addEventListener('click', nextQuestion);

    finishBtn.addEventListener('click', finishInterview);

    // Clean up before unloading the page
    window.addEventListener('beforeunload', cleanUp);

    // Initialize camera on page load
    initializeCamera();
});