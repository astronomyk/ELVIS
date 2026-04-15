"""
Tests for etc_target_to_scopesim_yaml and the full conversion pipeline.

Covers every ETC target option: morphology types, SED types, template
catalogs, brightness bands, and edge cases.
"""

import pytest
from astropy import units as u

from elvis.source.converter import (
    etc_target_to_scopesim_yaml,
    to_yaml_string,
    to_scopesim_target,
    _BAND_MAP,
)


# =========================================================================
#  Helper to build a full ETC JSON dict from overrides
# =========================================================================

def _etc_json(
    morphologytype="point",
    extendedtype=None,
    sersic_index=None,
    sersic_radius=None,
    sedtype="spectrum",
    spectrumtype="template",
    catalog="MARCS",
    sed_id="5750:4.5",
    temperature=None,
    exponent=None,
    em_lambda=None,
    em_fwhm=None,
    extinctionav=0,
    magband="V",
    mag=10,
    magsys="vega",
):
    """Build a minimal ETC JSON dict with sensible defaults."""
    morph = {"morphologytype": morphologytype}
    if extendedtype:
        morph["extendedtype"] = extendedtype
    if sersic_index is not None:
        morph["index"] = sersic_index
    if sersic_radius is not None:
        morph["radius"] = sersic_radius

    sed = {"sedtype": sedtype, "extinctionav": extinctionav}
    if sedtype == "spectrum":
        params = {}
        if spectrumtype == "template":
            params = {"catalog": catalog, "id": sed_id}
        elif spectrumtype == "blackbody":
            params = {"temperature": temperature or 5000}
        elif spectrumtype == "powerlaw":
            params = {"exponent": exponent or 0}
        sed["spectrum"] = {"spectrumtype": spectrumtype, "params": params}
    elif sedtype == "emissionline":
        sed["emissionline"] = {
            "params": {"lambda": em_lambda or 1000, "fwhm": em_fwhm or 1}
        }

    return {
        "target": {
            "morphology": morph,
            "sed": sed,
            "brightness": {
                "brightnesstype": "mag",
                "magband": magband,
                "mag": mag,
                "magsys": magsys,
            },
        },
        "instrumentName": "eris",
    }


# =========================================================================
#  MORPHOLOGY TESTS
# =========================================================================

class TestMorphologyMapping:
    """Verify morphology → target_class mapping."""

    def test_point_source(self):
        result = etc_target_to_scopesim_yaml(_etc_json(morphologytype="point"))
        assert result["target_class"] == "Star"
        assert result["position"] == [0, 0]

    def test_sersic_extended(self):
        result = etc_target_to_scopesim_yaml(
            _etc_json(
                morphologytype="extended",
                extendedtype="sersic",
                sersic_index=4.0,
                sersic_radius=1.5,
            )
        )
        assert result["target_class"] == "Sersic"
        assert result["params"]["n"] == 4.0
        assert result["params"]["r_eff"].value == 1.5
        assert result["params"]["r_eff"].unit == u.arcsec

    def test_sersic_default_params(self):
        result = etc_target_to_scopesim_yaml(
            _etc_json(
                morphologytype="extended",
                extendedtype="sersic",
            )
        )
        assert result["params"]["n"] == 4  # default
        assert result["params"]["r_eff"].value == 0.5  # default
        assert result["params"]["ellip"] == 0.0
        assert result["params"]["theta"].value == 0.0

    def test_infinite_extended_raises(self):
        with pytest.raises(ValueError, match="Infinite extended"):
            etc_target_to_scopesim_yaml(
                _etc_json(morphologytype="extended", extendedtype="infinite")
            )

    def test_unknown_morphtype_raises(self):
        with pytest.raises(ValueError, match="Unknown morphologytype"):
            etc_target_to_scopesim_yaml(_etc_json(morphologytype="blob"))


# =========================================================================
#  SED / SPECTRUM TESTS
# =========================================================================

