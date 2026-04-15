"""
Tests for etc_sky_to_skycalc and the skycalc_ipy integration.

Unit tests verify the parameter mapping logic (no network calls).
Integration tests (marked with ``@skycalc_required``) call the ESO
skycalc microservice and check the returned data.
"""

import math
import pytest

from elvis.sky.converter import (
    etc_sky_to_skycalc,
    _fli_to_moon_sun_sep,
    _fli_to_moon_alt,
    _nearest_pwv,
)


# =========================================================================
#  FLI → Moon parameter conversion tests
# =========================================================================

class TestFLIConversion:
    """Verify FLI → moon_sun_sep and moon_alt conversions."""

    def test_new_moon_fli_0(self):
        """FLI=0 (new moon): moon_sun_sep ≈ 0°."""
        sep = _fli_to_moon_sun_sep(0.0)
        assert sep == pytest.approx(0.0, abs=0.1)

    def test_full_moon_fli_1(self):
        """FLI=1 (full moon): moon_sun_sep ≈ 180°."""
        sep = _fli_to_moon_sun_sep(1.0)
        assert sep == pytest.approx(180.0, abs=0.1)

    def test_half_moon_fli_05(self):
        """FLI=0.5 (quarter moon): moon_sun_sep ≈ 90°."""
        sep = _fli_to_moon_sun_sep(0.5)
        assert sep == pytest.approx(90.0, abs=0.1)

    def test_fli_roundtrip(self):
        """Converting FLI→sep→FLI gives back the original value."""
        for fli in [0.0, 0.1, 0.25, 0.5, 0.75, 1.0]:
            sep = _fli_to_moon_sun_sep(fli)
            fli_back = (1.0 - math.cos(math.radians(sep))) / 2.0
            assert fli_back == pytest.approx(fli, abs=1e-10)

    def test_fli_clamped_below_zero(self):
        """FLI < 0 is clamped to 0."""
        sep = _fli_to_moon_sun_sep(-0.5)
        assert sep == pytest.approx(0.0, abs=0.1)

    def test_fli_clamped_above_one(self):
        """FLI > 1 is clamped to 1."""
        sep = _fli_to_moon_sun_sep(1.5)
        assert sep == pytest.approx(180.0, abs=0.1)

    def test_moon_alt_new_moon(self):
        """FLI=0 → moon below horizon (−90°)."""
        assert _fli_to_moon_alt(0.0) == pytest.approx(-90.0)

    def test_moon_alt_full_moon(self):
        """FLI=1 → moon at 45°."""
        assert _fli_to_moon_alt(1.0) == pytest.approx(45.0)

    def test_moon_alt_half(self):
        """FLI=0.5 → above horizon."""
        alt = _fli_to_moon_alt(0.5)
        assert alt > 0


# =========================================================================
#  PWV snapping tests
# =========================================================================

class TestPWVNearest:
    """Verify PWV is snapped to the nearest valid step."""

    def test_exact_match(self):
        assert _nearest_pwv(3.5) == 3.5

    def test_snap_down(self):
        assert _nearest_pwv(4.0) == 3.5

    def test_snap_up(self):
        assert _nearest_pwv(6.0) == 5.0

    def test_very_low(self):
        assert _nearest_pwv(0.1) == 0.5  # 0.1 is closest to 0.5

    def test_very_high(self):
        assert _nearest_pwv(100.0) == 20.0


# =========================================================================
#  ETC JSON → skycalc parameter dict tests
# =========================================================================

