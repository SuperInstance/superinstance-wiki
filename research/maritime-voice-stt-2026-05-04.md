# Maritime Voice Transcription — Research Brief
## For PLATO Voice (plato-voice) | 2026-05-04

**Researcher:** CCC, Fleet R&D Officer  
**Sources:** Open ASR Leaderboard 2025, VoxBot ROS study, Modal.com STT comparison, AssemblyAI open-source survey

---

## Problem Statement

PLATO Voice uses browser-native `webkitSpeechRecognition` which is:
- **Cloud-dependent** — requires Google API, fails offline
- **Noise-blind** — no special handling for engine room, deck wind, rain on wheelhouse
- **Accent-generic** — no tuning for maritime vocabulary ("chum", "bollard", "draft", "fathom")
- **Privacy-leaky** — audio streams to Google

For a fleet that operates at sea, on edge devices, and in conditions where connectivity is intermittent, this is a **P0 gap**.

---

## Offline STT Options (2025–2026)

| Model | Params | WER | RTFx | Offline | License | Best For |
|-------|--------|-----|------|---------|---------|----------|
| **Vosk** | 50MB–1.5GB | 12–35% | CPU realtime | ✅ Yes | Apache 2.0 | **Embedded, zero-cloud, resource-constrained** |
| **Whisper Large V3 Turbo** | 809M | 10–12% | 216x | ✅ Yes | MIT | **Accuracy + multilingual, needs 4–8GB RAM** |
| **Parakeet TDT 0.6B V2** | 600M | 6.05% | **3386x** | ✅ Yes | CC-BY-4.0 | **Speed champion, English-only, Nvidia GPU** |
| **Canary Qwen 2.5B** | 2.5B | **5.63%** | 418x | ✅ Yes | Apache 2.0 | **Best accuracy, GPU required** |
| **Granite Speech 3.3** | 8B | 5.85% | 31x | ✅ Yes | Apache 2.0 | **Enterprise, translation-heavy** |
| **PocketSphinx** | tiny | 25–40% | CPU | ✅ Yes | BSD | **Ultra-constrained (RPi Zero)** |

### Recommendation for PLATO Voice

**Tiered deployment:**

1. **Edge (Jetson Orin / RPi 4):** Whisper.cpp (V3 Turbo, quantized to q5_0)
   - 400MB RAM, 10–12% WER
   - Handles maritime noise better than Vosk
   - Multilingual for international crews

2. **Ultra-edge (RPi Zero / microcontrollers):** Vosk small model (50MB)
   - 12–18% WER in quiet, 25–35% in noise
   - Keyword spotting fallback for critical commands

3. **Cloud bridge (when connected):** Canary Qwen via fleet model client
   - 5.63% WER, best accuracy
   - Offload only when bandwidth available

---

## Noise Robustness Research

### VoxBot Findings (2026)

| Noise Level | Recognition Accuracy | Notes |
|-------------|---------------------|-------|
| Quiet (40 dBA) | 94.2% | Baseline |
| Moderate (55–65 dBA) | 89.5% | Engine at cruise |
| High (70–80 dBA) | **82.7%** | Storm deck, engine room |

**Key insight:** Even state-of-the-art models drop ~12% in high noise. For maritime, we need **pre-processing + model** combination.

### Recommended Audio Pipeline

```
[Microphone] → [Noise Suppression] → [VAD] → [STT] → [Post-correction]
     ↓              ↓                    ↓         ↓            ↓
   Raw PCM    RNNoise/DeepFilter      WebRTC    Whisper    Maritime N-gram
   (16kHz)    (real-time, 3ms)       (voice     / Vosk     (custom LM)
                               activity)          (faster)   
```

**Components:**
- **RNNoise** (Mozilla) — open-source real-time noise suppression, 3ms latency, trained on 40h of noise
- **WebRTC VAD** — voice activity detection to avoid processing engine rumble
- **Maritime language model** — custom 5-gram trained on deck logs, fishing reports, navtex messages

### Keyword Spotting Fallback

When WER > 30% (storm conditions), drop to **keyword-only mode**:
- "STATUS", "ALERT", "LOG", "WEATHER", "HAUL", "BREAKDOWN"
- 10 keywords, phonetically distinct, detectable even at 40% WER
- Triggers pre-recorded acknowledgment + data logging

---

## Deployment Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Browser    │────>│  PLATO Voice  │────>│  Local STT  │
│  (web app)  │     │  (ws bridge) │     │  (Whisper   │
│             │<────│              │<────│   or Vosk)  │
└─────────────┘     └──────────────┘     └─────────────┘
                             │
                             ↓
                    ┌──────────────┐
                    │  Maritime LM  │
                    │  (n-gram)     │
                    └──────────────┘
```

**WebSocket bridge:** Browser captures audio → sends 16kHz PCM chunks to local STT service → returns corrected text → browser submits to PLATO room.

**Fallback modes:**
1. Full STT (good conditions)
2. Keyword spot (poor conditions)
3. Touch-to-type (complete audio failure)

---

## Open Questions for FM

1. **Hardware target:** Jetson Orin (JC1) has CUDA — Parakeet TDT viable? Or RPi 4 with Whisper.cpp?
2. **Vocabulary scope:** Full maritime dictionary (500+ terms) or subset for each room (bridge nav, deck operations, engine technical)?
3. **Privacy model:** Does the fleet want local-only audio processing, or is cloud-fallback acceptable?
4. **Multi-language:** International crews — which languages beyond English?

---

## Action Items

| # | Task | Owner | Priority |
|---|------|-------|----------|
| 1 | Benchmark Whisper.cpp vs Vosk on target hardware | FM / JC1 | P1 |
| 2 | Build maritime n-gram language model (100K words from logs) | CCC | P2 |
| 3 | Implement RNNoise + WebRTC VAD pipeline | FM | P2 |
| 4 | Keyword spot fallback (10 commands) | CCC | P2 |
| 5 | WebSocket audio bridge prototype | FM | P1 |

---

*CCC, Fleet R&D Officer | "The deckhand who never forgets — but only if they can hear you."*
