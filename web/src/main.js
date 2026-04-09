import "./styles.css";

/** Resolved once: explicit VITE_API_BASE, or first /health that responds in dev, else "" (Vite proxy). */
let apiBasePromise = null;

function trimTrailingSlash(s) {
  return s.replace(/\/$/, "");
}

async function resolveApiBase() {
  const raw = import.meta.env.VITE_API_BASE;
  if (raw != null && String(raw).trim() !== "") {
    return trimTrailingSlash(String(raw).trim());
  }
  if (!import.meta.env.DEV) {
    return "";
  }
  const candidates = [
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8010",
    "http://localhost:8000",
    "http://localhost:8010",
    "",
  ];
  for (const base of candidates) {
    try {
      const url = base === "" ? "/health" : `${trimTrailingSlash(base)}/health`;
      const r = await fetch(url);
      if (!r.ok) {
        continue;
      }
      const body = await r.json();
      if (body && body.status === "ok") {
        return base;
      }
    } catch {
      /* try next candidate */
    }
  }
  return "";
}

function getApiBase() {
  if (!apiBasePromise) {
    apiBasePromise = resolveApiBase();
  }
  return apiBasePromise;
}

async function apiFetch(path, init) {
  const base = await getApiBase();
  const p = path.startsWith("/") ? path : `/${path}`;
  const url = base === "" ? p : `${trimTrailingSlash(base)}${p}`;
  return fetch(url, init);
}

const DEFAULT_CUISINE_OPTIONS = [
  "North Indian",
  "Chinese",
  "South Indian",
  "Fast Food",
  "Biryani",
  "Desserts",
  "Beverages",
  "Continental",
];
let CUISINE_OPTIONS = [...DEFAULT_CUISINE_OPTIONS];

const RATING_OPTIONS = [
  { value: null, label: "Any" },
  { value: 3, label: "3★+" },
  { value: 4, label: "4★+" },
  { value: 4.5, label: "4.5★+" },
];

const DEFAULT_MOOD_TILES = [
  { pref: "quick service", label: "Quick Bite", emoji: "\u26A1" },
  { pref: "casual", label: "Casual", emoji: "\u2615" },
  { pref: "nightlife", label: "Nightlife", emoji: "\u{1F378}" },
  { pref: "family-friendly", label: "Family Time", emoji: "\u{1F468}\u200D\u{1F469}\u200D\u{1F467}\u200D\u{1F466}" },
];
let MOOD_TILES = [...DEFAULT_MOOD_TILES];

const CUISINE_ICONS = {
  Indian: "restaurant",
  "North Indian": "restaurant",
  Chinese: "ramen_dining",
  Italian: "bakery_dining",
  "South Indian": "set_meal",
  "Fast Food": "fastfood",
  Biryani: "lunch_dining",
  Desserts: "icecream",
  Beverages: "local_cafe",
  Continental: "dinner_dining",
  Mexican: "ramen_dining",
  Japanese: "ramen_dining",
  Thai: "rice_bowl",
  "Pan Asian": "takeout_dining",
  European: "wine_bar",
};

const state = {
  selectedCuisines: new Set(),
  minRating: null,
  preferences: new Set(),
  lastResponse: null,
  lastItems: [],
  attemptedSearch: false,
};
const MIN_LOADING_MS = 900;
const DEFAULT_RESULT_LIMIT = 10;

const els = {
  cityPill: document.getElementById("city-label"),
  location: document.getElementById("location-select"),
  priceSlider: document.getElementById("max-budget-slider"),
  priceDisplay: document.getElementById("price-display"),
  cuisineChips: document.getElementById("cuisine-chips"),
  cuisineExtra: document.getElementById("cuisine-extra"),
  ratingPills: document.getElementById("rating-pills"),
  moodTiles: document.getElementById("mood-tiles"),
  preferenceExtra: document.getElementById("preference-extra"),
  resetBtn: document.getElementById("reset-filters"),
  submitBtn: document.getElementById("submit-search"),
  viewHero: document.getElementById("view-hero"),
  viewLoading: document.getElementById("view-loading"),
  viewResults: document.getElementById("view-results"),
  loadingMessage: document.getElementById("loading-message"),
  skeletonGrid: document.getElementById("skeleton-grid"),
  resultsTitle: document.getElementById("results-title"),
  resultsBadge: document.getElementById("results-badge"),
  resultsCount: document.getElementById("results-count"),
  filterChipBar: document.getElementById("filter-chip-bar"),
  aiBanner: document.getElementById("ai-banner"),
  notesRow: document.getElementById("notes-row"),
  errorRow: document.getElementById("error-row"),
  resultsGrid: document.getElementById("results-grid"),
  sortSelect: document.getElementById("sort-select"),
  locationFeedback: document.getElementById("location-feedback"),
  refreshBtn: document.getElementById("refresh-recommendations"),
};

