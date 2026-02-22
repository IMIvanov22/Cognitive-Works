const history_insert = document.getElementById("history_container");
const no_account = document.getElementById("no_account");
const no_history = document.getElementById("no_history");
const history_list = document.getElementById("history");

async function loadHistory() {
state = 1
history = []
if (window.username != null)
{
    token = localStorage.getItem("token");
    history = await window.api.history(token);
    if (history.length < 1){
        state = 2
    }else{
        state = 3
    }
}
switch(1) {
    case 1:
        no_account.removeAttribute("style");
        break;
    case 2:
        no_history.removeAttribute("style");
        break;
    case 3:
        for (var i = 0; i < history.length; i++){
            skinType = history[i].skinType
        }
        history_list.innerHTML = `
            <div class="history__row">
              <div class="history__meta">
                <div class="history__title">Skin Type: ${skinType} </div>
                <div class="muted small">blah</div>
                <div class="muted">blah</div>
              </div>
            </div>
            `;
        history_list.removeAttribute("style");
        break;
}
}

loadHistory();