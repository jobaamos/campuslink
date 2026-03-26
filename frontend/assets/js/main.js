const API_URL = "https://campuslink-api-o67t.onrender.com";

// TOKEN MANAGEMENT
function getToken() {
    return localStorage.getItem("token");
}

function setToken(token) {
    localStorage.setItem("token", token);
}

function removeToken() {
    localStorage.removeItem("token");
}

function getUser() {
    const user = localStorage.getItem("user");
    return user ? JSON.parse(user) : null;
}

function setUser(user) {
    localStorage.setItem("user", JSON.stringify(user));
}

function removeUser() {
    localStorage.removeItem("user");
}

function isLoggedIn() {
    return !!getToken();
}

function logout() {
    removeToken();
    removeUser();
    window.location.href = "login.html";
}

// REDIRECT IF NOT LOGGED IN
function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = "login.html";
    }
}

// REDIRECT IF ALREADY LOGGED IN
function redirectIfLoggedIn() {
    if (isLoggedIn()) {
        window.location.href = "dashboard.html";
    }
}

// API REQUESTS
async function apiRequest(endpoint, method = "GET", body = null, auth = false) {
    const headers = { "Content-Type": "application/json" };
    if (auth) {
        headers["Authorization"] = `Bearer ${getToken()}`;
    }

    const options = { method, headers };
    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_URL}${endpoint}`, options);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Something went wrong");
    }

    return data;
}

// SHOW ALERT
function showAlert(message, type = "success", containerId = "alert-container") {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
    setTimeout(() => { container.innerHTML = ""; }, 4000);
}

// FORMAT DATE
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-GB", {
        day: "numeric", month: "short", year: "numeric"
    });
}

// FORMAT CURRENCY
function formatCurrency(amount) {
    return `₦${Number(amount).toLocaleString()}`;
}

// LOAD UNREAD NOTIFICATION COUNT
async function loadNavNotifCount() {
    if (!isLoggedIn()) return;
    try {
        const data = await apiRequest("/notifications/unread-count", "GET", null, true);
        const els = document.querySelectorAll(".notif-count");
        els.forEach(el => {
            if (data.count > 0) {
                el.textContent = `(${data.count})`;
            } else {
                el.textContent = "";
            }
        });
    } catch (error) {
        console.error(error);
    }
}

loadNavNotifCount();