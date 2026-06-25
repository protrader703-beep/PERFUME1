/**
 * main.js — Attar Store
 *
 * Vanilla JavaScript for UI interactions.
 * Currently handles: mobile menu toggle, flash message auto-dismiss.
 * More functionality will be added in later steps.
 */

document.addEventListener('DOMContentLoaded', function () {

    // =================================================================
    // MOBILE NAVIGATION TOGGLE
    // =================================================================

    const menuToggle = document.getElementById('mobile-menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');

    if (menuToggle && mobileMenu) {
        menuToggle.addEventListener('click', function () {
            const isOpen = mobileMenu.classList.toggle('is-open');
            menuToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
            mobileMenu.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', function (e) {
            if (!menuToggle.contains(e.target) && !mobileMenu.contains(e.target)) {
                mobileMenu.classList.remove('is-open');
                menuToggle.setAttribute('aria-expanded', 'false');
                mobileMenu.setAttribute('aria-hidden', 'true');
            }
        });
    }


    // =================================================================
    // FLASH MESSAGES — Auto Dismiss After 5 Seconds
    // =================================================================

    const messages = document.querySelectorAll('.message');
    messages.forEach(function (msg) {
        setTimeout(function () {
            // Fade out by setting opacity
            msg.style.transition = 'opacity 0.5s ease';
            msg.style.opacity = '0';
            setTimeout(function () {
                msg.remove();
            }, 500);
        }, 5000); // 5 second delay before fade
    });


    // =================================================================
    // QUANTITY INPUT — Prevent Values Below 1
    // =================================================================

    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(function (input) {
        input.addEventListener('change', function () {
            if (parseInt(this.value) < 1 || isNaN(parseInt(this.value))) {
                this.value = 1;
            }
        });
    });

});
