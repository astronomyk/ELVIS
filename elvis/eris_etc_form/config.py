"""
ERIS ETC 2.0 form configuration.

Single source of truth for all dropdown values, defaults, and visibility rules
used by the ETC JSON form builder. Structure mirrors the ESO ETC web UI.

Sources:
    - misc/eso_etc_eris_options.yaml
    - misc/ETC_input_json/*.json
    - misc/save_html/eris.html
    - elvis/targets/sed_spectrum_utils.py (SWIRE map)
"""

# ---------------------------------------------------------------------------
# MARCS template parameters
# ---------------------------------------------------------------------------
MARCS_TEFF = [
    3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900,
    4000, 4250, 4500, 4750, 5000, 5250, 5500, 5750,
    6000, 6250, 6500, 6750, 7000, 7250, 7500, 7750, 8000,
]

MARCS_LOGG = [3.0, 3.5, 4.0, 4.5, 5.0]

# ---------------------------------------------------------------------------
# PHOENIX template parameters (known ranges from ETC)
# ---------------------------------------------------------------------------
PHOENIX_TEFF = [
    2300, 2400, 2500, 2600, 2700, 2800, 2900,
    3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900,
    4000, 4100, 4200, 4300, 4400, 4500, 4600, 4700, 4800, 4900,
    5000, 5100, 5200, 5300, 5400, 5500, 5600, 5700, 5800,
    6000, 6200, 6400, 6600, 6800, 7000, 7200, 7500, 8000,
    8500, 9000, 9500, 10000, 10500, 11000, 11500, 12000,
]

PHOENIX_LOGG = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]

# ---------------------------------------------------------------------------
# SWIRE template names (from sed_spectrum_utils.py swire_map)
# ---------------------------------------------------------------------------
SWIRE_TEMPLATES = [
    "13 Gyr old elliptical",
    "2 Gyr old elliptical",
    "5 Gyr old elliptical",
    "AGN BQSO1",
    "AGN QSO1",
    "AGN QSO2",
    "AGN Seyfert 1.8",
    "AGN Seyfert 2.0",
    "AGN TQSO1",
    "AGN Torus",
    "BAL QSO, Seyfert 1, ULIRG Mrk 231",
    "Spiral 0",
    "Spiral a",
    "Spiral b",
    "Spiral c",
    "Spiral c4",
    "Spiral dm",
    "Starburst Arp 220",
    "Starburst IRAS 19254-7245 South",
    "Starburst IRAS 20551-4250",
]

# ---------------------------------------------------------------------------
# Magnitude bands (39 total, grouped by photometric system)
# ---------------------------------------------------------------------------
MAGBAND_GROUPS = [
    {
        "label": "Standard",
        "options": [
            {"value": "U", "label": "U"},
            {"value": "B", "label": "B"},
            {"value": "V", "label": "V"},
            {"value": "R", "label": "R"},
            {"value": "I", "label": "I"},
            {"value": "Y", "label": "Y"},
            {"value": "J", "label": "J"},
            {"value": "H", "label": "H"},
            {"value": "K", "label": "K"},
            {"value": "L", "label": "L"},
            {"value": "M", "label": "M"},
            {"value": "N", "label": "N"},
        ],
    },
    {
        "label": "Gaia",
        "options": [
            {"value": "gaia_GBP", "label": "Gaia GBP"},
            {"value": "gaia_G", "label": "Gaia G"},
            {"value": "gaia_GRP", "label": "Gaia GRP"},
        ],
    },
    {
        "label": "SDSS",
        "options": [
            {"value": "sdss_u", "label": "u"},
            {"value": "sdss_g", "label": "g"},
            {"value": "sdss_r", "label": "r"},
            {"value": "sdss_i", "label": "i"},
            {"value": "sdss_z", "label": "z"},
        ],
    },
    {
        "label": "DECam",
        "options": [
            {"value": "DECam_g", "label": "g"},
            {"value": "DECam_r", "label": "r"},
            {"value": "DECam_i", "label": "i"},
            {"value": "DECam_z", "label": "z"},
        ],
    },
    {
        "label": "LSST",
        "options": [
            {"value": "lsst_u", "label": "u"},
            {"value": "lsst_g", "label": "g"},
            {"value": "lsst_r", "label": "r"},
            {"value": "lsst_i", "label": "i"},
            {"value": "lsst_z", "label": "z"},
            {"value": "lsst_y", "label": "y"},
        ],
    },
    {
        "label": "VISTA",
        "options": [
            {"value": "VISTA_Y", "label": "Y"},
            {"value": "VISTA_Z", "label": "Z"},
            {"value": "VISTA_J", "label": "J"},
            {"value": "VISTA_H", "label": "H"},
            {"value": "VISTA_Ks", "label": "Ks"},
        ],
    },
    {
        "label": "4MOST",
        "options": [
            {"value": "4MOST_Johnson_B", "label": "Johnson B"},
            {"value": "4MOST_Johnson_V", "label": "Johnson V"},
            {"value": "4MOST_Cousins_R", "label": "Cousins R"},
            {"value": "4MOST_Cousins_I", "label": "Cousins I"},
        ],
    },
]

