"""Tests for the ELVIS simulation pipeline."""

import copy
from unittest.mock import patch

import pytest
from astropy.io import fits

from elvis.pipeline import (
    run_simulation,
    _create_source,
    _fallback_header_only,
    _readout_to_hdulist,
)
from elvis.opticaltrain.factory import create_optical_train, INSTRUMENT_MAP

# ---------------------------------------------------------------------------
# Check optional dependencies for skip guards
# ---------------------------------------------------------------------------
try:
    import scopesim
    scopesim.rc.__config__["!SIM.file.local_packages_path"] = "D:/Repos/irdb"
    _opt = create_optical_train("hawki")
    HAS_SCOPESIM = _opt is not None
    del _opt
except Exception:
    HAS_SCOPESIM = False

requires_scopesim = pytest.mark.skipif(
    not HAS_SCOPESIM,
    reason="ScopeSim or IRDB packages not available",
)


# ---------------------------------------------------------------------------
# Sample ETC JSON payloads
# ---------------------------------------------------------------------------

POINT_SOURCE_JSON = {
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
    "sky": {"airmass": 1.2, "fli": 0.5, "waterVapour": 2.5, "moonDistance": 30},
    "seeing": {"turbulence_category": 50, "aperturepix": 9, "separation": 0},
    "instrument": {"ins_configuration": "img_noao", "INS.FILT.NAME": "Ks"},
    "timesnr": {"DET.DIT": 10, "DET.NDIT": 6},
    "output": {},
    "instrumentName": "hawki",
}

BLACKBODY_POINT_JSON = {
    "target": {
        "morphology": {"morphologytype": "point"},
        "sed": {
            "sedtype": "spectrum",
            "spectrum": {
                "spectrumtype": "blackbody",
                "params": {"temperature": 3000},
            },
            "extinctionav": 0,
        },
        "brightness": {
            "brightnesstype": "mag",
            "magband": "H",
            "mag": 18,
            "magsys": "AB",
        },
    },
    "instrumentName": "hawki",
}

SERSIC_SOURCE_JSON = {
    "target": {
        "morphology": {
            "morphologytype": "extended",
            "extendedtype": "sersic",
            "index": 4,
            "radius": 1.0,
        },
        "sed": {
            "sedtype": "spectrum",
            "spectrum": {
                "spectrumtype": "blackbody",
                "params": {"temperature": 5000},
            },
            "extinctionav": 0,
        },
        "brightness": {
            "brightnesstype": "mag",
            "magband": "K",
            "mag": 15,
            "magsys": "vega",
        },
    },
    "instrumentName": "hawki",
}

EMISSION_LINE_JSON = {
    "target": {
        "morphology": {"morphologytype": "point"},
        "sed": {
            "sedtype": "emissionline",
            "emissionline": {"params": {"lambda": 1000, "fwhm": 1}},
            "extinctionav": 0,
        },
        "brightness": {
            "brightnesstype": "mag",
            "magband": "V",
            "mag": 10,
            "magsys": "vega",
        },
    },
    "instrumentName": "hawki",
}


# =========================================================================
# Fallback (header-only) path
# =========================================================================

class TestFallbackHeaderOnly:
    """The fallback should reproduce the old ElvisSimulation behaviour."""

    def test_returns_hdulist(self):
        hdul = _fallback_header_only(POINT_SOURCE_JSON)
        assert isinstance(hdul, fits.HDUList)
        assert len(hdul) == 1

    def test_header_contains_json_keys(self):
        hdul = _fallback_header_only(POINT_SOURCE_JSON)
        header = hdul[0].header
        assert header["SKY AIRMASS"] == 1.2
        assert header["INSTRUMENTNAME"] == "hawki"
        assert header["TIMESNR DET.DIT"] == 10

    def test_empty_json(self):
        hdul = _fallback_header_only({})
        assert isinstance(hdul, fits.HDUList)

    def test_fallback_has_no_image_data(self):
        hdul = _fallback_header_only(POINT_SOURCE_JSON)
        assert hdul[0].data is None


# =========================================================================
# run_simulation — forced fallback via mocking
# =========================================================================

class TestRunSimulationFallback:
    """Force the fallback path by mocking the factory to return None."""

    @patch("elvis.pipeline.create_optical_train", return_value=None)
    def test_returns_hdulist_when_no_opticaltrain(self, _mock):
        hdul = run_simulation(POINT_SOURCE_JSON)
        assert isinstance(hdul, fits.HDUList)

    def test_empty_json_returns_hdulist(self):
        hdul = run_simulation({})
        assert isinstance(hdul, fits.HDUList)

    def test_missing_instrument_name_returns_hdulist(self):
        json_no_inst = {k: v for k, v in POINT_SOURCE_JSON.items()
                        if k != "instrumentName"}
        hdul = run_simulation(json_no_inst)
        assert isinstance(hdul, fits.HDUList)

    @patch("elvis.pipeline.create_optical_train", return_value=None)
    def test_fallback_header_contains_keys(self, _mock):
        hdul = run_simulation(POINT_SOURCE_JSON)
        assert hdul[0].header["SKY AIRMASS"] == 1.2


# =========================================================================
# _readout_to_hdulist
# =========================================================================

