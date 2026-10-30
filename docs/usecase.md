# Problem Statement and Opportunity

## Problem statement

### How incidents are managed today

Today, preschool incident management is a fragmented, high-friction triage divided between classroom clipboards, childcare messaging apps, and physical compliance binders. When an incident occurs—such as a toddler bite or playground fall—teachers operating under strict supervision ratios quickly jot down brief details on carbon-copy "ouch reports" or mobile tablets, leaving the director to manually intercept and sanitize the narrative to protect peer confidentiality before parents see it.

Directors must then mentally track strict statutory deadlines (such as mandatory 24- to 48-hour state licensing notifications for serious injuries) while making proactive, de-escalating phone calls to anxious families and stepping into classrooms to cover staff breaks. The process culminates in a chaotic evening lobby rush to capture legally mandated parent signatures on clipboards, after which documents are archived in static office binders, leaving missing sign-offs, regulatory deadlines, and recurring behavioral triggers undetected until an unannounced state licensing inspection or formal parent dispute.

### The cost of getting it wrong

Unreported serious injuries or failure to collect parent signatures within the mandated window results in immediate licensing deficiencies, public inspection violations, or loss of accreditation (e.g., NAEYC). See, for example, [Washington childcare licensing](https://neztio.com/en/blog/washington-childcare-licensing).

## Opportunity and challenge

An incident policy management agent can significantly alleviate the administrative burden on teachers and center directors, freeing valuable time for direct engagement with children and core operational leadership. However, every decision the agent makes must follow the statutory compliance policy without exception. Unvetted generative outputs or hallucinations could lead to improper triage, missed regulatory reporting deadlines, or compromised child safety.

## Why this needs neurosymbolic AI

### Why LLMs can't do this alone

LLM-based assistants can interact naturally with staff, understanding incidents as they're reported, mid-supervision and a fragment at a time ("fell off the slide, bumped her head, she's crying but talking", then later "nurse looked at it"), but they can't be relied on to apply the policy:

- **They can under-triage.** A head bump described casually ("just a little bonk") can be classified as a minor injury, although the policy treats any head injury as significant.
- **They can skip or reorder steps,** or declare a step done because the narrative implies it.
- **Their operation isn't repeatable.** The same description can produce a different tier on a different run, and a licensing inspector will ask why.


### What symbolic reasoning adds

Adding symbolic reasoning keeps the LLM where it is strong, listening to staff, and encodes the policy itself as rules the assistant follows:

- **Tiers come from the policy.** The LLM only suggests a tier; it counts once staff confirm it, and the tier's checklist comes straight from the policy.
- **Deadlines are computed, not remembered.** Each one is calculated from the time of the incident and tracked as the incident unfolds.
- **Steps happen in order.** The next step is always the earliest unfinished one, and a step is done only when staff confirm it.
- **Decisions are repeatable and traceable.** The same state always leads to the same next step, and each one can be traced to the policy rule behind it, ready for a licensing inspection.

| Neural: reading what staff say | Symbolic: following the policy |
|---|---|
| Suggest a tier from the description | Confirm the tier with staff before it counts |
| Notice when an update says a step was done | Build the tier's checklist and fix the step order |
| | Compute and track every deadline |
| | Decide the next step, the same way every time |

The LLM never writes to the incident record: each reading is a proposal that a staff member confirms with a yes or no, so the judgment stays with staff and the policy is followed to the letter.

## Impact

A policy-tracking assistant transforms incident management by interpreting classroom narratives, recommending triage tiers for staff to confirm, and guiding staff through the required steps. It removes administrative friction by tracking strict statutory compliance deadlines and drafting sanitized incident records, replacing the manual overhead of clipboard logs and office binders, with every decision provably following the policy.

## Technical approach

See [the technical approach](approach.md) for how an agent with cognition inside meets this challenge.
