function warn(msg) {
    const warningEl = document.getElementById('warning');
    warningEl.textContent = msg;
    warningEl.removeAttribute('style');
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form.form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = form.querySelector('input[name="username"]').value.trim();
    const password = form.querySelector('input[name="password"]').value;
    const password2 = form.querySelector('input[name="password2"]').value;

    if (!username || !password) {
        warn('Please fill out all fields');
        return;
    }

    if (password !== password2) {
        warn('Passwords do not match');
        return;
    }

    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.textContent = 'Creating...';

    try {
        await window.api.register(username, password);
        window.location.href = '/login';
    } catch (err) {
        warn(err.message || 'Registration failed');
        btn.disabled = false;
        btn.textContent = 'Create Account';
    }
    });
});