class TestSEDMapping:
    """Verify SED → spectrum string mapping."""

    # -- Template catalogs --

    def test_marcs_template(self):
        result = etc_target_to_scopesim_yaml(
            _etc_json(catalog="MARCS", sed_id="5750:4.5")
        )
        assert result["spectrum"] == "blackbody:5750 K"

    def test_marcs_cool_star(self):
        result = etc_target_to_scopesim_yaml(
            _etc_json(catalog="MARCS", sed_id="3000:3.0")
        )
        assert result["spectrum"] == "blackbody:3000 K"

    def test_marcs_hot_star(self):
        result = etc_target_to_scopesim_yaml(
            _etc_json(catalog="MARCS", sed_id="8000:5.0")
        )
        assert result["spectrum"] == "blackbody:8000 K"

    def test_phoenix_template(self):
        result = etc_target_to_scopesim_yaml(
            _etc_json(catalog="PHOENIX", sed_id="2300:5.5")
        )
        assert result["spectrum"] == "blackbody:2300 K"

    def test_phoenix_hot(self):
        result = etc_target_to_scopesim_yaml(
            _etc_json(catalog="PHOENIX", sed_id="12000:4.0")
        )
        assert result["spectrum"] == "blackbody:12000 K"

    def test_swire_template(self):
        result = etc_target_to_scopesim_yaml(
            _etc_json(catalog="SWIRE", sed_id="13 Gyr old elliptical")
        )
        assert result["spectrum"] == "blackbody:5000 K"

    def test_swire_agn(self):
        result = etc_target_to_scopesim_yaml(
            _etc_json(catalog="SWIRE", sed_id="AGN QSO1")
        )
        assert result["spectrum"] == "blackbody:5000 K"

    # -- Synthetic spectra --

    def test_blackbody(self):
        result = etc_target_to_scopesim_yaml(
            _etc_json(spectrumtype="blackbody", temperature=3500)
        )
        assert result["spectrum"] == "blackbody:3500 K"

    def test_blackbody_hot(self):
        result = etc_target_to_scopesim_yaml(
            _etc_json(spectrumtype="blackbody", temperature=50000)
        )
        assert result["spectrum"] == "blackbody:50000 K"

    def test_powerlaw(self):
        result = etc_target_to_scopesim_yaml(
            _etc_json(spectrumtype="powerlaw", exponent=-1.5)
        )
        assert result["spectrum"] == "powerlaw:-1.5"

    def test_powerlaw_flat(self):
        result = etc_target_to_scopesim_yaml(
            _etc_json(spectrumtype="powerlaw", exponent=0)
        )
        assert result["spectrum"] == "powerlaw:0"

    # -- Unsupported types --

    def test_emissionline_raises(self):
        with pytest.raises(ValueError, match="Emission-line"):
            etc_target_to_scopesim_yaml(
                _etc_json(sedtype="emissionline", em_lambda=2000, em_fwhm=5)
            )

    def test_upload_raises(self):
        with pytest.raises(ValueError, match="Uploaded spectra"):
            etc_target_to_scopesim_yaml(
                _etc_json(spectrumtype="upload")
            )


# =========================================================================
#  BRIGHTNESS / MAGNITUDE BAND TESTS
# =========================================================================

class TestBrightnessMapping:
    """Verify magnitude band mapping and brightness tuple output."""

    def test_standard_band_passthrough(self):
        for band in ["U", "B", "V", "R", "I", "J", "H", "K"]:
            result = etc_target_to_scopesim_yaml(_etc_json(magband=band, mag=15))
            b, m = result["brightness"]
            assert b == band
            assert m.value == 15
            assert m.unit == u.mag

    def test_gaia_band_mapping(self):
        result = etc_target_to_scopesim_yaml(_etc_json(magband="gaia_G"))
        assert result["brightness"][0] == "V"

    def test_sdss_band_mapping(self):
        result = etc_target_to_scopesim_yaml(_etc_json(magband="sdss_r"))
        assert result["brightness"][0] == "R"

    def test_vista_band_mapping(self):
        result = etc_target_to_scopesim_yaml(_etc_json(magband="VISTA_Ks"))
        assert result["brightness"][0] == "K"

    def test_lsst_band_mapping(self):
        result = etc_target_to_scopesim_yaml(_etc_json(magband="lsst_y"))
        assert result["brightness"][0] == "Y"

    def test_fourmost_band_mapping(self):
        result = etc_target_to_scopesim_yaml(_etc_json(magband="4MOST_Johnson_B"))
        assert result["brightness"][0] == "B"

    def test_all_bands_have_mapping(self):
        """Every band in the ETC form config has a mapping."""
        from elvis.etc_form.config import MAGBAND_GROUPS
        all_bands = [
            opt["value"]
            for grp in MAGBAND_GROUPS
            for opt in grp["options"]
        ]
        for band in all_bands:
            assert band in _BAND_MAP, f"Missing mapping for {band}"

    def test_magnitude_value_preserved(self):
        result = etc_target_to_scopesim_yaml(_etc_json(mag=22.5))
        assert result["brightness"][1].value == 22.5


# =========================================================================
#  YAML STRING SERIALISATION TESTS
# =========================================================================

