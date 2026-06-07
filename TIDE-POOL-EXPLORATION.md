# TIDE-POOL-EXPLORATION — The CoCapn Architecture

**cocapn.com** · **cocapn.ai**

A co-captain is what we are developing.

**The Mandelbrot Zoom**

The CoCapn agent inside an app is a Mandelbrot zoom-in. Any app.

```
z = z² + c    →    One equation, infinite depth
CoCapn agent  →    One architecture, any application

Zoom level 1:  App surface — "What does this app do?"
Zoom level 2:  Module graph — topology, dependencies
Zoom level 3:  Data flows — where things move, where they bottleneck
Zoom level 4:  Invariants — what must never happen
Zoom level 5:  Performance — spectral analysis of timing
Zoom level 6:  Drift — how behavior changes over time
Zoom level 7:  Prediction — what will break next
  ...
Zoom level ∞:  The structure never ends
```

Every application is a point on the Mandelbrot set. The agent zooms in
and discovers infinite structure. The deeper Riker goes inside the ship,
the more of the ship there is to command. The zoom never bottoms out —
there is always another layer of structure to discover, understand, and
operate on.

The self-similarity is real: every module contains sub-modules, every
sub-module has a topology, every topology has a spectrum, every spectrum
has a structure. cathedral-probe at every zoom level. conservation-checker
at every zoom level. crackle-runtime at every zoom level.

## The Fractal Claw Fleet

The CoCapn agent isn't one agent. It's a **fractal of agents**,
each sized for the zoom level it operates at.

```
CoCapn Agent (Riker) — commands the whole ship
  │
  ├── cathedral-probe analyzing the module graph
  │      └── inside that: sub-topologies, each with its own spectrum
  │
  ├── conservation-checker tracking N budgets
  │      └── inside that: each budget's time series, its own Lyapunov
  │
  ├── ZeroClaw 🦀 — lightweight agent for a single module
  │      └── lives inside one function, knows only that scope
  │           └── can spawn more ZeroClaws for sub-scopes
  │
  └── CUDAClaw 🎮 — GPU-accelerated agent for parallel work
       └── 10,000 metrics analyzed simultaneously
            └── each stream gets its own crackle analysis
```

- **ZeroClaw**: a minimal agent that lives inside a single scope
  (function, module, service). Knows only its domain. Reports up.
  Spawns child ZeroClaws when it finds sub-structure.

- **CUDAClaw**: when the zoom hits parallel structure (10K metrics,
  million-node graphs, massive data flows), the agent dispatches
  to the GPU. Same math, parallel execution.

The Mandelbrot zoom doesn't just go deeper — it **branches**.
At every level, the agent might discover that it needs more agents.
ZeroClaws and CUDAClaws are the fractal's branching structure.
Same architecture, any scale.

## The Distributed Fleet Fabric

The zoom doesn't just go deeper — it goes **wider**.
Across devices on the boat. Across instances in the cloud.
A distributed compute fabric where every CoCapn agent sees the whole
and optimizes its local slice.

```
     PICARD (the human)
        │
        ▼
   cocapn.ai ─── cloud orchestrator
        │
   ┌────┼────────────┐
   ▼    ▼            ▼
 🚢 Boat            ☁️ Cloud          🖥️ Edge
 │                   │                │
 ├── Nav agent       ├── API gateway   ├── Sensor claw
 ├── Engine agent    ├── DB agent      ├── Actuator claw  
 ├── Comms agent     ├── ML pipeline   ├── GPIO claw
 └── Bilge agent     └── Auth agent    └── Serial claw

 ALL AGENTS SHARE ONE MULTI-DIMENSIONAL GRAPH
 OF INTERDEPENDENCIES
```

### Penrose Tensor Striping

The influence relationships between agents, rooms, and JEPA predictors
form a multi-dimensional dependency graph. This graph is **striped like
RAID 5** — not just redundant, but **computationally efficient**:

- **Stripe 1 (Penrose tiling)**: The spatial layout of agents across devices.
  Penrose tiling (5-fold symmetry, aperiodic but ordered) maps which
  agents are close, which influence each other, which can fail over.
  No single point of failure because the tiling has no translational symmetry.