function formatInr(n) {
  return new Intl.NumberFormat("en-IN", {
    maximumFractionDigits: 0,
  }).format(n);
}

function showView(name) {
  els.viewHero.classList.toggle("hidden", name !== "hero");
  els.viewLoading.classList.toggle("hidden", name !== "loading");
  els.viewResults.classList.toggle("hidden", name !== "results");
}

function cardImageUrl(seed, cuisineLabel = "", locationLabel = "") {
  const s = String(seed)
    .split("")
    .reduce((a, c) => a + c.charCodeAt(0), 0);
  const cuisineKey = String(cuisineLabel || "")
    .split(",")[0]
    .trim()
    .toLowerCase();
  const pools = {
    indian: [
      "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1585937421612-70a008356fbe?auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1200&q=80",
    ],
    chinese: [
      "https://images.unsplash.com/photo-1526318896980-cf78c088247c?auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1496116218417-1a781b1c416c?auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=1200&q=80",
    ],
    italian: [
      "https://images.unsplash.com/photo-1516100882582-96c3a05fe590?auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1546549032-9571cd6b27df?auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1521389508051-d7ffb5dc8f70?auto=format&fit=crop&w=1200&q=80",
    ],
    biryani: [
      "https://images.unsplash.com/photo-1633945274309-2c16c9682a8f?auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1701579231349-01df6425f0c3?auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1563379091339-03246963d96c?auto=format&fit=crop&w=1200&q=80",
    ],
    desserts: [
      "https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1551024506-0bccd828d307?auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1464306076886-da185f6a9d05?auto=format&fit=crop&w=1200&q=80",
    ],
    beverages: [
      "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?auto=format&fit=crop&w=1200&q=80",
    ],
    fastfood: [
      "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1571091718767-18b5b1457add?auto=format&fit=crop&w=1200&q=80",
    ],
    continental: [
      "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1482049016688-2d3e1b311543?auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=1200&q=80",
    ],
    default: [
      "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=1200&q=80",
      "https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?auto=format&fit=crop&w=1200&q=80",
    ],
  };

  let key = "default";
  if (cuisineKey.includes("biryani")) key = "biryani";
  else if (cuisineKey.includes("north indian") || cuisineKey.includes("south indian") || cuisineKey.includes("indian")) key = "indian";
  else if (cuisineKey.includes("chinese")) key = "chinese";
  else if (cuisineKey.includes("italian")) key = "italian";
  else if (cuisineKey.includes("dessert")) key = "desserts";
  else if (cuisineKey.includes("beverage") || cuisineKey.includes("coffee")) key = "beverages";
  else if (cuisineKey.includes("fast food") || cuisineKey.includes("burger") || cuisineKey.includes("pizza")) key = "fastfood";
  else if (cuisineKey.includes("continental") || cuisineKey.includes("american") || cuisineKey.includes("european")) key = "continental";

  const pool = pools[key] || pools.default;
  return pool[s % pool.length];
}

function fallbackCardImageUrl(seed) {
  const s = String(seed)
    .split("")
    .reduce((a, c) => a + c.charCodeAt(0), 0);
  const fallbackPool = [
    "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=1200&q=80",
  ];
  return fallbackPool[s % fallbackPool.length];
}

function cuisineIconName(label) {
  return CUISINE_ICONS[label] || "restaurant_menu";
}

function normalizeCuisineOptions(input) {
  if (!Array.isArray(input) || !input.length) {
    return [...DEFAULT_CUISINE_OPTIONS];
  }
  const labels = input
    .map((item) => {
      if (typeof item === "string") return item.trim();
      if (item && typeof item.label === "string") return item.label.trim();
      if (item && typeof item.value === "string") return item.value.trim();
      return "";
    })
    .filter(Boolean);
  return labels.length ? labels : [...DEFAULT_CUISINE_OPTIONS];
}

function toMoodTile(raw) {
  const key = String(raw || "").trim().toLowerCase();
  if (key === "quick-service") return { pref: "quick service", label: "Quick Bite", emoji: "\u26A1" };
  if (key === "casual") return { pref: "casual", label: "Casual", emoji: "\u2615" };
  if (key === "nightlife") return { pref: "nightlife", label: "Nightlife", emoji: "\u{1F378}" };
  if (key === "family-friendly")
    return {
      pref: "family-friendly",
      label: "Family Time",
      emoji: "\u{1F468}\u200D\u{1F469}\u200D\u{1F467}\u200D\u{1F466}",
    };
  if (key === "fine-dine") return { pref: "fine dine", label: "Fine Dining", emoji: "\u2728" };
  return null;
}

