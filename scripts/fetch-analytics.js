#!/usr/bin/env node
/**
 * Pulls Cloudflare Web Analytics (RUM) numbers via the GraphQL Analytics API
 * and bakes them into data/analytics.json so the static site can render them
 * without anyone logging into the Cloudflare dashboard.
 *
 * Deliberately uses only the GraphQL API, which needs a single token
 * permission: Account -> Account Analytics -> Read. The REST endpoint that
 * lists RUM sites would additionally require Account Settings: Read, so the
 * site tag is left unset and the account-level aggregate is used instead.
 *
 * Env:
 *   CF_API_TOKEN   (required) token with Account Analytics -> Read
 *   CF_ACCOUNT_ID  (required) Cloudflare account id
 *   CF_SITE_TAG    (optional) only needed once the account has >1 RUM site
 *   LOOKBACK_DAYS  (optional) how many days to re-fetch each run (default 7)
 */

const fs = require("node:fs");
const path = require("node:path");

const GRAPHQL = "https://api.cloudflare.com/client/v4/graphql";
const OUT = path.join(__dirname, "..", "data", "analytics.json");

const token = requireEnv("CF_API_TOKEN");
const accountTag = requireEnv("CF_ACCOUNT_ID");
const siteTag = process.env.CF_SITE_TAG?.trim() || null;
const lookbackDays = Number(process.env.LOOKBACK_DAYS || 7);

function requireEnv(name) {
  const v = process.env[name];
  if (!v) {
    console.error(`Missing required env var ${name}`);
    process.exit(1);
  }
  return v.trim();
}

/** Optional site filter; omitted entirely when the account has a single site. */
const siteFilter = siteTag ? "siteTag: $siteTag, " : "";
const siteParam = siteTag ? ", $siteTag: String!" : "";

const QUERY = `
query SiteAnalytics($accountTag: String!, $dayStart: Time!, $rangeStart: Time!, $end: Time!${siteParam}) {
  viewer {
    accounts(filter: { accountTag: $accountTag }) {
      last24h: rumPageloadEventsAdaptiveGroups(
        filter: { ${siteFilter}datetime_geq: $dayStart, datetime_leq: $end }
        limit: 1
      ) {
        count
        sum { visits }
      }
      daily: rumPageloadEventsAdaptiveGroups(
        filter: { ${siteFilter}datetime_geq: $rangeStart, datetime_leq: $end }
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

async function fetchAnalytics() {
  const now = new Date();
  const variables = {
    accountTag,
    end: now.toISOString(),
    dayStart: new Date(now.getTime() - 24 * 3600 * 1000).toISOString(),
    rangeStart: new Date(now.getTime() - lookbackDays * 24 * 3600 * 1000).toISOString(),
    ...(siteTag ? { siteTag } : {}),
  };

  const res = await fetch(GRAPHQL, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({ query: QUERY, variables }),
  });
  const body = await res.json();

  if (body.errors?.length) {
    const messages = body.errors.map((e) => e.message).join("; ");
    if (/auth|permission|denied|forbidden/i.test(messages)) {
      throw new Error(
        `GraphQL auth failure: ${messages}\n` +
          `The token needs exactly: Account -> Account Analytics -> Read, ` +
          `scoped to account ${accountTag}.`
      );
    }
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
  const { last24h, daily: freshDays } = await fetchAnalytics();

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
    siteTag: siteTag || "account-wide",
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
