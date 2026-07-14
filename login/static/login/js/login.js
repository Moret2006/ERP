document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.toggle-password').forEach((button) => {
        button.addEventListener('click', () => {
            const targetId = button.dataset.target;
            const input = document.getElementById(targetId);
            if (!input) return;

            const isPassword = input.type === 'password';
            input.type = isPassword ? 'text' : 'password';
            button.classList.toggle('active', isPassword);
            button.setAttribute(
                'aria-label',
                isPassword ? 'Ocultar senha' : 'Mostrar senha'
            );
        });
    });

    const clearButton = document.getElementById('clear-form');
    const form = document.querySelector('.login-form');

    if (clearButton && form) {
        clearButton.addEventListener('click', () => {
            form.reset();
            const emailInput = document.getElementById('email');
            if (emailInput) {
                emailInput.focus();
            }
        });
    }

    const forgotLink = document.getElementById('forgot-password');
    if (forgotLink) {
        forgotLink.addEventListener('click', (event) => {
            event.preventDefault();
            alert('Entre em contato com o administrador para redefinir sua senha.');
        });
    }
});