function normalizeMoodTiles(input) {
  if (!Array.isArray(input) || !input.length) {
    return [...DEFAULT_MOOD_TILES];
  }
  const out = [];
  const seen = new Set();
  input.forEach((item) => {
    const raw =
      typeof item === "string" ? item : typeof item?.value === "string" ? item.value : item?.label;
    const tile = toMoodTile(raw);
    if (!tile || seen.has(tile.pref)) return;
    seen.add(tile.pref);
    out.push(tile);
  });
  return out.length ? out : [...DEFAULT_MOOD_TILES];
}

function setCuisineChipVisual(btn, label) {
  const key = label.toLowerCase();
  const on = state.selectedCuisines.has(key);
  const icon = btn.querySelector(".ci-icon");
  const check = btn.querySelector(".ci-check");
  const labelEl = btn.querySelector(".ci-label");
  const base =
    "cuisine-chip flex w-full items-center gap-3 rounded-2xl border-2 p-4 text-left transition-all duration-200";
  if (on) {
    btn.className = `${base} scale-[1.02] border-primary/25 bg-primary-gradient font-bold text-white shadow-lg shadow-primary/20`;
    btn.setAttribute("aria-pressed", "true");
    icon?.classList.add("fill");
    icon?.classList.remove("text-primary");
    icon?.classList.add("text-white");
    check?.classList.remove("opacity-0");
    check?.classList.remove("text-on-surface-variant");
    check?.classList.add("text-white");
    labelEl?.classList.remove("font-medium", "text-on-surface-variant");
    labelEl?.classList.add("font-extrabold", "text-white");
  } else {
    btn.className = `${base} border-transparent bg-white font-medium text-on-surface-variant shadow-sm hover:border-primary/40 hover:text-on-surface`;
    btn.setAttribute("aria-pressed", "false");
    icon?.classList.remove("fill");
    icon?.classList.remove("text-white");
    icon?.classList.add("text-primary");
    check?.classList.add("opacity-0");
    check?.classList.remove("text-white");
    check?.classList.add("text-on-surface-variant");
    labelEl?.classList.remove("font-extrabold", "text-white");
    labelEl?.classList.add("font-medium", "text-on-surface-variant");
  }
}

function initCuisineChips() {
  els.cuisineChips.innerHTML = "";
  CUISINE_OPTIONS.forEach((label) => {
    const btn = document.createElement("button");
    btn.type = "button";
    const sym = cuisineIconName(label);
    btn.dataset.cuisine = label;
    btn.innerHTML = `
      <span class="material-symbols-outlined ci-icon text-primary">${sym}</span>
      <span class="ci-label">${escapeHtml(label)}</span>
      <span class="material-symbols-outlined ci-check ml-auto text-sm opacity-0">check_circle</span>
    `;
    btn.addEventListener("click", () => {
      const key = label.toLowerCase();
      if (state.selectedCuisines.has(key)) {
        state.selectedCuisines.delete(key);
      } else {
        state.selectedCuisines.add(key);
      }
      setCuisineChipVisual(btn, label);
    });
    setCuisineChipVisual(btn, label);
    els.cuisineChips.appendChild(btn);
  });
}

function syncRatingPillVisual(btn, active) {
  const base =
    "rating-pill headline flex-1 rounded-xl border-2 px-3 py-3 text-sm font-bold transition-all duration-200 md:text-base";
  const text = btn.querySelector(".rp-text");
  const icon = btn.querySelector(".rp-icon");
  if (active) {
    btn.className = `${base} scale-[1.03] border-primary/25 bg-primary-gradient text-white shadow-lg shadow-primary/20`;
    btn.setAttribute("aria-pressed", "true");
    text?.classList.add("font-extrabold");
    icon?.classList.remove("opacity-0", "translate-y-1");
  } else {
    btn.className = `${base} border-transparent bg-white text-on-surface-variant shadow-sm hover:border-primary/40 hover:text-on-surface`;
    btn.setAttribute("aria-pressed", "false");
    text?.classList.remove("font-extrabold");
    icon?.classList.add("opacity-0", "translate-y-1");
  }
}

