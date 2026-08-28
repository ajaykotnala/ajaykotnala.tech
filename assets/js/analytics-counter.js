/**
 * Renders the Cloudflare Web Analytics numbers baked into /data/analytics.json
 * by the "Refresh Cloudflare analytics" GitHub Action.
 *
 * Usage: <span data-cf-stat="totals.pageViews">—</span>
 *        <span data-cf-stat="windows.last24h.visits">—</span>
 *        <time data-cf-stat="updatedAt"></time>
 */
(function () {
  "use strict";

  const targets = document.querySelectorAll("[data-cf-stat]");
  if (targets.length === 0) return;

  const pluck = (obj, path) => path.split(".").reduce((acc, key) => acc?.[key], obj);

  fetch("/data/analytics.json", { cache: "no-cache" })
    .then((res) => (res.ok ? res.json() : Promise.reject(new Error(res.status))))
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
    .catch(() => {
      // Never let a missing stats file break the page — just leave it hidden.
      document.querySelectorAll("[data-cf-stats-container]").forEach((el) => el.remove());
    });
})();
