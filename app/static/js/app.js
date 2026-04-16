document.addEventListener("DOMContentLoaded", () => {
  const categorySelect = document.getElementById("categorySelect");
  const randomBtn = document.getElementById("randomBtn");
  const jokeDisplay = document.getElementById("jokeDisplay");
  const jokeCategory = document.getElementById("jokeCategory");
  const jokeId = document.getElementById("jokeId");
  const copyBtn = document.getElementById("copyBtn");
  const copyStatus = document.getElementById("copyStatus");
  const statusMessage = document.getElementById("statusMessage");

  // --- Helpers ---

  function setStatus(message, type = "info") {
    statusMessage.textContent = message;
    statusMessage.className = "";
    if (message) {
      statusMessage.classList.add("status-message", `status-${type}`);
    }
  }

  function clearStatus() {
    setStatus("", "info");
  }

  function setLoading(isLoading) {
    if (isLoading) {
      document.body.classList.add("loading");
    } else {
      document.body.classList.remove("loading");
    }
  }

  function updateJokeView(data) {
    jokeDisplay.textContent = data.joke || "No joke received.";
    jokeCategory.textContent = `Category: ${data.category || "—"}`;
    jokeId.textContent = `ID: ${data.id || "—"}`;
  }

  async function fetchJSON(url) {
    setLoading(true);
    clearStatus();
    try {
      const res = await fetch(url, {
        headers: {
          Accept: "application/json",
        },
      });

      const data = await res.json().catch(() => null);

      if (!res.ok) {
        // Handle Cloudflare / rate limiting specifically
        if (res.status === 429) {
          const msg =
            "Too many requests. This instance is rate-limited. " +
            "Please slow down and try again in a moment.";
          setStatus(msg, "error");
          throw new Error(msg);
        }

        // All other errors
        const msg = data?.message || `Request failed with status ${res.status}`;
        setStatus(msg, "error");
        throw new Error(msg);
      }

      return data;
    } catch (err) {
      console.error("Fetch error:", err);
      if (!statusMessage.textContent) {
        setStatus("Unable to reach the API. Please try again.", "error");
      }
      throw err;
    } finally {
      setLoading(false);
    }
  }

  // --- API calls ---

  async function loadCategories() {
    try {
      const data = await fetchJSON("/api/categories");
      if (data.status !== "success" || !Array.isArray(data.categories)) {
        setStatus("Failed to load categories.", "error");
        return;
      }

      // Keep the first "Any category" option; clear the rest
      while (categorySelect.options.length > 1) {
        categorySelect.remove(1);
      }

      data.categories.forEach((cat) => {
        const opt = document.createElement("option");
        opt.value = cat;
        opt.textContent = cat;
        categorySelect.appendChild(opt);
      });
    } catch {
      // Error already handled in fetchJSON
    }
  }

  async function getJokeBasedOnSelection() {
    const cat = categorySelect.value;

    // If "Any category" (empty), use /api/random
    const url = cat
      ? `/api/random/${encodeURIComponent(cat)}`
      : "/api/random";

    try {
      const data = await fetchJSON(url);
      if (data.status !== "success") {
        setStatus("Failed to fetch a joke.", "error");
        return;
      }
      updateJokeView(data);
      clearStatus();
    } catch {
      // handled
    }
  }

  async function copyJokeToClipboard() {
    const text = jokeDisplay.textContent.trim();
    if (!text || text.startsWith("Click “Get Random Joke”")) {
      copyStatus.textContent = "Nothing to copy yet.";
      copyStatus.className = "copy-status copy-error";
      return;
    }

    if (!navigator.clipboard) {
      copyStatus.textContent = "Clipboard not supported in this browser.";
      copyStatus.className = "copy-status copy-error";
      return;
    }

    try {
      await navigator.clipboard.writeText(text);
      copyStatus.textContent = "Copied!";
      copyStatus.className = "copy-status copy-success";
      setTimeout(() => {
        copyStatus.textContent = "";
        copyStatus.className = "copy-status";
      }, 2000);
    } catch (err) {
      console.error("Clipboard error:", err);
      copyStatus.textContent = "Failed to copy.";
      copyStatus.className = "copy-status copy-error";
    }
  }

  // --- Event listeners ---

  randomBtn.addEventListener("click", (e) => {
    e.preventDefault();
    getJokeBasedOnSelection();
  });

  copyBtn.addEventListener("click", (e) => {
    e.preventDefault();
    copyJokeToClipboard();
  });

  // --- Initial load ---

  loadCategories();
});

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/static/js/sw.js")
      .catch((err) => console.error("SW registration failed:", err));
  });
}