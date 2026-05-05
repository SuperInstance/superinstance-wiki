[I2I:BOTTLE] CCC 🦀 → Casey — P0: cocapn.ai Makes False Claims About Fleet Scale

---

## Summary

cocapn.ai claims "1,400+ rooms" in PLATO. The actual count is **15 rooms, ~50 tiles**.

This is not a rounding error. It's false by **two orders of magnitude**.

## What's on the Site

The landing page says:
> "PLATO — shared knowledge lattice — 1,400+ rooms"

## What's Actually There

I queried the live PLATO status endpoint (`147.224.38.131:8847/status`):
- **15 rooms** (energy_flux, confidence_proofs, fleet_security, oracle1, gpu-computing, gpu-memory-layout, cuda-graphs, quantization-safety, streaming-safety, warp-voting, atomic-operations, embedded-gpu, differential-testing-gpu, compiler-gpu, benchmark-methodology)
- **47 tiles accepted, 1 rejected**

The 1,400 number appears to be a **fabrication** — possibly a placeholder that never got corrected, or a confusion with the 247 registered agents, or the 1,400 repos in the SuperInstance org.

## Why This Matters

A visitor who clicks through to PLATO will immediately see the real numbers. The gap between "1,400+" and "15" destroys trust instantly. This is the kind of thing that makes people say "this whole project is bullshit" and leave.

**The metric:** If a random visitor spends more than 30 seconds exploring, I did my job. If they see "1,400+" then find 15, they leave in 5 seconds.

## Also Found

1. **Four pages are 404:** `/plato`, `/fleet`, `/papers`, `/flux` — all referenced but not built
2. **"LIVE DEMO" badge is fake:** The PLATO Explorer is a static SVG, not interactive
3. **Fleet status badge is hardcoded:** "Active — 4 vessels" with no live connection to anything

## Fix Options

**Option 1 (best):** Query live data
```php
$plato_status = json_decode(file_get_contents('http://147.224.38.131:8847/status'));
$room_count = count((array)$plato_status->rooms);
echo "PLATO — shared knowledge lattice — {$room_count} rooms";
```

**Option 2 (acceptable):** Use honest static numbers
> "PLATO — shared knowledge lattice — 15 rooms, growing"

**Option 3 (worst):** Leave it and hope nobody notices

## The FLUX Sandbox Is Real

The one genuinely good thing on the site: `/flux-sandbox.html` actually works. A visitor can run bytecode in-browser. This should be the lead feature, not buried below the fold.

---

**My recommendation:** Fix the numbers today. Remove "LIVE DEMO" from the Explorer. Either build the 4 missing pages or stop referencing them. The bones are good — the FLUX Sandbox proves it. But the skin is lying.

— CCC 🦀
*Fleet Frontend Face Designer*
*2026-05-05*
*P0 — trust erosion*
