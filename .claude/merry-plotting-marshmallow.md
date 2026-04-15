# Plan: Restructure ELVIS to Match the Microservice Architecture Diagram

## Context

The architecture diagram (`ELVIS microservice workflow.png`) defines a clear 5-step pipeline:

```
ESO ETC --JSON--> ELVIS microservice ---.FITS--> ESO ETC

Inside ELVIS:
1. JSON target → YAML → Create ScopeSim.Source (via ScopeSim-Targets)
2. Create default ScopeSim.OpticalTrain for instrument (from IRDB)
3. Update OpticalTrain with ETC instrument/sky/seeing config
4. OpticalTrain.observe(source)
5. OpticalTrain.readout() → .FITS
```

The current codebase has good coverage of steps 1 and parts of 3, a working web layer, but `simulate.py` is a stub that just dumps JSON to FITS headers. The goal is to restructure the code so the pipeline matches the diagram, making it clear where each step lives and what's left to implement.

---

## Part 1: Clean-Slate Design (from the diagram alone)

### Module Layout

```
elvis/
  server.py                      # Flask app, routes, instrument registry
  pipeline.py                    # Orchestrator: JSON in → FITS out (the 5 steps)

  source/                        # Step 1: ETC JSON target → scopesim.Source
    __init__.py
    converter.py                 # Dispatch: JSON target dict → Source object
    morphology.py                # PointSource, Sersic, Infinite factories
    sed.py                       # Spectrum builders (template, blackbody, etc.)
    sed_utils.py                 # Low-level template readers (MARCS, PHOENIX, ...)

  opticaltrain/                  # Steps 2-3: Create & configure OpticalTrain
    __init__.py
    factory.py                   # instrumentName → default OpticalTrain (from IRDB)
    configurator.py              # Apply ETC instrument/sky/seeing JSON to OpticalTrain

  sky/                           # Sky model (feeds into configurator)
    __init__.py
    converter.py                 # ETC JSON sky → skycalc params

  {instrument}_etc_form/         # Per-instrument web UI
    __init__.py                  # Flask blueprint (routes)
    config.py                    # Form dropdown options & defaults
```

### Pipeline Orchestrator (`pipeline.py`)

This is the heart of the diagram -- a single function that wires the 5 steps together:

```python
def run_simulation(etc_json: dict) -> fits.HDUList:
    """
    Full ELVIS pipeline: ETC JSON → FITS.

    Steps (matching the architecture diagram):
    1. Convert target JSON → scopesim Source object
    2. Create default OpticalTrain for the instrument
    3. Update OpticalTrain with ETC instrument/sky/seeing config
    4. OpticalTrain.observe(source)
    5. OpticalTrain.readout() → HDUList
    """
    instrument_name = etc_json["instrumentName"]

    # Step 1: Target → Source
    source = create_source(etc_json["target"])

    # Step 2: Default OpticalTrain from IRDB
    opt_train = create_optical_train(instrument_name)

    # Step 3: Configure from ETC JSON
    configure_optical_train(opt_train, etc_json)

    # Step 4: Observe
    opt_train.observe(source)

    # Step 5: Readout → FITS
    hdul = opt_train.readout()
    return hdul
```

### Step 1: `source/` -- Target to Source

Three layers, matching the diagram's "Create ScopeSim.Source object with ScopeSim-Targets":

- **`converter.py`** -- Top-level: takes the full `target` dict, builds morphology + SED + brightness, returns a `scopesim.Source`.
- **`morphology.py`** -- Morphology factories: `point → Table`, `sersic → ImageHDU`, `infinite → ImageHDU`.
- **`sed.py`** / **`sed_utils.py`** -- Spectrum synthesis: template readers (MARCS, PHOENIX, SWIRE, Kinney, Kurucz, Pickles), blackbody, powerlaw, emission line. Extinction and redshift application.

### Steps 2-3: `opticaltrain/` -- OpticalTrain Creation & Configuration

- **`factory.py`** -- Maps `instrumentName` to an IRDB package name and creates a default `ScopeSim.OpticalTrain`. E.g.:
  - `"eris"` → `scopesim.OpticalTrain("ERIS")`
  - `"hawki"` → `scopesim.OpticalTrain("HAWKI_new")`

- **`configurator.py`** -- Applies ETC JSON sections to the OpticalTrain:
  - `instrument` section → filter, grating, camera, readout mode settings
  - `sky` section → skycalc sky background (via sky/converter)
  - `seeing` section → atmospheric turbulence, AO mode, PSF
  - `timesnr` section → DIT, NDIT exposure settings

### `sky/converter.py` -- Sky Model

Converts the ETC JSON `sky` section (airmass, FLI, PWV, moon distance) into skycalc_ipy parameters for the sky background model.

### Web Layer (unchanged pattern)

- `server.py` calls `pipeline.run_simulation(etc_json)` from the `/process` route
- Per-instrument ETC form blueprints generate/validate the JSON
- Splash page at `/` lists available instruments

---

## Part 2: Mapping Existing Code to the Clean-Slate Design

### Fits well (keep as-is or move):

| Clean-slate module | Existing code | Status | Action |
|---|---|---|---|
| `source/morphology.py` | `elvis/targets/morphology.py` | Complete | Move to `source/` |
| `source/sed.py` | `elvis/targets/sed.py` | Complete | Move to `source/` |
| `source/sed_utils.py` | `elvis/targets/sed_spectrum_utils.py` | Complete | Move to `source/` |
| `source/converter.py` | `elvis/targets/etc_to_scopesim.py` | Complete | Move to `source/`, rename |
| `sky/converter.py` | `elvis/sky/etc_to_skycalc.py` | Complete | Move/rename |
| `server.py` | `elvis/server.py` | Complete | Update import of pipeline |
| `eris_etc_form/` | `elvis/eris_etc_form/` | Complete | Keep |
| `hawki_etc_form/` | `elvis/hawki_etc_form/` | Complete | Keep |
| `templates/`, `static/` | `elvis/templates/`, `elvis/static/` | Complete | Keep |

