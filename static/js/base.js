async function loadUser() {
    // Default to null
    window.username = null;

    // Get token from storage (adjust if you store it elsewhere)
    const token = localStorage.getItem("token");

    if (!token) {
        return;
    }

    try {
        const username = await window.api.self(token);
        window.username = username || null;
    } catch (err) {
        console.error("Failed to load user:", err);
        window.username = null;
    }
}

loadUser();

addEventListener("DOMContentLoaded", (event) => {
    e1 = document.getElementsByClassName("no_account")
    e2 = document.getElementsByClassName("account")
    if (window.username != null){
    for (var i = 0; i < e1.length; i++){
        e1[i].setAttribute("style", "display: none;")
    }
    for (var i = 0; i < e2.length; i++){
        e2[i].removeAttribute("style")
    }
}})