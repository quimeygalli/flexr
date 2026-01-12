document.addEventListener('DOMContentLoaded', function() {
    // Select the elements
    const passwordInput = document.getElementById('password');
    const confirmInput = document.getElementById('confirm_password');

    // 1. Minimum Length Check (Applies to Login & Register)
    // We check if passwordInput exists to avoid errors on pages without it
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            if (passwordInput.value.length < 8) {
                // Sets a custom error message and blocks form submission
                passwordInput.setCustomValidity('Password must be at least 8 characters long.');
            } else {
                // Clears the error so the form can submit
                passwordInput.setCustomValidity('');
            }
            
            // If we are on the register page, re-check matching whenever the main password changes
            if (confirmInput) {
                checkPasswordsMatch();
            }
        });
    }

    // 2. Password Match Check (Applies only to Register)
    if (confirmInput) {
        confirmInput.addEventListener('input', checkPasswordsMatch);
    }

    function checkPasswordsMatch() {
        if (passwordInput.value !== confirmInput.value) {
            confirmInput.setCustomValidity('Passwords do not match.');
        } else {
            confirmInput.setCustomValidity('');
        }
    }
});