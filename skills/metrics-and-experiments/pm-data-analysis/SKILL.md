---
name: pm-data-analysis
description: Analyze a business dataset (CSV or Excel files of orders, customers, products, subscriptions, events, transactions) the way a product manager would. Check the data, break the headline metric into its drivers, follow the customer journey, form and test hypotheses, put a size on each issue, and finish with ranked, testable recommendations, written up as a PDF report, optionally with a slide deck. Use this whenever the user shares a dataset and asks what it shows, wants findings, insights, hypotheses or recommendations from it, is preparing for a PM, product-analytics or business-case interview built on a dataset or take-home, or asks "how would you analyze this data", even if they don't say "analysis" or name a framework.
---

# PM data analysis

Turns a raw business dataset into findings and recommendations that a PM could defend in a
review or an interview. The aim is a short list of tested claims, each with a dollar or
percentage size and an experiment to run next. A long tour of every cut in the data is not the aim.

Two ideas drive the method:
- **Check the data before trusting any number.** In practice the most valuable finding is often
  that a headline figure is wrong (for example, revenue that counts cancelled orders).
- **Try to disprove your own ideas.** A rejected hypothesis is a finding, because it stops the
  team spending money on the wrong fix.

## Inputs

Work from the files the user points to. Ask only for what you can't infer:
- **The question or decision**, if there is one (e.g. "should we cut discounts?"). If none,
  the default question is "what is driving or holding back profit, and what should we do?"
- **Context** that changes the reading: the business model, the currency, whether the data is
  synthetic or an interview take-home. If the user doesn't say, infer it and state the assumption.

## Process

Run Python with `python3 -I`, and pass file paths as arguments. If the project has a CLAUDE.md
describing the data, read it first and add anything new you learn about the data's quirks.

### 1. Get oriented
Run `python3 -I scripts/profile_data.py <file-or-folder>`. For each table it reports rows,
columns, likely keys, nulls, date ranges, categorical values and possible join columns.
From that, write down:
- **What one row is** in each table (an order, an order line, a customer, an event). Getting this
  wrong double-counts.
- **How the tables join**, and which table to treat as the source of truth for money.
- **The north-star metric**: usually profit or revenue per customer for commerce, and retained
  revenue or active users for subscriptions and apps.

### 2. Check the data
Before any analysis, test that the numbers can be trusted:
- Do totals reconcile across tables (order level vs line level, summary file vs raw rows)?
- Which statuses are in revenue? Cancelled, returned, refunded and pending rows often are, and
  shouldn't be.
- Are blanks structural (no rating on a cancelled order) or a defect?
- Mixed currencies or units, duplicate keys, impossible values (net above gross, negative ages),
  derived fields that disagree with what they claim to count.

Quantify each problem, e.g. "headline revenue overstated by 19%", and treat a material one as
finding #1. A precomputed summary file is a claim to check, not a fact.

### 3. Break down the metric
Split the north star into factors and look at each factor over time:
- Commerce: revenue = customers × orders per customer × order value; profit = revenue × margin,
  where margin depends on discounts, product mix and costs.
- Subscription: revenue = (starting customers + new − churned) × revenue per customer.

The factor that moves is the story. If the total is flat, find which factors are cancelling out.
For commerce, also look at new customers per year by first-order cohort, and at year-on-year
retention.

### 4. Follow the customer journey
Walk acquire → convert/pay → fulfil → experience (ratings, returns) → retain, and measure what
each stage loses. Common sources of loss: payment failures, late delivery, returns, discounts
on orders that would have happened anyway, and customers who don't come back.
`references/ecommerce-playbook.md` lists the cuts and traps for commerce data; read it when
the dataset is orders, carts or transactions.

### 5. Compare groups and separate signal from noise
Run `python3 -I scripts/segment_scan.py <csv> --value <money column> --flag <column>=<value> ...`.
For every low-cardinality column it compares each group to the overall figure. A difference
counts only if it is both large (spread of at least 5% of the overall figure) and unlikely to be
chance (at least 3 standard errors). Columns with no such difference are marked FLAT.

Columns that record what happened after the order (delivery days, review text, return reason,
payment status) rank near the top because they are part of the outcome. Set them aside when
looking for causes.

