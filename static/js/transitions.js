document.addEventListener('DOMContentLoaded', function() {
    // Check if the browser supports the View Transitions API
    if (!document.startViewTransition) {
        setupLegacyTransitions();
    }
});

function setupLegacyTransitions() {
    // Create transition overlay
    const overlay = document.createElement('div');
    overlay.className = 'page-transition';
    document.body.appendChild(overlay);

    // Handle all navigation links
    document.querySelectorAll('a, form').forEach(element => {
        if (element.tagName === 'FORM') {
            element.addEventListener('submit', handleNavigation);
        } else {
            element.addEventListener('click', handleNavigation);
        }
    });
}

function handleNavigation(event) {
    // Don't handle if it's an external link or has a specific target
    if (event.target.tagName === 'A' && 
        (event.target.target === '_blank' || event.target.href.startsWith('http'))) {
        return;
    }

    event.preventDefault();
    const target = event.target.tagName === 'FORM' ? 
        event.target.action : 
        event.target.href;

    // Start transition
    document.body.classList.add('page-transitioning');
    const overlay = document.querySelector('.page-transition');
    
    if (overlay) {
        overlay.style.transform = 'translateX(0)';
    }

    // Navigate after transition
    setTimeout(() => {
        if (event.target.tagName === 'FORM') {
            event.target.submit();
        } else {
            window.location.href = target;
        }
    }, 400);
}