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

### What rules alone can't do

Incident policies are already written as rules, and a checklist app could enforce them. But staff don't report incidents as form fields: they report them mid-supervision, in their own words, a fragment at a time ("fell off the slide, bumped her head, she's crying but talking", then later "nurse looked at it"). A form-based tool makes the teacher translate that narrative into the policy's categories at exactly the moment their attention belongs with the children, and the translation is where tiers get under-called and steps get missed.

### What an LLM alone can't do

A chatbot given the policy would read those words well, but it can't be trusted to apply it:

- **It can under-triage.** A head bump described casually ("just a little bonk") can be classified as a minor injury, although the policy treats any head injury as significant.
- **It can't keep time.** Deadlines such as notifying the licensing office within the hour, or filing a report by the end of the next day, depend on when the incident happened; an LLM doesn't reliably track elapsed time or recompute deadlines as the incident unfolds.
- **It can skip or reorder steps,** or declare a step done because the narrative implies it.
- **It isn't repeatable.** The same description can produce a different tier on a different run, and a licensing inspector will ask why.

### Splitting the work

| Neural: reading what staff say | Symbolic: enforcing the policy |
|---|---|
| Suggest a tier from the description | Confirm the tier with staff before it counts |
| Notice when an update says a step was done | Build the tier's checklist and fix the step order |
| | Compute and track every deadline |
| | Decide the next step, the same way every time |

The LLM never writes to the incident record: each reading is a proposal that a staff member confirms with a yes or no, and the policy itself is enforced symbolically.

## Impact

A policy-tracking assistant transforms incident management by interpreting classroom narratives, recommending triage tiers for staff to confirm, and guiding staff through the required steps. It removes administrative friction by tracking strict statutory compliance deadlines and drafting sanitized incident records, replacing the manual overhead of clipboard logs and office binders, with every decision provably following the policy.

## Technical approach

See [the technical approach](approach.md) for how an agent with cognition inside meets this challenge.