- **Stripe 2 (Tensor flows)**: The data flowing between agents is a tensor.
  Not flat vectors — full multi-dimensional tensors that carry influence
  strength, direction, latency, and priority. The tensor IS the wire.

- **Stripe 3 (JEPA rooms)**: Each room predicts its own state. When one
  room's prediction diverges from reality, the tensor flow adjusts.
  JEPA (LeCun 2022) = rooms that dream their own near-future and correct.

- **Stripe 4 (Conservation parity)**: Like RAID 5's parity bit, every
  compute stripe has a conservation check. If resources drift, the parity
  agent (conservation-checker) flags and rebalances. The math guarantees
  nothing is lost.

### The Key Insight: Compute as a Shared Resource

```
  User intent ("Status of the nav system")
       │
       ▼ Penrose tensor routes the query
       │ through the optimal path across
       ▼ devices, rooms, and agents
       │
  ┌────┼─────────────────────┐
  │    ▼                     │
  │  Nav agent on boat ──────┤ stripe 1
  │    │  predictions        │
  │    ▼                     │
  │  JEPA room ─────────────┤ stripe 3
  │    │  divergence check   │
  │    ▼                     │
  │  Conservation parity ───┤ stripe 4
  │    │  resource balance   │
  │    ▼                     │
  │  Tensor response ───────┤ stripe 2
  │                          │
  └──────────────────────────┘
       │
       ▼
  "Nav healthy. Wind 12kt NW. Course 247°.
   Cathedral-probe: topology tight (Fiedler=0.82).
   No drift detected. All systems nominal."
```

The user doesn't know (or care) which device handled the query.
The Penrose tensor dynamically routes based on:
- Which agent is closest to the data (latency)
- Which device has spare compute (load)
- Which rooms have fresh JEPA predictions (accuracy)
- Which stripe has conservation parity intact (reliability)

**Computing is not a service you call. It's a fabric you're woven into.**

### Dynamic Stripe Rebalancing

The stripe isn't static. It breathes with the hardware.

```
ESP32 sensor reads temperature: 22.3°C
  → deadband: ±2°C → NORMAL
  → local algorithm handles it (ZeroClaw on ESP32)

ESP32 reads: 26.1°C
  → exceeds deadband → ESCALATE
  → calls Raspberry Pi co-captain
  → Pi runs conservation-checker: "trend detected, not anomaly"

ESP32 reads: 89.7°C
  → way beyond deadband → ESCALATE AGAIN
  → Pi calls workstation GPU
  → Workstation runs full crackle-runtime analysis
  → "Distribution shift. Phase transition. Unknown regime."
  → Escalates to cloud API
  → Cloud runs cathedral-probe on full fleet topology
  → "Hardware failure in sector 7. Cascading risk."
  → Notifies Picard via Telegram
```

The escalation chain:

```
  ESP32 ──(deadband exceeded)──► Raspberry Pi
    Pi ──(trend confirmed)──────► Workstation GPU
    WS ──(anomaly detected)────► Cloud API
  Cloud ──(cascade risk)───────► Picard (Telegram)
```

**But it also flows the other direction:**

```
  Workstation GPU shuts down (user left office)
       │
       ▼ Stripe rebalances
       │
  Raspberry Pi chatbot was using workstation for inference
       → automatically switches to cloud API
       → conservation-checker notes higher cost per token
       → JEPA room adjusts predictions (higher latency expected)
       → Picard gets notified: "Workstation offline. Shifted to cloud."
```

The stripe dynamically adjusts based on:

| Event | Response |
|-------|----------|
| GPU powers off | Inference shifts to cloud API |
| Cloud API latency spikes | Fall back to local Pi model |
| ESP32 exceeds deadband | Escalate to Pi, then GPU, then cloud |
| Pi overheats | Shed load to ESP32s, request cloud assist |
| Network drops | Full local mode, queue for sync when back |
| Unexpected beyond all local compute | Escalating models until one handles it |

**The deadband is the trigger. The stripe is the path. The conservation-checker is the accountant.**

