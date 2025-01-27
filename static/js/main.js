document.addEventListener('DOMContentLoaded', function() {
    // Animate elements on page load
    const animatedElements = document.querySelectorAll('.animate-fade-in');
    animatedElements.forEach(element => {
        element.style.opacity = '1';
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Toggle mobile menu
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            document.querySelector('.navbar-collapse').classList.toggle('show');
        });
    }

    // Add loading spinner to buttons when clicked
    document.querySelectorAll('.btn-custom').forEach(button => {
        button.addEventListener('click', function() {
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
            setTimeout(() => {
                this.innerHTML = originalText;
            }, 1000);
        });
    });
});
