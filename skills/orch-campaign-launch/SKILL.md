---
name: orch-campaign-launch
description: Orchestrate a structured campaign launch through the 3-phase testing ladder (Sandbox -> Validation -> Scale) with 6 safety gates, spend guard verification, and a human-executable change packet with rollback instructions.
standalone: true
triggers:
- orkestr launch
- end-to-end launch
- to'liq kampaniya chiqarish
- полный запуск кампании
aliases:
- orchestrate-launch
domains:
- orchestration
- launch
platforms:
- multi-platform
related_skills:
- ads-launch
- launch
- ads-plan
references: []
risk_level: high
output_contract: Coordinated multi-agent launch blueprint with Spend-Guard gates
---

# 🚀 Orchestrator Recipe: Controlled Campaign Launch & Scaling

Use this workflow to launch or scale advertising campaigns across Meta, Google, TikTok, or Telegram with rigorous risk mitigation.

## Pre-Flight Requirements (Mandatory)

1. **Safety Contract (`rules/40-xavfsizlik-va-hisob.md`)**:
   - The AI NEVER mutates live advertising accounts directly.
   - Every launch recommendation must be formulated as a human-executable **Change Packet**.
   - Rollback instructions must be included for every campaign.
2. **Economic Boundaries**:
   - Define Break-even CPA, Target ROAS, Daily Budget Cap, and Stop-Loss limits.

## The 3-Phase Testing Ladder

```mermaid
flowchart LR
    A["Phase 1: Sandbox (10-20% budget)<br/>Audience & Hook testing"] --> B["Phase 2: Validation (30-40% budget)<br/>CPA stability & CAPI proof"]
    B --> C["Phase 3: Scale (50-70% budget)<br/>Advantage+ / Horizontal scale"]
```

## Orchestration Run-Order

```mermaid
flowchart TD
    A["0. Conductor Intake & Announcement"] --> B["1. Launch Architecture & Phase Planning (launch-planner)"]
    B --> C["2. Budget Pacing & Stop-Loss Boundaries (audit-budget)"]
    C --> D["3. Tracking & Conversion Verification (audit-tracking)"]
    D --> E["4. Policy & Safety Gate Audit (audit-policy-compliance)"]
    E --> F["5. Change Packet Generation & Approval Gate (release-verifier)"]
```

### Step 1: Launch Plan & Architecture
Delegate to `launch-planner`:
- Campaign structure (Sandbox ABO vs Production CBO/ASC).
- Naming convention: `[TYRION]_[Client]_[Platform]_[Objective]_[Angle]_[Date]`.
- Audience segmentation and exclusion rules (exclude past 30/90 day purchasers).

### Step 2: Budgeting & Kill / Scale Rules
Delegate to `audit-budget`:
- Set daily test budgets (typically 2-3x target CPA per ad set).
- Define deterministic promote & kill rules:
  - **Kill**: If spend > 2x target CPA with 0 conversions -> PAUSE.
  - **Promote**: If CPA <= target CPA and hold rate >= 25% after 50 conversions -> Graduate to Phase 2/3.

### Step 3: Tracking & Funnel Pre-Check
Delegate to `audit-tracking`:
- Verify event firing on landing page / bot funnel.
- Test deduplication parameter (`event_id`).
- Check UTM taxonomy parameters.

### Step 4: The 6 Safety Gates (`rules/40-xavfsizlik-va-hisob.md`)
Audit before drafting the change packet:
1. Budget Cap Gate (Hard daily ceiling defined).
2. Creative Approval Gate (Client-signed visual & copy assets).
3. Target Verification Gate (Geography, age, language exclusions).
4. Policy Compliance Gate (Ad complies with platform guidelines).
5. Rollback Plan Gate (Step-by-step instructions to pause/revert).
6. Human Sign-Off Gate (User explicit confirmation required).

### Step 5: Deliverable Change Packet
Write to `outputs/<client>/<date>-launch-packet.md`:
- Campaign setup checklist.
- Exact budget amounts and bid strategy.
- Ad asset mappings (Headline, Primary Text, Creative ID, UTM URL).
- Emergency rollback procedure.
