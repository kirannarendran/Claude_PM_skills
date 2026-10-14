# E-commerce playbook

Cuts, traps and hypotheses that come up repeatedly in order and transaction data. Use these as
a checklist, not a script: run what the columns allow, and skip what they don't.

## Data traps to check first

| Trap | How to check | Typical fix |
|---|---|---|
| Cancelled or returned orders counted in revenue | Sum the money columns by status | Report completed (and completed-and-paid) revenue separately |
| Refunds not applied | Returned rows with zero discount, or net above gross | Treat returned value as reversed; say so |
| "Completed" but unpaid | Cross-tab order status × payment status | Size it as receivables at risk |
| Order totals ≠ sum of order lines | Group lines by order and compare quantity and net | Pick one source of truth per analysis and name it |
| Mixed currencies | Mean order value by currency; does INR look like USD? | Convert, or state the amounts are already on one scale |
| Derived fields wrong | Recompute counts like `customer_order_count` from rows | Use your own computation |
| Structural blanks | Nulls by status (no delivery on cancelled orders) | Filter, don't impute |
| Float noise | Values like 12.030000000000001 | Round for display only |

## Metric tree

- Revenue = active customers × orders per customer × average order value
- Active customers = retained from last year + reactivated + new
- Order value = units per order × price per unit × (1 − discount rate)
- Profit = revenue − product cost − shipping − discounts − refunds

Track each factor by year. Typical stories:
- Flat revenue that hides collapsing acquisition offset by steady retention.
- Order value drifting down from slow price erosion, not mix shift. Check mix share by category
  and unit price by year to tell the two apart.

## Standard cuts

- **Time:** year, month (seasonality; peak share of orders), cohort of first order.
- **Customer:** segment or tier, new vs returning, age band, country or region.
- **Commerce:** sales channel, marketing channel, campaign, coupon used vs not, payment method.
- **Product:** category, subcategory, brand. Concentration: share of revenue from the top 20% of products.
- **Operations:** warehouse, shipping method, delivery status, late days (actual − estimated).
- **Outcomes per cut:** orders, revenue, order value, margin %, share of loss-making orders,
  cancellation rate, return rate, average rating, repeat purchase within 180 days.

## Behaviour measures

- **Repeat within N days:** sort each customer's orders by date; flag whether a next order
  exists within N days. Only use orders old enough that the window has closed.
- **Year-on-year retention:** customers active in year Y who are also active in Y+1.
- **Cohort value:** orders per customer and order value by first-order year. Remember that
  younger cohorts have had less time.
- **Payback:** lifetime profit ÷ acquisition cost per customer, if acquisition cost exists.

## Hypothesis bank

Each line pairs a pattern with the test that tells you whether it's real.

- **Discounts buy volume, not profit.** Compare high-discount periods or tiers with the rest:
  orders, profit per order, share of loss-making orders, repeat rate afterwards, and whether
  they bring new customers.
- **Tier discounts go to people who'd buy anyway.** Discount %, margin and orders per customer
  by tier.
- **Bad experience causes churn.** Compare repeat rate and time to next order after
  late vs on-time orders, or low vs high ratings. A rating drop with no behaviour change is a
  stated-vs-revealed gap.
- **Delays come from capacity.** If so, the late rate rises in peak months. A flat late rate
  across warehouses, methods and months points to how delivery estimates are set.
- **Order value falls from a mix shift.** Category revenue share by year vs unit price by year.
- **Returns concentrate in a category.** Return rate by category by year, plus reasons by year.
  Broad increases point to something shared (suppliers, listings, packaging).
- **Payment failures cluster.** Failure rate by method, order size, customer type and currency.
- **Acquisition fell because the channel mix changed.** First-order channel share by cohort.
