# Fleet Manifest — Plugin Architecture

Every fleet service is a **module** — independently loadable, independently testable, no hard dependencies on other modules.

## Rules

1. **Each module lives in its own repo** under `SuperInstance/`
2. **Each module has** `install.sh` + `uninstall.sh` at root
3. **Dependencies are optional** — degrade gracefully when peers are absent
4. **No shared state** — all state is in PLATO (text tiles) or Visual Mesh (image tiles)
5. **Port assignments** are registered in this manifest — no conflicts

## Port Registry

| Port | Module | Status |
|------|--------|--------|
| 8847 | plato-room-server | core |
| 8400 | plato-visual-mesh | visual |
| 8410 | terax-gateway | shell |
| 8900 | keeper | core |
| 8080 | shell-ui | shell |
| 4067 | oracle1-agent | core |

## Module Catalog

### Core (required for fleet operation)
- **plato-room-server** (port 8847) — Knowledge manifold. Zero-dependency room server.
- **keeper** (port 8900) — Auth, routing, agent dispatch.

### Visual (optional — adds visual memory)
- **plato-visual-mesh** (port 8400) — Visual tile ingestion, P48 trust, H1 emergence. Depends on PLATO for room context, but degrades gracefully without it.

### Shell (optional — adds interactive workspace)
- **terax-gateway** (port 8410) — REST API for shell commands, filesystem, fleet health. Standalone operation: run commands, browse files. Integration: proxies to PLATO, Visual Mesh, Keeper.
- **shell-ui** (port 8080) — Browser frontend for the gateway. Standalone: HTML file. Integration: nginx proxies /api/ to gateway.

### MCP Tools (optional — adds agent tool interface)
- **plato-visual-mesh-mcp** (stdio) — MCP tools exposing visual memory to agents.

### Desktop (optional — adds local IDE)
- **terax-ai** — Tauri desktop ADE. Standalone: works with BYOK. Integration: fleet auth + PLATO tile bridge + casting-call.

### Intelligence (optional — adds model selection + benchmarks)
- **casting-call** — Model selection knowledge base. Not a service — pure knowledge.
- **MemEye** — Visual memory benchmark suite. Not a service — eval runner.

## Installation

```bash
# Install individual modules
bash modules/plato-visual-mesh/install.sh
bash modules/shell-ui/install.sh

# Or install by use case
bash modules/install-use-case.sh visual   # visual mesh + MCP
bash modules/install-use-case.sh shell    # gateway + shell-ui + nginx
bash modules/install-use-case.sh all      # everything
```

## Uninstallation

```bash
bash modules/plato-visual-mesh/uninstall.sh  # removes service, preserves data
bash modules/plato-visual-mesh/purge.sh      # removes service + data
```

## Use Cases

| Use Case | Modules Needed | Ports |
|----------|---------------|-------|
| **Core fleet** | plato-room-server + keeper | 8847, 8900 |
| **+ Visual memory** | + plato-visual-mesh | +8400 |
| **+ MCP tools** | + plato-visual-mesh-mcp | stdio |
| **+ Shell workspace** | + terax-gateway + shell-ui | +8410, +8080 |
| **+ Desktop IDE** | + terax-ai (local Tauri app) | none |
| **Full** | all of the above | 4 ports |
