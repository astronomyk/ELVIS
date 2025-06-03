import pytest
from synphot import SourceSpectrum
from elvis.targets import sed


@pytest.mark.parametrize("input_dict", [
    {
        "sedtype": "spectrum",
        "spectrum": {
            "spectrumtype": "template",
            "params": {
                "catalog": "MARCS",
                "id": "5750:4.5"
            }
        },
        "extinctionav": 0
    },
    {
        "sedtype": "spectrum",
        "spectrum": {
            "spectrumtype": "blackbody",
            "params": {
                "temperature": 1000
            }
        },
        "extinctionav": 0,
        "redshift": {
            "redshift": 0.000003335646515223445,
            "baryvelcor": 1000
        }
    },
    {
        "sedtype": "spectrum",
        "spectrum": {
            "spectrumtype": "powerlaw",
            "params": {
                "exponent": 0
            }
        },
        "extinctionav": 0,
        "redshift": {
            "redshift": 1,
            "baryvelcor": 1000
        }
    },
    {
        "sedtype": "emissionline",
        "emissionline": {
            "params": {
                "lambda": 1000,
                "fwhm": 1
            }
        }
    }
])
def test_valid_spectra(input_dict):
    result = sed.get_spectrum(input_dict) if input_dict["sedtype"] != "emissionline" else sed.get_emission_line(input_dict)
    assert isinstance(result, SourceSpectrum)


def test_upload_not_implemented():
    input_dict = {
        "sedtype": "spectrum",
        "spectrum": {
            "spectrumtype": "upload"
        },
        "extinctionav": 0,
        "redshift": {
            "redshift": 1,
            "baryvelcor": 1000
        }
    }
    with pytest.raises(NotImplementedError):
        sed.get_spectrum(input_dict)


def test_emissionline_missing_params():
    bad_dict = {
        "sedtype": "emissionline",
        "emissionline": {
            "params": {
                "lambda": 1000
            }
        }
    }
    with pytest.raises(ValueError):
        sed.get_emission_line(bad_dict)


def test_emissionline_bad_values():
    bad_dict = {
        "sedtype": "emissionline",
        "emissionline": {
            "params": {
                "lambda": -10,
                "fwhm": 1
            }
        }
    }
    with pytest.raises(ValueError):
        sed.get_emission_line(bad_dict)


def test_template_missing_catalog():
    input_dict = {
        "sedtype": "spectrum",
        "spectrum": {
            "spectrumtype": "template",
            "params": {
                "id": "5750:4.5"
            }
        }
    }
    with pytest.raises(ValueError):
        sed.get_spectrum(input_dict)


def test_template_invalid_catalog():
    input_dict = {
        "sedtype": "spectrum",
        "spectrum": {
            "spectrumtype": "template",
            "params": {
                "catalog": "INVALID",
                "id": "5750:4.5"
            }
        }
    }
    with pytest.raises(ValueError):
        sed.get_spectrum(input_dict)