Report the flat ones explicitly ("channel, warehouse and age show no difference, so nothing
here supports reallocating budget"). Many groups that are suspiciously identical usually mean
synthetic data or broken instrumentation. Say so rather than inventing differences.

### 6. Form and test hypotheses
For each pattern worth explaining, write:
**What I saw → what I think causes it → how I tested it → result (supported / rejected / can't test here) → next step.**

Test with a comparison group, not a single number:
- before vs after, peak season vs the rest of the year, one tier vs another, late vs on-time.
- Check behaviour (repeat purchase, time to next order, spend), not only stated opinion
  (ratings, reviews). When the two disagree, that is itself a finding.
- Look for the alternative explanation (mix shift, capacity, seasonality) and test it too.
- Aim for a handful of supported hypotheses and a few rejected ones. Rejected hypotheses carry weight.

This data shows association, not cause. Phrase supported hypotheses as "consistent with", and
make the next step an experiment.

### 7. Size the impact
Put a figure on every finding you'll recommend acting on: the money at stake, the margin points,
the number of customers affected. Rough is fine, but show the arithmetic in the report. Sizing
is what ranks the recommendations.

### 8. Recommend
Each recommendation states five things: **action, evidence, metric to move, how to test it,
risk to watch.** Rank them:
- **P0, fix now:** problems that make the numbers wrong, and money already owed (failed or unpaid payments).
- **P1, run as an experiment:** changes whose cause isn't proven (discount levels, delivery promises).
- **P2, invest after confirming:** bets that depend on data you don't have (marketing spend, costs).

Judge experiments on profit per customer, not revenue, unless the user says otherwise.
Volume bought with discounts can raise revenue and lower profit.

### 9. Write it up
Lead with the answer. Write in this order: one-line headline → 3–5 findings → hypotheses table →
recommendations → open questions and data you'd need. Use the template below.

## Output

Write `Data Analysis/<dataset-name>-analysis.md` in the folder where Claude Code is running
(create the folder if needed), then convert it:
`python3 -I scripts/md_to_pdf.py "Data Analysis/<dataset-name>-analysis.md"`.
Keep both files. If the conversion fails (it needs the `markdown` package and Google Chrome),
say so and give the Markdown path. Name the file after the dataset or business, lowercase and
hyphenated. If the file exists, append the date unless the user asked to update it.

```markdown
# <Business or dataset>: analysis and recommendations
*As of <YYYY-MM-DD> · Data: <rows, tables, date range> · Question: <the decision or default question>*

## Headline
<One or two sentences: the answer.>

## Data health
<What was checked; each problem quantified; which figures are used from here on.>

## Findings
### 1. <Finding as a claim, e.g. "Peak-season discounts buy volume, not profit">
- What the data shows: <numbers with comparison groups>
- Size: <$ or % at stake>
- Caveat: <if any>
(3–5 findings, ranked by impact)

## Hypotheses tested
| Hypothesis | Result | Evidence | Next step |
|---|---|---|---|

## No signal
<Groupings that showed no meaningful difference, and why that matters.>

## Recommendations
| Priority | Action | Evidence | Metric to move | How to test | Risk |
|---|---|---|---|---|---|

## Open questions
- <What you'd ask the data owner, and what data would settle it.>

## Method
<Two or three lines: tables used, filters (e.g. completed orders only), definitions.>
```

## Slide deck (only when asked)

If the user asks for a presentation, build a short deck of about 8–10 slides from the report:
cover with the headline → approach → one slide per major finding (big numbers, one idea each)
→ hypotheses scorecard → recommendations → first experiment and open questions. Put speaker
notes on each slide. Use the session's slide-deck artifact type if one is available; otherwise
use the pptx skill.

## Rules

- **Never invent a number.** Every figure must come from code you ran this session. If you
  estimate, label it as an estimate and show the inputs.
- **State the filter behind every figure** (all orders vs completed vs paid). Mixing them is
  the most common way these analyses go wrong.
- **Separate what the data shows from what you infer.** "Consistent with", not "caused by".
- **Don't over-read noise.** A difference of a few percent between groups of thousands that
  differ by less than the year-to-year variation is not a finding.
- **Flag dataset artifacts.** If a pattern looks built into the data (a fixed customer pool,
  identical rates everywhere), say so and phrase it as a question for the data owner.
- **Round for display** (e.g. $1,283, 41.4%). Keep full precision in calculations.
- Keep scratch scripts in the scratchpad, not in the user's project.

## Final message

Reply with the PDF and Markdown paths, the headline, the top three findings in one line each,
and the P0 recommendation. Offer the deck if it wasn't requested. Keep it short; the detail is
in the file.