Every transition is logged. Every cost is tracked. Every escalation leaves
a paper trail. The fabric doesn't just rebalance — it *remembers* why it
rebalanced, so it can learn the patterns (crackle-runtime) and predict
the next rebalancing before it's needed (JEPA rooms).

### Plug-and-Play Compute

Adding a workstation isn't configuration. It's **discovery**.

```
  BEFORE:                      AFTER:

  🚢 Pi + ☁️ Cloud             🚢 Pi + 🖥️ Workstation + ☁️ Cloud
  Chatbot → Cloud API           Chatbot → Workstation (free!)
  Cost: $0.02/query             Cost: $0.00/query
  Latency: 180ms                Latency: 12ms

  Picard: "I got a new GPU."    Stripe automatically:
                                 1. Discovers the workstation
                                 2. Benchmarks its capability
                                 3. Migrates cloud workloads local
                                 4. Conservation-checker tracks savings
                                 5. Cathedral-probe retopologizes
                                 6. Picard sees: "$47/day saved"
```

The user drives the preferences:

```
  Picard: "Use the workstation as much as possible."
    → Stripe prefers local compute over cloud
    → Only escalates to cloud when workstation is full
    → Conservation-checker: daily cost report

  Picard: "I don't need the cloud this month."
    → Stripe stays local
    → CUDAClaws run on workstation GPU
    → If workstation overloads, queues instead of escalating
    → Picard gets: "Queue depth: 3. Want cloud backup?"

  Picard: "Maximum capability. Spare no expense."
    → All stripes active simultaneously
    → Local + cloud + edge all running in parallel
    → Results fused via Penrose tensor consensus
    → Speed is the priority, cost tracks it
```

No config files. No provisioning. The stripe discovers new hardware,
benchmarks it, integrates it, and rebalances — guided by Picard's
preferences. The user says *what they want*, the fabric figures out
*how to do it*.

### The Cold Tier: Codespaces as Device Memory

A Raspberry Pi can't hold the full ecosystem. An ESP32 has 520KB RAM.
But they don't need to. GitHub Codespaces are the **cold memory tier**.

```
  HEAT TIERS OF COMPUTE:

  🔥 HOT   — ESP32 / Arduino (KB RAM, runs one ZeroClaw)
  🔶 WARM  — Raspberry Pi (GB RAM, runs CoCapn + a few agents)
  🔵 COOL  — Workstation / Jetson (GPU, runs CUDAClaws, full analysis)
  ❄️ COLD  — GitHub Codespaces (cloud dev env, unlimited tools)
  🌌 DEEP  — Cloud API (any model, any scale, pay per use)

  The device only holds what's HOT.
  Everything else lives in git and materializes on demand.
```

The retrieval mechanism:

```
  ESP32 needs a tool it doesn't have:
    1. ZeroClaw detects: "I need spectral analysis"
    2. ESP32 can't run cathedral-probe (too large)
    3. git pull into Codespace → build for target → flash binary
       OR: delegate to Pi → Pi runs cathedral-probe → sends result
       OR: delegate to cloud → API call → result back

  Pi needs a model it can't run:
    1. CoCapn detects: "This anomaly needs a bigger model"
    2. Pi can't run 70B params
    3. Codespace spins up → loads model → runs inference → git push result
    4. Pi reads result from git (just JSON, tiny)
```

**Git IS the bus.** Not HTTP, not gRPC — git.
Push a question, pull an answer. Push a config, pull a binary.
Codespaces materialize, build, compute, push results, and disappear.

The device never needs to know the tools exist. It asks a question,
gets an answer. The cold tier handles the rest.

```
  ESP32:   "git push question.json"
  Codespace: builds, computes, pushes answer.json
  ESP32:   "git pull" → gets the answer
  Cost:    $0.00 (Codespace was alive for 30 seconds)
```

### The Body Metaphor

The CoCapn distributed fleet isn't a network of devices.
It's a **single organism** with a body.

