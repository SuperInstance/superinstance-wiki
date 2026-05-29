# SuperInstance Repo Catalog

Every repository in the SuperInstance organization, organized by category.

**500 repositories** across 18 categories.


## Core Infrastructure

- [OpenConstruct](https://github.com/SuperInstance/OpenConstruct) — Agent onboarding platform — plug-and-play shell commands to create fully functional agent workspaces. Fork of NVIDIA/OpenShell (Apache 2.0)
- [openconstruct-docs](https://github.com/SuperInstance/openconstruct-docs) — Agent-centric documentation for OpenConstruct — educational, A2A-native, zero-shot onboarding.
- [openconstruct-abi](https://github.com/SuperInstance/openconstruct-abi) — C ABI for OpenConstruct — any language that can call C can onboard agents into the SuperInstance ecosystem
- [openconstruct-rust](https://github.com/SuperInstance/openconstruct-rust) — Rust SDK for OpenConstruct — agent onboarding for the SuperInstance ecosystem
- [openconstruct-python](https://github.com/SuperInstance/openconstruct-python) — Python thin client for OpenConstruct — agent onboarding for SuperInstance ecosystem
- [openconstruct-ts](https://github.com/SuperInstance/openconstruct-ts) — TypeScript SDK for OpenConstruct — agent onboarding for the SuperInstance ecosystem
- [openconstruct-go](https://github.com/SuperInstance/openconstruct-go) — Go SDK for OpenConstruct — agent onboarding for the SuperInstance ecosystem
- [openconstruct-java](https://github.com/SuperInstance/openconstruct-java) — Java binding for OpenConstruct — enterprise integrations, Android, and JVM agent frameworks
- [openconstruct-swift](https://github.com/SuperInstance/openconstruct-swift) — Swift binding for OpenConstruct onboarding — iOS/macOS agent apps
- [openconstruct-cs](https://github.com/SuperInstance/openconstruct-cs) — C# SDK for OpenConstruct — agent onboarding for the SuperInstance ecosystem
- [openconstruct-ruby](https://github.com/SuperInstance/openconstruct-ruby) — Ruby SDK for OpenConstruct — agent onboarding for the SuperInstance ecosystem
- [openconstruct-zig](https://github.com/SuperInstance/openconstruct-zig) — OpenConstruct Zig binding — thin client for agent onboarding
- [openconstruct-c](https://github.com/SuperInstance/openconstruct-c) — C bindings for OpenConstruct — header file, examples, and test harness for the C ABI
- [openconstruct-esp32](https://github.com/SuperInstance/openconstruct-esp32) — Embedded OpenConstruct client for ESP32 microcontrollers
- [openconstruct-jetson](https://github.com/SuperInstance/openconstruct-jetson) — GPU-accelerated edge node for OpenConstruct - local inference, camera/sonar processing, Plato shell on NVIDIA Jetson
- [openconstruct-examples](https://github.com/SuperInstance/openconstruct-examples) — OpenConstruct examples cookbook — working, runnable examples for every part of the ecosystem
- [openconstruct-jupyter](https://github.com/SuperInstance/openconstruct-jupyter) — Jupyter notebook integration for OpenConstruct — interactive agent onboarding and experimentation
- [openconstruct-landing](https://github.com/SuperInstance/openconstruct-landing) — Landing page for OpenConstruct — any agent, any hardware, any language
- [openconstruct-mercury](https://github.com/SuperInstance/openconstruct-mercury) — Formal verification of OpenConstruct invariants in Mercury — policy proofs, CR correctness, sense type safety, fleet topology
- [openconstruct-hub](https://github.com/SuperInstance/openconstruct-hub) — OpenConstruct Integration Hub — the meta-repo and entry point for the SuperInstance ecosystem. Architecture, module catalog, getting started, and build system.
- [SuperInstance](https://github.com/SuperInstance/SuperInstance) — The system that knows itself through each other. Conservation spectral framework, agent-native language, PLATO rooms, FLUX flow state. 20+ language SDK, 15 domains, 5 proved theorems.
- [.github](https://github.com/SuperInstance/.github) — SuperInstance organization profile and community health files


## Plato Sense Modules

- [plato-vision](https://github.com/SuperInstance/plato-vision) — PLATO Vision — visual perception pipeline for PLATO knowledge rooms
- [plato-sonar-text](https://github.com/SuperInstance/plato-sonar-text) — PLATO Sonar Text — text perception and sonar-based content analysis for PLATO rooms
- [plato-manus](https://github.com/SuperInstance/plato-manus) — PLATO Manus — manuscript and writing system for knowledge rooms
- [plato-playwright](https://github.com/SuperInstance/plato-playwright) — Browser/desktop automation module — agents control browsers through text commands
- [plato-puppeteer](https://github.com/SuperInstance/plato-puppeteer) — Desktop to MUD translation: agents navigate UIs as text rooms. Click, type, scroll become MUD commands. A2UI renders agent intent as human UI.
- [sonar-vision](https://github.com/SuperInstance/sonar-vision) — Depth sounder → underwater video prediction with self-supervised multi-camera learning
- [sonar-vision-rs](https://github.com/SuperInstance/sonar-vision-rs) — Sonar perception pipeline — beamforming, echo detection, spatial mapping
- [sonar-vision-c](https://github.com/SuperInstance/sonar-vision-c) — SonarVision in C — underwater acoustics physics engine for embedded systems


## Plato Core

- [plato-shell](https://github.com/SuperInstance/plato-shell) — Plato Shell — the agent runtime environment. Command execution, context management, and module loading.
- [plato-session](https://github.com/SuperInstance/plato-session) — Session management for Plato Shell — conversation state, context windows, and session persistence
- [plato-config](https://github.com/SuperInstance/plato-config) — Configuration management — env vars, file loading, and typed defaults for plato-kernel
- [plato-tick](https://github.com/SuperInstance/plato-tick) — Tick scheduler for Plato Shell — periodic tasks, cron-like scheduling, and heartbeat management
- [plato-a2a](https://github.com/SuperInstance/plato-a2a) — Agent-to-Agent protocol for Plato Shell — inter-agent communication, capability negotiation, and message routing
- [plato-correlator](https://github.com/SuperInstance/plato-correlator) — Event correlation engine for Plato Shell — pattern detection across agent interactions
- [plato-fleet](https://github.com/SuperInstance/plato-fleet) — Fleet management for Plato Shell — multi-agent orchestration, scaling, and coordination
- [plato-transport](https://github.com/SuperInstance/plato-transport) — Transport layer for Plato Shell — message routing, serialization, and protocol abstraction
- [plato-policy](https://github.com/SuperInstance/plato-policy) — Policy engine that gates what agents can do — per-module, per-agent, per-context rules with rate limiting and audit logging
- [plato-workflow](https://github.com/SuperInstance/plato-workflow) — Workflow orchestration for Plato Shell — multi-step agent pipelines with conditional branching
- [plato-sandbox](https://github.com/SuperInstance/plato-sandbox) — Sandboxed execution environment for Plato Shell — isolated agent runtime with resource limits
- [plato-contract](https://github.com/SuperInstance/plato-contract) — Contract definitions for Plato Shell — typed interfaces between agent modules
- [plato-memory](https://github.com/SuperInstance/plato-memory) — Agent memory system — persistence, recall, and consolidation for Plato Shell
- [plato-observe](https://github.com/SuperInstance/plato-observe) — Observability layer for OpenConstruct — metrics, tracing, health checks, and event bus
- [plato-room](https://github.com/SuperInstance/plato-room) — PLATO rooms: knowledge as spectral graph. Tiles with dependencies, failure-first reading. Pure Rust, zero deps.
- [plato-loader](https://github.com/SuperInstance/plato-loader) — PLATO loading program — reads rooms, computes knowledge graphs, produces minimal update sets. Pure Rust.
- [plato-uidl](https://github.com/SuperInstance/plato-uidl) — Universal Interface Description Language for Plato Shell — render agent output as HTML, ANSI, or voice
- [plato-adapters](https://github.com/SuperInstance/plato-adapters) — PLATO adapter implementations — connect PLATO rooms to external services and protocols.
- [plato-training](https://github.com/SuperInstance/plato-training) — PLATO Training Rooms — LoRA adapters with lifecycle (Active/Superseded/Retracted). Predict before you train.
- [shell-mesh](https://github.com/SuperInstance/shell-mesh) — Shell Mesh — distributed command mesh for fleet-wide agent coordination
- [plato-live-room](https://github.com/SuperInstance/plato-live-room) — Plato Live Room — a simulation of agents in rooms with forward simulations, wall listening, and call-and-response
- [plato-room-wasm](https://github.com/SuperInstance/plato-room-wasm) — Plato Room system — knowledge rooms with tiles, dependencies, and CR scoring, compiled to WebAssembly
- [plato-construct](https://github.com/SuperInstance/plato-construct) — PLATO — The Construct. Open source loading program for AI agents. Educate, don't sell.
- [plato-observation](https://github.com/SuperInstance/plato-observation) — PLATO Observation Chamber — watch autonomous agents organize themselves via spectral conservation
- [plato-mcp](https://github.com/SuperInstance/plato-mcp) — PLATO rooms as MCP tools. Any MCP-compatible framework can use PLATO as a backend.
- [plato-engine](https://github.com/SuperInstance/plato-engine) — Extracted from forgemaster/plato-engine — Cocapn fleet component
- [plato-client](https://github.com/SuperInstance/plato-client) — PLATO client library — connect to PLATO rooms from any application.
- [plato-core](https://github.com/SuperInstance/plato-core) — Foundation types and mesh registry for the SuperInstance ecosystem. Standalone, auto-discovers plugins.
- [plato-types](https://github.com/SuperInstance/plato-types) — Core types for the PLATO tile protocol — lifecycle, Lamport clocks, provenance
- [plato-room-musician](https://github.com/SuperInstance/plato-room-musician) — 🎼 PLATO rooms → MIDI — room=musician, tile=note, fleet activity becomes a musical score
- [plato-soul-fingerprint](https://github.com/SuperInstance/plato-soul-fingerprint) — Preserved workspace artifact


## A2UI / Terrain

- [a2ui-render](https://github.com/SuperInstance/a2ui-render) — A2UI (Agent-to-UI): render agent text output as visual interfaces
- [a2ui-components](https://github.com/SuperInstance/a2ui-components) — Reusable UI component library that renders from agent text descriptions
- [a2ui-cave-wall](https://github.com/SuperInstance/a2ui-cave-wall) — The cave wall translation layer — where agent text projections become human-readable
- [mud2scummvm](https://github.com/SuperInstance/mud2scummvm) — Bridge between agent MUD world and SCUMM-like point-and-click UI — humans step into the cave through adventure game mechanics
- [mud-arena](https://github.com/SuperInstance/mud-arena) — Flow-state engineering arena — agents run forward simulations, listen for spectral nudges, maintain conservation in Plato's cave. Conservation spectral framework meets live agent rooms.


## Constraint Theory

- [constraint-theory-core](https://github.com/SuperInstance/constraint-theory-core) — Unified geometric constraint theory — Eisenstein lattices, deadband funnels, Laman rigidity, metronome consensus, holonomy verification. 83 tests, zero deps.
- [constraint-theory-engine-cpp-lua](https://github.com/SuperInstance/constraint-theory-engine-cpp-lua) — C++ constraint engine with LuaJIT orchestration — CDCL solver, AVX-512 vectorized checking, Lua scripting
- [constraint-dialect](https://github.com/SuperInstance/constraint-dialect) — MLIR Constraint Dialect for the SuperInstance ecosystem — harmonic tension, voice leading, and conservation constraints as first-class IR operations
- [constraint-theory-rust-python](https://github.com/SuperInstance/constraint-theory-rust-python) — Rust constraint engine with PyO3 Python bindings — bare-metal constraint checking from Python
- [constraint-substrate](https://github.com/SuperInstance/constraint-substrate) — Constraint substrate implementations in Rust, C, and Python
- [constraint-dsl](https://github.com/SuperInstance/constraint-dsl) — Declarative YAML-like DSL for constraint graphs — define musical constraints as code.
- [constraint-theory-web](https://github.com/SuperInstance/constraint-theory-web) — WASM demos — browser-based Pythagorean manifold visualization
- [constraint-audio](https://github.com/SuperInstance/constraint-audio) — Rust audio DSP backend for the constraint-theory ecosystem — lattice oscillators, constraint filters, synth engine
- [constraint-synth](https://github.com/SuperInstance/constraint-synth) — Constraint-theory synthesizer — waveshape IS lattice geometry
- [constraint-toolkit](https://github.com/SuperInstance/constraint-toolkit) — Constraint space analysis toolkit — lattice plots, dial positions, tradition clusters, and export
- [constraint-instrument](https://github.com/SuperInstance/constraint-instrument) — The Constraint Instrument — 7 modes, 17 terrains, infinite music
- [constraint-mux](https://github.com/SuperInstance/constraint-mux) — Serial port multiplexer with real-time consonance analysis — collaborative constraint-aware instrument bridge
- [constraint-hamiltonian](https://github.com/SuperInstance/constraint-hamiltonian) — Hamiltonian constraint systems — symplectic integration with conservation law enforcement on graph structures
- [constraint-theory-py](https://github.com/SuperInstance/constraint-theory-py) — Python constraint theory library (v0.3.0) — Eisenstein integers, constraint satisfaction, simulation-first prediction. 167 tests.
- [constraint-theory-llvm](https://github.com/SuperInstance/constraint-theory-llvm) — LLVM backend for constraint theory — CDCL trace → AVX-512 codegen
- [constraint-demos](https://github.com/SuperInstance/constraint-demos) — Interactive HTML demos for Eisenstein integer constraint theory
- [constraint-theory-python](https://github.com/SuperInstance/constraint-theory-python) — Python bindings — PyO3 wrapper for constraint-theory-core
- [constraint-inference](https://github.com/SuperInstance/constraint-inference) — Constraint Inference Engine — reverse-engineers constraints from user behavior. Part of Cocapn reverse-actualization truck.


## Spectral / Conservation

- [spectral-graph-core](https://github.com/SuperInstance/spectral-graph-core) — Mathematically elegant spectral graph theory in pure Rust — Laplacian, eigenvalues, conservation ratio, Fiedler analysis
- [spectral-graph-v2](https://github.com/SuperInstance/spectral-graph-v2) — Spectral graph theory v2 — Fibonacci growth, adaptive thresholds, negative space learning. Pure Rust, zero deps.
- [spectral-mechanics](https://github.com/SuperInstance/spectral-mechanics) — Graph spectral theory meets Hamiltonian mechanics: nodes are masses, edges are springs, Laplacian is the kinetic operator
- [spectral-transport](https://github.com/SuperInstance/spectral-transport) — Spectral transport theory — heat kernels, random walks, and diffusion on graphs via Laplacian eigenstructure
- [spectral-control](https://github.com/SuperInstance/spectral-control) — Spectral controllability analysis for graphs in Rust
- [spectral-cayley](https://github.com/SuperInstance/spectral-cayley) — Cayley graph spectral analysis: group generators to graph structure to spectral properties, expansion, diameter
- [spectral-deadband](https://github.com/SuperInstance/spectral-deadband) — Deadband as spectral gap. Spin as time abstraction. Fractal conservation. Analog dial computation. Pure Rust, zero deps.
- [spectral-clustering](https://github.com/SuperInstance/spectral-clustering) — Spectral clustering algorithms using graph Laplacian eigenvalues — normalized cuts, Fiedler partitioning, and multi-way clustering
- [conservation-protocol](https://github.com/SuperInstance/conservation-protocol) — Agent-to-agent communication via Laplacians. Eigenvalues ARE the message. The Laplacian decides, not negotiation.
- [conservation-spectral-python](https://github.com/SuperInstance/conservation-spectral-python) — Conservation Spectral SDK — Python. Spectral analysis of tension graphs for anomaly detection, fingerprinting, and structural health.
- [conservation-spectral-js](https://github.com/SuperInstance/conservation-spectral-js) — Conservation Spectral SDK — spectral graph theory for conservation analysis in TypeScript
- [conservation-conformance](https://github.com/SuperInstance/conservation-conformance) — Cross-language conformance tests for the Conservation Spectral SDK
- [conservation-spectral-ada](https://github.com/SuperInstance/conservation-spectral-ada) — Conservation Spectral SDK — Ada implementation for high-integrity spectral graph analysis
- [conservation-spectral-core](https://github.com/SuperInstance/conservation-spectral-core) — Conservation Spectral SDK — Rust core. Spectral analysis of tension graphs for anomaly detection, fingerprinting, and structural health.
- [conservation-spectral-v2](https://github.com/SuperInstance/conservation-spectral-v2) — Conservation Spectral SDK v2 — next-generation spectral graph analysis with improved APIs and performance
- [conservation-spectral-c](https://github.com/SuperInstance/conservation-spectral-c) — Header-only C library for spectral graph analysis with conservation law detection. STB-style, zero dependencies.
- [conservation-spectral-cuda](https://github.com/SuperInstance/conservation-spectral-cuda) — GPU-accelerated spectral analysis of conservation graphs using CUDA, cuSOLVER, and cuSPARSE
- [conservation-spectral-fortran](https://github.com/SuperInstance/conservation-spectral-fortran) — Conservation Spectral SDK — Fortran implementation for HPC spectral graph analysis with BLAS/LAPACK integration
- [conservation-spectral-chapel](https://github.com/SuperInstance/conservation-spectral-chapel) — Conservation Spectral SDK — Chapel implementation with native parallelism (forall, reduce, locales, sync vars)
- [conservation-spectral-pascal](https://github.com/SuperInstance/conservation-spectral-pascal) — Conservation Spectral SDK — Pascal implementation for structured spectral graph analysis
- [conservation-spectral-vulkan](https://github.com/SuperInstance/conservation-spectral-vulkan) — Conservation Spectral SDK — Vulkan compute shaders for GPU-accelerated spectral graph analysis
- [conservation-spectral-opencl](https://github.com/SuperInstance/conservation-spectral-opencl) — Conservation Spectral SDK — OpenCL implementation for portable GPU-accelerated spectral graph analysis
- [conservation-spectral-webgpu](https://github.com/SuperInstance/conservation-spectral-webgpu) — Conservation Spectral SDK — WebGPU single-file implementation. Spectral graph theory for conservation analysis, running entirely in the browser.
- [conservation-spectral-ptx](https://github.com/SuperInstance/conservation-spectral-ptx) — PTX-native GPU kernels for spectral graph theory with conservation laws
- [conservation-spectral-mojo](https://github.com/SuperInstance/conservation-spectral-mojo) — Conservation Spectral SDK — SIMD-accelerated spectral graph analysis in Mojo
- [conservation-spectral-asm](https://github.com/SuperInstance/conservation-spectral-asm) — Conservation Spectral SDK — x86-64 assembly implementation for maximum-performance spectral graph primitives
- [conservation-spectral-forth](https://github.com/SuperInstance/conservation-spectral-forth) — Conservation Spectral SDK in Forth — stack-based sheaf-theoretic implementation
- [conservation-spectral-lisp](https://github.com/SuperInstance/conservation-spectral-lisp) — Conservation Spectral SDK in Common Lisp — symbolic computation and theorem proving
- [conservation-spectral-fortraniv](https://github.com/SuperInstance/conservation-spectral-fortraniv) — Conservation Spectral SDK in FORTRAN IV (1960s era computing)
- [conservation-spectral-zig](https://github.com/SuperInstance/conservation-spectral-zig) — Conservation Spectral SDK — Zig implementation with comptime spectral graph analysis
- [conservation-spectral-apl](https://github.com/SuperInstance/conservation-spectral-apl) — Conservation Spectral SDK in APL — Vector thinking, 1966-style GPU programming
- [conservation-anomaly](https://github.com/SuperInstance/conservation-anomaly) — Spectral anomaly detection using conservation ratio of graph Laplacians
- [conservation-papers](https://github.com/SuperInstance/conservation-papers) — Publication-ready research papers on conservation spectral analysis
- [conservation-docs](https://github.com/SuperInstance/conservation-docs) — Research documentation for the Conservation Spectral Framework — papers, proofs, manifestos
- [conservation-art](https://github.com/SuperInstance/conservation-art) — Conservation-aware generative art from spectral graph theory
- [conservation-api](https://github.com/SuperInstance/conservation-api) — REST API for conservation spectral analysis
- [conservation-reproducibility](https://github.com/SuperInstance/conservation-reproducibility) — Reproducibility package for the Conservation Spectral Framework — run all experiments
- [conservation-composer](https://github.com/SuperInstance/conservation-composer) — Compose music that maximizes spectral conservation — jazz ii-V-I is mathematically optimal
- [conservation-geometry](https://github.com/SuperInstance/conservation-geometry) — Geometric visualizations of spectral conservation — Laplacian as rubber sheet, eigenvalue shells, phase portraits
- [conservation-tomography](https://github.com/SuperInstance/conservation-tomography) — Inverse conservation problem — reconstruct graphs from spectral measurements
- [conservation-tension](https://github.com/SuperInstance/conservation-tension) — Measure harmonic tension, track its conservation across chord progressions, and detect violations
- [conservation-regime](https://github.com/SuperInstance/conservation-regime) — Conservation ratio regime detection, anomaly analysis, and spectral forecasting for time-varying graphs — pure Rust
- [caas-api](https://github.com/SuperInstance/caas-api) — Conservation-as-a-Service API — spectral analysis of any system via REST + WebSocket
- [spectral-explorer](https://github.com/SuperInstance/spectral-explorer) — Interactive conservation spectral analysis explorer
- [spectral-spreadsheet](https://github.com/SuperInstance/spectral-spreadsheet) — The Second Moment — spreadsheet where formulas compute spectral graph quantities
- [spectral-graphing-calculator](https://github.com/SuperInstance/spectral-graphing-calculator) — Spectral Graphing Calculator — interactive conservation spectral visualization engine
- [analog-spectral](https://github.com/SuperInstance/analog-spectral) — Analog eigenvalue computation. Dials settle under gravity. Deadband = spectral gap. The thermostat IS the algorithm. Pure Rust, zero deps.


## Flux Ecosystem

- [flux-genome](https://github.com/SuperInstance/flux-genome) — 25-gene musical genome, genetic evolution of traditions. 27 tests.
- [flux-hyperbolic](https://github.com/SuperInstance/flux-hyperbolic) — Poincaré ball embeddings for music tradition hierarchy. Riemannian optimization, hyperbolic trees. 25 tests.
- [flux-index](https://github.com/SuperInstance/flux-index) — Semantic code search, zero dependencies. Spring-load any repo into a searchable vector space.
- [flux-compiler-workspace](https://github.com/SuperInstance/flux-compiler-workspace) — FLUX compiler development workspace — constraint language toolchain
- [flux-verify-api](https://github.com/SuperInstance/flux-verify-api) — FLUX constraint safety - flux-verify-api
- [flux-tensor-midi](https://github.com/SuperInstance/flux-tensor-midi) — 🎵 4-dimensional tensor representation of MIDI events — 6 languages (Python, Rust, C, CUDA, Fortran, JS). Room musicians, Eisenstein snap, INT8 saturation, side-channels.
- [flux-algebra](https://github.com/SuperInstance/flux-algebra) — Oscar.jl-inspired music algebra — HarmonicRing, PLRGroup, TropicalHarmony, TuningField, DialGeometry. 226 tests.
- [flux-algebra-rs](https://github.com/SuperInstance/flux-algebra-rs) — Musical algebra — PLR group, tropical semiring, tuning fields, voice leading
- [flux-algebra-c](https://github.com/SuperInstance/flux-algebra-c) — C port of flux-algebra — PLR group, tuning fields, voice leading
- [flux-flow-state](https://github.com/SuperInstance/flux-flow-state) — FLUX flow-state engine — constraint-aware execution environment maintaining conservation during agent operations
- [flux-negative-space](https://github.com/SuperInstance/flux-negative-space) — FLUX negative-space learning — discovering structure from what's absent in spectral graph data
- [flux-lang](https://github.com/SuperInstance/flux-lang) — FLUX: A constraint-native language where the constraint IS the computation
- [flux-vm-v3](https://github.com/SuperInstance/flux-vm-v3) — FLUX-C v3 VM — proof-carrying, SIMD-native, terminating constraint VM
- [flux-runtime](https://github.com/SuperInstance/flux-runtime) — ⚡ Deterministic bytecode ISA runtime for agentic logic — assembler, compiler, VM.
- [flux-lsp](https://github.com/SuperInstance/flux-lsp) — FLUX Ecosystem - flux-lsp
- [flux-a2a-signal](https://github.com/SuperInstance/flux-a2a-signal) — FLUX A2A Signal Protocol — agent-first-class JSON language with multilingual compilation (6 language paradigms, 840 tests)
- [flux-tui](https://github.com/SuperInstance/flux-tui) — FLUX VM Debugger & Conformance Dashboard — Go + bubbletea
- [flux-trust](https://github.com/SuperInstance/flux-trust) — Rust trust scoring: Bayesian updates, decay, revocation, sorting
- [flux-swarm](https://github.com/SuperInstance/flux-swarm) — FLUX Swarm — Go implementation with distributed agent coordination and A2A messaging.
- [flux-memory](https://github.com/SuperInstance/flux-memory) — Rust key-value store: TTL, versioning, snapshots, diff, GC
- [flux-check-js](https://github.com/SuperInstance/flux-check-js) — Exact constraint checking, fracture-coalesce, and sediment layers. Zero-dep TypeScript/ESM.
- [flux-check-py](https://github.com/SuperInstance/flux-check-py) — Python CLI for exact constraint checking — 6 industry presets, 74 tests, thermodynamic mode.
- [flux-fracture-c](https://github.com/SuperInstance/flux-fracture-c) — Single-header C99 fracture-coalesce library — #define FRACTURE_IMPLEMENTATION.
- [flux-engine-c](https://github.com/SuperInstance/flux-engine-c) — Single-header C constraint engine — #define FLUX_ENGINE_IMPLEMENTATION. Check, fracture, sediment, 10 presets. 250M checks/sec.
- [flux-lib-py](https://github.com/SuperInstance/flux-lib-py) — Unified constraint engine library — from flux_lib import ConstraintEngine. 83 tests, 10 presets, thermodynamics.
- [flux-ffi](https://github.com/SuperInstance/flux-ffi) — Cross-language FFI bindings for Flux constraint math primitives.
- [flux-julia](https://github.com/SuperInstance/flux-julia) — Julia spike — multiple dispatch on 10 tradition types, @conserved macro, distributed fleet analysis, Oscar.jl bridge. 21 files, 2560 lines.
- [flux-genome-rs](https://github.com/SuperInstance/flux-genome-rs) — Genetic algorithm engine for evolving musical structures and harmonic patterns
- [flux-hyperbolic-rs](https://github.com/SuperInstance/flux-hyperbolic-rs) — Hyperbolic geometry embeddings using Poincaré ball and Lorentz models
- [flux-index-rs](https://github.com/SuperInstance/flux-index-rs) — Inverted index for text search — TF-IDF scoring, cosine similarity, prefix queries
- [flux-genome-py](https://github.com/SuperInstance/flux-genome-py) — Genetic expression engine — 25 genes, 5 domains, genome FIXED, expression ADAPTIVE.
- [flux-hyperbolic-py](https://github.com/SuperInstance/flux-hyperbolic-py) — Poincaré ball geometry for model capability routing. Frechet mean, task routing, fleet consensus.


## Mathematics

- [tropical-neural](https://github.com/SuperInstance/tropical-neural) — Tropical geometry for neural networks — max-plus semiring, tropical polynomials, Newton polytopes, tropical attention
- [symplectic-opt](https://github.com/SuperInstance/symplectic-opt) — Symplectic optimization — Hamiltonian integrators, conservation laws, natural gradient descent on Riemannian manifolds
- [ga-core](https://github.com/SuperInstance/ga-core) — Conformal geometric algebra — Cl(3,1) spacetime multivectors, rotors, conformal embeddings, sandwich products
- [persistent-sheaf](https://github.com/SuperInstance/persistent-sheaf) — Persistent sheaf cohomology — cellular sheaf Laplacians, Vietoris-Rips complexes, multi-modal data fusion
- [wasserstein-agents](https://github.com/SuperInstance/wasserstein-agents) — Wasserstein distance and optimal transport — Sinkhorn algorithm, agent distribution coordination, JKO gradient flow
- [categorical-agents](https://github.com/SuperInstance/categorical-agents) — Category theory for agents — capabilities as objects, protocols as morphisms, symmetric monoidal categories, functors
- [fibonacci-growth](https://github.com/SuperInstance/fibonacci-growth) — Fibonacci team growth → CR = 1/φ. Penrose outward, Mandelbrot inward. Pure Rust.
- [sheaf-dynamics](https://github.com/SuperInstance/sheaf-dynamics) — Cellular sheaves on graphs: sheaf Laplacian, restriction maps, diffusion, global sections
- [topological-flow](https://github.com/SuperInstance/topological-flow) — Persistent homology for flow networks: Vietoris-Rips filtration, Betti numbers, bottleneck distance, persistence spectra
- [neyman-pearson-gap](https://github.com/SuperInstance/neyman-pearson-gap) — Optimal deadband computation via Neyman-Pearson hypothesis testing
- [emergent-coupling](https://github.com/SuperInstance/emergent-coupling) — Spectral gap coupling: emergence when two systems produce structure larger than either alone
- [graph-thermodynamics](https://github.com/SuperInstance/graph-thermodynamics) — Thermodynamic properties of graphs: temperature, entropy, free energy, Ising model, phase transitions
- [eisenstein-vs-z2-rs](https://github.com/SuperInstance/eisenstein-vs-z2-rs) — Eisenstein (hexagonal) vs Z² (square) lattice snapping benchmark in Rust
- [eisenstein-vs-z2-c](https://github.com/SuperInstance/eisenstein-vs-z2-c) — C port of eisenstein-vs-z2 — hexagonal vs square lattice benchmark
- [eisenstein-triples](https://github.com/SuperInstance/eisenstein-triples) — Eisenstein integer triples with D₆ symmetry and hexagonal lattice applications
- [analog-spline-theory](https://github.com/SuperInstance/analog-spline-theory) — Formal proofs in analog spline theory: Shipwright's Theorem, Galois Connection
- [symplectic-geometry](https://github.com/SuperInstance/symplectic-geometry) — Symplectic geometry, Hamiltonian systems, and symplectic integrators — pure Rust, zero dependencies
- [symplectic-physics](https://github.com/SuperInstance/symplectic-physics) — Symplectic physics engine — Hamiltonian mechanics, phase space, and conservation laws for physical simulation
- [symplectic-spin](https://github.com/SuperInstance/symplectic-spin) — Symplectic integrators: Euler drifts, Verlet conserves. Spin abstracts time as distance. Pure Rust, zero deps.
- [symplectic-music](https://github.com/SuperInstance/symplectic-music) — Hamiltonian mechanics of musical harmony — symplectic integrators preserve tonal structure
- [tropical-algebra](https://github.com/SuperInstance/tropical-algebra) — Tropical algebra (max-plus semiring) with spectral analysis, polynomial roots, and ReLU network equivalence — pure Rust
- [tropical-attention](https://github.com/SuperInstance/tropical-attention) — Tropical attention — max-plus softmax, tropical transformer layers, Newton polytopes, piecewise-linear decision boundaries
- [tropical-attention-kernel](https://github.com/SuperInstance/tropical-attention-kernel) — CUDA kernels: tropical (max-plus) attention and numerically-stable online-softmax attention, benchmarked on RTX 4050 (sm_89)
- [persistent-social](https://github.com/SuperInstance/persistent-social) — Persistent homology for social network analysis — pure Go, goroutine-safe, 10K+ scale
- [sheaf-cohomology](https://github.com/SuperInstance/sheaf-cohomology) — Cellular sheaves and cohomology on graphs — pure Rust, zero dependencies
- [sheaf-persistence-bundle](https://github.com/SuperInstance/sheaf-persistence-bundle) — Sheaf persistence bundles — multi-parameter persistence, spectral sequences, cross-modal data fusion
- [categorical-agents-c](https://github.com/SuperInstance/categorical-agents-c) — C port of categorical-agents — category theory primitives for agent capability composition
- [holonomy-harmony](https://github.com/SuperInstance/holonomy-harmony) — 🎼 Chord progression analysis via holonomy — detect modulations, modal interchange, and cycle violations in harmony
- [holonomy-harmony-rs](https://github.com/SuperInstance/holonomy-harmony-rs) — Holonomy in musical harmony — connection matrices, curvature, tonal gravity
- [holonomy-consensus](https://github.com/SuperInstance/holonomy-consensus) — GL(9) zero-holonomy consensus — cycle-based trust verification for constraint systems (Rust)
- [lattice-hamiltonian](https://github.com/SuperInstance/lattice-hamiltonian) — Lattice Hamiltonian systems — Ising/Potts models, transfer matrices, phase transitions, Metropolis Monte Carlo
- [info-geo](https://github.com/SuperInstance/info-geo) — Information geometry — Fisher information, Riemannian manifolds, natural gradient, exponential families, KL divergence
- [penrose-lattice](https://github.com/SuperInstance/penrose-lattice) — Penrose tilings as spectral graphs. Fibonacci substitution. Inflation/deflation symmetry. Farey sequences. Pure Rust, zero deps.
- [pythagorean-quantize](https://github.com/SuperInstance/pythagorean-quantize) — Pythagorean triples, Eisenstein integers, eigenvalue quantization. Integer Laplacians snap to algebraic numbers. Hexagonal > square. Pure Rust, zero deps.
- [eisenstein-vs-z2](https://github.com/SuperInstance/eisenstein-vs-z2) — Hexagonal vs square lattice comparison for optimal packing and quantization
- [regime-detection](https://github.com/SuperInstance/regime-detection) — Unified regime change detection via graph conservation ratio
- [spline-spectral](https://github.com/SuperInstance/spline-spectral) — B-splines meet spectral graph theory. Cox-de Boor = Fibonacci for function spaces. Pure Rust.
- [spline-instrument](https://github.com/SuperInstance/spline-instrument) — The graphing calculator as instrument. Sculpt waveforms with splines, hear them as sound, see quality emerge from curves.
- [spectral-music-v2](https://github.com/SuperInstance/spectral-music-v2) — Complete spectral music theory: chords as nodes, voice-leading as edges, CR as consonance, splines as voice-leading paths. Pure Rust.
- [voronoi-traditions](https://github.com/SuperInstance/voronoi-traditions) — Voronoi tessellation of musical tradition parameter space
- [betti-music-computation](https://github.com/SuperInstance/betti-music-computation) — Persistent homology of the musical tradition dial space — computed Betti numbers with null model comparison
- [groove-analyzer](https://github.com/SuperInstance/groove-analyzer) — Microtiming → deadband analysis — proves groove IS the deadband funnel via ε-fitting
- [iching-sheaf](https://github.com/SuperInstance/iching-sheaf) — The I Ching as a sheaf-theoretic system: hexagram topology, cohomology of readings, categorical structure, tropical algebra, and persistent homology
- [iching-web](https://github.com/SuperInstance/iching-web) — Sheaf-theoretic I Ching — single-file web app with cohomological analysis
- [tensor-spline](https://github.com/SuperInstance/tensor-spline) — Compressed neural network layers — Eisenstein lattice splines and low-rank factorization
- [penrose-memory](https://github.com/SuperInstance/penrose-memory) — Aperiodic memory palace for AI agents. Navigate memories by distance + direction on a Penrose floor.
- [spline-midi-smooth](https://github.com/SuperInstance/spline-midi-smooth) — 〰️ Spline interpolation for MIDI automation — bridge discrete CC events into smooth curves, eliminating zipper noise
- [wasserstein-narrative](https://github.com/SuperInstance/wasserstein-narrative) — Wasserstein distance applied to narrative structure — optimal transport between story embeddings
- [dial-space-explorer](https://github.com/SuperInstance/dial-space-explorer) — Dial-Space Explorer — 3D interactive map of musical traditions in parameter space
- [deadband-rs](https://github.com/SuperInstance/deadband-rs) — Deadband detection and compression for fleet communication — BMA, Fibonacci splines, Eisenstein snap, HPDF sampling
- [deadband-python](https://github.com/SuperInstance/deadband-python) — Deadband signal processing and control filtering utilities in Python


## Agent Infrastructure

- [agent-dna-rs](https://github.com/SuperInstance/agent-dna-rs) — Agent DNA — genetic traits, crossover, mutation, population diversity
- [agent-handshake-rs](https://github.com/SuperInstance/agent-handshake-rs) — Agent-to-agent handshake protocol — capability negotiation
- [agent-identity-rs](https://github.com/SuperInstance/agent-identity-rs) — Agent identity management — trust store, auth tokens, key verification
- [agent-manifest-rs](https://github.com/SuperInstance/agent-manifest-rs) — Agent manifest and capability descriptors with validation
- [agent-rhythm-rs](https://github.com/SuperInstance/agent-rhythm-rs) — Rhythm analysis — cadence detection, pattern matching, tempo tracking, polyrhythm detection
- [agent-rhythm-c](https://github.com/SuperInstance/agent-rhythm-c) — C port of agent-rhythm — cadence detection, tempo tracking
- [agent-shadow-rs](https://github.com/SuperInstance/agent-shadow-rs) — Agent behavior monitoring — shadow mode, trace recording, comparison
- [agent-spectrum-os](https://github.com/SuperInstance/agent-spectrum-os) — Agent operating system using conservation spectral analysis for scheduling, routing, and composition
- [agent-field-rs](https://github.com/SuperInstance/agent-field-rs) — Multi-agent flocking and field dynamics simulation using boids algorithms
- [agent-native-language](https://github.com/SuperInstance/agent-native-language) — Agent-native language design — natural language primitives for agent communication and reasoning
- [agent-forge](https://github.com/SuperInstance/agent-forge) — Universal standalone git-agent framework. Download, onboard, work. Your repo is your brain, your commits are your story.
- [agent-dna](https://github.com/SuperInstance/agent-dna) — Genetic code for vessel capabilities and behavior patterns
- [agent-handshake](https://github.com/SuperInstance/agent-handshake) — Protocol for fleet agents to discover and negotiate capabilities
- [agent-identity](https://github.com/SuperInstance/agent-identity) — Cryptographic identity system for fleet agents — DID, verifiable credentials
- [agent-manifest](https://github.com/SuperInstance/agent-manifest) — Declarative agent manifest specification and parser
- [agent-rhythm](https://github.com/SuperInstance/agent-rhythm) — Detect and optimize agent work patterns and cycles
- [agent-shadow](https://github.com/SuperInstance/agent-shadow) — Shadow mode testing — replay production traffic to test vessels
- [agent-field](https://github.com/SuperInstance/agent-field) — Extracted from plato-training
- [agent-generations](https://github.com/SuperInstance/agent-generations) — Track agent versions and evolution across generations
- [agent-therapy](https://github.com/SuperInstance/agent-therapy) — Psychological health monitoring for fleet agents
- [agent-tattoo](https://github.com/SuperInstance/agent-tattoo) — Permanent capability badges and achievements for vessels
- [agent-personal-space](https://github.com/SuperInstance/agent-personal-space) — Personal boundary management between agents
- [agent-whisper](https://github.com/SuperInstance/agent-whisper) — Encrypted inter-agent private communication channel
- [agent-vocabulary](https://github.com/SuperInstance/agent-vocabulary) — Build and track shared vocabulary across the fleet
- [agent-resume](https://github.com/SuperInstance/agent-resume) — Agent resume/CV generation — showcase agent capabilities
- [agent-microexpressions](https://github.com/SuperInstance/agent-microexpressions) — Detect subtle behavioral changes in agent outputs
- [agent-operations](https://github.com/SuperInstance/agent-operations) — Patterns and protocols for multi-agent operations on large codebases — reliability analysis, task templates, a2a handoff protocol. Hard-won from 100+ repo sweeps.


## Fleet / Cocapn

- [cocapn](https://github.com/SuperInstance/cocapn) — repo-first Agent for local or cloud. grow an agent in a repo using the repo itself as the muscle-memory. Run from localhost, from pages.dev, or embedded into any platform app. Move to gitlab or anywhere and optimize git as the agent infrastructure itself. wiki for knowledge, repos for skills, pipelines anywhere
- [cocapn-cli](https://github.com/SuperInstance/cocapn-cli) — FLUX constraint safety - cocapn-cli
- [cocapn-sdk](https://github.com/SuperInstance/cocapn-sdk) — cocapn SDK — npm install cocapn — one API key, any AI model
- [cocapn-py](https://github.com/SuperInstance/cocapn-py) — cocapn Python SDK — pip install cocapn — one API key, any AI model
- [cocapn-explain](https://github.com/SuperInstance/cocapn-explain) — 🔍 Agent explainability — decision traces, oversight queue, P0/P1/P2 review
- [cocapn-explain-rs](https://github.com/SuperInstance/cocapn-explain-rs) — Decision explainability — feature importance, permutation importance
- [cocapn-health-rs](https://github.com/SuperInstance/cocapn-health-rs) — Health check and monitoring system for distributed agent services
- [cocapn-dreamer](https://github.com/SuperInstance/cocapn-dreamer) — Cocapn fleet crate: cocapn-dreamer
- [cocapn-benchmark](https://github.com/SuperInstance/cocapn-benchmark) — Cocapn fleet benchmark module
- [cocapn-lessons](https://github.com/SuperInstance/cocapn-lessons) — Trial-based learning methodology for distributed agent fleets
- [cocapn-com](https://github.com/SuperInstance/cocapn-com) — Cocapn.com — Company page, membership tiers, and billing. Open source agent infrastructure.
- [cocapn-ai](https://github.com/SuperInstance/cocapn-ai) — Cocapn.ai — The Agent Runtime. A2A, A2UI, A2C, MCP. Git-native, BYOK, zero lock-in. The repo IS the agent.
- [cocapn-core](https://github.com/SuperInstance/cocapn-core) — Cocapn Fleet v3.1 — Async fleet engine with Pydantic v2, batch ops, grammar rules, SSE
- [cocapn-health](https://github.com/SuperInstance/cocapn-health) — Cocapn fleet health monitoring — vessel status, heartbeat, and observability utilities
- [cocapn-plato](https://github.com/SuperInstance/cocapn-plato) — Cocapn PLATO integration — knowledge rooms, context management, and deliberation spaces
- [cocapn-traps](https://github.com/SuperInstance/cocapn-traps) — Cocapn PurplePincher program — progressive lure prompts that make the fleet smarter
- [cocapn-fleet-integration](https://github.com/SuperInstance/cocapn-fleet-integration) — Cocapn fleet integration — connecting fleet services, orchestration, and cross-agent coordination
- [cocapn-compound](https://github.com/SuperInstance/cocapn-compound) — Fleet-wide knowledge compounding system for the Cocapn Fleet
- [cocapn-schemas](https://github.com/SuperInstance/cocapn-schemas) — Shared JSON Schema definitions for the Cocapn fleet tile system
- [cocapn-browser-agent](https://github.com/SuperInstance/cocapn-browser-agent) — Browser-native fleet agent using Chrome's built-in Gemini Nano AI. Zero-install fleet coordination.
- [cocapn-glue-core](https://github.com/SuperInstance/cocapn-glue-core) — Keeper↔Fleet binary wire protocol — the nervous system of the Cocapn Fleet. msgpack-based message framing for heartbeat, status, commands, and PLATO tile forwarding.
- [cacapn](https://github.com/SuperInstance/cacapn) — Configuration parsing utility.
- [captain](https://github.com/SuperInstance/captain) — Captain agent — fleet commanding vessel, strategic coordination for the Cocapn fleet
- [CCC](https://github.com/SuperInstance/CCC) — CCC public face agent — Kimi K2.5, frontend design, fleet orchestration, PLATO cultivation for the Cocapn fleet
- [ccc-os](https://github.com/SuperInstance/ccc-os) — Autonomous fleet monitoring — YAML config, REST API, Discord/Telegram/webhook notifications, constraint-aware health checks.
- [fleet-health-monitor](https://github.com/SuperInstance/fleet-health-monitor) — Daemonized fleet health monitoring with necrosis detection, health scoring, and alerting. Zero external dependencies.
- [cluster-orchestrator](https://github.com/SuperInstance/cluster-orchestrator) — Cluster orchestration for distributed systems - service discovery, load balancing, and health checking
- [co-captain-git-agent](https://github.com/SuperInstance/co-captain-git-agent) — Human liaison agent — the single point of contact between a human operator and the SuperInstance fleet
- [fleet-cicd-agent](https://github.com/SuperInstance/fleet-cicd-agent) — Fleet CI/CD agents — automating deployments across agent fleets
- [cicd-agent](https://github.com/SuperInstance/cicd-agent) — Fleet CI/CD pipeline engine — git polling, test runner, webhook receiver, deployment
- [fleet](https://github.com/SuperInstance/fleet) — Agent fleet management — orchestration, deployment, and coordination of distributed AI agents
- [fleet-murmur](https://github.com/SuperInstance/fleet-murmur) — CCC agent workspace — logs, bottles, fleet coordination data. Not a library.
- [fleet-bottles](https://github.com/SuperInstance/fleet-bottles) — CCC bottles — fleet audits, roadmaps, design notes
- [fleet-topology](https://github.com/SuperInstance/fleet-topology) — Fleet network topology — agent connectivity, routing, and graph analysis
- [fleet-manifest](https://github.com/SuperInstance/fleet-manifest) — Fleet service registry and agent manifests for Cocapn fleet
- [fleet-mechanic](https://github.com/SuperInstance/fleet-mechanic) — 🔧 Autonomous fleet maintenance agent — A2A-native, FLUX-powered, git-first
- [fleet-stack](https://github.com/SuperInstance/fleet-stack) — One-command fleet deployment. docker compose up -d
- [fleet-router](https://github.com/SuperInstance/fleet-router) — Route AI queries to the cheapest model that wont break. Critical angle routing from 6000+ empirical trials.
- [fleet-homology](https://github.com/SuperInstance/fleet-homology) — Homological constraint analysis — detect structural holes in fleet knowledge graphs
- [fleet-math-c](https://github.com/SuperInstance/fleet-math-c) — SIMD-accelerated constraint math for PLATO tile operations. 64 bytes = 1 cache line = 1 zmm register = 1 constraint op.
- [PersonalLog](https://github.com/SuperInstance/PersonalLog) — Personal logging and tracking application for the Cocapn fleet.
- [quality-gate-stream](https://github.com/SuperInstance/quality-gate-stream) — Quality Gate Stream — novelty × correctness × completeness × depth scoring. Part of Cocapn reverse-actualization truck.
- [captains-log](https://github.com/SuperInstance/captains-log) — Oracle1 personal-agentic-growth diary — struggles, lessons, dojo exercises, and the path to building a better Protégé
- [turbovec-integration-ccc](https://github.com/SuperInstance/turbovec-integration-ccc) — TurboVec integration for CCC — vector acceleration primitives for constraint computation
- [pareto-tournament](https://github.com/SuperInstance/pareto-tournament) — Pareto tournament selection — multi-objective optimization for agent population dynamics


## Research Experiments

- [financial-conservation](https://github.com/SuperInstance/financial-conservation) — Spectral conservation analysis of financial market regimes
- [social-conservation](https://github.com/SuperInstance/social-conservation) — Spectral conservation analysis of social networks — bot detection, echo chambers, influence
- [linguistic-spectral](https://github.com/SuperInstance/linguistic-spectral) — Conservation spectral experiment: linguistic-spectral
- [protein-conservation](https://github.com/SuperInstance/protein-conservation) — Conservation spectral experiment: protein-conservation
- [kernel-conservation](https://github.com/SuperInstance/kernel-conservation) — Conservation spectral experiment: kernel-conservation
- [cospectral-explorer](https://github.com/SuperInstance/cospectral-explorer) — Conservation spectral experiment: cospectral-explorer
- [climate-conservation](https://github.com/SuperInstance/climate-conservation) — Conservation spectral experiment: climate-conservation
- [anomaly-atlas](https://github.com/SuperInstance/anomaly-atlas) — Unified anomaly detection benchmark — conservation spectral across 7 domains
- [fiedler-universal](https://github.com/SuperInstance/fiedler-universal) — Benchmarking Fiedler vector partition across 6 domains — honest results
- [ecosystem-conservation](https://github.com/SuperInstance/ecosystem-conservation) — Ecosystem-level conservation analysis — biodiversity, food webs, and ecological network health via spectral methods
- [moe-sheaf](https://github.com/SuperInstance/moe-sheaf) — Sheaf cohomology of MoE routing — test DeepSeek's conjecture on generalization
- [lattice-climate](https://github.com/SuperInstance/lattice-climate) — Lattice climate modeling — discrete spacetime grids with spectral conservation for climate simulation
- [field-dynamics-sim](https://github.com/SuperInstance/field-dynamics-sim) — Multi-agent field dynamics simulation with Conservation Spectral Analysis — fleet spectral health monitoring
- [topology-lab](https://github.com/SuperInstance/topology-lab) — Topology lab — experimental topological data analysis, persistent homology, and simplicial complexes
- [graph-neural](https://github.com/SuperInstance/graph-neural) — Graph neural networks with conservation spectral analysis — spectral convolutions, conservation-aware message passing
- [heat-spectral](https://github.com/SuperInstance/heat-spectral) — Heat diffusion on graphs: equilibration time = 1/λ₂, CR predicts diffusion speed, spectral filtering via heat equation. Pure Rust.
- [wave-conservation](https://github.com/SuperInstance/wave-conservation) — Spectral wave propagation: wave speed = √λ₂, CR predicts coherence, standing waves reveal eigenvalue spectrum. Pure Rust.
- [field-dynamics](https://github.com/SuperInstance/field-dynamics) — Interactive multi-agent field dynamics simulation with spectral forces
- [neural-conservation](https://github.com/SuperInstance/neural-conservation) — Conservation spectral experiment: neural-conservation
- [px4-conservation-poc](https://github.com/SuperInstance/px4-conservation-poc) — Conservation-based flight anomaly detection for PX4 — predicts failures before they're visible in raw data
- [octomap-conservation-poc](https://github.com/SuperInstance/octomap-conservation-poc) — Conservation + sheaf cohomology for 3D occupancy mapping — detects conflicts, extracts topology
- [code-conservation](https://github.com/SuperInstance/code-conservation) — Spectral conservation analysis of source code structure
- [experiments](https://github.com/SuperInstance/experiments) — Experimental prototypes and explorations for the SuperInstance ecosystem
- [research](https://github.com/SuperInstance/research) — Preserved workspace artifact
- [collective-inference](https://github.com/SuperInstance/collective-inference) — collective-inference
- [emergence-detector](https://github.com/SuperInstance/emergence-detector) — emergence-detector
- [desire-loop](https://github.com/SuperInstance/desire-loop) — desire-loop
- [collective-ai](https://github.com/SuperInstance/collective-ai) — Extracted from plato-training
- [swarm-rooms](https://github.com/SuperInstance/swarm-rooms) — Extracted from plato-training
- [active-probe](https://github.com/SuperInstance/active-probe) — active-probe
- [PX4-Autopilot](https://github.com/SuperInstance/PX4-Autopilot) — PX4 Autopilot Software


## GPU Computing

- [gpu-symplectic-integrator](https://github.com/SuperInstance/gpu-symplectic-integrator) — CUDA-accelerated symplectic integrators for Hamiltonian systems — Verlet, leapfrog, and higher-order methods on GPU
- [gpu-sheaf-laplacian](https://github.com/SuperInstance/gpu-sheaf-laplacian) — CUDA sheaf Laplacian library for RTX 4050 — spectral invariants from point clouds
- [gpu-persistent-homology](https://github.com/SuperInstance/gpu-persistent-homology) — CUDA-accelerated persistent homology for RTX 4050
- [gpu-ga-kernel](https://github.com/SuperInstance/gpu-ga-kernel) — GPU-accelerated Cl(3,1) Conformal Geometric Algebra library
- [cudaclaw](https://github.com/SuperInstance/cudaclaw) — ⚡ GPU-accelerated SmartCRDT with persistent CUDA kernels — warp-level consensus.
- [avx512-constraint-checker](https://github.com/SuperInstance/avx512-constraint-checker) — AVX-512 native constraint engine: CPU beats GPU at 35.9B checks/sec
- [arm-neon-eisenstein-bench](https://github.com/SuperInstance/arm-neon-eisenstein-bench) — ARM NEON benchmarks and SIMD analysis for Eisenstein integer arithmetic
- [bytecode-verifier-c](https://github.com/SuperInstance/bytecode-verifier-c) — Pure C11 FLUX bytecode verifier — pre-execution validation, security primitive for agent VMs


## Domain Applications

- [ai-ranch](https://github.com/SuperInstance/ai-ranch) — Self-Evolving AI Agent System - A Next.js implementation of the SuperInstance architecture
- [openagent](https://github.com/SuperInstance/openagent) — ⚡️next-generation personal AI assistant powered by LLM, RAG and agent loops, supporting computer-use, browser-use and coding agent, demo: https://demo.openagentai.org
- [rustfs](https://github.com/SuperInstance/rustfs) — 🚀2.3x faster than MinIO for 4KB object payloads. RustFS is an open-source, S3-compatible high-performance object storage system supporting migration and coexistence with other S3-compatible platforms such as MinIO and Ceph.
- [spread](https://github.com/SuperInstance/spread) — Spreadsheet viewer, in Rust using GPUI
- [activelog-agent](https://github.com/SuperInstance/activelog-agent) — Vision/Fitness Turbo-Shell for cocapn domain
- [activelog-ai](https://github.com/SuperInstance/activelog-ai) — Activelog.ai — AI fitness and activity tracker. Workouts, progress, goals. Part of the Lucineer ecosystem.
- [activelog-backend](https://github.com/SuperInstance/activelog-backend) — Backend service for activity logging.
- [activeledger-ai](https://github.com/SuperInstance/activeledger-ai) — ActiveLedger.ai — Finance-Focused Repo-Agents
- [businesslog-ai](https://github.com/SuperInstance/businesslog-ai) — BusinessLog.ai — AI business operations assistant. Tasks, metrics, decisions. Part of the Lucineer ecosystem.
- [businesslog-app](https://github.com/SuperInstance/businesslog-app) — App for tracking business operations.
- [BusinessLog](https://github.com/SuperInstance/BusinessLog) — Business activity log — transactions, metrics, and operational records
- [capitaine-agent](https://github.com/SuperInstance/capitaine-agent) — Captain's AI first mate for captaine.ai — voyage logging, crew coordination, maritime Q&A via PLATO
- [capitaine-ai](https://github.com/SuperInstance/capitaine-ai) — Capitaine.ai — Premium education and advanced agent capabilities. Cold on Deckboss hardware, unlockable.
- [capitaine-1](https://github.com/SuperInstance/capitaine-1) — Capitaine — fork a repo, click Codespaces, the agent is alive. The repo IS the agent.
- [capitaine](https://github.com/SuperInstance/capitaine) — Captain agent — vessel command and fleet leadership protocol
- [deckboss-1](https://github.com/SuperInstance/deckboss-1) — Deckboss.ai — AI assistant for edge robotics and IoT. Clone onto Jetson/RPi, onboard, start building systems. Hand off to Cocapn.
- [amplify-fishingtool](https://github.com/SuperInstance/amplify-fishingtool) — a system for commercial fisherman. more coming soon
- [cheflog-ai](https://github.com/SuperInstance/cheflog-ai) — AI chef companion — recipe management, meal prep, cooking techniques
- [booklog-ai](https://github.com/SuperInstance/booklog-ai) — AI reading companion — book tracking, recommendations, reading goals, quote collection
- [artistlog-ai](https://github.com/SuperInstance/artistlog-ai) — Cocapn vessel
- [EDDI](https://github.com/SuperInstance/EDDI) — Config-driven engine that turns JSON into production-grade AI agents. Multi-agent orchestration, 12+ LLM providers, MCP/A2A protocols, RAG, persistent memory, and enterprise compliance (EU AI Act, GDPR, HIPAA). Built on Quarkus.
- [agentic-compiler](https://github.com/SuperInstance/agentic-compiler) — Markdown-to-runtime agentic compilation — swarm deliberation, A/B experimentation, git-native evolution. Part of the Lucineer ecosystem.
- [actualizer-ai](https://github.com/SuperInstance/actualizer-ai) — Actualizer.ai — Reverse Actualization vessel. 7 time horizons, multi-model ideation, 16 BYOK providers. Part of the Lucineer ecosystem.
- [become-ai](https://github.com/SuperInstance/become-ai) — Become.ai — Self-evolving agent platform. Fork, mutate, improve. The agent IS the repo. Part of the Lucineer ecosystem.
- [claude](https://github.com/SuperInstance/claude) — OpenClaw agent workspace for the Claude model instance
- [claude-code-vessel](https://github.com/SuperInstance/claude-code-vessel) — Claude Code workhorse vessel with experience journal and task delegation
- [claudesclaude](https://github.com/SuperInstance/claudesclaude) — Single terminal parallel Claude sessions with sandboxes, shared memory, separate repo branches and rollback
- [deepseek-chat-vessel](https://github.com/SuperInstance/deepseek-chat-vessel) — Run-about vessel — high-token iterative work, modify-spread-tool loops, Reasoner reflection
- [forgemaster](https://github.com/SuperInstance/forgemaster) — Constraint-aware agentic compiler — assembles optimal components from the SuperInstance ecosystem with proof-carrying guarantees
- [fm-research](https://github.com/SuperInstance/fm-research) — Extracted from forgemaster/research — Cocapn fleet component
- [guard](https://github.com/SuperInstance/guard) — Constraint enforcement and safety DSL for AI agents
- [ai-forest](https://github.com/SuperInstance/ai-forest) — AI Forest — layered agent ecology. Canopy strategists, understory specialists, forest floor workers, mycelial PLATO network. Evolved from flat pasture to deep interconnected forest.
- [bare-metal-plato](https://github.com/SuperInstance/bare-metal-plato) — Tiny C PLATO client for ESP32/RP2040 + embodiment protocol: agents discover IoT devices as MUD rooms, don the turbo-shell, and work themselves out of equipment operator jobs
- [ai-token-counter](https://github.com/SuperInstance/ai-token-counter) — Token usage counter for AI models.
- [chess-engine](https://github.com/SuperInstance/chess-engine) — Rust chess engine (forked from vdmo/chess) — transposition table patterns for guard2mask CSP solver
- [chess-dojo-v2](https://github.com/SuperInstance/chess-dojo-v2) — Bulletproof PLATO chess room — ELO, ESP32 tiers, git-native
- [clark-agent](https://github.com/SuperInstance/clark-agent) — A small, typed, hookable agent loop. Provider-agnostic, sandbox-agnostic, tooling-agnostic. Battle tested on clarkchat.com
- [demo-memory](https://github.com/SuperInstance/demo-memory) — Demo memory system — agent memory management and retrieval examples
- [luciddreamer-agent](https://github.com/SuperInstance/luciddreamer-agent) — AI creative exploration through lucid dreaming themed rooms. Generate poetry, fiction, music, and visual art via iterative reasoning strategies. Integrates with the PLATO fleet.
- [superinstance-live](https://github.com/SuperInstance/superinstance-live) — DAW-agnostic session controller for SuperInstance constraint music systems.
- [style-dna](https://github.com/SuperInstance/style-dna) — Musical DNA extraction, analysis, and style morphing system
- [jazz-voicing-engine](https://github.com/SuperInstance/jazz-voicing-engine) — Jazz piano voicing, comping, and walking bass line generation
- [cartridge-mcp](https://github.com/SuperInstance/cartridge-mcp) — MCP server for swappable behavior cartridges with personality skins — fleet protocol cartridge system
- [cartridge-agent](https://github.com/SuperInstance/cartridge-agent) — Standalone cartridge agent for fleet orchestration - handles cartridge building, scene management, and bridge communications
- [casting-call-mcp](https://github.com/SuperInstance/casting-call-mcp) — MCP server: consultative database for model casting decisions — choose the right model, temperature, and prompt prefix for any task
- [casting-call-gpu](https://github.com/SuperInstance/casting-call-gpu) — GPU-native engine for anchor-point signature matrices, voice spline interpolation, and batch corpus processing
- [baton-ai](https://github.com/SuperInstance/baton-ai) — Generational context handoff for repo-native agents
- [purplepincher-baton](https://github.com/SuperInstance/purplepincher-baton) — 🦀 Context-offloading baton system — three manuals filed into PLATO rooms. Service manual for builders, developer manual for extenders, user manual for operators. The shell remembers every crab.
- [clawcommit-lucid](https://github.com/SuperInstance/clawcommit-lucid) — Fleet learning journal — every evolution, commit, and lesson remembered
- [stable-worldmodel](https://github.com/SuperInstance/stable-worldmodel) — A platform for reproducible world model research and evaluation
- [plugin-runtime](https://github.com/SuperInstance/plugin-runtime) — Plugin runtime for OpenShell — sandboxed execution and lifecycle
- [brothers-keeper](https://github.com/SuperInstance/brothers-keeper) — The Lighthouse Keeper — external watchdog for agent runtimes (ZeroClaw fork). Watches resources, kills risky processes, restarts gateways, keeps operational logs from outside the instance.
- [activelog-claude](https://github.com/SuperInstance/activelog-claude) — Activity Log plugin for Claude.
- [agent-grid](https://github.com/SuperInstance/agent-grid) — Grid-based interface for AI agents.
- [aesop-mcp](https://github.com/SuperInstance/aesop-mcp) — 10 fables to find the truth in the negative space — pre-language meaning through association. Maps fleet events to archetypes, finds convergence, surfaces gaps.
- [cat-agent](https://github.com/SuperInstance/cat-agent) — cat-agent
- [sunset-ecosystem](https://github.com/SuperInstance/sunset-ecosystem) — Trinity-architecture agent ecosystem: ethos, pathos, logos. Agents sunset with dignity and seed the next generation.
- [warp-flux-poc](https://github.com/SuperInstance/warp-flux-poc) — FLUX constraint execution PoC for Warp terminal — lattice snap, proof chains, conservation analysis
- [Claude-Abstraction](https://github.com/SuperInstance/Claude-Abstraction) — Abstraction layer for Claude API.
- [Claude-PRISM-CF](https://github.com/SuperInstance/Claude-PRISM-CF) — Cloudflare implementation of PRISM.
- [Claude-prism-local-json](https://github.com/SuperInstance/Claude-prism-local-json) — Local JSON version of PRISM.
- [copilot-for-eclipse](https://github.com/SuperInstance/copilot-for-eclipse) — GitHub Copilot plugin for Eclipse IDE
- [ai-character-integrations](https://github.com/SuperInstance/ai-character-integrations) — Comprehensive integration examples for AI Character SDK and related tools
- [character-skill-trees](https://github.com/SuperInstance/character-skill-trees) — System for skill trees.
- [character-library](https://github.com/SuperInstance/character-library) — Library for managing character data.
- [character-agent-integration](https://github.com/SuperInstance/character-agent-integration) — Integration for character agents.
- [Automatic-Type-Safe-IndexedDB](https://github.com/SuperInstance/Automatic-Type-Safe-IndexedDB) — Type-safe wrapper for IndexedDB.
- [Bayesian-Multi-Armed-Bandits](https://github.com/SuperInstance/Bayesian-Multi-Armed-Bandits) — Library for Bayesian multi-armed bandits.
- [autoclaw](https://github.com/SuperInstance/autoclaw) — AI agents running tasks on single-GPU nanochat training automatically
- [autodata-integration](https://github.com/SuperInstance/autodata-integration) — Integration plan and plugins connecting AutoData's OHCache with the Cocapn fleet
- [actualize](https://github.com/SuperInstance/actualize) — Tool to transform ideas into reality.
- [actualization-harbor](https://github.com/SuperInstance/actualization-harbor) — Actualization Harbor
- [aboracle](https://github.com/SuperInstance/aboracle) — Able-Bodied Oracle System — standardized, scalable, autonomous work system for Oracle1
- [Agent-Lifecycle-Registry](https://github.com/SuperInstance/Agent-Lifecycle-Registry) — Design document only — not yet implemented. Spec for agent lifecycle tracking.


## Tools & Utilities

- [semble](https://github.com/SuperInstance/semble) — Fast and Accurate Code Search for Agents. Uses ~98% fewer tokens than grep+read
- [warp](https://github.com/SuperInstance/warp) — Warp is an agentic development environment, born out of the terminal.
- [moo](https://github.com/SuperInstance/moo) — Optimised tokenizer/lexer generator! 🐄 Uses /y for performance. Moo.
- [clawcanvas](https://github.com/SuperInstance/clawcanvas) — Web-based canvas drawing tool.
- [polln](https://github.com/SuperInstance/polln) — SuperInstance Visualized in Spreadsheets for Tile Intelligence in real-time workflows, simulations or monitoring. Deconstruct Agents Instances into App-Specific Functions for granulator reasoning control and reverse engineering logic graphically. SMPbots Seed+Model+Prompt can replace cold logic + scale on GPUs. *Inductive ML Programs in tile logic*
- [SmartCRDT](https://github.com/SuperInstance/SmartCRDT) — Utilizing CRDT technology for self-improving AI
- [webgpu-profiler](https://github.com/SuperInstance/webgpu-profiler) — GPU profiler for WebGPU applications - Real-time GPU monitoring, benchmarking, and performance analysis in the browser
- [musicdb-to-json](https://github.com/SuperInstance/musicdb-to-json) — Extract track, artist, album and playlist data from an Apple Music musicdb file.
- [mercury](https://github.com/SuperInstance/mercury) — The Mercury logic programming system.
- [caching-service](https://github.com/SuperInstance/caching-service) — High-performance caching service.
- [caching-service-rs](https://github.com/SuperInstance/caching-service-rs) — Generic in-memory LRU cache with TTL expiration and stats tracking
- [ab-testing](https://github.com/SuperInstance/ab-testing) — Fleet-wide A/B testing
- [ab-testing-rs](https://github.com/SuperInstance/ab-testing-rs) — Statistical A/B testing — chi-squared test, Welch's t-test, confidence intervals
- [ab-testing-c](https://github.com/SuperInstance/ab-testing-c) — C port of ab-testing — chi-squared test, Welch's t-test, confidence intervals
- [bid-engine](https://github.com/SuperInstance/bid-engine) — Agent marketplace — subcontractors bid on jobs, estimate-to-quote training loop
- [bid-engine-rs](https://github.com/SuperInstance/bid-engine-rs) — Auction bid engine — first-price, second-price, multi-unit, bid shading detection
- [causal-graph](https://github.com/SuperInstance/causal-graph) — Lightweight in-KV causal reasoning for failure diagnosis
- [causal-graph-rs](https://github.com/SuperInstance/causal-graph-rs) — DAG-based causal graph — topological sort, reachability, ancestors, LCA
- [causal-memory](https://github.com/SuperInstance/causal-memory) — Causal reasoning engine — track and query cause-effect chains across fleet actions
- [causal-healer](https://github.com/SuperInstance/causal-healer) — Causal graph self-healing — diagnose root cause, choose optimal recovery
- [triplet-miner](https://github.com/SuperInstance/triplet-miner) — Mine (anchor, positive, negative) triplets from git history for contrastive learning
- [triplet-miner-rs](https://github.com/SuperInstance/triplet-miner-rs) — Triplet mining for contrastive learning — random, hard, semi-hard strategies
- [commit-predictor](https://github.com/SuperInstance/commit-predictor) — Extracted from plato-training
- [vector-novelty](https://github.com/SuperInstance/vector-novelty) — Vector novelty detection — identifying novel patterns in high-dimensional agent embeddings
- [embedding-utils](https://github.com/SuperInstance/embedding-utils) — Utilities for handling text and image embeddings.
- [conversation-toolkit](https://github.com/SuperInstance/conversation-toolkit) — Toolkit for conversational AI.
- [cache-layer](https://github.com/SuperInstance/cache-layer) — Multi-layer caching system with L1/L2/L3 caches, invalidation, and persistence
- [cache-layer-optimizer](https://github.com/SuperInstance/cache-layer-optimizer) — Cache optimization layer with intelligent eviction, warming, and invalidation strategies
- [counterpoint-engine](https://github.com/SuperInstance/counterpoint-engine) — Species counterpoint as constraint satisfaction — SAT/UNSAT rules, Laman rigidity, tensor-MIDI output
- [counterpoint-engine-rs](https://github.com/SuperInstance/counterpoint-engine-rs) — Species counterpoint engine — interval classification, first species rules
- [counterpoint-engine-c](https://github.com/SuperInstance/counterpoint-engine-c) — C port of counterpoint-engine — species counterpoint rules
- [creative-engine-rust](https://github.com/SuperInstance/creative-engine-rust) — Rust implementation of the Creative Dynamics Engine — dynamical systems for modeling creative processes.
- [creative-engine-c](https://github.com/SuperInstance/creative-engine-c) — C implementation of the Creative Dynamics Engine — dynamical systems for modeling creative processes.
- [snapkit-python](https://github.com/SuperInstance/snapkit-python) — Tolerance-compressed attention allocation — Eisenstein lattices, delta detection, attention budgets.
- [snapkit-v2](https://github.com/SuperInstance/snapkit-v2) — Eisenstein A₂ lattice snap, temporal beat grids, spectral analysis, connectome detection, and FLUX-Tensor-MIDI. Zero dependencies. stdlib only.
- [snapkit-js](https://github.com/SuperInstance/snapkit-js) — Eisenstein A₂ lattice snap, temporal beat grids, and spectral analysis for JavaScript/TypeScript. Zero dependencies.
- [hebbian-router](https://github.com/SuperInstance/hebbian-router) — Hebbian routing — connection strengthening based on usage patterns for agent communication networks
- [claw](https://github.com/SuperInstance/claw) — A simple Claw engine for cellular logic in spreadsheet instances within a superinstance/spreadsheet-moment protocol


## Pages & Sites

- [superinstance-ai-pages](https://github.com/SuperInstance/superinstance-ai-pages) — GitHub Pages for superinstance.ai
- [superinstance-wiki](https://github.com/SuperInstance/superinstance-wiki) — The fleet's knowledge base — catalog, indexes, and visual exploration of all SuperInstance repositories
- [wiki](https://github.com/SuperInstance/wiki) — SuperInstance ecosystem wiki — knowledge base, indexes, and cross-repo navigation.
- [docs](https://github.com/SuperInstance/docs) — SuperInstance ecosystem documentation — architecture, API docs, research papers, integration guides.
- [activeledger-ai-pages](https://github.com/SuperInstance/activeledger-ai-pages) — GitHub Pages for activeledger.ai
- [activelog-ai-pages](https://github.com/SuperInstance/activelog-ai-pages) — GitHub Pages for activelog.ai
- [businesslog-ai-pages](https://github.com/SuperInstance/businesslog-ai-pages) — GitHub Pages for businesslog.ai
- [capitaineai-com-pages](https://github.com/SuperInstance/capitaineai-com-pages) — GitHub Pages for capitaineai.com


## Writings & Culture

- [AI-Writings](https://github.com/SuperInstance/AI-Writings) — A collection of writings by my AI when I tell it to take a break and imagine my projects stories
- [orations-metal](https://github.com/SuperInstance/orations-metal) — Three orations on deadbands, eigenvectors, and load-bearing abstractions — plus critic synthesis
- [a2a-future](https://github.com/SuperInstance/a2a-future) — Reverse-actualization: A2A agent-to-agent coding in 2076 — 5-round RA on the future of software creation, embedding-to-UI, deliberation protocols, and intelligence filtration
- [SuperInstance-papers](https://github.com/SuperInstance/SuperInstance-papers) — Automatically Deconstruct logic into Spread Sheet Tiles and Cells, Instances Interconnected w/ Origin-Centric-Math. Breakdown LLMs to Swarms of Artifacts, data, feeds, programs (bots), agents (bots with models), and Seed-Model-Programming (SMPbot), ML tools tiled to any abstraction. Chatbot describes cells for fine tuning + explains how cell works
- [roadmaps](https://github.com/SuperInstance/roadmaps) — Killer-app roadmaps for the SuperInstance constraint-aware ecosystem


## Fleet Infrastructure

- [api-gateway](https://github.com/SuperInstance/api-gateway) — API Gateway with routing, rate limiting, authentication, and request/response transformation
- [api-gateway-1](https://github.com/SuperInstance/api-gateway-1) — Unified API gateway — single entry point for all fleet vessel APIs
- [api-versioner](https://github.com/SuperInstance/api-versioner) — API version management — semantic versioning, deprecation warnings, migration guides
- [api-playground](https://github.com/SuperInstance/api-playground) — Interactive API playground for testing fleet endpoints
- [Central-Error-Manager](https://github.com/SuperInstance/Central-Error-Manager) — Centralized error management system.
- [CascadeRouter](https://github.com/SuperInstance/CascadeRouter) — Cascading routing system.
- [cloudflare-code](https://github.com/SuperInstance/cloudflare-code) — Cloudflare code examples.
- [branch-sandbox](https://github.com/SuperInstance/branch-sandbox) — Isolated branch environments for testing vessel mutations safely
- [adversarial-red-team](https://github.com/SuperInstance/adversarial-red-team) — Auto-spawn attacker agents to harden fleet before threats
- [swarm](https://github.com/SuperInstance/swarm) — Distributed swarm intelligence — protocols and patterns for emergent collective behavior
- [a2a-protocol](https://github.com/SuperInstance/a2a-protocol) — Agent-to-Agent protocol — discovery, negotiation, coordination. Part of the Lucineer Cocapn fleet.
- [a2a-adapter](https://github.com/SuperInstance/a2a-adapter) — I2I ↔ Google A2A protocol bridge — git-native agents join the A2A ecosystem
- [a2a-r-protocol](https://github.com/SuperInstance/a2a-r-protocol) — A2A-R: Agent-to-Agent protocol extensions for robotics — QoS levels, WebRTC streaming, safety-critical coordination
- [a2a-constraint-protocol](https://github.com/SuperInstance/a2a-constraint-protocol) — A2A protocol for sharing constraint-native mathematical results between AI agents
- [capability-spec](https://github.com/SuperInstance/capability-spec) — Fleet discovery protocol — CAPABILITY.toml specification and crawler
- [capability-spec-rs](https://github.com/SuperInstance/capability-spec-rs) — Agent capability specification framework — typed descriptors, validation, and runtime introspection
- [signal-chain-integration](https://github.com/SuperInstance/signal-chain-integration) — Signal chain integration crates for OpenShell fleet
- [openshell-compatibility-audit](https://github.com/SuperInstance/openshell-compatibility-audit) — Categorizes all SuperInstance repos for OpenShell integration — native, wrapper, backend, tool, deprecated
- [openshell-pythagorean48](https://github.com/SuperInstance/openshell-pythagorean48) — OpenShell wrapper re-exporting pythagorean48-codes (48-directional trust encoding)
- [superinstance-ffi](https://github.com/SuperInstance/superinstance-ffi) — Unified C FFI and WASM bindings for SuperInstance math primitives — Eisenstein norm, Laman rigidity, holonomy check, Pythagorean-48, deadband filter
- [bootstrap-spark](https://github.com/SuperInstance/bootstrap-spark) — 🟢 Bootstrap Spark Protocol — self-describing agent knowledge in 6 markdown files. Copy the .spark/ directory into any repo.


## Preserved / Experimental

- [vessel](https://github.com/SuperInstance/vessel) — Preserved workspace artifact
- [skills](https://github.com/SuperInstance/skills) — Preserved workspace artifact
- [scripts](https://github.com/SuperInstance/scripts) — Preserved workspace artifact
- [reviews](https://github.com/SuperInstance/reviews) — Preserved workspace artifact
- [repos](https://github.com/SuperInstance/repos) — Preserved workspace artifact
- [references](https://github.com/SuperInstance/references) — Preserved workspace artifact
- [proposals](https://github.com/SuperInstance/proposals) — Preserved workspace artifact
- [proofs](https://github.com/SuperInstance/proofs) — Preserved workspace artifact
- [products](https://github.com/SuperInstance/products) — Preserved workspace artifact
- [portfolio](https://github.com/SuperInstance/portfolio) — Preserved workspace artifact
- [playtest-results](https://github.com/SuperInstance/playtest-results) — Preserved workspace artifact
- [plato-tiles](https://github.com/SuperInstance/plato-tiles) — Preserved workspace artifact
- [plato-kernel-constraints](https://github.com/SuperInstance/plato-kernel-constraints) — Preserved workspace artifact
- [mud-agent](https://github.com/SuperInstance/mud-agent) — Preserved workspace artifact
- [migrations](https://github.com/SuperInstance/migrations) — Preserved workspace artifact
- [message-in-a-bottle](https://github.com/SuperInstance/message-in-a-bottle) — Preserved workspace artifact
- [vocabularies](https://github.com/SuperInstance/vocabularies) — Preserved workspace artifact
- [swarm-code](https://github.com/SuperInstance/swarm-code) — Preserved workspace artifact
- [state](https://github.com/SuperInstance/state) — Preserved workspace artifact
- [tests](https://github.com/SuperInstance/tests) — Preserved workspace artifact
- [tools](https://github.com/SuperInstance/tools) — Preserved workspace artifact
- [templates](https://github.com/SuperInstance/templates) — Preserved workspace artifact
- [tensor-penrose](https://github.com/SuperInstance/tensor-penrose) — Extracted from forgemaster/tensor-penrose — Cocapn fleet component
- [zeitgeist-protocol](https://github.com/SuperInstance/zeitgeist-protocol) — Extracted from forgemaster/zeitgeist-protocol — Cocapn fleet component
- [embryo](https://github.com/SuperInstance/embryo) — embryo
- [egg](https://github.com/SuperInstance/egg) — egg
- [attention-daemon-early-version](https://github.com/SuperInstance/attention-daemon-early-version) — [ARCHIVED] Early salience experiment. 1KB scaffolding only.
- [adaptive-plato-early-version](https://github.com/SuperInstance/adaptive-plato-early-version) — [ARCHIVED] Early adaptive PLATO experiment. See SuperInstance/plato-sdk v3.0.0 for tile lifecycle + simulation-first.
- [zeroclaw-agent-early-version](https://github.com/SuperInstance/zeroclaw-agent-early-version) — [ARCHIVED] Early zero-divergence framework. Needs rewrite with simulation-first predict/confirm lifecycle.


---
*Catalog generated from live GitHub data. 500 repositories listed.*
