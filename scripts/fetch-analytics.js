#!/usr/bin/env node
/**
 * Pulls Cloudflare Web Analytics (RUM) numbers via the GraphQL Analytics API
 * and bakes them into data/analytics.json so the static site can render them
 * without anyone logging into the Cloudflare dashboard.
 *
 * Env:
 *   CF_API_TOKEN   (required) token with Account Analytics -> Read
 *   CF_ACCOUNT_ID  (required) Cloudflare account id
 *   CF_SITE_TAG    (optional) RUM site tag; auto-discovered when omitted
 *   CF_SITE_TOKEN  (optional) beacon token, used to pick the right site
 *   LOOKBACK_DAYS  (optional) how many days to re-fetch each run (default 7)
 */

const fs = require("node:fs");
const path = require("node:path");

const API = "https://api.cloudflare.com/client/v4";
const OUT = path.join(__dirname, "..", "data", "analytics.json");

const token = requireEnv("CF_API_TOKEN");
const accountTag = requireEnv("CF_ACCOUNT_ID");
const lookbackDays = Number(process.env.LOOKBACK_DAYS || 7);

function requireEnv(name) {
  const v = process.env[name];
  if (!v) {
    console.error(`Missing required env var ${name}`);
    process.exit(1);
  }
  return v.trim();
}

const authHeaders = {
  Authorization: `Bearer ${token}`,
  "Content-Type": "application/json",
};

/** Cloudflare's REST envelope: { success, errors, result }. */
async function rest(path) {
  const res = await fetch(`${API}${path}`, { headers: authHeaders });
  const body = await res.json();
  if (!res.ok || body.success === false) {
    throw new Error(`${path} failed: ${JSON.stringify(body.errors || body)}`);
  }
  return body.result;
}

/**
 * The beacon token in the HTML snippet is not the same value as the siteTag
 * the GraphQL API filters on, so resolve it from the RUM site list.
 */
async function resolveSiteTag() {
  if (process.env.CF_SITE_TAG) return process.env.CF_SITE_TAG.trim();

  const sites = await rest(`/accounts/${accountTag}/rum/site_info/list`);
  if (!Array.isArray(sites) || sites.length === 0) {
    throw new Error("No Web Analytics sites found on this account");
  }

  const wanted = process.env.CF_SITE_TOKEN?.trim();
  const match = wanted && sites.find((s) => s.site_token === wanted);
  const chosen = match || sites[0];

  if (!match && sites.length > 1) {
    console.warn(
      `${sites.length} sites found and no CF_SITE_TOKEN match; defaulting to ${chosen.site_tag}`
    );
  }
  console.log(`Using siteTag ${chosen.site_tag} (${chosen.ruleset?.zone_name || "JS snippet"})`);
  return chosen.site_tag;
}

const QUERY = `
query SiteAnalytics($accountTag: String!, $siteTag: String!, $dayStart: Time!, $rangeStart: Time!, $end: Time!) {
  viewer {
    accounts(filter: { accountTag: $accountTag }) {
      last24h: rumPageloadEventsAdaptiveGroups(
        filter: { siteTag: $siteTag, datetime_geq: $dayStart, datetime_leq: $end }
        limit: 1
      ) {
        count
        sum { visits }
      }
      daily: rumPageloadEventsAdaptiveGroups(
        filter: { siteTag: $siteTag, datetime_geq: $rangeStart, datetime_leq: $end }
        limit: 1000
        orderBy: [date_ASC]
      ) {
        count
        sum { visits }
        dimensions { date }
      }
    }
  }
}`;

async function fetchAnalytics(siteTag) {
  const now = new Date();
  const variables = {
    accountTag,
    siteTag,
    end: now.toISOString(),
    dayStart: new Date(now.getTime() - 24 * 3600 * 1000).toISOString(),
    rangeStart: new Date(now.getTime() - lookbackDays * 24 * 3600 * 1000).toISOString(),
  };

  const res = await fetch(`${API}/graphql`, {
    method: "POST",
    headers: authHeaders,
    body: JSON.stringify({ query: QUERY, variables }),
  });
  const body = await res.json();

  if (body.errors?.length) {
    throw new Error(`GraphQL errors: ${JSON.stringify(body.errors, null, 2)}`);
  }
  const account = body.data?.viewer?.accounts?.[0];
  if (!account) throw new Error(`No account data returned: ${JSON.stringify(body)}`);
  return account;
}

function readExisting() {
  try {
    return JSON.parse(fs.readFileSync(OUT, "utf8"));
  } catch {
    return { daily: {} };
  }
}

function sumWindow(daily, days) {
  const cutoff = new Date(Date.now() - days * 24 * 3600 * 1000).toISOString().slice(0, 10);
  return Object.entries(daily)
    .filter(([date]) => date >= cutoff)
    .reduce(
      (acc, [, v]) => ({ pageViews: acc.pageViews + v.pageViews, visits: acc.visits + v.visits }),
      { pageViews: 0, visits: 0 }
    );
}

async function main() {
  const siteTag = await resolveSiteTag();
  const { last24h, daily: freshDays } = await fetchAnalytics(siteTag);

  // Merge fresh days over the archive. Cloudflare's free plan drops old data,
  // so the committed file becomes the long-term record.
  const previous = readExisting();
  const daily = { ...(previous.daily || {}) };
  for (const row of freshDays) {
    daily[row.dimensions.date] = {
      pageViews: row.count,
      visits: row.sum?.visits ?? 0,
    };
  }

  const sorted = Object.fromEntries(Object.entries(daily).sort(([a], [b]) => a.localeCompare(b)));
  const rolling = last24h[0] || { count: 0, sum: { visits: 0 } };

  const payload = {
    source: "cloudflare-web-analytics",
    siteTag,
    totals: sumWindow(sorted, 1e6),
    windows: {
      last24h: { pageViews: rolling.count, visits: rolling.sum?.visits ?? 0 },
      last7d: sumWindow(sorted, 7),
      last30d: sumWindow(sorted, 30),
    },
    daily: sorted,
  };

  // Only rewrite when the numbers actually moved, so a quiet site does not
  // generate a commit on every scheduled run.
  const { updatedAt: _ignored, ...previousData } = previous;
  if (JSON.stringify(previousData) === JSON.stringify(payload)) {
    console.log("No change in analytics data; leaving file untouched.");
    return;
  }

  fs.writeFileSync(OUT, JSON.stringify({ updatedAt: new Date().toISOString(), ...payload }, null, 2) + "\n");
  console.log(
    `Wrote data/analytics.json — all time: ${payload.totals.pageViews} views / ${payload.totals.visits} visits, ` +
      `last 24h: ${payload.windows.last24h.pageViews} / ${payload.windows.last24h.visits}`
  );
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
