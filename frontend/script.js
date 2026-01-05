/* =========================================================
   script.js - SAFE & FINAL VERSION (NO REPEATED CALLS)
   ========================================================= */

const API_BASE = "http://127.0.0.1:5000";

/* =========================================================
   AUTH HELPERS
   ========================================================= */

function setToken(token) {
  localStorage.setItem("access_token", token);
}

function getToken() {
  return localStorage.getItem("access_token");
}

function clearAuth() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("google_picture");
  localStorage.removeItem("google_name");
}

/* =========================================================
   AUTH APIs
   ========================================================= */

async function doLogin(username, password) {
  return fetch(`${API_BASE}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });
}

async function doSignup(username, email, password) {
  return fetch(`${API_BASE}/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password })
  });
}

async function handleGoogleCredential(credential) {
  return fetch(`${API_BASE}/google-login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token: credential })
  });
}

/* =========================================================
   PROFILE APIs
   ========================================================= */

async function fetchProfile() {
  const token = getToken();
  if (!token) throw new Error("No token");

  const res = await fetch(`${API_BASE}/profile`, {
    headers: { Authorization: "Bearer " + token }
  });

  if (!res.ok) throw new Error("Failed to load profile");
  return res.json();
}

async function updateProfile(payload) {
  const token = getToken();
  if (!token) throw new Error("No token");

  return fetch(`${API_BASE}/profile/update`, {
    method: "PATCH",
    headers: {
      "Authorization": "Bearer " + token,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
}

function logoutAndRedirect() {
  clearAuth();
  window.location.href = "login.html";
}

/* =========================================================
   PREDICTION LOGIC (100% LOOP SAFE)
   ========================================================= */

const predictionForm = document.getElementById("predictionForm");

if (predictionForm && !predictionForm.dataset.bound) {
  // 🔒 Bind only ONCE
  predictionForm.dataset.bound = "true";

  predictionForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    // 🔒 Block double submit
    if (this.dataset.submitting === "true") return;
    this.dataset.submitting = "true";

    const resultDiv = document.getElementById("result");
    resultDiv.innerHTML =
      `<div style="text-align:center; padding:20px;">🔮 AI is analyzing your profile...</div>`;

    try {
      const token = getToken();
      if (!token) {
        resultDiv.innerHTML =
          `<div style="color:red;">❌ Please login first.</div>`;
        return;
      }

      // Collect form data
      const formData = {
        Field_of_Study: document.getElementById("field").value,
        University_GPA: parseFloat(document.getElementById("gpa").value),
        Certifications: document.getElementById("certs").value,
        Internships_Completed: parseInt(document.getElementById("internships").value)
      };

      // Send request
      const response = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer " + token
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (data.status !== "success") {
        resultDiv.innerHTML =
          `<div style="color:red;">❌ ${data.error || "Prediction failed"}</div>`;
        return;
      }

      // Render result
      const topRole = data.recommendations[0];
      const alternatives = data.recommendations.slice(1);

      let html = `
        <div style="padding:20px;">
          <h3>⭐ Top Recommended Role</h3>
          <h2>${topRole.role}</h2>
          <p><b>${topRole.confidence}</b> confidence</p>
          <hr>
          <h4>🔄 Alternatives</h4>
      `;

      alternatives.forEach(r => {
        html += `<p>${r.role} — ${r.confidence}</p>`;
      });

      html += `</div>`;
      resultDiv.innerHTML = html;

    } catch (err) {
      console.error(err);
      resultDiv.innerHTML =
        `<div style="color:red;">❌ Server connection failed.</div>`;
    } finally {
      // 🔓 Unlock submit
      this.dataset.submitting = "false";
    }
  });
}
