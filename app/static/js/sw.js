self.addEventListener("install", (event) => {
  // Skip waiting so new SW takes control ASAP
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  // Claim clients so the SW starts controlling them immediately.
  event.waitUntil(self.clients.claim());
});
