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
            throw Error("Serverside error");
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
            throw Error("Serverside error");
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
            return null;
        }

        const responseBody = await r.json();
        return responseBody.id;
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
    }
};