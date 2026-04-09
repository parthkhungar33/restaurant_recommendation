const form = document.getElementById("query-form");
const locationSelect = document.getElementById("location");
const resultsEl = document.getElementById("results");
const notesEl = document.getElementById("notes");
const errorEl = document.getElementById("error");
const metaEl = document.getElementById("meta");
const submitBtn = document.getElementById("submit-btn");
const additionalPreferencesSelect = document.getElementById("additional_preferences");

function hide(el) {
  el.classList.add("hidden");
}

function show(el) {
  el.classList.remove("hidden");
}

function toPreferenceOption(raw) {
  const key = String(raw || "").trim().toLowerCase();
  if (key === "quick-service") return { value: "quick service", label: "Quick Service" };
  if (key === "family-friendly") return { value: "family-friendly", label: "Family-Friendly" };
  if (key === "casual") return { value: "casual", label: "Casual" };
  if (key === "nightlife") return { value: "nightlife", label: "Nightlife" };
  if (key === "fine-dine") return { value: "fine dine", label: "Fine Dine" };
  return null;
}

async function loadLocations() {
  try {
    const response = await fetch("/metadata/locations");
    const data = await response.json();
    const locations = data.locations || [];
    const experiences = data.top_experiences || [];
    locationSelect.innerHTML = '<option value="">Select location</option>';
    locations.forEach((loc) => {
      const option = document.createElement("option");
      option.value = loc;
      option.textContent = loc;
      locationSelect.appendChild(option);
    });
    additionalPreferencesSelect.innerHTML = "";
    const prefs = experiences
      .map((x) => toPreferenceOption(typeof x === "string" ? x : x.value))
      .filter(Boolean);
    if (!prefs.length) {
      additionalPreferencesSelect.innerHTML =
        '<option value="quick service">Quick Service</option><option value="casual">Casual</option><option value="family-friendly">Family-Friendly</option>';
    } else {
      prefs.forEach((p) => {
        const option = document.createElement("option");
        option.value = p.value;
        option.textContent = p.label;
        additionalPreferencesSelect.appendChild(option);
      });
    }
  } catch (error) {
    locationSelect.innerHTML = '<option value="">Failed to load locations</option>';
    additionalPreferencesSelect.innerHTML =
      '<option value="quick service">Quick Service</option><option value="casual">Casual</option><option value="family-friendly">Family-Friendly</option>';
  }
}

function renderResults(payload) {
  resultsEl.innerHTML = "";
  const recommendations = payload.recommendations || [];
  if (!recommendations.length) {
    resultsEl.innerHTML = '<div class="result-card"><strong>No recommendations found.</strong></div>';
    return;
  }

  recommendations.forEach((item) => {
    const card = document.createElement("article");
    card.className = "result-card";
    card.innerHTML = `
      <h3>${item.restaurant_name}</h3>
      <div class="muted">Cuisine: ${item.cuisine || "N/A"}</div>
      <div class="muted">Rating: ${item.rating ?? "N/A"} | Cost: ${item.estimated_cost ?? "N/A"}</div>
      <p>${item.ai_explanation || ""}</p>
    `;
    resultsEl.appendChild(card);
  });
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  hide(errorEl);
  hide(notesEl);
  hide(metaEl);
  resultsEl.innerHTML = "";
  submitBtn.disabled = true;
  submitBtn.textContent = "Loading...";

  const selectedPreferences = Array.from(additionalPreferencesSelect.selectedOptions).map(
    (option) => option.value
  );

  const payload = {
    location: locationSelect.value,
    max_budget: document.getElementById("max_budget").value
      ? Number(document.getElementById("max_budget").value)
      : null,
    cuisine: document.getElementById("cuisine").value.trim() || null,
    min_rating: document.getElementById("min_rating").value
      ? Number(document.getElementById("min_rating").value)
      : null,
    additional_preferences: selectedPreferences.length ? selectedPreferences : null,
    limit: Number(document.getElementById("limit").value || 5),
  };

  try {
    const response = await fetch("/recommendations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Request failed");
    }

    metaEl.textContent = `Request ID: ${data.request_id}`;
    show(metaEl);

    if (data.notes && data.notes.length) {
      notesEl.textContent = data.notes.join(" | ");
      show(notesEl);
    }

    renderResults(data);
  } catch (error) {
    errorEl.textContent = `Error: ${error.message}`;
    show(errorEl);
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Get Recommendations";
  }
});

loadLocations();