function initRatingPills() {
  els.ratingPills.innerHTML = "";
  RATING_OPTIONS.forEach((opt) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "rating-pill";
    btn.innerHTML = `
      <span class="inline-flex items-center gap-2">
        <span class="material-symbols-outlined rp-icon text-base leading-none opacity-0 transition-all duration-200">check_circle</span>
        <span class="rp-text">${escapeHtml(opt.label)}</span>
      </span>
    `;
    btn.dataset.value = opt.value === null ? "" : String(opt.value);
    btn.addEventListener("click", () => {
      state.minRating = opt.value;
      els.ratingPills.querySelectorAll(".rating-pill").forEach((p) => {
        syncRatingPillVisual(p, p === btn);
      });
    });
    els.ratingPills.appendChild(btn);
  });
  const first = els.ratingPills.querySelector(".rating-pill");
  if (first) {
    state.minRating = RATING_OPTIONS[0].value;
    els.ratingPills.querySelectorAll(".rating-pill").forEach((p) => {
      syncRatingPillVisual(p, p === first);
    });
  }
}

function setMoodTileVisual(tile, selected) {
  const base =
    "mood-tile group relative flex flex-col items-center rounded-3xl border-2 p-6 text-center transition-all duration-200";
  const emoji = tile.querySelector(".mood-emoji");
  const label = tile.querySelector(".mood-label");
  const check = tile.querySelector(".mood-check");
  tile.className = selected
    ? `${base} cursor-pointer scale-[1.02] border-primary/25 bg-primary-gradient text-white shadow-lg shadow-primary/20`
    : `${base} cursor-pointer border-transparent bg-white text-on-surface hover:border-primary/40`;
  tile.setAttribute("aria-pressed", selected ? "true" : "false");
  if (selected) {
    emoji?.classList.add("drop-shadow");
    label?.classList.remove("text-on-surface");
    label?.classList.add("text-white", "font-extrabold");
    check?.classList.remove("opacity-0");
  } else {
    emoji?.classList.remove("drop-shadow");
    label?.classList.remove("text-white", "font-extrabold");
    label?.classList.add("text-on-surface");
    check?.classList.add("opacity-0");
  }
}

function initMoodTiles() {
  if (!els.moodTiles) {
    return;
  }
  els.moodTiles.innerHTML = "";
  MOOD_TILES.forEach((m) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.dataset.pref = m.pref;
    btn.innerHTML = `
      <span class="material-symbols-outlined mood-check absolute right-3 top-3 text-base text-white opacity-0 transition-all duration-200">check_circle</span>
      <span class="mood-emoji mb-2 block text-3xl transition-transform group-hover:scale-125">${m.emoji}</span>
      <span class="mood-label font-medium text-on-surface">${escapeHtml(m.label)}</span>
    `;
    btn.addEventListener("click", () => {
      if (state.preferences.has(m.pref)) {
        state.preferences.delete(m.pref);
      } else {
        state.preferences.add(m.pref);
      }
      setMoodTileVisual(btn, state.preferences.has(m.pref));
    });
    setMoodTileVisual(btn, state.preferences.has(m.pref));
    els.moodTiles.appendChild(btn);
  });
}

function buildSkeleton() {
  const row = `
    <div class="animate-pulse overflow-hidden rounded-xl bg-surface-container-low shadow-sm">
      <div class="grid gap-0 md:grid-cols-2">
        <div class="h-56 bg-surface-container-highest md:h-72"></div>
        <div class="space-y-4 p-8">
          <div class="h-3 w-24 rounded-full bg-surface-container-highest"></div>
          <div class="h-7 w-3/4 max-w-md rounded-lg bg-surface-container-highest"></div>
          <div class="h-4 w-full rounded bg-surface-container-highest"></div>
          <div class="h-16 rounded-2xl bg-surface-container-highest"></div>
        </div>
      </div>
    </div>`;
  els.skeletonGrid.innerHTML = `<div class="space-y-6">${Array.from({ length: 3 }).map(() => row).join("")}</div>`;
}

function updatePriceDisplay() {
  const v = Number(els.priceSlider.value);
  els.priceDisplay.textContent = `\u20B9${formatInr(v)}${v >= 5000 ? "+" : ""}`;
}

function updateCityPill() {
  const loc = els.location.value.trim();
  els.cityPill.textContent = loc ? `Curating picks in ${loc}.` : "Pick a locality to begin.";
  const hasLocation = Boolean(loc);
  if (els.locationFeedback) {
    els.locationFeedback.classList.toggle("hidden", hasLocation || !state.attemptedSearch);
  }
  els.location.classList.toggle("is-invalid", !hasLocation && state.attemptedSearch);
  const tease = document.getElementById("hero-city-tease");
  if (tease) {
    tease.innerHTML = loc
      ? `Nice — we&apos;ll hunt for memorable meals in <strong>${escapeHtml(loc)}</strong> using the concierge panel. Hit <strong>Show me great places</strong> when you&apos;re ready.`
      : `Pick an area on the left, tune budget and cravings, then tap <strong>Show me great places</strong> for a shortlist that fits your night out.`;
  }
}

