/**
 * script.js
 * ---------
 * Handles all UI interactions for ResumeIQ:
 *  - Drag-and-drop / click file upload
 *  - Form validation & submit
 *  - API call to Flask /analyze
 *  - Results rendering with animation
 */

"use strict";

/* ── Config ── */
const API_BASE = "http://localhost:5000";

/* ── DOM references ── */
const dropZone        = document.getElementById("dropZone");
const resumeFile      = document.getElementById("resumeFile");
const browseBtn       = document.getElementById("browseBtn");
const removeFileBtn   = document.getElementById("removeFile");
const dropIdle        = document.getElementById("dropIdle");
const dropSelected    = document.getElementById("dropSelected");
const fileNameEl      = document.getElementById("fileName");

const jobDescEl       = document.getElementById("jobDescription");
const charCountEl     = document.getElementById("charCount");

const analyzeBtn      = document.getElementById("analyzeBtn");
const errorBanner     = document.getElementById("errorBanner");
const errorMessage    = document.getElementById("errorMessage");

const loadingState    = document.getElementById("loadingState");
const emptyState      = document.getElementById("emptyState");
const resultsContent  = document.getElementById("resultsContent");

const scoreValueEl    = document.getElementById("scoreValue");
const scoreVerdictEl  = document.getElementById("scoreVerdict");
const ringFillEl      = document.getElementById("ringFill");

const matchCountEl    = document.getElementById("matchCount");
const matchingKeyEl   = document.getElementById("matchingKeywords");

const missingCountEl  = document.getElementById("missingCount");
const missingSkillsEl = document.getElementById("missingSkills");
const missingNoteEl   = document.getElementById("missingNote");

const suggestionListEl = document.getElementById("suggestionList");
const reanalyzeBtn    = document.getElementById("reanalyzeBtn");

/* ── State ── */
let selectedFile = null;

/* ─────────────────────────────────────────────
   FILE HANDLING
   ───────────────────────────────────────────── */

/**
 * Set or clear the selected file and update UI accordingly.
 * @param {File|null} file
 */
function setFile(file) {
  if (file && !isAllowedFile(file)) {
    showError("Only PDF and DOCX files are supported.");
    return;
  }
  if (file && file.size > 5 * 1024 * 1024) {
    showError("File too large. Maximum size is 5 MB.");
    return;
  }

  selectedFile = file;
  clearError();

  if (file) {
    fileNameEl.textContent = file.name;
    dropIdle.classList.add("hidden");
    dropSelected.classList.remove("hidden");
    dropZone.classList.add("has-file");
  } else {
    fileNameEl.textContent = "";
    dropIdle.classList.remove("hidden");
    dropSelected.classList.add("hidden");
    dropZone.classList.remove("has-file");
    resumeFile.value = "";
  }

  updateSubmitButton();
}

function isAllowedFile(file) {
  return /\.(pdf|docx)$/i.test(file.name);
}

/* Click to browse */
browseBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  resumeFile.click();
});

dropZone.addEventListener("click", () => resumeFile.click());

dropZone.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    resumeFile.click();
  }
});

resumeFile.addEventListener("change", () => {
  setFile(resumeFile.files[0] || null);
});

removeFileBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  setFile(null);
});

/* Drag-and-drop */
["dragenter", "dragover"].forEach((evt) =>
  dropZone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropZone.classList.add("drag-over");
  })
);

["dragleave", "drop"].forEach((evt) =>
  dropZone.addEventListener(evt, () => dropZone.classList.remove("drag-over"))
);

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  const file = e.dataTransfer.files[0];
  if (file) setFile(file);
});

/* ─────────────────────────────────────────────
   JOB DESCRIPTION — character count
   ───────────────────────────────────────────── */

jobDescEl.addEventListener("input", () => {
  const len = jobDescEl.value.length;
  charCountEl.textContent = `${len.toLocaleString()} character${len !== 1 ? "s" : ""}`;
  updateSubmitButton();
});

/* ─────────────────────────────────────────────
   FORM VALIDATION
   ───────────────────────────────────────────── */

function updateSubmitButton() {
  const hasFile = Boolean(selectedFile);
  const hasJD   = jobDescEl.value.trim().length >= 50;
  analyzeBtn.disabled = !(hasFile && hasJD);
}

/* ─────────────────────────────────────────────
   SUBMIT — call Flask API
   ───────────────────────────────────────────── */

analyzeBtn.addEventListener("click", submitAnalysis);

