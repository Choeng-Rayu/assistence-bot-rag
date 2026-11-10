# 20. How tokens are charged

This page is the exact math behind a credit charge on **Rayu-hosted** models:
how the four token buckets are counted, what each bucket costs, and how
precision and rounding work.

> TL;DR
> - You are charged from the model's **actual reported usage**, never an
>   estimate.
> - Each model has four **absolute per-1M-credit rates** (credits per
>   1,000,000 tokens in each bucket).
> - Cache reads are heavily discounted; a failed request costs 0.
> - Sub-credit precision means a tiny request is charged tiny, not zero and not
>   rounded up.

---

## The formula

Every hosted response reports per-bucket token usage. Each bucket is priced
independently:

```
credits = ( input      × rIn
          + output     × rOut
          + cacheRead  × rRead
          + cacheWrite × rWrite ) ÷ 1,000,000
```

where each `r…` is that model's **credits per 1,000,000 tokens** for that
bucket — an absolute price, not a multiplier. Four buckets because real
providers price them differently:

| Bucket | What it is |
|---|---|
| **input** | Fresh prompt tokens (cache miss). |
| **output** | Completion tokens the model generated. |
| **cacheRead** | Prompt tokens served from the provider's prompt cache. |
| **cacheWrite** | Prompt tokens written into the cache when a prefix is created. |

## Sample rates (current defaults)

These are current rates for a few hosted models, in **credits per 1M tokens**:

| Model (id) | rIn | rOut | rRead | rWrite |
|---|---:|---:|---:|---:|
| DeepSeek V4 Flash (`deepseek-v4-flash`) | 330 | 330 | 33 | 330 |
| DeepSeek V4 Pro (`deepseek-v4-pro`) — the reference tier | 1,000 | 1,000 | 100 | 1,000 |
| LongCat 2.0 (`longcat-2`) | 500 | 2,000 | 10 | 500 |
| GLM-5.2 (`glm-5.2`) | 2,500 | 2,500 | 250 | 2,500 |

Reading the table: on DeepSeek V4 Flash, 1,000,000 output tokens cost 330
credits; on GLM-5.2 the same million cost 2,500. LongCat costs 4× more for output
than input because its provider does. Cache reads are ~10% of the input rate
everywhere here.

Every hosted model is available on the paid plans (Basic and above). **Rates can
change** — this table is a guide, not a fixed price list. For the current
per-model rates and what plans include, see
[18-subscription-plans.md](./18-subscription-plans.md).

## Cache reads are cheap — on purpose

In an agentic session the CLI resends the whole growing conversation on every
turn, because chat APIs are stateless. Providers with prompt caching (DeepSeek's
caching is on by default) then serve all but the newest increment from their own
cache and charge only a small fraction — typically 2–8% — of the full input
price. Rayu mirrors that: cache-hit tokens are billed at the `rRead` rate, about
a tenth of `rIn`. When a model has no separate cache-read rate, cache reads are
billed at 10% of the input rate.

Without this, a long tool-use session would burn a plan's monthly allowance at
several times the provider's actual cost.

## Precision and rounding

Credits are tracked to **six decimal places**, and conversions round **half-up**
(ties away from zero). Two consequences you can rely on:

- A small request is charged its true tiny amount — it is never floored to free,
  and never rounded up to a whole credit. A 28-token "hi" on DeepSeek V4 Flash
  costs `20×330 + 8×330 = 9,240` rate-adjusted tokens ÷ 1,000,000 ≈ **0.0092
  credits**.
- Balances add up exactly: charges are kept at that precision, so the total you
  see is the total that was charged.

## Charges follow actual usage

The real token split is unknown until the model responds. Rayu therefore checks
that your balance can cover a request before it starts, and the final charge
always uses the **actual** per-bucket usage the provider reports afterward, not
the estimate. A request refused before it starts costs nothing, and a retried
request is not charged twice.

## Worked example

A typical agentic turn on **DeepSeek V4 Pro** (rates 1,000 / 1,000 / 100 / 1,000):

| Bucket | Tokens | Rate (credits/1M) | Rate × tokens |
|---|---:|---:|---:|
| Fresh input | 20,000 | 1,000 | 20,000,000 |
| Cache read | 80,000 | 100 | 8,000,000 |
| Output | 2,000 | 1,000 | 2,000,000 |
| **Total** | 102,000 | | 30,000,000 |

```
credits = 30,000,000 ÷ 1,000,000 = 30 credits
```

Note how the 80k cache-read tokens — nearly the whole prompt — contribute only a
quarter of the charge. On the same turn with Flash (330 / 330 / 33 / 330) the
cost would be 9.9 credits.

## What is not charged

- **Failed or errored requests** — you are charged for actual usage, so a turn
  that never completes costs 0. A request refused up front (limit, unavailable
  model, no plan access) costs nothing and burns no daily turn.
- **BYOK traffic** — going straight to your own provider bypasses Rayu billing
  entirely; you pay your provider, not us.
- **Anything beyond actual usage** — you are never billed for a request's
  estimate.

---

## Related docs

- [19-credits-and-limits.md](./19-credits-and-limits.md) — allowances, pacing, and how limits apply.
- [18-subscription-plans.md](./18-subscription-plans.md) — plans and the hosted-model catalog.