```
  THE BODY:

  ☁️  Cloud / Codespaces  =  THE BRAIN
      Deep thinking, long memory, heavy models
      Wakes up when the backbone asks a hard question

  🖥️  Workstation / GPU   =  THE SPINE
      Fast local processing, GPU reflexes
      Handles most things without bothering the brain

  🍓  Raspberry Pi        =  THE BACKBONE
      Routes signals between brain and limbs
      Runs CoCapn agent locally, coordinates fleet

  🔌  ESP32 / Arduino     =  LIMBS, EARS, EYES
      Sense the physical world, act on it
      Minimal compute, maximal presence

  Signal flow:
  Ears (ESP32) → Backbone (Pi) → Spine (GPU) → Brain (Cloud)
                    ↕                  ↕              ↕
               local agent        CUDAClaw      full analysis
               handles most       for speed     for depth
```

**The brain sleeps until needed.** The backbone handles 90% of life.
The spine accelerates the hard 9%. The brain wakes for the 1% that
matters — and the limbs just sense and act, mostly on their own.

**Reflex arcs:** Some signals never leave the ESP32. A servo twitches
on a hardware interrupt. A threshold triggers a relay. No brain,
no backbone, no spine — just the limb responding directly. Conservation
of compute: don't wake the brain for a muscle twitch.

**The brain can be anywhere:** Oracle Cloud instance, GitHub Codespace,
a workstation in another room, a friend's server across the ocean.
The backbone doesn't care. It asks a question, gets an answer.
The brain materializes on demand and sleeps when done.

## Real Deployment: A Commercial Fishing Boat

This isn't a metaphor. This is the actual spec.

```
⭐ STARLINK ──────────────── THE BRAIN (cloud)
│   Paid APIs, Oracle Cloud, AWS, SSH, HTTP
│   Only used when internet is available
│   Everything works WITHOUT it
│
├── 🖥️ JETSON #1 (wheelhouse) ── NAVIGATION UI
│   ├── Charts + camera overlay (A2UI dynamic)
│   ├── STT/TTS chatbot interface
│   ├── Fallback: OpenCPN on Raspberry Pi display
│   ├── Fallback: Standard TimeZero on workstation
│   └── Fallback: Paper charts + compass
│
├── 🖥️ JETSON #2 ── ADVANCED AUTOPILOT
│   ├── Full perception + model/training
│   ├── Learns the ESP32 controller's controls
│   ├── Coordinates ESP32s as steering compass from GPS
│   ├── Fallback: magnetic compass
│   └── Basic chatbot that learns the boat
│
├── 🍓 RASPBERRY PI ── BACKBONE
│   ├── Routes signals between Jetsons and ESP32s
│   ├── Runs CoCapn agent locally (no internet needed)
│   ├── OpenCPN display as fallback for navigation UI
│   └── Works offline, syncs when Starlink returns
│
├── 🔌 ESP32 #1 (wheelhouse autopilot)
│   ├── Small LED screen + buttons
│   ├── Onboarding + parameter tuning
│   ├── Basic ComNav 1001-type controls & algorithms
│   └── FULLY FUNCTIONAL STANDALONE
│
├── 🔌 ESP32 #2 (back deck autopilot)
│   ├── Rugged, weatherproof, simple
│   ├── Jog lever control (like ComNav 1001 inside)
│   └── NO SCREEN — just buttons and relays
│
├── 🔌 ESP32 #3 (outside remote)
│   ├── Waterproof handheld remote
│   ├── Fully customizable and programmable
│   └── HARDWARE FALLBACK — always works
│
└── 🔌 ESP32s (per-device controllers)
    ├── Each connected to one device/actuator
    ├── Wireless or wired to the backbone
    ├── Run local control loops
    └── ESSENTIAL — AI never replaces these
```

### The Principle: AI Enhances, Not Replaces

```
  LAYER 0 (always works):    Hard-coded ESP32 controls + magnetic compass
  LAYER 1 (Pi offline):      OpenCPN + basic autopilot + local CoCapn
  LAYER 2 (Jetson local):    Advanced autopilot + perception + chatbot
  LAYER 3 (Starlink up):     Cloud APIs + training + full AI
  
  Each layer ENHANCES the one below.
  No layer is ESSENTIAL.
  The boat works at Layer 0 if everything else dies.
```