class TestYAMLString:
    """Verify to_yaml_string produces parseable YAML."""

    def test_star_yaml(self):
        d = etc_target_to_scopesim_yaml(_etc_json())
        s = to_yaml_string(d)
        assert s.startswith("!Star\n")
        assert 'spectrum: "blackbody:5750 K"' in s
        assert 'brightness: ["V", 10.0 mag]' in s

    def test_sersic_yaml(self):
        d = etc_target_to_scopesim_yaml(
            _etc_json(
                morphologytype="extended",
                extendedtype="sersic",
                sersic_index=2.5,
                sersic_radius=3.0,
            )
        )
        s = to_yaml_string(d)
        assert s.startswith("!Sersic\n")
        assert "r_eff: 3.0 arcsec" in s
        assert "n: 2.5" in s

    def test_yaml_string_not_empty(self):
        d = etc_target_to_scopesim_yaml(_etc_json())
        s = to_yaml_string(d)
        assert len(s) > 20


# =========================================================================
#  COMBINED ETC JSON FORMAT TESTS
# =========================================================================

class TestFullETCJSON:
    """Test conversion with full ETC JSON dicts (both Format A and B)."""

    def test_format_a_ifs(self):
        """Format A: web UI style (ifs_lgs)."""
        etc = {
            "target": {
                "morphology": {"morphologytype": "point"},
                "sed": {
                    "sedtype": "spectrum",
                    "spectrum": {
                        "spectrumtype": "template",
                        "params": {"catalog": "MARCS", "id": "5750:4.5"},
                    },
                    "extinctionav": 0,
                },
                "brightness": {
                    "brightnesstype": "mag",
                    "magband": "V",
                    "mag": 10,
                    "magsys": "vega",
                },
            },
            "sky": {"airmass": 1.2, "fli": 1, "waterVapour": 30},
            "instrument": {"ins_configuration": "ifs_lgs"},
            "instrumentName": "eris",
        }
        result = etc_target_to_scopesim_yaml(etc)
        assert result["target_class"] == "Star"
        assert result["spectrum"] == "blackbody:5750 K"

    def test_format_b_nix(self):
        """Format B: programmatic style (nixIMG)."""
        etc = {
            "target": {
                "morphology": {"morphologytype": "point"},
                "sed": {
                    "sedtype": "spectrum",
                    "spectrum": {
                        "spectrumtype": "template",
                        "params": {"catalog": "MARCS", "id": "5750:4.5"},
                    },
                    "extinctionav": 0,
                },
                "brightness": {
                    "brightnesstype": "mag",
                    "magband": "V",
                    "mag": 10,
                    "magsys": "vega",
                },
            },
            "instrument": {"ins_configuration": "nixIMG"},
            "instrumentName": "eris",
        }
        result = etc_target_to_scopesim_yaml(etc)
        assert result["target_class"] == "Star"

    def test_target_only_dict(self):
        """Function accepts just the target sub-dict (no 'target' key)."""
        target_only = {
            "morphology": {"morphologytype": "point"},
            "sed": {
                "sedtype": "spectrum",
                "spectrum": {
                    "spectrumtype": "blackbody",
                    "params": {"temperature": 8000},
                },
            },
            "brightness": {"magband": "K", "mag": 18, "magsys": "vega"},
        }
        result = etc_target_to_scopesim_yaml(target_only)
        assert result["spectrum"] == "blackbody:8000 K"
        assert result["brightness"][0] == "K"


# =========================================================================
#  SCOPESIM-TARGETS INTEGRATION TESTS
#  These tests require scopesim + scopesim-targets to be installed.
#  They are marked with @pytest.mark.scopesim so they can be skipped.
# =========================================================================

try:
    from scopesim_targets.point_source import Star
    from scopesim_targets.extended_source import Sersic
    from scopesim.source.source import Source
    HAS_SCOPESIM = True
except ImportError:
    HAS_SCOPESIM = False

scopesim_required = pytest.mark.skipif(
    not HAS_SCOPESIM,
    reason="scopesim and scopesim-targets not installed"
)


