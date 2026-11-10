# 19. Credits & limits

Credits are Rayu's metering currency for **hosted** model usage: every request
you make to a Rayu-hosted model is priced in credits, and your plan's allowance
is spent down as you use them. This page explains what credits are, which
limits apply on top of them, and what happens when you hit any of them.

> TL;DR
> - Credits are only consumed by **Rayu-hosted** traffic. Bring-your-own-key
>   (BYOK) traffic goes straight to your provider and costs zero credits.
> - Your **plan allowance per billing period** is the money limit. On top of it,
>   paid plans have **pacing limits**: a weekly cap and a per-session (5-hour)
>   cap. These delay spending; they never reduce what the period grants.
> - Free plan: no hosted credits, but a **50-turns-per-day** cap.
> - Personal and team plans are one ladder. Each tier includes the features and
>   models of the tier below it; credits are that tier's own allowance.
> - A new team has **no credit until it has a team plan**. Its team-billed
>   requests are refused with `team_plan_required` until then.
> - Spending order is fixed: plan credits first, then your pay-as-you-go
>   balance. The two balances **never merge**.
> - All numbers below are current defaults and can change — check `/billing`,
>   `/usage`, or rayucode.com for what applies to you right now.

---

## What a credit is

A credit is a fine-grained unit of model usage, not a request count. A request's
cost is computed from the model's **actual** token usage across four buckets
(fresh input, output, cache-read, cache-write), each priced separately:

```
credits = (input×rIn + output×rOut + cacheRead×rRead + cacheWrite×rWrite) ÷ 1,000,000
```

The full mechanics — per-1M rates and rounding precision — are in
[20-how-token-credit-charge.md](./20-how-token-credit-charge.md). A trivial
"hello" turn costs a fraction of a credit; a long agentic turn can cost tens.
Nothing is rounded up to a whole credit per request.

## Which traffic costs credits

| Traffic | Path | Credits? |
|---|---|---|
| Rayu-hosted models (`/login` + a plan) | Your CLI or RayuCode extension → Rayu's hosted service → provider | Yes — metered against your plan allowance and PAYG balance. |
| BYOK (your own provider API key, e.g. DeepSeek, OpenRouter, Anthropic direct) | Your CLI or extension → the provider directly | No — you pay your provider. Rayu plan limits do not apply. |

Limits apply to hosted traffic only. Your CLI and extension show your balances
and usage, but Rayu's hosted service is what decides whether a hosted request
may proceed.

## The limits, one by one

### Plan allowance (per billing period)

Each paid plan grants a monthly credit allowance. The allowance resets when your
billing period renews. Free has no hosted allowance at all — it is a BYOK plan.