class TestReadoutToHDUList:
    """Verify conversion of ScopeSim readout() return values."""

    def test_already_hdulist(self):
        hdul = fits.HDUList([fits.PrimaryHDU()])
        result = _readout_to_hdulist(hdul)
        assert isinstance(result, fits.HDUList)

    def test_nested_list_single_detector(self):
        readout = [[fits.PrimaryHDU(), fits.ImageHDU(data=[[1, 2]])]]
        result = _readout_to_hdulist(readout)
        assert isinstance(result, fits.HDUList)
        assert len(result) == 2
        assert result[1].data is not None

    def test_nested_list_multi_detector(self):
        readout = [
            [fits.PrimaryHDU(), fits.ImageHDU(data=[[1]])],
            [fits.PrimaryHDU(), fits.ImageHDU(data=[[2]])],
        ]
        result = _readout_to_hdulist(readout)
        assert isinstance(result, fits.HDUList)
        # 1 PrimaryHDU + 1 ImageHDU from det0 + 1 ImageHDU(converted) + 1 ImageHDU from det1
        assert isinstance(result[0], fits.PrimaryHDU)
        assert all(isinstance(h, (fits.PrimaryHDU, fits.ImageHDU))
                    for h in result)

    def test_empty_readout(self):
        result = _readout_to_hdulist([])
        assert isinstance(result, fits.HDUList)
        assert isinstance(result[0], fits.PrimaryHDU)


# =========================================================================
# OpticalTrain factory (step 2)
# =========================================================================

class TestOpticalTrainFactory:

    def test_unknown_instrument_raises(self):
        with pytest.raises(ValueError, match="Unknown instrument"):
            create_optical_train("nonexistent_instrument")

    def test_known_instruments_in_map(self):
        assert "eris" in INSTRUMENT_MAP
        assert "hawki" in INSTRUMENT_MAP

    @requires_scopesim
    def test_eris_creates_optical_train(self):
        opt = create_optical_train("eris")
        assert opt is not None
        assert hasattr(opt, "observe")
        assert hasattr(opt, "readout")

    @requires_scopesim
    def test_hawki_creates_optical_train(self):
        opt = create_optical_train("hawki")
        assert opt is not None
        assert hasattr(opt, "observe")
        assert hasattr(opt, "readout")

    @requires_scopesim
    def test_optical_train_has_effects(self):
        opt = create_optical_train("hawki")
        assert len(opt.effects) > 0


# =========================================================================
# Source creation (step 1)
# =========================================================================

class TestCreateSourcePointSource:
    """Point sources should produce a Source with a Table field."""

    def test_returns_source_object(self):
        source = _create_source(POINT_SOURCE_JSON)
        assert source is not None

    def test_has_fields(self):
        source = _create_source(POINT_SOURCE_JSON)
        assert hasattr(source, "fields")
        assert len(source.fields) >= 1

    def test_has_spectrum(self):
        source = _create_source(POINT_SOURCE_JSON)
        assert hasattr(source, "spectra")
        assert len(source.spectra) >= 1

    def test_spectrum_is_callable(self):
        """The spectrum should be a SourceSpectrum (callable)."""
        source = _create_source(POINT_SOURCE_JSON)
        spec = list(source.spectra.values())[0]
        assert callable(spec)


class TestCreateSourceBlackbody:
    """Blackbody SED should work the same as template for point sources."""

    def test_returns_source(self):
        source = _create_source(BLACKBODY_POINT_JSON)
        assert source is not None

    def test_has_spectrum(self):
        source = _create_source(BLACKBODY_POINT_JSON)
        assert len(source.spectra) >= 1


class TestCreateSourceSersic:
    """Sersic extended sources need an OpticalTrain for .to_source()."""

    def test_sersic_without_opticaltrain_returns_none(self):
        """Sersic .to_source() requires optical_train, so _create_source
        falls back to None gracefully."""
        source = _create_source(SERSIC_SOURCE_JSON)
        assert source is None


class TestCreateSourceFallbacks:
    """Edge cases that should return None gracefully, not crash."""

    def test_no_target_returns_none(self):
        assert _create_source({}) is None

    def test_emission_line_returns_none(self):
        source = _create_source(EMISSION_LINE_JSON)
        assert source is None

    def test_infinite_extended_returns_none(self):
        json_data = copy.deepcopy(POINT_SOURCE_JSON)
        json_data["target"]["morphology"] = {
            "morphologytype": "extended",
            "extendedtype": "infinite",
        }
        source = _create_source(json_data)
        assert source is None


# =========================================================================
# End-to-end pipeline (requires ScopeSim + IRDB)
# =========================================================================

@requires_scopesim
class TestEndToEndPipeline:

    def test_hawki_pipeline_returns_hdulist(self):
        hdul = run_simulation(POINT_SOURCE_JSON)
        assert isinstance(hdul, fits.HDUList)

    def test_pipeline_output_has_image_data(self):
        """When ScopeSim is available, the result should contain actual
        pixel data, not just headers."""
        hdul = run_simulation(POINT_SOURCE_JSON)
        has_data = any(
            hdu.data is not None and hasattr(hdu.data, "shape")
            for hdu in hdul
        )
        assert has_data, "Pipeline should produce image data, not just headers"

    def test_pipeline_image_is_2d(self):
        hdul = run_simulation(POINT_SOURCE_JSON)
        for hdu in hdul:
            if hdu.data is not None and hasattr(hdu.data, "shape"):
                assert len(hdu.data.shape) == 2
                break
        else:
            pytest.fail("No HDU with 2D image data found")

    def test_pipeline_output_differs_from_fallback(self):
        """The real pipeline should produce pixel data unlike the
        header-only fallback."""
        real = run_simulation(POINT_SOURCE_JSON)
        fallback = _fallback_header_only(POINT_SOURCE_JSON)
        assert fallback[0].data is None
        has_real_data = any(hdu.data is not None for hdu in real)
        assert has_real_data