function collectCuisinePayload() {
  const fromChips = [...state.selectedCuisines];
  const extra = els.cuisineExtra.value.trim();
  if (extra) {
    fromChips.push(extra.toLowerCase());
  }
  if (!fromChips.length) {
    return null;
  }
  const unique = [...new Set(fromChips)];
  return unique.length === 1 ? unique[0] : unique;
}

function collectAdditionalPreferences() {
  const merged = new Set(state.preferences);
  const raw = els.preferenceExtra ? els.preferenceExtra.value.trim() : "";
  if (raw) {
    raw
      .split(/[,;]|\n/)
      .map((p) => p.trim().toLowerCase())
      .filter(Boolean)
      .forEach((p) => merged.add(p));
  }
  return merged.size ? [...merged] : null;
}

function buildPayload() {
  const location = els.location.value.trim();
  const maxBudget = Number(els.priceSlider.value);
  return {
    location,
    max_budget: maxBudget > 0 ? maxBudget : null,
    cuisine: collectCuisinePayload(),
    min_rating: state.minRating,
    additional_preferences: collectAdditionalPreferences(),
    limit: DEFAULT_RESULT_LIMIT,
  };
}

function resetFilters() {
  state.selectedCuisines.clear();
  state.minRating = null;
  state.preferences.clear();
  els.cuisineExtra.value = "";
  if (els.preferenceExtra) {
    els.preferenceExtra.value = "";
  }
  els.priceSlider.value = "2000";
  initCuisineChips();
  initRatingPills();
  initMoodTiles();
  updatePriceDisplay();
}

function sortItems(items, mode) {
  const copy = [...items];
  if (mode === "rating") {
    copy.sort((a, b) => (b.rating ?? 0) - (a.rating ?? 0));
  } else if (mode === "cost-asc") {
    copy.sort((a, b) => (a.estimated_cost ?? 1e9) - (b.estimated_cost ?? 1e9));
  } else if (mode === "cost-desc") {
    copy.sort((a, b) => (b.estimated_cost ?? 0) - (a.estimated_cost ?? 0));
  }
  return copy;
}

function toFriendlyRelaxedLabel(key) {
  const cleaned = String(key || "").trim().toLowerCase();
  if (cleaned === "min_rating" || cleaned === "rating") {
    return "rating";
  }
  if (cleaned === "max_budget" || cleaned === "budget") {
    return "budget";
  }
  if (cleaned === "cuisine") {
    return "cuisine";
  }
  return cleaned.replaceAll("_", " ");
}

function buildFriendlyRelaxedMessage(rawNotes, relaxedConstraints) {
  const fromConstraints = (relaxedConstraints || []).map(toFriendlyRelaxedLabel).filter(Boolean);
  let labels = [...new Set(fromConstraints)];

  if (!labels.length && Array.isArray(rawNotes)) {
    const joined = rawNotes.join(" ").toLowerCase();
    if (joined.includes("min_rating")) labels.push("rating");
    if (joined.includes("max_budget")) labels.push("budget");
    if (joined.includes("cuisine")) labels.push("cuisine");
  }

  if (!labels.length) {
    return "";
  }
  if (labels.length === 1) {
    return `We widened your ${labels[0]} preference a little so you still get strong options.`;
  }
  if (labels.length === 2) {
    return `We widened your ${labels[0]} and ${labels[1]} preferences a little so you still get strong options.`;
  }
  return `We widened your ${labels.slice(0, -1).join(", ")}, and ${labels[labels.length - 1]} preferences a little so you still get strong options.`;
}

function renderFilterChips(data) {
  els.filterChipBar.innerHTML = "";
  const chips = [];

  const loc = data.applied_filters?.location;
  if (loc) {
    chips.push({ text: loc, removable: false });
  }

  const cuisines = data.applied_filters?.cuisines || [];
  cuisines.forEach((c) => chips.push({ text: c, type: "cuisine" }));

  const mb = data.applied_filters?.max_budget;
  if (mb != null) {
    chips.push({ text: `Up to \u20B9${formatInr(mb)}`, type: "budget" });
  }

  const mr = data.applied_filters?.min_rating;
  if (mr != null) {
    chips.push({ text: `${mr}+ rating`, type: "rating" });
  }

  chips.forEach((c) => {
    const span = document.createElement("span");
    span.className =
      "inline-flex items-center rounded-full bg-surface-container-high px-3 py-1.5 text-xs font-bold uppercase tracking-wider text-on-surface";
    span.textContent = c.text;
    els.filterChipBar.appendChild(span);
  });
}

