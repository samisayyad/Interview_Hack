document.addEventListener('DOMContentLoaded', function() {
    // Get the feedback results from the page
    const resultsElement = document.querySelector('main');
    if (!resultsElement) return;
    
    // Initialize performance chart
    initPerformanceChart();
    
    // Apply animations to progress bars
    animateProgressBars();
    
    // Add event listener for the "Ask the Chatbot" button
    const chatbotButton = document.querySelector('a[href="/chatbot"]');
    if (chatbotButton) {
        chatbotButton.addEventListener('click', function(e) {
            // Optionally store something in localStorage to tell the chatbot page
            // that we're coming from the feedback page
            localStorage.setItem('from_feedback', 'true');
        });
    }
});

// Initialize the performance chart
function initPerformanceChart() {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;
    
    // Extract data from the page
    // In a real app, we would get this data from an API call or from the template
    // For this demo, we'll parse it from the DOM
    
    const speechScore = parseInt(document.querySelector('.text-primary.score-value').textContent) || 0;
    const bodyScore = parseInt(document.querySelector('.text-success.score-value').textContent) || 0;
    const contentScore = parseInt(document.querySelector('.text-info.score-value').textContent) || 0;
    
    // Speech detail scores
    const toneScore = parseInt(document.querySelectorAll('.progress-bar.bg-primary')[0].getAttribute('aria-valuenow')) || 0;
    const fluencyScore = parseInt(document.querySelectorAll('.progress-bar.bg-primary')[1].getAttribute('aria-valuenow')) || 0;
    const pronunciationScore = parseInt(document.querySelectorAll('.progress-bar.bg-primary')[2].getAttribute('aria-valuenow')) || 0;
    
    // Body language detail scores
    const postureScore = parseInt(document.querySelectorAll('.progress-bar.bg-success')[0].getAttribute('aria-valuenow')) || 0;
    const gesturesScore = parseInt(document.querySelectorAll('.progress-bar.bg-success')[1].getAttribute('aria-valuenow')) || 0;
    const eyeContactScore = parseInt(document.querySelectorAll('.progress-bar.bg-success')[2].getAttribute('aria-valuenow')) || 0;
    
    // Content detail scores
    const relevanceScore = parseInt(document.querySelectorAll('.progress-bar.bg-info')[0].getAttribute('aria-valuenow')) || 0;
    const structureScore = parseInt(document.querySelectorAll('.progress-bar.bg-info')[1].getAttribute('aria-valuenow')) || 0;
    const clarityScore = parseInt(document.querySelectorAll('.progress-bar.bg-info')[2].getAttribute('aria-valuenow')) || 0;
    
    // Create radar chart
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: [
                'Tone', 'Fluency', 'Pronunciation',
                'Posture', 'Gestures', 'Eye Contact',
                'Relevance', 'Structure', 'Clarity'
            ],
            datasets: [{
                label: 'Your Performance',
                data: [
                    toneScore, fluencyScore, pronunciationScore,
                    postureScore, gesturesScore, eyeContactScore,
                    relevanceScore, structureScore, clarityScore
                ],
                fill: true,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgb(54, 162, 235)',
                pointBackgroundColor: 'rgb(54, 162, 235)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgb(54, 162, 235)'
            }, {
                label: 'Industry Average',
                data: [75, 70, 72, 68, 65, 70, 75, 72, 74],
                fill: true,
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgb(255, 99, 132)',
                pointBackgroundColor: 'rgb(255, 99, 132)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgb(255, 99, 132)'
            }]
        },
        options: {
            elements: {
                line: {
                    borderWidth: 3
                }
            },
            scales: {
                r: {
                    angleLines: {
                        display: true
                    },
                    suggestedMin: 40,
                    suggestedMax: 100,
                    ticks: {
                        stepSize: 20
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                }
            },
            animation: {
                duration: 2000,
                easing: 'easeOutQuart'
            }
        }
    });
}

// Animate progress bars
function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(bar => {
        // Start with width 0
        bar.style.width = '0%';
        
        // Get the target width from aria-valuenow
        const targetWidth = bar.getAttribute('aria-valuenow') + '%';
        
        // Trigger reflow
        bar.offsetWidth;
        
        // Set the target width to animate
        setTimeout(() => {
            bar.style.width = targetWidth;
        }, 100);
    });
}