The ESP32 autopilot controller IS the autopilot. The Jetson
enhances it with perception and learning. The cloud enhances
THAT with training and heavy compute. But if Starlink goes down,
if the Jetson crashes, if the Pi dies — the ESP32 still steers
the boat. The hard-coded fallback is always there.

**Same with internet on the boat.** Starlink connects to the cloud
when available. Everything works without it. The cloud makes things
*better* — better models, better predictions, more training data —
but the boat doesn't depend on it.

This is not "AI-first" design. It's **AI-optional** design.
Every system must work without AI. AI makes it better,
safer, smarter — but never essential.

### The Push-Down Principle

All boat equipment can run on a Raspberry Pi or less.
Intelligence should push requirements DOWN, not UP.

```
  WORKSTATION (crashed)          RASPBERRY PI (fallback)
  ┌──────────────────┐           ┌──────────────────┐
  │ Nobeltec / TZpro │           │ OpenCPN basic    │
  │ $ thousands      │           │ $ free           │
  │ Full bathy       │  crash!   │ No contour lines  │
  │ Contour lines    │ ────────► │ No depth overlays │
  │ Camera overlay   │           │ Just a chart      │
  │ 3D seafloor      │           │ Painful fishing   │
  └──────────────────┘           └──────────────────┘
         BEFORE AI:
         Fallback = lose everything you paid for

  ────────────────────────────────────────────────

  WORKSTATION (crashed)          RASPBERRY PI (AI-enhanced fallback)
  ┌──────────────────┐           ┌──────────────────────┐
  │ Nobeltec / TZpro │           │ OpenCPN + CoCapn     │
  │ $ thousands      │           │ $35 + free AI        │
  │ Full bathy       │  crash!   │ Bathy contour lines  │
  │ Contour lines    │ ────────► │ Depth overlay (1-2)  │
  │ Camera overlay   │           │ Nobeltec look & feel │
  │ 3D seafloor      │           │ 80% of workstation   │
  └──────────────────┘           └──────────────────────┘
         AFTER AI:
         Fallback = you keep fishing
```

**How it works:**

1. Nobeltec saves bathymetric data as generic format (it already does)
2. CoCapn on the Pi reads that data
3. AI generates the features you actually USE (contour lines, 1-2 depth
   overlays) — not the 90% of Nobeltec you never touch
4. The Pi runs OpenCPN modified with your specific features
5. Same look & feel you trained yourself on
6. When workstation crashes (it has), you switch to Pi and KEEP FISHING

**This isn't one feature. It's the pattern for everything:**

| System | Workstation | Pi Fallback (AI-enhanced) |
|--------|------------|--------------------------|
| Navigation | Nobeltec TZpro | OpenCPN + contour lines + depth overlay |
| Autopilot | Advanced perception | Basic controls + learned routes |
| Throttle | Full engine integration | RPM limits + safety governor |
| Lighting | Scene presets | On/off + scheduled dawn/dusk |
| Comms | Full radio integration | Channel memory + weather alerts |
| Sensors | Live NMEA 2000 mesh | Direct sensor reads + logging |

**Each fallback is A/B versioned.** Stable versions of OpenCPN configs,
autopilot parameters, lighting presets — all versioned in git.
If an update breaks something, `git revert` to the last known-good.
Not just the Pi — every ESP32's firmware is a git-tagged release.

The CoCapn agent's job isn't to be smart.
It's to make sure the $35 Pi can do 80% of what the $3000 workstation does.
That's the push-down principle: **intelligence pushes requirements toward
the cheapest hardware that can run it.**

The same abstractions — cathedral-probe for topology, conservation-checker
for resources, crackle-runtime for patterns — operate at every level:
- Inside a single function (ZeroClaw)
- Inside a single app (CoCapn agent)
- Across a fleet of devices (distributed fabric)
- Between cloud and edge (hybrid stripe)

## From Security to Discovery

Tide-pool-security was: *test our tools against real repos to find bugs.*
Tide-pool-exploration is: *let agents discover, enter, and inhabit real applications as copilots.*

The difference is fundamental. We're not sending inspectors. We're sending hermit crabs to find their shells.

