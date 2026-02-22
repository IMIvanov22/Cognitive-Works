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

    if (!username || !password) {
        warn('Please fill out all fields');
        return;
    }

    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.textContent = 'Signing In...';

    try {
        const token = await window.api.login(username, password);
        localStorage.setItem('token', token);
        window.location.href = '/';
    } catch (err) {
        warn(err.message || 'Login failed');
        btn.disabled = false;
        btn.textContent = 'Sign In';
    }
    });
});
