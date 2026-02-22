document.addEventListener("DOMContentLoaded", async () => {
    await window.userLoaded;

    const e1 = document.getElementsByClassName("no_account");
    const e2 = document.getElementsByClassName("account");

    if (window.username != null) {
        for (let i = 0; i < e1.length; i++) {
            e1[i].setAttribute("style", "display: none;");
        }
        for (let i = 0; i < e2.length; i++) {
            e2[i].removeAttribute("style");
        }
    }

    document.querySelectorAll('.logout-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const token = localStorage.getItem("token");
            if (token) {
                await window.api.logout(token);
            }
            localStorage.removeItem("token");
            window.location.href = '/';
        });
    });
});