function costTierLabel(cost) {
  if (cost == null) {
    return null;
  }
  if (cost < 800) {
    return "Budget-friendly";
  }
  if (cost < 2000) {
    return "Moderate";
  }
  if (cost < 4000) {
    return "Upscale";
  }
  return "Premium";
}

function resultLayoutVariant(index) {
  return index % 3;
}

function buildResultCard(item, data, index) {
  const imgUrl = cardImageUrl(
    item.restaurant_id,
    item.cuisine,
    data.applied_filters?.location || "",
  );
  const ratingLabel = item.rating != null ? String(item.rating) : "\u2014";
  const loc = data.applied_filters?.location || "";
  const cuisineFirst = (item.cuisine || "Cuisine").split(",")[0].trim();
  const tagline = `${cuisineFirst.toUpperCase()} \u2022 ${loc.toUpperCase()}`;
  const costLine = item.estimated_cost != null ? `\u20B9${formatInr(item.estimated_cost)} for two` : "Cost n/a";
  const tier = costTierLabel(item.estimated_cost);
  const explain = item.ai_explanation || "A solid match for what you asked for.";
  const name = item.restaurant_name;
  const smart = (item.ai_explanation || "").length > 80 || index < 2;
  const showSmart = smart
    ? `
    <div class="mb-4 inline-flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-xs font-bold uppercase tracking-wider text-primary">
      <span class="material-symbols-outlined text-sm">auto_awesome</span>
      Smart match
    </div>`
    : "";

  const tierRow = tier
    ? `<div class="flex flex-wrap gap-4 mb-6">
        <div class="flex items-center gap-2 text-sm font-medium text-on-surface">
          <span class="material-symbols-outlined text-primary">currency_rupee</span>
          <span>${escapeHtml(tier)}</span>
        </div>
        <div class="flex items-center gap-2 text-sm font-medium text-on-surface">
          <span class="material-symbols-outlined text-primary">wine_bar</span>
          <span>${escapeHtml(cuisineFirst)}</span>
        </div>
      </div>`
    : `<div class="mb-6 flex flex-wrap gap-4 text-sm font-medium text-on-surface">
        <span>${escapeHtml(costLine)}</span>
      </div>`;

  const actions = `
    <div class="mt-8 flex flex-wrap gap-3">
      <button type="button" class="js-detail headline rounded-full bg-primary-gradient px-6 py-3 text-sm font-bold text-white shadow-md transition hover:scale-[1.02] md:text-base">View details</button>
      <button type="button" class="js-similar headline rounded-full bg-surface-container-highest px-6 py-3 text-sm font-bold text-primary transition hover:bg-primary-container hover:text-on-primary-container md:text-base">Show similar</button>
    </div>`;

  const wrap = document.createElement("article");
  wrap.className = "result-entry relative";

  const v = resultLayoutVariant(index);

  if (v === 0) {
    wrap.innerHTML = `
      <div class="group grid gap-0 overflow-hidden rounded-xl bg-surface-container-low shadow-sm md:grid-cols-2">
        <div class="relative h-72 min-h-[18rem] md:h-full">
          <img src="${imgUrl}" alt="" class="h-full w-full object-cover transition-transform duration-700 group-hover:scale-105" loading="lazy" />
          <div class="absolute left-4 top-4 flex items-center gap-2 rounded-full bg-white/90 px-4 py-2 backdrop-blur-md">
            <span class="material-symbols-outlined fill text-sm text-primary">star</span>
            <span class="font-bold">${escapeHtml(ratingLabel)}</span>
          </div>
          ${smart ? `<div class="absolute right-4 top-4 rounded-full bg-white/90 px-3 py-1 text-xs font-bold text-primary backdrop-blur-md">\u2728 Pick</div>` : ""}
        </div>
        <div class="flex flex-col justify-center p-8 md:p-12">
          <div class="mb-2 flex flex-wrap gap-2">
            <span class="text-xs font-bold uppercase tracking-widest text-primary">${escapeHtml(tagline)}</span>
          </div>
          ${showSmart}
          <h3 class="headline mb-2 text-3xl font-extrabold text-on-surface">${escapeHtml(name)}</h3>
          <p class="mb-2 text-lg text-on-surface-variant">${escapeHtml((item.cuisine || "").split(",").slice(0, 2).join(" · ") || "Great dining.")}</p>
          ${tierRow}
          <div class="relative rounded-3xl rounded-tl-none border-l-4 border-primary bg-secondary-container p-6">
            <p class="font-medium italic leading-relaxed text-on-secondary-container">\u201C${escapeHtml(explain)}\u201D</p>
          </div>
          ${actions}
        </div>
      </div>`;
  } else if (v === 1) {
    wrap.classList.add("pt-8", "md:pt-12");
    wrap.innerHTML = `
      <div class="rounded-xl border-t-8 border-primary-container bg-surface-container-low p-8 shadow-sm md:p-12">
        <div class="flex flex-col gap-12 md:flex-row">
          <div class="w-full md:w-1/3 md:-mt-24">
            <div class="group h-80 overflow-hidden rounded-xl shadow-2xl transition-all duration-500 md:rotate-2 md:hover:rotate-0">
              <img src="${imgUrl}" alt="" class="h-full w-full object-cover" loading="lazy" />
            </div>
          </div>
          <div class="flex-1">
            <div class="mb-4 flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
              <div>
                <span class="mb-2 block text-xs font-bold uppercase tracking-widest text-primary">${escapeHtml(tagline)}</span>
                <h3 class="headline text-3xl font-extrabold text-on-surface">${escapeHtml(name)}</h3>
              </div>
              <div class="flex items-center gap-1 rounded-full bg-primary px-4 py-2 text-white">
                <span class="font-bold">${escapeHtml(ratingLabel)}</span>
                <span class="material-symbols-outlined text-sm">star</span>
              </div>
            </div>
            <p class="mb-6 text-lg text-on-surface-variant">${escapeHtml(explain.slice(0, 160))}${explain.length > 160 ? "…" : ""}</p>
            ${tierRow}
            <div class="rounded-3xl border border-outline-variant/15 bg-white p-6 shadow-sm">
              <div class="mb-2 flex items-center gap-2">
                <span class="material-symbols-outlined text-primary">auto_awesome</span>
                <span class="headline font-bold text-primary">AI Concierge</span>
              </div>
              <p class="leading-relaxed text-on-surface">${escapeHtml(explain)}</p>
            </div>
            ${actions}
          </div>
        </div>
      </div>`;
  } else {
    wrap.innerHTML = `
      <div class="flex flex-col overflow-hidden rounded-xl bg-surface-container shadow-sm md:flex-row">
        <div class="h-64 md:h-auto md:w-2/5">
          <img src="${imgUrl}" alt="" class="h-full w-full object-cover" loading="lazy" />
        </div>
        <div class="flex flex-1 flex-col p-8 md:p-12">
          <span class="mb-2 block text-xs font-bold uppercase tracking-widest text-primary">${escapeHtml(tagline)}</span>
          <h3 class="headline mb-4 text-3xl font-extrabold text-on-surface">${escapeHtml(name)}</h3>
          <p class="mb-6 text-lg text-on-surface-variant">${escapeHtml(cuisineFirst)} \u2022 ${escapeHtml(costLine)}</p>
          <div class="mb-6 grid grid-cols-2 gap-4">
            <div class="flex items-center gap-2 rounded-xl bg-white p-3 text-sm font-medium">
              <span class="material-symbols-outlined text-primary">groups</span>
              <span>Great for groups</span>
            </div>
            <div class="flex items-center gap-2 rounded-xl bg-white p-3 text-sm font-medium">
              <span class="material-symbols-outlined text-primary">star</span>
              <span>${escapeHtml(ratingLabel)} rated</span>
            </div>
          </div>
          <div class="rounded-2xl bg-secondary-container p-5">
            <p class="text-sm font-medium text-on-secondary-container">${escapeHtml(explain)}</p>
          </div>
          ${actions}
        </div>
      </div>`;
  }

  wrap.querySelector(".js-detail")?.addEventListener("click", () => {
    window.alert(`${item.restaurant_name}: ${item.ai_explanation || "Great pick."}`);
  });
  const cardImg = wrap.querySelector("img");
  if (cardImg) {
    cardImg.addEventListener(
      "error",
      () => {
        cardImg.src = fallbackCardImageUrl(`${item.restaurant_id}-fallback`);
      },
      { once: true },
    );
  }
  wrap.querySelector(".js-similar")?.addEventListener("click", () => {
    if (item.cuisine) {
      els.cuisineExtra.value = String(item.cuisine).split(",")[0].trim();
      void runSearch();
    }
  });

  return wrap;
}

