const no_account = document.getElementById("no_account");
const no_history = document.getElementById("no_history");
const history_list = document.getElementById("history");

const AGE_LABELS = {
    0: "Young skin (0\u201318)",
    1: "Early aging (19\u201345)",
    2: "Mature skin (46+)"
};

async function loadHistory() {
    await window.userLoaded;

    let state = 1;
    let historyData = [];

    if (window.username != null) {
        const token = localStorage.getItem("token");
        historyData = await window.api.history(token);
        if (!historyData || historyData.length < 1) {
            state = 2;
        } else {
            state = 3;
        }
    }

    switch(state) {
        case 1:
            no_account.removeAttribute("style");
            break;
        case 2:
            no_history.removeAttribute("style");
            break;
        case 3:
            let html = '';
            for (let i = 0; i < historyData.length; i++) {
                const skinType = historyData[i].skinType;
                const timestamp = new Date(historyData[i].timestamp * 1000).toLocaleString();
                const ageLabel = AGE_LABELS[skinType] || "Unknown";
                const recs = historyData[i].recommendations || [];

                let recsHtml = '';
                if (recs.length > 0) {
                    recsHtml = '<div class="history__recs"><div class="history__recs-title">Recommended Products</div><ul class="history__recs-list">';
                    for (const r of recs) {
                        const acneBadge = r.good_for_acne ? '<span class="badge badge--acne">Acne-friendly</span>' : '';
                        recsHtml += `<li class="history__rec-item"><span class="rec-product">${r.product_name}</span> <span class="rec-brand">${r.brand}</span> ${acneBadge}</li>`;
                    }
                    recsHtml += '</ul></div>';
                }

                html += `
                    <div class="history__row">
                      <div class="history__meta">
                        <div class="history__title">Age Group: ${ageLabel}</div>
                        <div class="muted small">${timestamp}</div>
                      </div>
                      ${recsHtml}
                    </div>
                `;
            }
            history_list.innerHTML = html;
            history_list.removeAttribute("style");
            break;
    }
}

loadHistory();