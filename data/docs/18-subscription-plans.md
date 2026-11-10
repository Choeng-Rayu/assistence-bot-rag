# 18. Subscription plans

This page explains how Rayu bills you, what each plan unlocks, and where to see
your live numbers. Personal and team plans are one catalog with one ladder:
each tier includes the features and hosted models of the tier below it.

Plans, prices, and rates can change over time — every number below is a current
default and an administrator can change it. Treat the tables here as a guide and
check your account (see
[Checking your plan & balance](#checking-your-plan--balance)) for what applies
to you today.

## Two ways to use Rayu

You can run Rayu in two modes, in either the [CLI](./02-quickstart.md) or the
[VS Code extension](./17-vscode-extension.md):

| | **Rayu account (hosted)** | **Bring your own key (BYOK)** |
|---|---|---|
| What it is | Sign in with a Rayu account (`/login`). Model requests go to a curated set of models hosted by Rayu. | You connect your own provider API keys (`/connect`). Requests go straight from your machine to the provider. |
| Billing | In **credits**, drawn from your plan's monthly allowance (plus an optional pay-as-you-go wallet). BYOK traffic is not metered by Rayu — you pay your provider. | Nothing to Rayu. |
| Works on | Any paid plan, or a seat on a team with a live team plan. | **Every plan, including Free** — Free is BYOK-first. |
| Extras | Daily-turn caps don't apply on paid plans; features like Telegram, Orchestrator mode, and image/video generation unlock with the plan. | The full tool set of the agent itself (files, shell, MCP, skills) is yours on every plan. |

You can switch between the two at any time with `/model` — nothing about your
account prevents you from using your own keys.

## The plan ladder

Every plan sits on one ladder. There are eight rungs, plus Enterprise:

| Plan | Audience | Price | Credits per period | Daily turns | Weekly pacing budget | Per-5h window | Top-ups |
|---|---|---|---|---|---|---|---|
| **Free** | personal | $0 | none (BYOK only) | 50 turns/day | not applicable | not applicable | no |
| **Basic** | personal | $3/mo | 15,000 | unlimited | 3,750 | 5% of the weekly budget | yes |
| **Pro** | personal | $10/mo | 50,000 | unlimited | 12,500 | 5% of the weekly budget | yes |
| **Plus** | personal | $20/mo | 115,000 | unlimited | 28,750 | 5% of the weekly budget | yes |
| **Max** | personal | $50/mo | 300,000 | unlimited | 75,000 | 5% of the weekly budget | yes |
| **Team** | team | $10/mo | 30,000 shared | unlimited | 7,500 per member | 5% of the weekly budget | yes |
| **Team Plus** | team | $29/mo | 100,000 shared | unlimited | 25,000 per member | 5% of the weekly budget | yes |
| **Team Max** | team | $79/mo | 400,000 shared | unlimited | 100,000 per member | 5% of the weekly budget | yes |
| **Enterprise** | per contract | contact sales | negotiated | none | per contract | per contract | per contract |

The ladder order is **Free → Basic → Pro → Plus → Max → Team → Team Plus →
Team Max**. Enterprise is separate: it is negotiated per contract, sits outside
the ladder, and neither inherits from Team Max nor passes anything down.

**Each tier includes everything in the tier below it.** That means:

- Every gated **feature** that is on for a lower tier is on for every tier above
  it. Turning a feature off on a higher tier is not allowed.
- Every **hosted model** available on a lower tier is available on every tier
  above it.
- Team plans inherit from the personal ladder: **Team includes everything in
  Max**, Team Plus includes everything in Team, and Team Max includes everything
  in Team Plus.
- **Credits do not inherit.** The credit amount in the table is that tier's own
  allowance; it is not the sum of the tiers below.

How to read the pacing columns:

- Your monthly allowance is not usable all at once. Rayu also applies a
  **rolling weekly budget** and a **per-5-hour-session cap** (5% of the weekly
  budget — e.g. Pro releases at most ~625 credits per 5-hour window from a
  12,500 weekly budget). When a window is exhausted, requests wait until it
  frees; your credits are not lost.
- Free's limit is different in kind: a **50-turn-per-day cap** that applies to
  hosted turns (your BYOK requests never count toward it), and no hosted models
  at all. Because there is no hosted allowance to pace, Free cannot use the
  dashboard's **Use all credits** switch either — switching pacing off is a
  Basic-and-above control.
- On a team, the weekly and 5-hour windows apply **per member**, not to the team
  as a whole.
- Concurrency (how many requests stream at once) and the session-window length
  (default 300 minutes) are service-wide settings, not per-plan numbers.

## Individual or team?

| | **Personal plan** | **Team plan** |
|---|---|---|
| Who buys it | You, for yourself | The team's owner (admin), for the whole team |
| What you get | Your own monthly credit allowance | One shared credit **pool** the whole team draws from |
| Members | n/a | Unlimited — the pool is the only limit |
| Per-person ceiling | n/a | Each member gets an even split by default; the admin can set anyone's quota |
| Renewal | Manual (see [When a team plan ends](#when-a-team-plan-ends)) | Manual, by the team admin |
| Where to buy | `/billing` or [rayucode.com/plans](https://rayucode.com/plans) | Your team's dashboard page |

A team **member** can hold a personal plan and a team seat at the same time;
their personal plan is a floor, and the team plan can add to it. For the team
**owner**, buying a team plan puts their personal plan aside and moves its
unspent credit into the team (see
[Buying a team plan](#buying-a-team-plan-the-owner-credit-moves-in)).

## Teams: funding and the "no plan, no credit" rule

A team has its own shared pool. **A team cannot spend anything until it has a
team plan.**

### Team plans

- Creating a team is free and grants no credit. A new team starts with an empty
  pool and is team-funded, so a hosted request that asks the team to pay is
  refused until the admin buys a plan.
- The refusal is explicit and stable: HTTP **402** with error type
  `team_plan_required` and the message **"This team has no credit until you buy
  a team plan."** The CLI and the dashboard use that to offer the plan purchase
  instead of showing a generic payment failure.
- Until the plan exists, members can still use their own plans and BYOK keys.
  Nothing about joining a team blocks personal usage.

Teams created before this rule are **owner-funded**: they spend the owner's
personal plan and PAYG and keep working exactly as before. They are not migrated
automatically; buying a team plan switches them onto team funding.

## Buying a team plan: the owner credit moves in

When the owner buys a team plan, the purchase does two things:

1. The team gets the plan's shared allowance, and every active member gets a
   share of the pool.
2. The owner's **remaining personal plan credit** and **personal PAYG credit**
   move into the team pool. The owner's personal subscription is put aside, and
   they use the team plan while the team has it.

What moves and what does not:

- **Only the owner's credit moves.** Members' personal plans and PAYG are never
  transferred. A member who joined a team with their own credits keeps them.
- The checkout shows a preview before payment: "N credits from your <plan> move
  into this team and come back if you remove the team plan."
- The transfer is idempotent. A retried payment or a reloaded checkout cannot
  move the same credit twice.
- If the owner has no active paid personal plan, there is nothing to transfer;
  only the team plan's allowance is seeded.

## What a team plan gives its members

**Every active member of a team with a live team plan gets that plan's features
and models, even if their own plan is Free.**

- A member's effective entitlements are their personal plan **OR** the team
  plan, whichever grants more. Joining a team can only add a feature or a model,
  never remove one.
- This covers **features and model access only**. Team management — invites,
  billing, roles, deleting the team — stays with the owner and admins.
- **A member's own credit never moves.** The "Who pays for my requests" choice
  decides whose balance is charged, not what the member is entitled to.
- A member who chooses **personal billing keeps the team's model access**. Their
  request is charged to their own plan or PAYG, but the model catalog is the
  union of their plan and the team plan.
- When the member leaves, is removed, or the team plan ends, their entitlements
  drop back to their own plan immediately.

Today every team tier ships with every catalog feature enabled, the same set a
Pro subscriber gets: Telegram, Orchestrator mode, subagent model routing, image
and video generation, multiple API keys, OCR, audio, and **API access**. An
administrator can turn a feature off per tier, but the inheritance rule means a
team tier can never have less than the tier below it.

- A **Free user on a team can create API keys**, even though Free alone cannot.
- A key created this way bills the **team's credits**, and stops working if the
  seat ends (it falls back to the member's own plan — for a Free user, no hosted
  models). The key itself is not revoked, so rejoining restores it.
- A key can carry its own **per-key credit limit**; that limit applies to
  team-billed traffic too, so you can hand an integration a capped key.

## Who pays for a member's requests

Each member has their own setting, **"Who pays for my requests"**:

| Choice | What is billed | Default |
|---|---|---|
| **My team's credits** | The team's shared pool | yes |
| **My own credits** | The member's **own** plan and PAYG, even while they hold a seat | no |

- **Every member sets their own** — including the team owner. No admin can change
  it for somebody else, because the person whose credits are being spent is the
  person who should choose.
- If the team is **new and has no team plan**, "My team's credits" is refused
  with the `team_plan_required` error above. It is **not** silently charged to
  the member instead.
- It applies to **every** product they use through Rayu, not only chat: image,
  video, audio, OCR and realtime sessions honour the same choice.
- A member on *"My own credits"* with no personal plan or PAYG is refused their
  own requests until they add credit; the dashboard warns before they switch.
- Team usage reports keep the distinction: a member's team-financed spend and
  their personally-billed spend are listed separately, and the roster marks
  anyone on personal billing as **own credits** — which is also why their team
  usage can legitimately read as zero.

The setting takes effect on the member's next request. There is a short cache in
the request path (about 30 seconds) that the dashboard refreshes immediately, so
if the very first request after switching still bills the old source, wait a
moment and retry.

## Members and quotas

- **Unlimited members.** There is deliberately no seat cap: the shared pool is
  the real limit, which is what makes "add whoever you need" safe.
- **Quotas split evenly by default.** When the pool is seeded, every active
  member receives `pool ÷ member count`. Someone who joins later gets a share of
  the same allowance, so existing members keep their quota and the newcomer is
  not locked out part-way through a period.
- **The admin can override any member's quota** from the members table. Raising
  a quota also raises that member's pacing ceiling (see below); lowering it clamps
  what they can still spend, without rewriting history.
- Removing a member zeroes their remaining quota but keeps their record, so the
  audit trail of who spent what survives. Re-admitting them restores a share.

## Pacing on a team

Team plans use the same two pacing windows as personal plans — a **rolling
weekly budget** and a **per-5-hour session window** (5% of the weekly budget) —
and they apply **per member**, not to the team as a whole.

- The team admin can turn pacing off for the whole team with the **No pacing**
  switch on the team page. Members cannot change it themselves.
- Pacing never changes what the team can spend; it only paces how fast. The pool
  remains the hard limit.
- An admin-assigned quota raises that member's pacing ceiling. Assigning credits
  never leaves a member blocked by a window sized for the plan's smaller default.

## Buying team credits

On top of the plan's allowance, a team can buy **pay-as-you-go credits** for its
own pool from the team page (card or QR), either for the whole team or earmarked
for one member. Team PAYG **never expires** — it is not reset by a renewal, and
it survives the plan ending.

- Team PAYG needs a team pool, so the team must have had a team plan. A brand-new
  team with no plan cannot spend and has nothing to top up; buy the plan first.
- Spending order is the same as everywhere: the plan's allowance first, then the
  purchased credit.

## When a team plan ends

**Team plans do not renew automatically.** Both payment rails are one-shot
payments, so when the purchased period ends:

1. The plan **expires**. The plan's remaining allowance and every member's
   remaining quota are cleared; those credits were backed by a period that no
   longer exists.
2. **The owner's transferred credit comes back.** The unspent part of what the
   owner moved in when they bought the team plan returns to them as **personal
   credit**.
3. **The owner's old personal plan comes back** for whatever remains of its
   original period. If that period has already ended, they fall back to Free.
4. **Other members fall back to their own plans.** Their features and models
   drop to their personal plan (Free, if that is what they hold).
5. **Team-purchased PAYG is kept.** It is a separate balance, never expires, and
   is not part of the owner's transfer.
6. The team **stops being funded by the plan**. The admin must **buy a plan
   again** to restore team credit.

This is intentional: it mirrors an individual plan falling back to Free. It is
also why an expired team cannot be renewed for free — a renewal only rolls an
*active* plan forward by a period; restarting needs a purchase.

If the admin **renews early**, unused plan credit is **carried forward**: the new
period's allowance plus whatever was left of the old one. Renewing does not throw
away credits you already paid for.

## Removing the team plan or deleting the team

The owner can remove the team plan or delete the team from its page.

- **Removing the team plan** ends the team's plan immediately. The return rule
  above applies: the unspent part of the owner's transferred credit returns as
  personal credit, and the owner's old personal plan is restored until its
  original end date (Free if it already ended).
- **Deleting a team** is a soft delete: the team disappears from every dashboard,
  all seats are revoked, and join links and pending invites stop working, but
  invoices and payment records are retained for accounting. The same return rule
  applies to the owner.
- **Only credit the owner brought in is returned.** The return is capped by what
  is still unspent in the pool and by what was transferred in the first place.
  Credit the team bought for itself is a separate balance and is not part of that
  transfer.
- Members lose their seats and their team features immediately.

## Joining a team

Teams are joined in one of two ways:

- **Shareable join link** — the admin creates a link from the team page and
  shares it. Anyone who opens it can *ask* to join; an admin approves. Holding
  the link grants no seat and no credits. Regenerating the link invalidates the
  previous one.
- **Google Workspace auto-join** — if the team was created with a company
  domain, anyone signing in with an account on that domain joins automatically.

One team per account in this version: you must leave your team before joining or
creating another.

## Feature access by plan

Rayu unlocks a number of features with your plan. Current defaults:

| Gated feature | What it is | Free | Basic | Pro | Plus | Max | Team tiers |
|---|---|---|---|---|---|---|---|
| Telegram bot | Drive sessions from Telegram | off | on | on | on | on | on |
| Orchestrator mode | Multi-agent delegation | off | on | on | on | on | on |
| Delegated-worker model override | Model choice for delegated background workers | off | on | on | on | on | on |
| Model per subagent | Route subagents to a different model/provider | off | on | on | on | on | on |
| Image generation | Native image tool | off* | on | on | on | on | on |
| Video generation | Native video tool | off* | on | on | on | on | on |
| Multiple API keys | Several keys per provider with failover | off | on | on | on | on | on |
| API access | Programmatic keys for hosted models (OpenAI- and Anthropic-compatible) | off | **off** | on | on | on | on |
| OCR (document scanning) | Scan documents with a hosted model | off | on | on | on | on | on |
| Audio (STT / TTS) | Speech-to-text and text-to-speech with a hosted model | off | on | on | on | on | on |

Notes:

- \* Image and video can also be paid for **from a funded pay-as-you-go
  balance** even when your plan does not grant them — so you can pay per use
  without subscribing, where top-ups are available. Every other gated feature
  needs the plan.
- Basic deliberately keeps **API access off** (every other feature is on with
  Basic).
- **Team tiers ship with every feature on**, because they sit above Max on the
  ladder and inherit its features.
- **A member's effective entitlements are personal OR team, not whoever pays.**
  A Free user on a team with a live plan gets the team features and models even
  on personal billing; their personal balance is charged, not their
  entitlements.
- Enterprise (coming soon) turns all features on with negotiated limits.
- Gating is soft in the UI (a locked feature shows you an "upgrade required"
  note instead of disappearing) but enforced for anything that runs on Rayu's
  hosted models.

## Hosted models and example credit rates

With a Rayu account on **Basic, Pro, Plus, Max, or any team tier**, you get the
hosted model catalog — the models Rayu hosts for you, billed in credits. The Free
plan has no hosted models (BYOK only).

Model access follows the same inheritance rule: a model available on a lower
tier is available on every tier above it. A team seat gets the **team plan's
models**, even if the member is on Free, and even when the member chose personal
billing — the model catalog is the union of their personal plan and the team
plan.

Credit cost is computed per token bucket:
`credits = (input·rIn + output·rOut + cacheRead·rRead + cacheWrite·rWrite) / 1,000,000`
where each `r` is that model's credits-per-1M rate. See
[How token credits are charged](./20-how-token-credit-charge.md) for the full
mechanics.

Every model below is available on **Basic and above**. Rates are in credits per
1M tokens:

| Model (code) | Input | Output | Cache read | Cache write | Context |
|---|---|---|---|---|---|
| DeepSeek V4 Flash (`deepseek-v4-flash`) | 330 | 330 | 33 | 330 | 1M |
| DeepSeek V4 Pro (`deepseek-v4-pro`) | 1,000 | 1,000 | 100 | 1,000 | 1M |
| LongCat 2.0 (`longcat-2`) | 500 | 2,000 | 10 | 500 | 1M |
| GLM-5.2 (Ollama Cloud) (`glm-5.2`) | 2,500 | 2,500 | 250 | 2,500 | 1M |
| Kimi K2.7 Code (Ollama Cloud) (`kimi-k2.7`) | 2,500 | 2,500 | 250 | 2,500 | 256K |
| MiniMax M3 (Ollama Cloud) (`minimax-m3`) | 2,500 | 2,500 | 250 | 2,500 | 128K |
| Llama 4 (Ollama Cloud) (`llama-4`) | 1,000 | 1,000 | 100 | 1,000 | 128K |
| GPT-OSS 120B (Ollama Cloud) (`gpt-oss-120b`) | 750 | 750 | 75 | 750 | 128K |
| Qwen3.5 397B (Ollama Cloud) (`qwen3.5-397b`) | 750 | 750 | 75 | 750 | 256K |
| Qwen3.5 122B (Ollama Cloud) (`qwen3.5-122b`) | 750 | 750 | 75 | 750 | 256K |

A worked example: one Pro-plan turn on `deepseek-v4-pro` using 8,000 input +
2,000 output tokens with no caching costs
`(8,000·1,000 + 2,000·1,000) / 1M = 10 credits`. Cache hits are the big saver in
long sessions — on DeepSeek V4 Pro a cached input token costs a tenth of an
uncached one, and agentic loops hit cache for most of the prompt.

> **Note:** these are current default rates. Plans, prices, model availability,
> and every rate can change. For live values check `/billing` or `/usage` in the
> CLI/extension, or [rayucode.com/plans](https://rayucode.com/plans).

## Which providers exist per path

| Path | Providers |
|---|---|
| Hosted (Rayu account) | The curated catalog above — models hosted by Rayu. The exact set follows what Rayu offers at the time. |
| BYOK (`/connect`) | Any of the ~30 provider presets regardless of plan — Anthropic, OpenAI, NVIDIA, DeepSeek, Kimi, Gemini, Bedrock, Azure, Vertex, Copilot, Kiro, OpenRouter, Fireworks, Together, Cerebras, DeepInfra, HuggingFace, xAI, Groq, MiniMax, LongCat, local OpenAI-compatible servers, and custom endpoints. See [Providers](./03-providers.md). |

A single session can mix them: main agent on a hosted model, a subagent on your
own provider key (paid plans include per-subagent model routing).

## Top-ups and pay-as-you-go

Beyond your plan allowance, you can buy **pay-as-you-go (PAYG) credits**:

- In the terminal or the extension: `/topup [credits]` (alias `/buy-credits`) —
  shows the live price quote and a payment flow (card or QR).
- In the dashboard: [rayucode.com](https://rayucode.com) → billing.
- For a **team**: the team page has its own "Buy credits" panel. Team PAYG goes
  into the team's pool (optionally earmarked for one member) and never expires.
- Top-up availability and the credit-per-dollar rate can change; if purchasing
  is unavailable, `/topup` tells you. The minimum top-up is $1. Paid plans
  (Basic and up) include top-up spending.

Your personal PAYG and a team's PAYG are **separate balances**: personal top-ups
fund your own requests, team top-ups fund the team's pool. A member on "My own
credits" spends their personal PAYG; on "My team's credits" they spend the pool.
The one exception is the team owner's transfer: when the owner buys a team plan,
their personal PAYG moves into the team pool, and the unspent part comes back as
personal credit if the team plan is removed, the team is deleted, or the plan
expires.

How money is spent, per request:

1. **Plan credits first.** The current period's subscription allowance is drawn
   down to zero.
2. **Then your PAYG wallet.** Whatever the plan could not cover comes from your
   permanent top-up balance. (This split happens *within* a single request, so
   the last few credits of a period are never wasted.)
3. **Then refusal.** If neither balance covers the cost, the request is denied
   rather than silently over-billed — top up, wait for the window to free, or
   switch to BYOK.

Two important properties:

- **The two balances never merge within an account.** Plan credits reset with
  your billing period; PAYG credits are permanent. They are tracked separately
  and drawn in the order above. (The owner's team-plan transfer is a move
  between accounts, not a merge of the plan and PAYG wallets.)
- **Pacing still applies.** The weekly and 5-hour windows gate the *rate* of
  hosted spending even when your balances are healthy; that is a pace, not a
  budget. See [Credits & limits](./19-credits-and-limits.md).

## Checking your plan & balance

| Command / page | What you see |
|---|---|
| `/login` (and `/logout`) | Sign in or out of the Rayu account that carries your plan. |
| `/billing` | Your current plan, and a link to upgrade on the web. |
| `/usage` | Plan allowance plus hosted-model usage: what you have spent and what is left. |
| `/topup` | Buy PAYG credits at the live rate. |
| `/stats` | Your local session usage statistics and activity. |
| `/insights` | A generated report analyzing your Rayu sessions. |
| Dashboard | [rayucode.com](https://rayucode.com) — plan, invoices, credit balance, and plan changes in the browser. |
| Team page | [rayucode.com/dashboard/team](https://rayucode.com/dashboard/team) — the shared pool and how much is left, the member roster with each person's quota, who pays for your requests, members' usage, buy/renew the team plan, buy team credits, the join link, and (for the owner) delete. |

Billing commands require a Rayu account sign-in. Upgrades and downgrades
(prorated) are handled on the dashboard; the plan change takes effect for the
CLI and extension automatically — no reinstall.

The CLI reports the **personal** side. A team member's pool balance and quota are
on the team page, because the pool belongs to the organisation rather than to
their account.

## Team quick reference

| Question | Answer |
|---|---|
| Does creating a team charge me? | No. It is free, and it grants no credit either. |
| Can the team spend before it has a team plan? | No. A team-billed request is refused with `team_plan_required` until the admin buys a team plan. |
| Does buying a team plan cancel my personal plan? | It puts it aside. Its unspent credit and your PAYG move into the team pool, and the old plan comes back if the team plan goes away. |
| How many members can I add? | Unlimited — the pool is the limit. |
| Do team plans auto-renew? | No. When the period ends the plan expires and the admin buys again. |
| Do I lose credits when it ends? | The team plan's allowance is gone, but the unspent part of what the owner transferred comes back as personal credit. Team-bought PAYG is a separate balance. |
| Do I lose credits when I renew early? | No — unused plan credit carries into the new period. |
| If I have my own plan and a team seat, who pays? | Your choice, per member, on the team page. Default is the team. |
| Can my admin choose that for me? | No. It is self-service, like your own plan. |
| Do I keep team features if I pay personally? | Yes. Entitlements are personal OR team; only the credit comes from you. |
| What happens to the owner's credit if the team is deleted? | The unspent part of the transferred credit returns as personal credit, and the owner's old personal plan comes back. |
| Can a person buy a team plan for themselves? | No — team plans are bought for a team from its dashboard. |

## See also

- [Credits & limits](./19-credits-and-limits.md) — pacing windows, concurrency,
  shortfall handling in detail
- [How token credits are charged](./20-how-token-credit-charge.md) — the exact
  billing formula and precision
- [VS Code Extension](./17-vscode-extension.md) — the same account on the
  editor side
- [API Keys & Credentials](./15-api-keys.md) — programmatic access for hosted
  models
