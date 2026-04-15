"""
HAWK-I ETC 2.0 form configuration.

Single source of truth for all dropdown values, defaults, and visibility rules
used by the HAWK-I ETC JSON form builder.

Sources:
    - ESO HAWK-I ETC v1.0 form parameters
    - misc/ETC_input_json/*.json (v2.0 schema patterns)
    - elvis/etc_form/config.py (shared catalog / band definitions)
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
# Turbulence categories (HAWK-I: includes 100% since seeing-limited)
# ---------------------------------------------------------------------------
TURBULENCE_CATEGORIES = [
    {"value": 10, "label": "10% (seeing \u2264 0.6\")"},
    {"value": 20, "label": "20% (seeing \u2264 0.7\")"},
    {"value": 30, "label": "30% (seeing \u2264 0.8\")"},
    {"value": 50, "label": "50% (seeing \u2264 1.0\")"},
    {"value": 70, "label": "70% (seeing \u2264 1.15\")"},
    {"value": 85, "label": "85% (seeing \u2264 1.4\")"},
    {"value": 100, "label": "100% (unconstrained)"},
]

# ---------------------------------------------------------------------------
# Aperture pixel options
# ---------------------------------------------------------------------------
APERTURE_PIXELS = [1, 3, 5, 7, 9, 11, 13, 15, 17, 21, 35, 55, 89]

# ---------------------------------------------------------------------------
# HAWK-I Filters
# ---------------------------------------------------------------------------
HAWKI_FILTERS = [
    # Broadband
    {"value": "Y", "label": "Y (1.021 \u00b5m)", "type": "broadband"},
    {"value": "J", "label": "J (1.258 \u00b5m)", "type": "broadband"},
    {"value": "H", "label": "H (1.620 \u00b5m)", "type": "broadband"},
    {"value": "Ks", "label": "Ks (2.146 \u00b5m)", "type": "broadband"},
    # Narrowband
    {"value": "NB0984", "label": "NB0984 (0.984 \u00b5m)", "type": "narrowband"},
    {"value": "NB1060", "label": "NB1060 (1.060 \u00b5m)", "type": "narrowband"},
    {"value": "NB1190", "label": "NB1190 (1.190 \u00b5m)", "type": "narrowband"},
    {"value": "NB2090", "label": "NB2090 (2.090 \u00b5m)", "type": "narrowband"},
    # Molecular
    {"value": "CH4", "label": "CH4 (1.573 \u00b5m)", "type": "molecular"},
    {"value": "H2", "label": "H2 (2.124 \u00b5m)", "type": "molecular"},
    {"value": "BrGamma", "label": "Br\u03b3 (2.165 \u00b5m)", "type": "molecular"},
]

# ---------------------------------------------------------------------------
# HAWK-I AO modes
# ---------------------------------------------------------------------------
HAWKI_AO_MODES = [
    {"value": "noao", "label": "No AO (seeing-limited)"},
    {"value": "tts", "label": "TTS (tip-tilt sensor)"},
]

# ---------------------------------------------------------------------------
# Output plot options (same structure as ERIS)
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
HAWKI_FORM_CONFIG = {
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
    "hawki_filters": HAWKI_FILTERS,
    "hawki_ao_modes": HAWKI_AO_MODES,
    "output_groups": OUTPUT_GROUPS,
    "defaults": {
        "morphologytype": "point",
        "sedtype": "spectrum",
        "spectrumtype": "template",
        "catalog": "MARCS",
        "teff": 5750,
        "logg": 4.5,
        "extinctionav": 0,
        "magband": "K",
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
        "aoMode": "noao",
        "filter": "Ks",
        "dit": 10,
        "ndit": 6,
    },
}