class TestETCSkyMapping:
    """Verify ETC JSON sky section → skycalc parameter dict."""

    def test_format_a_basic(self):
        """Format A (web UI) with all fields present."""
        etc = {
            "sky": {
                "airmass": 1.5,
                "fli": 0.5,
                "waterVapour": 5.0,
                "moonDistance": 60,
            }
        }
        p = etc_sky_to_skycalc(etc)
        assert p["airmass"] == 1.5
        assert p["pwv"] == 5.0
        assert p["moon_sun_sep"] == pytest.approx(90.0, abs=0.1)
        assert p["moon_target_sep"] == 60.0
        assert p["pwv_mode"] == "pwv"
        assert p["observatory"] == "paranal"

    def test_format_b_basic(self):
        """Format B (programmatic) with alternative key names."""
        etc = {
            "sky": {
                "airmass": 1.1,
                "moon_fli": 0.3,
                "pwv": 2.5,
            }
        }
        p = etc_sky_to_skycalc(etc)
        assert p["airmass"] == 1.1
        assert p["pwv"] == 2.5
        assert p["moon_sun_sep"] > 0
        # moonDistance not in Format B → default 45°
        assert p["moon_target_sep"] == 45.0

    def test_defaults_when_empty(self):
        """Missing keys use sensible defaults."""
        p = etc_sky_to_skycalc({"sky": {}})
        assert p["airmass"] == 1.2
        assert p["pwv"] == 3.5  # nearest to default 3.5
        assert p["moon_target_sep"] == 45.0

    def test_sky_only_dict(self):
        """Accepts just the sky sub-dict (no 'sky' wrapper key)."""
        p = etc_sky_to_skycalc({"airmass": 2.0, "fli": 1.0, "waterVapour": 10})
        assert p["airmass"] == 2.0
        assert p["pwv"] == 10.0
        assert p["moon_sun_sep"] == pytest.approx(180.0, abs=0.1)

    def test_airmass_range(self):
        """Airmass values at the extremes are passed through."""
        p_low = etc_sky_to_skycalc({"sky": {"airmass": 1.0}})
        p_high = etc_sky_to_skycalc({"sky": {"airmass": 3.0}})
        assert p_low["airmass"] == 1.0
        assert p_high["airmass"] == 3.0

    def test_pwv_snapped(self):
        """PWV is snapped to nearest valid step."""
        p = etc_sky_to_skycalc({"sky": {"waterVapour": 4.2}})
        assert p["pwv"] == 3.5  # nearest valid step

    def test_fli_zero(self):
        """FLI=0 (new moon) → moon disabled, sep ≈ 0."""
        p = etc_sky_to_skycalc({"sky": {"fli": 0}})
        assert p["moon_sun_sep"] == pytest.approx(0.0, abs=0.1)
        assert p["incl_moon"] == "N"

    def test_fli_one(self):
        """FLI=1 (full moon) produces moon_sun_sep ≈ 180."""
        p = etc_sky_to_skycalc({"sky": {"fli": 1}})
        assert p["moon_sun_sep"] == pytest.approx(180.0, abs=0.1)
        assert p["moon_alt"] == pytest.approx(45.0, abs=0.1)
        assert p["incl_moon"] == "Y"

    def test_incl_moon_on_when_fli_positive(self):
        p = etc_sky_to_skycalc({"sky": {"fli": 0.5}})
        assert p["incl_moon"] == "Y"

    def test_real_eris_inputform(self):
        """Parse the actual eris_etc_inputform.json sky section."""
        import json
        from pathlib import Path
        fpath = Path("D:/Repos/ELVIS/misc/ETC_input_json/eris_etc_inputform.json")
        if not fpath.exists():
            pytest.skip("ETC input JSON not found")
        with open(fpath) as f:
            etc = json.load(f)
        p = etc_sky_to_skycalc(etc)
        assert 1.0 <= p["airmass"] <= 3.0
        assert p["pwv"] in [-1, 0.5, 1, 1.5, 2.5, 3.5, 5, 7.5, 10, 20]
        assert 0.0 <= p["moon_sun_sep"] <= 180.0
        assert 0.0 <= p["moon_target_sep"] <= 180.0

    def test_real_eris_nix(self):
        """Parse the actual eris_nix.json sky section."""
        import json
        from pathlib import Path
        fpath = Path("D:/Repos/ELVIS/misc/ETC_input_json/eris_nix.json")
        if not fpath.exists():
            pytest.skip("ETC input JSON not found")
        with open(fpath) as f:
            etc = json.load(f)
        p = etc_sky_to_skycalc(etc)
        assert p["airmass"] == 1.1
        assert p["pwv"] == 2.5


# =========================================================================
#  skycalc_ipy integration tests
#  Require skycalc_ipy installed and network access to ESO microservice.
# =========================================================================

try:
    from skycalc_ipy.ui import SkyCalc as _SkyCalc
    HAS_SKYCALC = True
except ImportError:
    HAS_SKYCALC = False

skycalc_required = pytest.mark.skipif(
    not HAS_SKYCALC, reason="skycalc_ipy not installed"
)