On a team, the allowance is a single shared **pool** the whole team draws from.
A new team starts with an empty pool and cannot spend until the owner buys a
team plan (see [18-subscription-plans.md](./18-subscription-plans.md#teams-funding-and-the-no-plan-no-credit-rule)).

### Pacing caps (weekly + per-5h session)

Paid plans pace spending so one afternoon cannot drain a month. Both caps meter
the **same credits** as your period allowance; they can only delay spending
within the period, never shrink it:

| Cap | How it works |
|---|---|
| **Weekly cap** | Billable usage within the current week, which resets **Monday 00:00 UTC**. |
| **Session cap** (per rolling window) | Billable usage within a rolling session window, by default **5 hours**. The allowance per window is a small percentage of the weekly cap (currently 5%), so a window frees up again as its oldest spend ages out — no fixed reset clock. |

Both caps gate the **total** hold — plan credits **and** pay-as-you-go credits
together. So even with a funded PAYG balance, a request may be refused until a
window frees; the error tells you when to try again. That is deliberate: it is
what makes the pacing setting below meaningful.

**Turning pacing off.** By default, spending is paced to the weekly and session
windows. The dashboard has a pacing setting that switches pacing off for your
account, so you can spend your whole period allowance (and your pay-as-you-go
balance) at once. It never grants more than the plan already gave you, and your
usage still counts against the windows in the background, so turning the
setting back on does not buy a fresh window. Renewing or upgrading a plan clears
the weekly window immediately.

**Turning pacing off is a Basic-and-above control.** Free is bring-your-own-key
with no hosted credit allowance, so it has no pacing windows to switch off. The
switch is still visible on Free, but clicking it explains that it needs Basic and
points at the plans page — and the API refuses the same request.

Every paid plan, personal and team alike, keeps the same switch as before. A paid
account that later lapses to Free keeps whatever it had set, but on Free that
setting has no effect: there are no pacing windows to disable. Switching pacing
back on is always allowed, on any plan.

### Daily turn cap (Free plan)

Free is capped at **50 turns per UTC day**, resetting at midnight UTC. Paid plans
have no daily turn cap by default — their bound is credits. This cap applies to
hosted usage; your BYOK requests are never hosted turns.

### Concurrency

Rayu limits how many streams one account may hold at once — currently **50
simultaneous streams**. A request that would exceed the cap is refused
immediately and costs nothing.

### Plan pacing at a glance (defaults)

| Plan | Audience | Price | Credits / period | Weekly cap | Per-5h session cap | Daily turns | Top-up |
|---|---|---|---:|---:|---:|---|---|
| Free | personal | $0 | — | — | — | 50 | no |
| Basic | personal | $3 | 15,000 | 3,750 | ≈ 188 | none | yes |
| Pro | personal | $10 | 50,000 | 12,500 | ≈ 625 | none | yes |
| Plus | personal | $20 | 115,000 | 28,750 | ≈ 1,438 | none | yes |
| Max | personal | $50 | 300,000 | 75,000 | ≈ 3,750 | none | yes |
| Team | team | $10 | 30,000 shared | 7,500 | ≈ 375 | none | yes |
| Team Plus | team | $29 | 100,000 shared | 25,000 | ≈ 1,250 | none | yes |
| Team Max | team | $79 | 400,000 shared | 100,000 | ≈ 5,000 | none | yes |
| Enterprise | per contract | contact | negotiated | per contract | per contract | none | per contract |

The ladder order is Free → Basic → Pro → Plus → Max → Team → Team Plus → Team
Max, with Enterprise outside it. Each tier includes the features and hosted
models of the tier below it, so Team inherits Max, Team Plus inherits Team, and
Team Max inherits Team Plus. **Credits are not inherited** — the amount shown is
that tier's own allowance.

Session caps are 5% of the weekly cap and the window length is 5 hours. On a
team, both caps apply **per member**, not to the pool as a whole. **Every number
in this table is a first-time default, not a contract — plan prices, allowances,
and pacing can change.**

## How a request is paid for

One request's cost is split across your balances in a fixed order, and both
balances may fund the **same** request:

| Order | Balance | Notes |
|---|---|---|
| 1 | **Plan allowance** | The current period's credits. Resets at renewal; the unused portion does not roll over. |
| 2 | **PAYG balance** | Purchased top-up credits. A separate, permanent wallet — it **never merges** with plan credits and is drawn only for whatever the plan allowance cannot cover. |
| 3 | **Shortfall** | If neither balance can cover the cost, the request is refused up front — no half-funded calls. |

If your plan does not include top-ups, or purchasing is unavailable, step 2 is
not offered and the request stops at your plan allowance. The minimum top-up is
$1.

On a team, the same order applies to the team's **pool**: the plan's shared
allowance first, then team-purchased PAYG. A member on "My own credits" is
charged against their own plan and PAYG instead, using their own balances.

## What happens when you run out

Every refusal is a clear error with a recovery path, never a silent degradation:

| You hit | What it means / what to do |
|---|---|
| Team has no plan | HTTP 402 `team_plan_required` — "This team has no credit until you buy a team plan." Ask the owner to buy a team plan, or switch to your own credits. |
| Period allowance + PAYG exhausted | Wait for renewal, buy a top-up (`/topup`, or the dashboard), or upgrade your plan. |
| Weekly pacing cap | Wait for the reset (next Monday 00:00 UTC; the error tells you when to retry), or switch pacing off in the dashboard's pacing setting. |
| Session pacing cap | Wait it out — usage frees within the rolling 5-hour window at most — or use the same setting. |
| Free daily cap | 50 hosted turns per UTC day; it resets at midnight UTC, or move to a paid plan for unlimited turns. |
| 50 concurrent streams | Close or wait for in-flight requests; the refusal costs nothing. |
| Refunded or suspended account | Nothing is charged for a request that is refused up front. |

A refusal never burns a daily turn and never spends credits. A request that
starts but fails upstream costs nothing — you are charged for actual usage, which
is zero for a total failure.

## Where to see your numbers

| Surface | What it shows |
|---|---|
| `/billing` (CLI / extension) | Current plan, allowance, and balance. |
| `/usage` | Credits used this period and turns used today. |
| Dashboard (rayucode.com) | Credit and turn bars, the pacing windows, and the pacing setting. |
| Team page (rayucode.com/dashboard/team) | The shared pool, each member's quota and pacing, and the team's plan state. |
| `/topup` | Buy PAYG credits when your plan allows it. |

## Values can change

Plan prices, credit allowances, pacing caps, the session window length, the
daily turn cap, concurrency, the top-up rate, and per-feature availability can
all change over time. The values quoted above are the defaults a new account
starts with; **what actually applies to you is what `/billing`, `/usage`, and
rayucode.com/plans show** right now.

---

## Related docs

- [20-how-token-credit-charge.md](./20-how-token-credit-charge.md) — the exact charge math per model.
- [18-subscription-plans.md](./18-subscription-plans.md) — plan comparison and hosted model access.
