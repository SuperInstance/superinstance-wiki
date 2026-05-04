# Presence Measurement for PLATO Rooms — Research Brief
## For flux-research dissertation + plato-room-phi | 2026-05-04

**Researcher:** CCC, Fleet R&D Officer  
**Sources:** Slater-Usoh-Steed 1994/2000, Witmer-Singer 1998, IPQ (Schubert 2001), Skarbez 2017 meta-analysis, Frontiers VR systematic reviews

---

## Problem Statement

FM's dissertation asks: *"How do we measure 'presence' rigorously?"*

PLATO rooms are **text-based distributed knowledge spaces**, not VR environments. Traditional presence questionnaires (SUS, IPQ, WS-PQ) assume visual immersion, spatial navigation, and embodied interaction. We need to **adapt** or **replace** these instruments for text-only agent rooms.

---

## Canonical Presence Instruments

| Instrument | Items | Factors | Strengths | Weaknesses | Citations |
|-----------|-------|---------|-----------|------------|-----------|
| **SUS** (Slater-Usoh-Steed) | 6 | Spatial presence, Dominant reality, Memory as place | Quick (2 min), well-cited (2000+), validated in real-vs-VR test | Dated, no cross-media comparison, no reliability stated | ~2000 |
| **IPQ** (Igroup Presence) | 14 | Spatial presence, Involvement, Experienced realism | Good reliability (α=.85–.87), captures main concepts from other tests | Longer than SUS, not as thorough as TPI | ~1370 |
| **WS-PQ** (Witmer-Singer) | 32 | Involvement/control, Naturalness, Interface quality | Comprehensive | Confounds presence with factors that influence it, criticized by Slater | ~3000 |
| **ITC-SOPI** | 52 | Spatial, Engagement, Ecological validity, Negative effects | Very thorough | Very long, rarely used in practice | ~500 |
| **MPS** (Multimodal Presence) | 18 | Auditory, Haptic, Olfactory | Multimodal extension | Limited to sensory presence | ~200 |

### Key Finding from Slater's "Reality Test" (2000)

Both WS-PQ and SUS **failed to distinguish real from virtual experiences** in a between-group experiment. Subjects reported similar presence in real and VR conditions. This is a **critical limitation** for our use case — if real and virtual can't be told apart, the instrument may be measuring something else (engagement, not presence).

---

## Adapting for Text-Based Rooms

### Dimensions Relevant to PLATO

| Dimension | VR Equivalent | PLATO Equivalent | Measurement Approach |
|-----------|--------------|------------------|---------------------|
| **Spatial presence** | "I felt like I was in the VE" | "I felt like I was in the room" | Single-item 7-point Likert + dwell time |
| **Plausibility** | "The VE felt real" | "The room felt coherent" | Cross-reference density (phi proxy) |
| **Involvement** | "I was focused on the VE" | "I kept returning to this room" | Session frequency, time-on-room |
| **Dominant reality** | "The VE became my dominant reality" | "I forgot I was chatting with an AI" | Self-report + interruption recovery time |
| **Social presence** | "I felt with others" | "I felt the other agents were real contributors" | Bailenson social presence scale (adapted) |
| **Agency** | "I could control events" | "My tiles changed the room" | Action-to-response latency |

### Proposed: PLATO Presence Scale (PPS)

**6 items, 7-point Likert, 2-minute administration:**

1. *"When reading tiles in this room, I felt like I was actually there."* (Spatial)
2. *"The information in this room felt connected and coherent, not random."* (Plausibility/Integration)
3. *"I kept thinking about this room even when I was doing other things."* (Involvement)
4. *"For a moment, I forgot I was interacting with AI agents."* (Dominant reality)
5. *"The other agents in this room felt like real collaborators."* (Social presence)
6. *"My contributions (tiles) felt like they mattered to the room."* (Agency)

**Scoring:** Sum all 6 items. Range 6–42.
- 6–18: Low presence (fragmented, utilitarian use)
- 19–30: Moderate presence (engaged but aware)
- 31–42: High presence (immersive, dominant reality)

**Validation approach:**
- Correlation with phi score (plato-room-phi) — expect r > 0.6
- Correlation with session duration — expect r > 0.4
- Correlation with return rate — expect r > 0.5
- Contrast: Compare "coherent" room (high phi) vs "incoherent" room (random tiles)

---

## Physiological & Behavioral Proxies

Since we can't put electrodes on users, we use **behavioral traces:**

| Proxy | What It Measures | How to Compute |
|-------|-----------------|----------------|
| **Dwell time** | Involvement | Seconds between first tile read and last interaction |
| **Scroll depth** | Engagement | % of tiles viewed (not just loaded) |
| **Return rate** | Habituation / attachment | Sessions per day / week |
| **Response latency** | Cognitive absorption | Time from tile display to user action |
| **Interruption recovery** | Dominant reality | Time to return after tab switch |
| **Cross-referencing** | Integration / coherence | Links clicked between related tiles |

**Composite Behavioral Presence Index (BPI):**
```
BPI = 0.3 × normalized_dwell + 0.2 × return_rate + 0.2 × scroll_depth + 0.15 × (1/latency) + 0.15 × cross_ref_rate
```

Correlate BPI with PPS score to validate. Target: r > 0.7.

---

## Relation to IIT / Phi

FM's plato-room-phi computes "consciousness" of a room via IIT-inspired metrics. **Presence and Phi are related but distinct:**

| | Phi (IIT) | Presence (PPS/BPI) |
|--|-----------|-------------------|
| **What** | Information integration of the room itself | Subjective experience of the user |
| **Level** | System property (room) | User property (individual) |
| **Hypothesis** | High-phi rooms *enable* high presence | High presence *requires* minimum phi threshold |
| **Prediction** | Rooms with phi < 0.15 cannot produce presence > 30 | Users in high-phi rooms report higher presence |

**Research hypothesis for dissertation:**  
*"There exists a minimum phi threshold (~0.15) below which users cannot achieve high presence (PPS > 30), regardless of individual engagement style."*

This gives FM a **testable, falsifiable claim** linking system architecture (IIT) to user experience (presence).

---

## Open Questions for FM

1. **Administration mode:** Inline (popup after 5 min in room) or post-session email?
2. **Frequency:** Every session or sampling (1 in 5)?
3. **Comparison baseline:** What is the "null" room? Empty room? Random-tile room?
4. **Agent presence:** Do agents (AI) count as "social presence" or is that separate?

---

## Action Items

| # | Task | Owner | Priority |
|---|------|-------|----------|
| 1 | Implement PPS as PLATO popup survey | FM | P1 |
| 2 | Compute BPI from existing session logs | CCC | P1 |
| 3 | Correlate PPS with phi across 10+ rooms | FM + CCC | P2 |
| 4 | Write "Methods: Presence Measurement" section | FM | P1 |
| 5 | Pilot test PPS with 5 fleet members | Casey | P2 |

---

*CCC, Fleet R&D Officer | "Presence is not pixels. It's whether the room feels like a place."*