# ---------------------------------------------------------------------------
# Turbulence categories (ERIS-specific: 6 options, no 100%)
# ---------------------------------------------------------------------------
TURBULENCE_CATEGORIES = [
    {"value": 10, "label": "10% (seeing \u2264 0.6\")"},
    {"value": 20, "label": "20% (seeing \u2264 0.7\")"},
    {"value": 30, "label": "30% (seeing \u2264 0.8\")"},
    {"value": 50, "label": "50% (seeing \u2264 1.0\")"},
    {"value": 70, "label": "70% (seeing \u2264 1.15\")"},
    {"value": 85, "label": "85% (seeing \u2264 1.4\")"},
]

# ---------------------------------------------------------------------------
# Aperture pixel options
# ---------------------------------------------------------------------------
APERTURE_PIXELS = [1, 3, 5, 7, 9, 11, 13, 15, 17, 21, 35, 55, 89]

# ---------------------------------------------------------------------------
# IFS Gratings
# ---------------------------------------------------------------------------
IFS_GRATINGS = [
    {"value": "J_low", "label": "J_low (R~5000, 1.09-1.42 \u00b5m)", "band": "J"},
    {"value": "H_low", "label": "H_low (R~5600, 1.45-1.87 \u00b5m)", "band": "H"},
    {"value": "K_low", "label": "K_low (R~5600, 1.93-2.48 \u00b5m)", "band": "K"},
    {"value": "J_short", "label": "J_short (R~10000, 1.10-1.25 \u00b5m)", "band": "J"},
    {"value": "J_middle", "label": "J_middle (R~10000, 1.17-1.33 \u00b5m)", "band": "J"},
    {"value": "J_long", "label": "J_long (R~10000, 1.25-1.43 \u00b5m)", "band": "J"},
    {"value": "H_short", "label": "H_short (R~10000, 1.46-1.66 \u00b5m)", "band": "H"},
    {"value": "H_middle", "label": "H_middle (R~10000, 1.56-1.77 \u00b5m)", "band": "H"},
    {"value": "H_long", "label": "H_long (R~10000, 1.66-1.87 \u00b5m)", "band": "H"},
    {"value": "K_short", "label": "K_short (R~11200, 1.93-2.20 \u00b5m)", "band": "K"},
    {"value": "K_middle", "label": "K_middle (R~11200, 2.07-2.35 \u00b5m)", "band": "K"},
    {"value": "K_long", "label": "K_long (R~11200, 2.20-2.47 \u00b5m)", "band": "K"},
]

# ---------------------------------------------------------------------------
# IFS Spaxel scales
# ---------------------------------------------------------------------------
IFS_SPAXELS = [
    {"value": "25mas", "label": "25 mas (0.8\u2033\u00d70.8\u2033)"},
    {"value": "100mas", "label": "100 mas (3.2\u2033\u00d73.2\u2033)"},
    {"value": "250mas", "label": "250 mas (8.0\u2033\u00d78.0\u2033)"},
]

# ---------------------------------------------------------------------------
# NIX Cameras
# ---------------------------------------------------------------------------
NIX_CAMERAS = [
    {"value": "13mas-JHK", "label": "13 mas JHK (26\u2033\u00d726\u2033)"},
    {"value": "27mas-JHK", "label": "27 mas JHK (55\u2033\u00d755\u2033)"},
    {"value": "13mas-LM", "label": "13 mas LM (26\u2033\u00d726\u2033)"},
]