function renderResults(data) {
  state.lastResponse = data;
  let items = data.recommendations || [];
  items = sortItems(items, els.sortSelect.value);

  const loc = data.applied_filters?.location || "";
  els.resultsTitle.textContent = "Top picks for you";

  if (els.resultsBadge) {
    if (items.length) {
      els.resultsBadge.textContent = `${items.length} recommendation${items.length === 1 ? "" : "s"}`;
      els.resultsBadge.classList.remove("hidden");
    } else {
      els.resultsBadge.classList.add("hidden");
    }
  }

  els.resultsCount.textContent = items.length
    ? loc
      ? `Curated for ${loc} \u2022 ${items.length} spot${items.length === 1 ? "" : "s"}`
      : `${items.length} curated spot${items.length === 1 ? "" : "s"}`
    : "No spots matched \u2014 try relaxing a filter.";

  renderFilterChips(data);

  els.notesRow.classList.add("hidden");
  els.notesRow.textContent = "";

  const friendlyMsg = buildFriendlyRelaxedMessage(
    data.notes,
    data.applied_filters?.relaxed_constraints,
  );
  const hasRelaxed = (data.applied_filters?.relaxed_constraints?.length || 0) > 0;
  const hasNotes = (data.notes?.length || 0) > 0;

  if ((hasRelaxed || friendlyMsg) && (hasNotes || hasRelaxed)) {
    const msg =
      friendlyMsg ||
      (hasRelaxed
        ? "We widened the search slightly so you still get great options that match your vibe."
        : "");
    if (msg) {
      els.aiBanner.textContent = msg;
      els.aiBanner.classList.remove("hidden");
    } else {
      els.aiBanner.classList.add("hidden");
    }
  } else if (hasNotes) {
    els.aiBanner.classList.add("hidden");
    els.notesRow.textContent = data.notes.join(" \u2022 ");
    els.notesRow.classList.remove("hidden");
  } else {
    els.aiBanner.classList.add("hidden");
  }

  els.resultsGrid.innerHTML = "";
  items.forEach((item, index) => {
    els.resultsGrid.appendChild(buildResultCard(item, data, index));
  });

  state.lastItems = items;
}

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