@skycalc_required
class TestSkyCalcYAMLString:
    """Verify YAML string can initialise a SkyCalc object."""

    def test_yaml_string_loads(self):
        from elvis.sky.converter import to_skycalc_yaml
        params = etc_sky_to_skycalc({"sky": {"airmass": 1.3, "fli": 0.5}})
        yml = to_skycalc_yaml(params)
        assert "airmass" in yml
        assert "pwv" in yml

    def test_apply_to_skycalc_creates_object(self):
        from elvis.sky.converter import apply_to_skycalc
        sc = apply_to_skycalc({"sky": {"airmass": 1.5, "fli": 0.8, "waterVapour": 5}})
        assert sc["airmass"] == 1.5
        assert sc["pwv"] == 5.0
        assert sc["moon_sun_sep"] == pytest.approx(
            _fli_to_moon_sun_sep(0.8), abs=0.01
        )

    def test_values_roundtrip_through_yaml(self):
        """Values survive YAML serialisation → SkyCalc load."""
        from elvis.sky.converter import to_skycalc_yaml
        params = etc_sky_to_skycalc({
            "sky": {"airmass": 2.0, "fli": 0.25, "waterVapour": 1.5}
        })
        yml = to_skycalc_yaml(params)
        sc = _SkyCalc(ipt_str=yml)
        assert sc["airmass"] == 2.0
        assert sc["pwv"] == 1.5


@skycalc_required
@pytest.mark.network
class TestSkyCalcMicroservice:
    """Call the ESO skycalc microservice and verify the response.

    These tests make real HTTP calls. Mark with ``pytest -m network``
    to select, or ``pytest -m 'not network'`` to skip.
    """

    def test_default_sky_spectrum(self):
        """Default parameters return a table with lam, trans, flux."""
        from elvis.sky.converter import apply_to_skycalc
        sc = apply_to_skycalc({"sky": {"airmass": 1.2, "fli": 0.5}})
        tbl = sc.get_sky_spectrum(return_type="table")
        assert "lam" in tbl.colnames
        assert "trans" in tbl.colnames
        assert "flux" in tbl.colnames
        assert len(tbl) > 100

    def test_transmission_in_valid_range(self):
        """Atmospheric transmission is between 0 and 1."""
        from elvis.sky.converter import apply_to_skycalc
        sc = apply_to_skycalc({"sky": {"airmass": 1.0, "fli": 0.0}})
        tbl = sc.get_sky_spectrum(return_type="table")
        assert all(tbl["trans"] >= 0)
        assert all(tbl["trans"] <= 1.001)  # small float tolerance

    def test_higher_airmass_lower_transmission(self):
        """Higher airmass should reduce mean transmission."""
        from elvis.sky.converter import apply_to_skycalc
        import numpy as np

        sc_low = apply_to_skycalc({"sky": {"airmass": 1.0, "fli": 0.0}})
        tbl_low = sc_low.get_sky_spectrum(return_type="table")

        sc_high = apply_to_skycalc({"sky": {"airmass": 2.5, "fli": 0.0}})
        tbl_high = sc_high.get_sky_spectrum(return_type="table")

        assert np.mean(tbl_low["trans"]) > np.mean(tbl_high["trans"])

    def test_full_moon_brighter_sky(self):
        """Full moon (FLI=1) should produce more sky emission than dim moon."""
        from elvis.sky.converter import apply_to_skycalc
        import numpy as np

        sc_dim = apply_to_skycalc({
            "sky": {"airmass": 1.2, "fli": 0.1, "moonDistance": 90}
        })
        tbl_dim = sc_dim.get_sky_spectrum(return_type="table")

        sc_full = apply_to_skycalc({
            "sky": {"airmass": 1.2, "fli": 1.0, "moonDistance": 30}
        })
        tbl_full = sc_full.get_sky_spectrum(return_type="table")

        assert np.mean(tbl_full["flux"]) > np.mean(tbl_dim["flux"])

    def test_higher_pwv_affects_spectrum(self):
        """Different PWV values produce different spectra."""
        from elvis.sky.converter import apply_to_skycalc
        import numpy as np

        sc_dry = apply_to_skycalc({"sky": {"airmass": 1.0, "pwv": 0.5}})
        tbl_dry = sc_dry.get_sky_spectrum(return_type="table")

        sc_wet = apply_to_skycalc({"sky": {"airmass": 1.0, "pwv": 10.0}})
        tbl_wet = sc_wet.get_sky_spectrum(return_type="table")

        # Spectra should differ (especially in water absorption bands)
        assert not np.allclose(tbl_dry["trans"], tbl_wet["trans"])

    def test_eris_inputform_produces_spectrum(self):
        """Full eris_etc_inputform.json sky section → valid spectrum."""
        import json
        from pathlib import Path
        from elvis.sky.converter import apply_to_skycalc

        fpath = Path("D:/Repos/ELVIS/misc/ETC_input_json/eris_etc_inputform.json")
        if not fpath.exists():
            pytest.skip("ETC input JSON not found")
        with open(fpath) as f:
            etc = json.load(f)

        sc = apply_to_skycalc(etc)
        tbl = sc.get_sky_spectrum(return_type="table")
        assert len(tbl) > 100
        assert all(tbl["trans"] >= 0)