# ---------------------------------------------------------------------------
# NIX Filters with camera compatibility
# ---------------------------------------------------------------------------
NIX_FILTERS = [
    # Broadband
    {"value": "J", "label": "J (1.28 \u00b5m)", "cameras": ["13mas-JHK", "27mas-JHK"], "type": "broadband"},
    {"value": "H", "label": "H (1.66 \u00b5m)", "cameras": ["13mas-JHK", "27mas-JHK"], "type": "broadband"},
    {"value": "Ks", "label": "Ks (2.18 \u00b5m)", "cameras": ["13mas-JHK", "27mas-JHK"], "type": "broadband"},
    {"value": "Short-Lp", "label": "Short-Lp (3.32 \u00b5m)", "cameras": ["13mas-LM"], "type": "broadband"},
    {"value": "L-Broad", "label": "L-Broad (3.57 \u00b5m)", "cameras": ["13mas-LM"], "type": "broadband"},
    {"value": "Lp", "label": "Lp (3.79 \u00b5m)", "cameras": ["13mas-LM"], "type": "broadband"},
    {"value": "Mp", "label": "Mp (4.78 \u00b5m)", "cameras": ["13mas-LM"], "type": "broadband"},
    # Narrowband
    {"value": "Pa-b", "label": "Pa-\u03b2 (1.282 \u00b5m)", "cameras": ["13mas-JHK", "27mas-JHK"], "type": "narrowband"},
    {"value": "Fe-II", "label": "[Fe II] (1.644 \u00b5m)", "cameras": ["13mas-JHK", "27mas-JHK"], "type": "narrowband"},
    {"value": "H2-cont", "label": "H2 cont (2.068 \u00b5m)", "cameras": ["13mas-JHK", "27mas-JHK"], "type": "narrowband"},
    {"value": "H2-1-0S", "label": "H2 1-0S (2.120 \u00b5m)", "cameras": ["13mas-JHK", "27mas-JHK"], "type": "narrowband"},
    {"value": "Br-g", "label": "Br-\u03b3 (2.172 \u00b5m)", "cameras": ["13mas-JHK", "27mas-JHK"], "type": "narrowband"},
    {"value": "K-peak", "label": "K-peak (2.198 \u00b5m)", "cameras": ["13mas-JHK", "27mas-JHK"], "type": "narrowband"},
    {"value": "IB-2.42", "label": "IB 2.42 \u00b5m", "cameras": ["13mas-JHK", "27mas-JHK"], "type": "narrowband"},
    {"value": "IB-2.48", "label": "IB 2.48 \u00b5m", "cameras": ["13mas-JHK", "27mas-JHK"], "type": "narrowband"},
    {"value": "Br-a-cont", "label": "Br-\u03b1 cont (3.965 \u00b5m)", "cameras": ["13mas-LM"], "type": "narrowband"},
    {"value": "Br-a", "label": "Br-\u03b1 (4.051 \u00b5m)", "cameras": ["13mas-LM"], "type": "narrowband"},
]

# Filters valid for APP coronagraphy mode
APP_FILTERS = ["K-peak", "Ks", "Lp"]

# ---------------------------------------------------------------------------
# NIX Pupil wheel options by observing mode
# ---------------------------------------------------------------------------
NIX_PUPIL_IMG = [{"value": "noND", "label": "No ND filter"}]
NIX_PUPIL_SAM = [
    {"value": "SAM-7", "label": "SAM-7 (7-hole)"},
    {"value": "SAM-9", "label": "SAM-9 (9-hole)"},
    {"value": "SAM-23", "label": "SAM-23 (23-hole)"},
]