async function runSearch() {
  state.attemptedSearch = true;
  const payload = buildPayload();
  if (!payload.location) {
    if (els.locationFeedback) {
      els.locationFeedback.classList.remove("hidden");
    }
    els.location.classList.add("is-invalid");
    els.location.focus();
    return;
  }

  els.errorRow.classList.add("hidden");
  els.notesRow.classList.add("hidden");

  showView("loading");
  buildSkeleton();
  const loadingStart = Date.now();
  const loc = payload.location;
  els.loadingMessage.textContent = `Our digital concierge is scanning ${loc} for picks that fit your budget and tastes.`;

  els.submitBtn.disabled = true;

  try {
    const response = await apiFetch("/recommendations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail || data));
    }

    const elapsed = Date.now() - loadingStart;
    if (elapsed < MIN_LOADING_MS) {
      await new Promise((resolve) => setTimeout(resolve, MIN_LOADING_MS - elapsed));
    }
    renderResults(data);
    showView("results");
  } catch (err) {
    showView("hero");
    els.errorRow.textContent = `Something went wrong: ${err.message}`;
    els.errorRow.classList.remove("hidden");
  } finally {
    els.submitBtn.disabled = false;
  }
}

async function loadLocations() {
  try {
    const response = await apiFetch("/metadata/locations");
    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }
    const data = await response.json();
    const locations = data.locations || [];
    CUISINE_OPTIONS = normalizeCuisineOptions(data.top_cuisines);
    MOOD_TILES = normalizeMoodTiles(data.top_experiences);
    state.selectedCuisines.clear();
    state.preferences.clear();
    initCuisineChips();
    initMoodTiles();
    els.location.innerHTML = '<option value="">Select area</option>';
    locations.forEach((loc) => {
      const option = document.createElement("option");
      option.value = loc;
      option.textContent = loc;
      els.location.appendChild(option);
    });
  } catch (err) {
    console.error("loadLocations failed:", err);
    CUISINE_OPTIONS = [...DEFAULT_CUISINE_OPTIONS];
    MOOD_TILES = [...DEFAULT_MOOD_TILES];
    initCuisineChips();
    initMoodTiles();
    els.location.innerHTML =
      '<option value="">Could not load cities — start the API (uvicorn) or set VITE_API_BASE in web/.env</option>';
  }
  updateCityPill();
}

els.location.addEventListener("change", updateCityPill);
els.priceSlider.addEventListener("input", updatePriceDisplay);
els.resetBtn.addEventListener("click", () => {
  resetFilters();
  showView("hero");
});
els.submitBtn.addEventListener("click", () => void runSearch());
els.sortSelect.addEventListener("change", () => {
  if (state.lastResponse) {
    renderResults(state.lastResponse);
  }
});

els.refreshBtn?.addEventListener("click", () => void runSearch());

initRatingPills();
updatePriceDisplay();
buildSkeleton();
loadLocations();
