document.addEventListener('DOMContentLoaded', function() {
    // Create particles for background effect
    createParticles();
    
    // Initialize stats counter animation
    initStatsCounter();
    
    // Add scroll animations
    initScrollAnimations();
    
    // Typewriter effect for the subtitle
    initTypewriterEffect();
    
    // Initialize 3D tilt effect on feature cards
    initTiltEffect();
});

// Create animated background particles
function createParticles() {
    const container = document.querySelector('.particle-container');
    if (!container) return;
    
    const colors = ['#4361ee', '#3a0ca3', '#7209b7', '#f72585', '#4cc9f0'];
    const particleCount = window.innerWidth < 768 ? 15 : 30;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        
        // Random size, position and color
        const size = Math.random() * 15 + 5;
        const posX = Math.random() * 100;
        const posY = Math.random() * 100;
        const color = colors[Math.floor(Math.random() * colors.length)];
        const delay = Math.random() * 5;
        const duration = Math.random() * 10 + 10;
        
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${posX}%`;
        particle.style.top = `${posY}%`;
        particle.style.backgroundColor = color;
        particle.style.animationDelay = `${delay}s`;
        particle.style.animationDuration = `${duration}s`;
        
        container.appendChild(particle);
    }
}

// Animate statistics counters when they come into view
function initStatsCounter() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    if (statNumbers.length === 0) return;
    
    const options = {
        threshold: 0.5
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const countTo = parseInt(target.getAttribute('data-count'), 10);
                
                // Animate the counter
                let current = 0;
                const increment = countTo / 50; // Adjust speed here
                const timer = setInterval(() => {
                    current += increment;
                    target.textContent = Math.ceil(current);
                    
                    if (current >= countTo) {
                        target.textContent = countTo;
                        clearInterval(timer);
                    }
                }, 30);
                
                // Stop observing once animation is triggered
                observer.unobserve(target);
            }
        });
    }, options);
    
    statNumbers.forEach(stat => {
        observer.observe(stat);
    });
}

// Initialize scrolling animations
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.feature-card, .benefit-item, .stat-item');
    
    const options = {
        threshold: 0.2
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, options);
    
    animatedElements.forEach(element => {
        observer.observe(element);
    });
}

// Typewriter effect for subtitle
function initTypewriterEffect() {
    const subtitle = document.querySelector('.hero-subtitle');
    if (!subtitle || !subtitle.getAttribute('data-text')) return;
    
    const text = subtitle.getAttribute('data-text');
    subtitle.textContent = '';
    subtitle.style.opacity = '1';
    
    let i = 0;
    const speed = 50; // milliseconds between each character
    
    function typeWriter() {
        if (i < text.length) {
            subtitle.textContent += text.charAt(i);
            i++;
            setTimeout(typeWriter, speed);
        }
    }
    
    setTimeout(typeWriter, 1000); // Start after a delay
}

// Initialize 3D tilt effect on cards
function initTiltEffect() {
    const cards = document.querySelectorAll('.feature-card');
    
    cards.forEach(card => {
        card.addEventListener('mousemove', function(e) {
            const cardRect = this.getBoundingClientRect();
            const cardCenterX = cardRect.left + cardRect.width / 2;
            const cardCenterY = cardRect.top + cardRect.height / 2;
            
            const mouseX = e.clientX;
            const mouseY = e.clientY;
            
            // Calculate rotation based on mouse position relative to card center
            const rotateY = (mouseX - cardCenterX) / 10;
            const rotateX = (cardCenterY - mouseY) / 10;
            
            this.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.05, 1.05, 1.05)`;
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
            this.style.transition = 'transform 0.5s ease';
        });
    });
}

// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop,
                behavior: 'smooth'
            });
        }
    });
});