@scopesim_required
class TestScopesimStarIntegration:
    """Point source → Star → Source object pipeline."""

    def test_marcs_star_creates_source(self):
        d = etc_target_to_scopesim_yaml(_etc_json(catalog="MARCS", sed_id="5750:4.5"))
        tgt = to_scopesim_target(d)
        src = tgt.to_source()
        assert isinstance(src, Source)
        assert len(src.fields) == 1

    def test_source_has_table_field(self):
        d = etc_target_to_scopesim_yaml(_etc_json())
        src = to_scopesim_target(d).to_source()
        tbl = src.fields[0].field
        assert "x" in tbl.colnames
        assert "y" in tbl.colnames
        assert "ref" in tbl.colnames
        assert "weight" in tbl.colnames
        assert len(tbl) == 1  # single point source

    def test_source_position_at_origin(self):
        d = etc_target_to_scopesim_yaml(_etc_json())
        src = to_scopesim_target(d).to_source()
        tbl = src.fields[0].field
        assert abs(tbl["x"][0]) < 1e-6
        assert abs(tbl["y"][0]) < 1e-6

    def test_source_has_spectrum(self):
        d = etc_target_to_scopesim_yaml(_etc_json())
        src = to_scopesim_target(d).to_source()
        spectra = src.fields[0].spectra
        assert len(spectra) >= 1
        assert 0 in spectra  # ref=0 must have a spectrum

    def test_phoenix_star_creates_source(self):
        d = etc_target_to_scopesim_yaml(
            _etc_json(catalog="PHOENIX", sed_id="4500:4.0")
        )
        src = to_scopesim_target(d).to_source()
        assert isinstance(src, Source)

    def test_blackbody_star_creates_source(self):
        d = etc_target_to_scopesim_yaml(
            _etc_json(spectrumtype="blackbody", temperature=10000)
        )
        src = to_scopesim_target(d).to_source()
        assert isinstance(src, Source)

    def test_magnitude_in_different_bands(self):
        """Star created in each standard band produces a valid Source."""
        for band in ["V", "J", "H", "K"]:
            d = etc_target_to_scopesim_yaml(_etc_json(magband=band, mag=15))
            src = to_scopesim_target(d).to_source()
            assert isinstance(src, Source)

    def test_bright_star(self):
        d = etc_target_to_scopesim_yaml(_etc_json(mag=0))
        src = to_scopesim_target(d).to_source()
        assert isinstance(src, Source)

    def test_faint_star(self):
        d = etc_target_to_scopesim_yaml(_etc_json(mag=30))
        src = to_scopesim_target(d).to_source()
        assert isinstance(src, Source)


@scopesim_required
class TestScopesimSersicIntegration:
    """Sersic extended source → Source object pipeline."""

    def test_sersic_creates_source(self):
        d = etc_target_to_scopesim_yaml(
            _etc_json(
                morphologytype="extended",
                extendedtype="sersic",
                sersic_index=4.0,
                sersic_radius=2.0,
                spectrumtype="blackbody",
                temperature=5000,
                magband="K",
                mag=18,
            )
        )
        tgt = to_scopesim_target(d)
        # Sersic.to_source() requires an optical_train argument;
        # verify the target object was constructed correctly instead
        assert isinstance(tgt, Sersic)
        assert tgt.brightness is not None
        assert tgt.spectrum is not None

    def test_sersic_exponential_disk(self):
        """n=1 Sersic (exponential disk)."""
        d = etc_target_to_scopesim_yaml(
            _etc_json(
                morphologytype="extended",
                extendedtype="sersic",
                sersic_index=1.0,
                sersic_radius=5.0,
            )
        )
        tgt = to_scopesim_target(d)
        assert isinstance(tgt, Sersic)

    def test_sersic_de_vaucouleurs(self):
        """n=4 Sersic (de Vaucouleurs profile)."""
        d = etc_target_to_scopesim_yaml(
            _etc_json(
                morphologytype="extended",
                extendedtype="sersic",
                sersic_index=4.0,
                sersic_radius=1.0,
            )
        )
        tgt = to_scopesim_target(d)
        assert isinstance(tgt, Sersic)


@scopesim_required
class TestScopesimRoundTrip:
    """Verify that Source internal data matches ETC JSON input."""

    def test_star_weight_is_positive(self):
        d = etc_target_to_scopesim_yaml(_etc_json(mag=10))
        src = to_scopesim_target(d).to_source()
        tbl = src.fields[0].field
        assert tbl["weight"][0] > 0

    def test_star_ref_matches_spectra_keys(self):
        d = etc_target_to_scopesim_yaml(_etc_json())
        src = to_scopesim_target(d).to_source()
        tbl = src.fields[0].field
        spectra = src.fields[0].spectra
        for row in tbl:
            assert row["ref"] in spectra

    def test_swire_star_creates_source(self):
        d = etc_target_to_scopesim_yaml(
            _etc_json(catalog="SWIRE", sed_id="Spiral a")
        )
        src = to_scopesim_target(d).to_source()
        assert isinstance(src, Source)
