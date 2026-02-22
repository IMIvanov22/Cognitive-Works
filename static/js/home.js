document.addEventListener('DOMContentLoaded', async () => {
    await window.userLoaded;

    const form = document.querySelector('.upload');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const token = localStorage.getItem('token');
        if (!token || !window.username) {
            alert('Please log in or create an account first.');
            return;
        }

        const fileInput = document.getElementById('image');
        if (!fileInput.files || !fileInput.files[0]) return;

        const btn = document.querySelector('[data-analyze-btn]');
        btn.disabled = true;
        btn.textContent = 'Analyzing...';

        try {
            const predictions = await window.api.analyze(token, fileInput.files[0]);
            if (predictions) {
                const resultsSection = document.getElementById('results-section');
                const resultsCard = document.getElementById('results-card');
                resultsCard.innerHTML = `
                    <div class="card__title">AI Predictions</div>
                    <p><strong>Age Group:</strong> ${predictions.age_group}</p>
                    <p><strong>Gender:</strong> ${predictions.gender}</p>
                    <p><strong>Acne Severity:</strong> ${predictions.acne_severity}</p>
                `;
                resultsSection.style.display = '';
                resultsSection.scrollIntoView({ behavior: 'smooth' });
            }
        } catch (err) {
            alert(err.message || 'Analysis failed');
        }

        btn.disabled = false;
        btn.textContent = 'Analyze';
    });
});