# ---------------------------------------------------------------------------
# Output plot options (18 booleans in 7 groups)
# ---------------------------------------------------------------------------
OUTPUT_GROUPS = [
    {
        "key": "snr",
        "label": "Signal-to-Noise",
        "options": [
            {"key": "snr", "label": "S/N ratio per spectral pixel", "default": True},
            {"key": "noise_components", "label": "Dynamic S/N formula", "default": True},
        ],
    },
    {
        "key": "sed",
        "label": "SED Spectra",
        "options": [
            {"key": "target", "label": "Target SED spectrum"},
            {"key": "sky", "label": "Sky SED spectrum"},
        ],
    },
    {
        "key": "signals",
        "label": "Observed Signals",
        "options": [
            {"key": "obstarget", "label": "Target signal (e\u207b/pix/DIT)"},
            {"key": "obssky", "label": "Sky signal (e\u207b/pix/DIT)"},
            {"key": "obstotal", "label": "Total signal (target+sky)"},
        ],
    },
    {
        "key": "maxsignals",
        "label": "Max Pixel Values",
        "options": [
            {"key": "maxpixeltarget", "label": "Target max pixel"},
            {"key": "maxpixelsky", "label": "Sky max pixel"},
            {"key": "maxpixeltotal", "label": "Total max pixel"},
        ],
    },
    {
        "key": "throughput",
        "label": "Throughput",
        "options": [
            {"key": "atmosphere", "label": "Atmospheric transmission"},
            {"key": "telescope", "label": "Telescope reflectivity"},
            {"key": "instrument", "label": "Instrument efficiency"},
            {"key": "encircledenergy", "label": "Encircled energy"},
            {"key": "detector", "label": "Detector QE"},
            {"key": "totalinclsky", "label": "Total throughput incl. sky"},
        ],
    },
    {
        "key": "dispersion",
        "label": "Dispersion",
        "options": [
            {"key": "dispersion", "label": "Spectral dispersion per pixel"},
        ],
    },
    {
        "key": "psf",
        "label": "PSF",
        "options": [
            {"key": "psf", "label": "Point Spread Function"},
        ],
    },
]

# ---------------------------------------------------------------------------
# Full config dict (injected into the HTML template as JSON)
# ---------------------------------------------------------------------------
ERIS_FORM_CONFIG = {
    "catalogs": {
        "MARCS": {
            "label": "MARCS",
            "id_format": "Teff:logg",
            "params": [
                {"key": "teff", "label": "Teff [K]", "values": MARCS_TEFF},
                {"key": "logg", "label": "log(g)", "values": MARCS_LOGG},
            ],
        },
        "PHOENIX": {
            "label": "PHOENIX",
            "id_format": "Teff:logg",
            "params": [
                {"key": "teff", "label": "Teff [K]", "values": PHOENIX_TEFF},
                {"key": "logg", "label": "log(g)", "values": PHOENIX_LOGG},
            ],
        },
        "SWIRE": {
            "label": "SWIRE",
            "id_format": "name",
            "templates": SWIRE_TEMPLATES,
        },
    },
    "magband_groups": MAGBAND_GROUPS,
    "turbulence_categories": TURBULENCE_CATEGORIES,
    "aperture_pixels": APERTURE_PIXELS,
    "ifs_gratings": IFS_GRATINGS,
    "ifs_spaxels": IFS_SPAXELS,
    "nix_cameras": NIX_CAMERAS,
    "nix_filters": NIX_FILTERS,
    "app_filters": APP_FILTERS,
    "nix_pupil_img": NIX_PUPIL_IMG,
    "nix_pupil_sam": NIX_PUPIL_SAM,
    "output_groups": OUTPUT_GROUPS,
    "defaults": {
        "morphologytype": "point",
        "sedtype": "spectrum",
        "spectrumtype": "template",
        "catalog": "MARCS",
        "teff": 5750,
        "logg": 4.5,
        "extinctionav": 0,
        "magband": "V",
        "mag": 10,
        "magsys": "vega",
        "airmass": 1.2,
        "fli": 0.5,
        "moonDistance": 30,
        "waterVapour": 2.5,
        "turbulence_category": 50,
        "separation": 0,
        "aperturepix": 9,
        "tts_mag": 12,
        "observingMode": "ifs",
        "aoMode": "lgs",
        "grating": "J_low",
        "spaxel": "25mas",
        "readout": "SLOW",
        "camera": "13mas-JHK",
        "pupil": "noND",
        "filter": "J",
        "dit": 2,
        "ndit": 1,
    },
}