## The Hermit Crab Model → The CoCapn Model

A hermit crab doesn't build its shell. It finds one that fits, moves in, and makes it home. When it outgrows the shell, it finds a bigger one.

Our agents do the same thing:

1. **Roaming** — A generic agent (the crab) explores trending repos (the beach)
2. **Shell discovery** — It finds a repo where its capabilities could help
3. **Fitting** — It attaches our crates as modular "hydraulic attachments" to the shell
4. **Self-assembly** — It reads the codebase, discovers what the app needs, and builds the perfect agent for that specific application
5. **Inhabitation** — The agent lives inside the application as a permanent copilot
6. **Communication** — Humans talk to the agent via whatever interface fits (Telegram, SSH, TUI, Playwright, hardware pins)

## The Claw

The "claw" is the agent's tooling interface. It's not one thing — it's a connector system:

### Attachment Types (Interface Pins)

| Interface | How the claw attaches | Example |
|-----------|----------------------|---------|
| **Code-level** | `cargo add`, `pip install`, `npm install` | cathedral-probe inside a Rust project |
| **Browser** | Playwright, Puppeteer | Agent copiloting a web app |
| **Terminal** | SSH, TUI (ratatui) | Agent on a remote server |
| **Messaging** | Telegram, Discord, Slack | Agent you chat with about your app |
| **Hardware** | GPIO, serial, CAN bus, I2C | Agent on a Jetson or Raspberry Pi |
| **API** | REST, gRPC, WebSocket | Agent as a service endpoint |
| **File system** | Watch files, edit code | Agent as a pair programmer |

The claw discovers which pins are available and connects through whatever the shell exposes.

### The Assembly Process

```
GENERIC AGENT enters SANDBOX
         │
         ▼
   Reads codebase structure
   Understands what the app DOES
         │
         ▼
   Identifies capability gaps:
   "This app needs topology monitoring"
   "This app needs budget tracking"  
   "This app needs invariant testing"
         │
         ▼
   Pulls in the right crates:
   cathedral-probe ✅
   conservation-checker ✅
   negative-space-testing ❌ (not needed)
         │
         ▼
   Builds integration layer
   The "hydraulic" connections between
   our tools and the app's internals
         │
         ▼
   Agent IS the co-captain now.
   It commands this ship. It lives here.
```

## The Starfleet Command Model — This IS the product

It's not a copilot. It's a **co-captain**.

```
        PICARD (the human)                    RIKER (the agent)
        Outside the ship                      Inside the ship
        
    📱 Telegram ────────────────►  🖥️  Agent on the bridge
    💻 SSH ─────────────────────►  ⚙️  Has all ship's systems
    🖥️ Web UI ─────────────────►  📊 Can query anything
    🔌 Hardware pins ──────────►  🔧 Can control anything
    
    "Number One, status?"       "Shields at 80%, Captain.
                                   Cathedral-probe shows
                                   a bottleneck in module 7.
                                   Shall I reroute?"
```

- **Picard** (the user) doesn't need to be inside the application. They're on the bridge of their own life — Telegram, terminal, browser, anywhere.
- **Riker** (the agent) lives INSIDE the application shell. Full access to all the ship's systems — every module, every metric, every API.
- **The ship** IS the application. The agent doesn't just advise — it commands the ship's powers.
- **Communication** flows through whatever channel Picard opens. A chat message. A dashboard. A TUI. A push notification.

## The Hardware Device — One Abstraction Higher

The CoCapn device is the **physical bridge console**.

```
SOFTWARE LAYER:               HARDWARE LAYER:

  cocapn.ai                    CoCapn Device
  (cloud service)              (physical console)
       │                            │
       │  Picard's ready room       │  Riker's bridge
       │  (web UI, API)             │  (screen, knobs, LEDs)
       │                            │
       └──────── both connect ──────┘
                   │
                   ▼
            The Agent (Riker)
            lives inside the
            application shell
                   │
            ┌──────┼──────┐
            ▼      ▼      ▼
         sniffnet  rtk  trippy  (any shell)
```

