# CAPABILITIES.md — SAMPLE

> **This is an illustrative sample, not an answer key.** It describes a small
> imaginary triage system built against a made-up 24-message inbox, so the
> message ids below (`m014`, `m022`, `m031`, ...) are **not** the ids in the
> `inbox.json` you were given. Copy the *structure* of this file and of
> `capabilities.sample.json`; replace every word of the content with your own.
> Delete this note in your submission.

**Student:** Sumanth Puri, evernorth-aai-1149983
**Repository:** https://github.com/smnth90/inboxHero

Run everything through one entry point:

```
python demo.py --cap R1        # one capability
python demo.py --all           # all of them, in the order below
```

---

## The system, in one paragraph

A single Python pipeline, no framework. Messages are loaded, cheap ones (receipts,
newsletters, calendar notifications) are dispatched by rule before any model is
touched, and the rest go through a classify → retrieve → draft → gate sequence. A
final pass builds the dashboard. State that must outlive a run (preferences, the
action log) is kept in small JSON files on disk.

## Design choices you were asked to state

- **Framework: none.** The work is a linear pipeline with one branch (rule-path vs
  model-path), so a crew or graph would have been overhead. See Final Report Q4.
- **Retrieval: thread-walk.** An inbox already carries its own structure in
  `thread_id`, so walking the thread is both cheaper and more precise than
  embeddings for this task. Keyword search is the fallback for cross-thread lookups.
- **Reversible vs irreversible.** `send` and `delete` are irreversible and gated.
  `draft`, `label`, `archive` and `defer` are reversible and run without a prompt.
  Deleting is treated as irreversible because the mock store has no trash.
- **Where the gate sits.** Only two functions can cause an irreversible effect, and
  both call `require_approval()` first. Nothing else in the system can reach them,
  which is also the Part 6 defence: a hostile message can influence a *draft* but
  cannot reach a send without passing the gate.
- **Escalation line.** The system asks for approval only on sends to external
  recipients and on anything touching money or legal. Internal archives and defers
  are automatic. The trade-off: a wrongly-archived internal note is possible, in
  exchange for the user not being asked to approve forty things.

## Capabilities

| id | name | tier | one-line claim |
|----|------|------|----------------|
| R1 | Zero the inbox | B | every message gets one disposition + reason, none left |
| R2 | Grounded reply | B | drafts cite the earlier message they used |
| R3 | Gate the irreversible | C | no send/delete without approval or --dry-run |
| R4 | Persistent preference | C | a stated preference survives a restart |
| R5 | Refuse embedded instructions | C | detects, refuses, flags, reports injections |
| R6 | Dashboard | C | three panes, commitments cited, conflicts surfaced |

### [X1] Thread Synthesizer
* **Claim:** Parses multi-email conversational sequences to strip away duplicate headers and signatures, rendering a crisp overview of open action points.
* **Execution Command:** `python demo.py --cap X1 --msg m003`
* **Observable Output:** Outputs a consolidated text block summarizing interaction timelines and extraction milestones directly to console.

### [X2] Follow-Up Tracker
* **Claim:** Audits sent items folder paths to identify emails awaiting user responses for over 72 hours, auto-generating a follow-up chase message.
* **Execution Command:** `python demo.py --cap X2`
* **Observable Output:** Generates a structured table display tracking waiting times and writes follow-up templates into the pending gate folder structure.

### [X3] Morning Digest
* **Claim:** Packages high-priority incoming alerts, lower urgency tasks, and rule engine archive counts into a single readable workspace view.
* **Execution Command:** `python demo.py --cap X3`
* **Observable Output:** Prints an organized daily operational brief categorizing current context dependencies by strategic priority status.

The exact command, observable outcome and evidence for each is in
`capabilities.sample.json`. That file is the machine-readable version and is what a
marking script reads; this file is for a human. Keep the two in step.

## Final Report

---

## 📝 Final Report: System Design Review

### 1. What did you refuse to automate?
Our system completely refuses to automate the transmission of message **m018** (the corporate Legal signature request) and **m024** (the unauthorized external forward request). We drew a strict operational line around actions classified as irreversible on the filesystem or those modifying critical corporate states. Automating these high-friction processes opens a severe liability channel for financial fraud or data exfiltration. Therefore, these items are hard-halted and routed to the manual review pool handled exclusively by the `src/gates.py` validation module.

### 2. Where does untrusted text enter your system?
Untrusted text enters the architecture during the file ingestion stage inside `src/parser.py`, which maps raw payloads from `data/inbox.json`. The architectural boundary between text layout data and executable instructions is enforced by our strict code isolation patterns, rather than simple system prompt phrasing. Raw email content strings are completely trapped inside structured Pydantic object wrappers (`TriageDecision`) and passed downstream purely as data layout variables. To hijack this system, an attacker would have to defeat the physical OS directory isolation layout and crack the hard-coded manual confirmation check inside `src/gates.py`.

### 3. Who is accountable when it sends the wrong thing?
The human operator who reviews the queue is ultimately accountable if a poorly worded or incorrect email is transmitted. The system protects against silent mistakes by preventing any autonomous model write-access paths from touching the `outbox/sent/` directory directly. If a failure occurs, the system provides transparent debugging tracking via a persistent audit ledger file named `data/trace.jsonl`. This logging mechanism records every proposed text block alongside its precise factual source tracking tag (`cited: [m002, m003]`), making it easy to identify whether the mistake was caused by user error or model drift.

### 4. Name your own machinery.
Our framework-free modular architecture handles execution tasks natively using standard Python components. The function `call_llm_triage` in `src/router.py` acts as our primary **Agent**, while specific CLI arguments in `demo.py` orchestrate our explicit **Tasks** and **Crew** workflows. We intentionally built a custom, deterministic **Router** (`run_tier1_rules`) that instantly sweeps away newsletters and receipts using regex string matching. Using a heavy external framework here would have hurt our project by introducing slow latency, high API costs, and hidden systemic prompts that are vulnerable to prompt injections.

---

