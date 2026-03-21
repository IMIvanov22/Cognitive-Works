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
                const picked = predictions.picked || [];

                const pickedHTML = `
                    <div class="card__title" style="margin-top:1rem;">Skin Conditions</div>
                    <p><strong>Picked:</strong> ${picked.join(', ') || '—'}</p>
                `;

                let recHTML = '';
                if (recommendations.length > 0) {
                    recHTML = `
                        <div class="card__title" style="margin-top:1.5rem;">Recommended Products</div>
                        <table class="rec-table">
                            <thead>
                                <tr>
                                    <th>Product</th>
                                    <th>Brand</th>
                                    <th>Good for Acne</th>
                                    <th>Good for Redness</th>
                                    <th>Good for Pigmentation</th>
                                    <th>Good for Wrinkles</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${recommendations.map(r => `
                                    <tr>
                                        <td>${r.product_name}</td>
                                        <td>${r.brand}</td>
                                        <td>${r.good_for_acne ? 'Yes' : 'No'}</td>
                                        <td>${r.good_for_redness ? 'Yes' : 'No'}</td>
                                        <td>${r.good_for_pigmentation ? 'Yes' : 'No'}</td>
                                        <td>${r.good_for_wrinkles ? 'Yes' : 'No'}</td>
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
                    ${predictions.age_group ? `<p><strong>Age Group:</strong> ${predictions.age_group}</p>` : ''}
                    ${predictions.gender ? `<p><strong>Gender:</strong> ${predictions.gender}</p>` : ''}
                    ${pickedHTML}
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