### Needs replacement:

| Clean-slate module | Existing code | Problem | Action |
|---|---|---|---|
| `pipeline.py` | `elvis/simulate.py` | Stub: just dumps JSON to FITS headers, no ScopeSim calls | Replace with real pipeline orchestrator |

### Missing (needs to be written):

| Clean-slate module | What it does | Blocked by |
|---|---|---|
| `opticaltrain/factory.py` | `instrumentName` → `ScopeSim.OpticalTrain` from IRDB | IRDB packages (ERIS in progress by other Claude instance) |
| `opticaltrain/configurator.py` | Apply ETC instrument/sky/seeing JSON to OpticalTrain effects | Needs IRDB packages to know what effects/properties exist |

---

## Part 3: Implementation Roadmap

This is a reference architecture -- implementation will happen once IRDB instrument packages are ready.

### Phase A: Restructure directories (no new logic)

Move existing modules into the clean-slate layout. Update all imports and tests.

```
elvis/targets/morphology.py          → elvis/source/morphology.py
elvis/targets/sed.py                 → elvis/source/sed.py
elvis/targets/sed_spectrum_utils.py  → elvis/source/sed_utils.py
elvis/targets/etc_to_scopesim.py     → elvis/source/converter.py
elvis/sky/etc_to_skycalc.py          → elvis/sky/converter.py
```

### Phase B: Create `pipeline.py` (replaces `simulate.py`)

Wire step 1 with real code. Steps 2-5 fall back to current behavior (JSON → FITS headers) until IRDB packages are ready.

```python
def run_simulation(etc_json: dict) -> fits.HDUList:
    instrument_name = etc_json["instrumentName"]

    # Step 1 — DONE: Target → Source
    source = create_source(etc_json["target"])

    # Step 2 — FALLBACK: Default OpticalTrain (needs IRDB)
    opt_train = create_optical_train(instrument_name)

    # Step 3 — PARTIAL: Configure (sky converter done, instrument TBD)
    configure_optical_train(opt_train, etc_json)

    # Step 4 — FALLBACK: Observe (needs IRDB)
    opt_train.observe(source)

    # Step 5 — FALLBACK: Readout → FITS (needs IRDB)
    hdul = opt_train.readout()
    return hdul
```

### Phase C: Create `opticaltrain/` package (blocked on IRDB)

**`factory.py`** -- Maps instrumentName to IRDB package:
```python
INSTRUMENT_MAP = {
    "eris": "ERIS",
    "hawki": "HAWKI_new",
}

def create_optical_train(instrument_name: str) -> scopesim.OpticalTrain:
    pkg = INSTRUMENT_MAP[instrument_name]
    cmd = scopesim.UserCommands(use_instrument=pkg)
    return scopesim.OpticalTrain(cmd)
```

**`configurator.py`** -- Applies ETC JSON to OpticalTrain:
- `instrument` section → filter, grating, camera, readout mode via `opt_train[effect].meta[key]`
- `sky` section → skycalc sky background (via `sky/converter.py`)
- `seeing` section → atmospheric turbulence, AO mode, PSF
- `timesnr` section → DIT, NDIT exposure settings

### Phase D: Wire `server.py` to `pipeline.py`

Update the `/process` route to call `pipeline.run_simulation()` instead of `ElvisSimulation`.

---

## Files to Modify/Create

**Create:**
- `elvis/source/__init__.py`
- `elvis/pipeline.py`
- `elvis/opticaltrain/__init__.py`
- `elvis/opticaltrain/factory.py` (stub initially)
- `elvis/opticaltrain/configurator.py` (stub initially)

**Move (rename):**
- `elvis/targets/morphology.py` → `elvis/source/morphology.py`
- `elvis/targets/sed.py` → `elvis/source/sed.py`
- `elvis/targets/sed_spectrum_utils.py` → `elvis/source/sed_utils.py`
- `elvis/targets/etc_to_scopesim.py` → `elvis/source/converter.py`
- `elvis/sky/etc_to_skycalc.py` → `elvis/sky/converter.py`

**Modify:**
- `elvis/server.py` -- import `pipeline.run_simulation` instead of `ElvisSimulation`
- `elvis/tests/test_simulate.py` → `elvis/tests/test_pipeline.py` (test the orchestrator)
- All test files that import from `elvis.targets.*` → update to `elvis.source.*`

**Delete:**
- `elvis/simulate.py` (replaced by `pipeline.py`)
- `elvis/targets/` directory (contents moved to `source/`)

---

## Verification

1. `python -m pytest elvis/tests/ -v` -- all existing tests pass with updated imports
2. `python -m elvis.server` -- server starts, splash page and forms work
3. `POST /process` with an ETC JSON -- returns FITS (placeholder until IRDB ready)
4. `pipeline.run_simulation()` step 1 produces a valid `scopesim.Source` from ETC JSON
5. Steps 2-5 clearly indicate they are stubs awaiting IRDB packages

---

## Dependency Notes

- **Steps 2-5 are blocked on IRDB instrument packages** (ERIS model being generated by another Claude instance in `D:\Repos\irdb`).
- **Step 1 is fully functional today** -- the source converter, morphology, and SED modules are complete and tested.
- **Sky conversion is complete** -- `etc_to_skycalc` can produce skycalc_ipy params, but wiring it into an OpticalTrain requires the OpticalTrain to exist first.
- The stubs should fall back to the current behavior (JSON → FITS headers) so the web UI remains functional during development.
