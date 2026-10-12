---
name: porters-five-forces
description: Analyze a company's competitive positioning using Porter's Five Forces (threat of new entrants, bargaining power of suppliers, bargaining power of buyers, threat of substitutes, rivalry among existing competitors), and produce a structured, evidence-backed write-up with an overall industry-attractiveness view and the company's position within it. Use whenever the user asks about competitive positioning, competitive strategy, industry structure or attractiveness, moats or barriers to entry, pricing power, "how strong is X's competitive position", "Porter's five forces", "five forces analysis", or wants to compare companies' competitive dynamics — even if they don't name the framework.
---

# Porter's Five Forces analysis

Produces a Five Forces assessment of one company (or a company vs. named peers) that
a PM could defend in a review: each force rated, the evidence behind each rating, what
would change the rating, and what it means for the company's positioning.

The framework is a lens, not a score. The output should make the reasoning inspectable,
not produce a number that looks precise.

## Inputs

Ask only for what's missing and can't be looked up:
- **Company** (required) and, if relevant, the specific business line or segment. Multi-segment
  companies often have different five-forces profiles per segment; analyze the segment that
  drives most of the economics, and note the others.
- **Geography/market** if it matters (e.g., India vs. global).
- **Time horizon** (default: next 3–5 years).
- **Peers** (optional). If none given, pick 2–3 direct competitors as reference points for
  rivalry and the margin check, and say which you picked. Build the full peer comparison
  only when the user names peers or asks for a comparison.

## Process

1. **Define the industry boundary.** State what market the five forces apply to. Be explicit
   about what's excluded. A boundary that's too wide hides real competition; too narrow
   overstates rivalry.
2. **Gather evidence before rating.** Use web search for recent filings, annual reports or
   investor presentations, earnings-call transcripts, industry reports, and regulatory
   documents. Prefer primary sources. Record the source and date for every claim that
   supports a rating. If web search isn't available, work from what the user provides and
   what you know, set confidence to "low" on every rating that lacks a dated source, and list
   the missing evidence under Gaps.
3. **Assess each force using these prompts** (they tell you what evidence to look for):
   - **Threat of new entrants**: capital requirements, economies of scale, switching costs,
     brand loyalty, regulatory licensing, access to distribution, expected retaliation,
     proprietary technology or patents. Ask: how much would it cost and how long would it
     take a well-funded new player to reach a comparable position?
   - **Bargaining power of suppliers**: number of suppliers vs. buyers in the supply chain,
     whether inputs are differentiated, switching costs for the company, whether suppliers
     could integrate forward, the share of costs they represent.
   - **Bargaining power of buyers**: buyer concentration, share of buyer's total spend,
     product differentiation, switching costs, price sensitivity, whether buyers could
     integrate backward, availability of alternatives.
   - **Threat of substitutes**: functional alternatives outside the industry definition,
     their price-performance trend, buyer propensity to switch, and whether substitutes are
     improving faster than the core product.
   - **Competitive rivalry**: number and size of competitors, industry growth rate, fixed-cost
     intensity, product differentiation, exit barriers, capacity utilization and pricing
     discipline, and the presence of consolidation or price wars.
4. **Rate each force** on a 1–5 scale of *force strength*: 1 = weak force (favorable to
   industry profitability), 5 = strong force (unfavorable). A higher number is always worse.
   For each force, write:
   - **Rating**, a one-line verdict, and confidence (high / medium / low)
   - **Drivers**: the specific factors pushing the force up or down
   - **Evidence**: concrete data points (market share, switching costs, capex per entrant,
     number of suppliers, customer concentration, price history, margin trends, patent or
     license counts, etc.), each with a source
   - **What would change it**: the one or two events that would move the rating
5. **Synthesize.**
   - **Industry attractiveness** is the inverse of overall force strength. Use the average as
     a starting point (roughly ≤2.5 Attractive, 2.5–3.5 Mixed, ≥3.5 Unattractive), then
     override it if one force is decisive — a single 5 can make an industry unattractive
     even when the average looks fine. Say which force dominates and why.
   - **Company positioning**: where the company sits relative to each force. Does it shape the
     force in its favor (scale, brand, switching costs, proprietary supply), or is it exposed to
     it? Tie this to its margin profile over the last 3–5 years. Margins that hold up while
     forces are unfavorable are evidence of advantage. Margins that fall are evidence the
     advantage is weaker than it looks.
   - **Strategic implications**: 2–4 concrete points, such as where the moat is durable, which
     force is the main risk, and what to monitor.
