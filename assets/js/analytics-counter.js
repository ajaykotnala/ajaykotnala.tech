/**
 * Renders the Cloudflare Web Analytics numbers baked into data/analytics.json
 * by the "Refresh Cloudflare analytics" GitHub Action.
 *
 * Usage: <span data-cf-stat="totals.pageViews">—</span>
 *        <span data-cf-stat="windows.last24h.visits">—</span>
 *        <time data-cf-stat="updatedAt"></time>
 *
 * The JSON URL is resolved from this script's own location rather than an
 * absolute "/data/..." path, so it works whether the site is served from a
 * domain root or from a GitHub Pages project subpath.
 */
(function () {
  "use strict";

  const targets = document.querySelectorAll("[data-cf-stat]");
  if (targets.length === 0) return;

  const self =
    document.currentScript ||
    document.querySelector('script[src*="analytics-counter"]');
  if (!self) return;

  // this file lives at <root>/assets/js/, the data at <root>/data/
  const dataUrl = new URL("../../data/analytics.json", self.src).href;
  const pluck = (obj, path) => path.split(".").reduce((acc, key) => acc?.[key], obj);

  fetch(dataUrl, { cache: "no-cache" })
    .then((res) => (res.ok ? res.json() : Promise.reject(new Error("HTTP " + res.status))))
    .then((data) => {
      targets.forEach((el) => {
        const value = pluck(data, el.dataset.cfStat);
        if (value === undefined || value === null) return;

        if (el.dataset.cfStat === "updatedAt") {
          const when = new Date(value);
          el.textContent = when.toLocaleDateString(undefined, { day: "numeric", month: "short" });
          el.setAttribute("datetime", value);
          el.title = when.toLocaleString();
        } else {
          el.textContent = Number(value).toLocaleString();
        }
      });
      document.querySelectorAll("[data-cf-stats-container]").forEach((el) => {
        el.hidden = false;
      });
    })
    .catch((err) => {
      // Leave the container hidden rather than showing zeroes, but say why.
      console.warn("[analytics-counter] could not load " + dataUrl + ": " + err.message);
    });
})();