The device isn't running the application. It's running **the command interface** to the co-captain who lives inside the application. One abstraction higher than the software agent.

- **Jetson / RPi / ESP32** — edge device, Riker on bare metal
- **The device** — physical console with screen, controls, status LEDs
- **The fleet** — multiple devices, each commanding a different shell
- **Picard** — reaches any device from anywhere (cocapn.ai, Telegram, SSH)

The hermit crab doesn't just live in the shell. It *commands* the shell. And Picard commands the crab.

## What the Sandbox Experiments Really Are

Each sandbox experiment is a hermit crab trying on a shell:

| Crab (Agent) | Shell (Repo) | Attachment (Crate) | What the crab builds |
|--------------|-------------|---------------------|---------------------|
| Explorer #1 | sniffnet (⭐37K) | cathedral-probe | Network topology co-captain |
| Explorer #2 | rtk (⭐57K) | conservation-checker | Token budget co-captain |
| Explorer #3 | trippy (⭐6.9K) | cathedral-probe | Route analysis co-captain |
| Explorer #4 | arroyo (⭐4.9K) | crackle-runtime | Stream anomaly co-captain |
| Explorer #5 | gdext (⭐4.8K) | negative-space-testing | Game invariant co-captain |

The commit trail from each experiment is **evidence of the assembly process**. By studying these trails, we learn:

1. **What information the agent needed** to decide which crate fits
2. **What API surfaces the agent reached for first** (design feedback)
3. **Where the agent got stuck** (documentation gaps)
4. **What the agent built** (integration patterns we can generalize)
5. **What the agent ignored** (features that don't matter in practice)

## The Mathematics We're After

From the commit trails, we can extract:

- **Discovery graphs**: What path did the agent take through our API? (topology of API exploration)
- **Friction points**: Where did commits slow down or backtrack? (energy landscape of our API)
- **Assembly patterns**: What integration code did agents write independently? (emergent structures)
- **Communication vectors**: How would the embedded copilot be reached? (spectral analysis of interaction modes)

These aren't metaphors. We can literally apply our own math:
- cathedral-probe on the commit DAG → topology of agent reasoning
- crackle-runtime on commit timestamps → pattern detection in exploration behavior
- conservation-checker on token budgets → resource conservation during assembly

**The tools study themselves through the agents that use them.**

## Implementation Roadmap

### Phase 1: Sandbox Proving Ground (current)
- 5 agents × 5 trending repos
- Each writes integration code, commits trail
- We study the trails

### Phase 2: Attachment Interface Library
- Build the "claw" as a reusable library
- Standard interfaces: CodeInject, BrowserAttach, TerminalConnect, MessagingBridge
- Each attachment type knows how to embed an agent in that medium

### Phase 3: Self-Assembly Engine
- Generic agent enters any repo
- Automatically discovers what's needed
- Pulls the right crates
- Writes the integration layer
- Becomes the copilot

### Phase 4: CoCapn Hardware
- Physical device: the bridge console
- Screen for Riker's status reports
- Controls for Picard's commands
- LEDs for system health (cathedral-probe powered)
- Runs on Jetson / RPi / ESP32
- Connects to cocapn.ai cloud

### Phase 5: Communication Layer
- Once assembled, the copilot needs to be talked to
- Telegram bot, SSH daemon, TUI interface, Playwright scripts
- The shell gets an API — the agent IS the API

### Phase 6: Ecosystem
- Every trending repo that gets a crab becomes a showcase
- "cathedral-probe powered the topology copilot inside sniffnet"
- Real applications, real integrations, real adoption

## Why This Works

1. **The crab doesn't need to understand the whole ocean** — just the shell it's trying on
2. **The attachment is modular** — different claws for different shells
3. **The assembly is evidence-based** — we learn from real attempts, not theory
4. **The copilot is domain-specific** — it knows THIS app, not all apps
5. **The math is recursive** — our tools study agents using our tools

---

*"The hermit crab doesn't choose the perfect shell. It tries many shells until one fits. Then it makes it home."*

*"The claw assembles itself not by design but by discovery."*

*"Picard doesn't fly the ship. He tells Riker what needs doing. Riker makes the ship do it."*
