window.api = {
    async register(username, password) {
        const formData = new FormData();
        formData.append("username", username);
        formData.append("password", password);

        const r = await fetch("/api/signup", {
            method: "POST",
            body: formData
        });

        if (r.status !== 200) {
            const body = await r.json().catch(() => ({}));
            throw Error(body.error || "Serverside error");
        }

        const responseBody = await r.json();
        return responseBody.message;
    },

    async login(username, password) {
        const formData = new FormData();
        formData.append("username", username);
        formData.append("password", password);

        const r = await fetch("/api/login", {
            method: "POST",
            body: formData
        });

        if (r.status !== 200) {
            const body = await r.json().catch(() => ({}));
            throw Error(body.error || "Serverside error");
        }

        const responseBody = await r.json();
        return responseBody.token;
    },

    async self(token) {
        const r = await fetch("/api/self", {
            method: "POST",
            headers: {
                "token": token
            }
        });

        if (r.status !== 200) {
            return null;
        }

        const responseBody = await r.json();
        return responseBody.username;
    },

    async analyze(token, file) {
        const formData = new FormData();
        formData.append("image", file);

        const r = await fetch("/api/analyze", {
            method: "POST",
            headers: {
                "token": token
            },
            body: formData
        });

        if (r.status !== 200) {
            const body = await r.json().catch(() => ({}));
            throw Error(body.error || "Analysis failed");
        }

        const responseBody = await r.json();
        return responseBody;
    },

    async history(token){
        const r = await fetch("/api/history", {
            method: "POST",
            headers: {
                "token": token
            }
        });

        if (r.status !== 200) {
            return null;
        }

        const responseBody = await r.json();
        return responseBody.history;
    },

    async logout(token) {
        const r = await fetch("/api/logout", {
            method: "POST",
            headers: {
                "token": token
            }
        });
        return r.status === 200;
    }
};

window.userLoaded = (async function() {
    window.username = null;
    const token = localStorage.getItem("token");
    if (!token) return;
    try {
        const username = await window.api.self(token);
        window.username = username || null;
    } catch (err) {
        console.error("Failed to load user:", err);
        window.username = null;
    }
})();