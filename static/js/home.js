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
            const data = await window.api.analyze(token, fileInput.files[0]);
            if (data && data.predictions) {
                const predictions = data.predictions;
                const recommendations = data.recommendations || [];
                const resultsSection = document.getElementById('results-section');
                const resultsCard = document.getElementById('results-card');

                let recHTML = '';
                if (recommendations.length > 0) {
                    recHTML = `
                        <div class="card__title" style="margin-top:1.5rem;">Recommended Products</div>
                        <table class="rec-table">
                            <thead>
                                <tr><th>Product</th><th>Brand</th><th>Good for Acne</th></tr>
                            </thead>
                            <tbody>
                                ${recommendations.map(r => `
                                    <tr>
                                        <td>${r.product_name}</td>
                                        <td>${r.brand}</td>
                                        <td>${r.good_for_acne ? 'Yes' : 'No'}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    `;
                } else {
                    recHTML = '<p class="muted" style="margin-top:1rem;">No matching product recommendations found.</p>';
                }

                resultsCard.innerHTML = `
                    <div class="card__title">AI Predictions</div>
                    <p><strong>Age Group:</strong> ${predictions.age_group}</p>
                    <p><strong>Gender:</strong> ${predictions.gender}</p>
                    <p><strong>Acne Severity:</strong> ${predictions.acne_severity}</p>
                    ${recHTML}
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