6. **Peer comparison (only if the user named peers or asked for a comparison).** A short table: forces (rows) × companies (columns),
   with a rating and one-line note in each cell. End with which company has the most
   favorable structure and which has the strongest execution inside a given structure. These
   are different questions.

## Output format

Write the analysis as a Markdown file in the `Competitive Strategy` folder at the project
root (create the folder if it doesn't exist):
`Competitive Strategy/<company>-five-forces.md`

Filename: lowercase the company name, replace spaces with hyphens, and drop punctuation
(`AT&T` → `att`, `L'Oréal` → `loreal`). For a segment-specific analysis, append the segment
(`amazon-aws-five-forces.md`); for a peer comparison, use the focal company's name. If the
file already exists, don't overwrite it — append the date (`<company>-five-forces-YYYY-MM-DD.md`)
unless the user asked to update the existing analysis.

Use this structure:

```markdown
# <Company>: Porter's Five Forces
*As of <YYYY-MM-DD> · Horizon: <period> · Market: <boundary>*
*Scale: 1 = weak force (favorable) … 5 = strong force (unfavorable)*

## Summary
- Industry attractiveness: <Attractive / Mixed / Unattractive> (<one-sentence reason>)
- Company position: <Advantaged / Neutral / Exposed> (<one-sentence reason>)
- Dominant force: <force> — <why>

## Force ratings
| Force | Rating (1–5) | Confidence | Verdict |
|---|---|---|---|
| New entrants | | | |
| Supplier power | | | |
| Buyer power | | | |
| Substitutes | | | |
| Rivalry | | | |

## 1. Threat of new entrants
**Rating:** x/5 (<confidence> confidence) — <verdict>
- Drivers: ...
- Evidence: ... [source, date]
- What would change it: ...

## 2. Bargaining power of suppliers
## 3. Bargaining power of buyers
## 4. Threat of substitutes
## 5. Competitive rivalry
(same four lines under each)

## Positioning and margin check
<How the company's position relates to the forces, tied to margin history.>

## Peer comparison
<Only if the user named peers or asked for a comparison: forces × companies table, then most favorable structure vs.
strongest execution.>

## Implications
- ...

## What this does and doesn't establish
<One or two sentences: e.g., structure is favorable, but this says nothing about valuation.>

## Sources
- ...

## Gaps
- <Anything you couldn't verify, and what would be needed to verify it.>
```

## Rules

- **Every rating needs evidence.** If a rating rests on judgment with no hard data, say so
  and set its confidence to "low."
- **Separate fact from interpretation.** Put reported figures in the Evidence line and the
  reasoning in the Drivers line.
- **Don't invent numbers.** If market share, switching costs, or capex figures aren't available,
  write "not disclosed" and state the proxy you used.
- **Dates matter.** Industry structure changes. Note the date of each source (write "undated"
  in the Sources entry when none can be found), and flag anything older than about 2 years as
  possibly stale.
- **Don't treat the framework as a verdict.** A "strong" industry can still be a poor investment
  at a given price, and a "weak" one can have a well-protected leader. Say what the analysis
  does and does not establish.
- **Keep it to one focal company per file.** Peers appear only in the Peer comparison
  section; omit that section unless the user named peers or asked for a comparison.

## Quality check

`scripts/check_output.py` tests the file against this contract: sections and order, the ratings
table, rating lines matching the table, dated citations in Evidence, the attractiveness label
matching the ratings, dated Sources, stale sources flagged, Gaps, and leftover placeholders.
If the optional PostToolUse hook is installed (see the README), it runs the checker after every write
or edit of a five-forces file, and any FAIL comes back to you. Fix each one in the file before replying. The check passing means the write-up is
well-formed; it does not mean the judgments are right, so still review the reasoning yourself.
Without the hook, run `python3 scripts/check_output.py "<output file>"` yourself after writing.

## Final message

After writing the file and passing the quality check, reply with: the file path, the summary
block (the three lines under "Summary"), the one or two gaps that most limit confidence, and the
check result (e.g. "14/14 checks passed"). Keep the chat reply short; the detail lives in the file.