async function submitAnalysis() {
  clearError();
  showView("loading");

  const formData = new FormData();
  formData.append("resume", selectedFile);
  formData.append("job_description", jobDescEl.value.trim());

  try {
    const response = await fetch(`${API_BASE}/analyze`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || `Server error (${response.status})`);
    }

    renderResults(data);

  } catch (err) {
    showView("empty");
    if (err.name === "TypeError" && err.message.includes("fetch")) {
      showError(
        "Cannot reach the server. Make sure Flask is running on localhost:5000."
      );
    } else {
      showError(err.message || "An unexpected error occurred.");
    }
  }
}

/* ─────────────────────────────────────────────
   VIEW MANAGEMENT
   ───────────────────────────────────────────── */

/**
 * Switch visible view in the results panel.
 * @param {'empty'|'loading'|'results'} view
 */
function showView(view) {
  emptyState.classList.toggle("hidden",    view !== "empty");
  loadingState.classList.toggle("hidden",  view !== "loading");
  resultsContent.classList.toggle("hidden", view !== "results");
}

/* ─────────────────────────────────────────────
   RENDER RESULTS
   ───────────────────────────────────────────── */

/**
 * Populate the results panel from API data.
 * @param {{ score: number, missing_skills: string[], suggestions: string[], matching_keywords: string[] }} data
 */
function renderResults(data) {
  const { score, missing_skills = [], suggestions = [], matching_keywords = [] } = data;

  // Score counter animation
  animateCounter(scoreValueEl, 0, score, 1000);

  // Ring progress (circumference = 2π × 50 ≈ 314.16)
  const circumference = 314.16;
  const offset = circumference - (score / 100) * circumference;
  ringFillEl.style.strokeDashoffset = offset;

  // Score colour + ring colour
  const { cls, label, color } = getScoreStyle(score);
  scoreVerdictEl.textContent = label;
  scoreVerdictEl.className = `score-verdict ${cls}`;
  ringFillEl.style.stroke = color;
  scoreValueEl.style.color = color;
  document.querySelector(".score-unit").style.color = color;

  // Matching keywords
  renderTagCloud(matchingKeywords, matching_keywords, "keyword-tag--match");
  matchCountEl.textContent = matching_keywords.length;

  // Missing skills
  if (missing_skills.length > 0) {
    renderTagCloud(missingSkillsEl, missing_skills, "keyword-tag--missing");
    missingNoteEl.classList.add("hidden");
  } else {
    missingSkillsEl.innerHTML = "";
    missingNoteEl.classList.remove("hidden");
  }
  missingCountEl.textContent = missing_skills.length;

  // Suggestions
  suggestionListEl.innerHTML = "";
  suggestions.forEach((tip, i) => {
    const li = document.createElement("li");
    li.textContent = tip;
    li.style.animationDelay = `${i * 80}ms`;
    suggestionListEl.appendChild(li);
  });

  showView("results");
}

/**
 * Populate a tag cloud container.
 * @param {HTMLElement} container
 * @param {string[]} words
 * @param {string} cssClass
 */
function renderTagCloud(container, words, cssClass) {
  container.innerHTML = "";
  words.forEach((word, i) => {
    const tag = document.createElement("span");
    tag.className = `keyword-tag ${cssClass}`;
    tag.textContent = word;
    tag.style.animationDelay = `${i * 30}ms`;
    container.appendChild(tag);
  });
}

/**
 * Map score to a colour, CSS class and verdict label.
 * @param {number} score
 * @returns {{ cls: string, label: string, color: string }}
 */
function getScoreStyle(score) {
  if (score >= 75) return { cls: "verdict--great", label: "Strong match ✓",  color: "#3fb950" };
  if (score >= 55) return { cls: "verdict--good",  label: "Good match",       color: "#00d4aa" };
  if (score >= 35) return { cls: "verdict--fair",  label: "Partial match",    color: "#f0a500" };
  return               { cls: "verdict--low",   label: "Needs improvement", color: "#f85149" };
}

/**
 * Animate a numeric counter from `from` to `to` over `duration` ms.
 * @param {HTMLElement} el
 * @param {number} from
 * @param {number} to
 * @param {number} duration
 */
function animateCounter(el, from, to, duration) {
  const start = performance.now();
  function step(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 4); // ease-out quartic
    el.textContent = (from + (to - from) * eased).toFixed(1);
    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = to.toFixed(1);
  }
  requestAnimationFrame(step);
}

/* ─────────────────────────────────────────────
   ERROR HANDLING
   ───────────────────────────────────────────── */

function showError(msg) {
  errorMessage.textContent = msg;
  errorBanner.classList.remove("hidden");
}

function clearError() {
  errorBanner.classList.add("hidden");
  errorMessage.textContent = "";
}

/* ─────────────────────────────────────────────
   RE-ANALYZE
   ───────────────────────────────────────────── */

reanalyzeBtn.addEventListener("click", () => {
  showView("empty");
  clearError();
});
