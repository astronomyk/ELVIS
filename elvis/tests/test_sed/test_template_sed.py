import pytest
from elvis.targets import SED
from synphot import SourceSpectrum


# Example valid input for each catalog
template_examples = {
    "MARCS": {"sedtype": "spectrum", "spectrum": {"spectrumtype": "template", "params": {"catalog": "MARCS", "id": "5750:4.5", "extinctionav": 0}, "redshift": {"redshift": 0, "baryvelcor": 0}}},
    "PHOENIX": {"sedtype": "spectrum", "spectrum": {"spectrumtype": "template", "params": {"catalog": "PHOENIX", "id": "5700:4.5", "extinctionav": 0}, "redshift": {"redshift": 0, "baryvelcor": 0}}},
    "SWIRE": {"sedtype": "spectrum", "spectrum": {"spectrumtype": "template", "params": {"catalog": "SWIRE", "id": "2 Gyr old elliptical", "extinctionav": 0}, "redshift": {"redshift": 0, "baryvelcor": 0}}},
    "Kinney": {"sedtype": "spectrum", "spectrum": {"spectrumtype": "template", "params": {"catalog": "Kinney", "id": "Sb Galaxy", "extinctionav": 0}, "redshift": {"redshift": 0, "baryvelcor": 0}}},
    "Kurucz": {"sedtype": "spectrum", "spectrum": {"spectrumtype": "template", "params": {"catalog": "Kurucz", "id": "G:2:V", "extinctionav": 0}, "redshift": {"redshift": 0, "baryvelcor": 0}}},
    "Pickles": {"sedtype": "spectrum", "spectrum": {"spectrumtype": "template", "params": {"catalog": "Pickles", "id": "G:2:V", "extinctionav": 0}, "redshift": {"redshift": 0, "baryvelcor": 0}}},
    "Various": {"sedtype": "spectrum", "spectrum": {"spectrumtype": "template", "params": {"catalog": "Various", "id": "Planetary Nebula", "extinctionav": 0}, "redshift": {"redshift": 0, "baryvelcor": 0}}}
}

# Simulate presence of .fits files for success cases
@pytest.mark.parametrize("catalog", template_examples.keys())
def test_valid_templates(catalog):
    import matplotlib.pyplot as plt
    import os
    sed_dict = template_examples[catalog]
    sed_obj = SED.from_dict(sed_dict)
    spectrum = sed_obj.get_spectrum()
    assert isinstance(spectrum, SourceSpectrum)

    # Optional plotting if not in CI environment
    if os.getenv("CI") != "true":
        wavelengths = spectrum.waveset
        fluxes = spectrum(wavelengths)
        plt.plot(wavelengths, fluxes)
        plt.title(f"Mock spectrum for {catalog}")
        plt.xlabel("Wavelength (AA)")
        plt.ylabel("Flux (FLAM)")
        plt.loglog()
        plt.grid(True)
        plt.show()

# Missing or malformed dictionary entries
@pytest.mark.parametrize("bad_input", [
    {},
    {"sedtype": "spectrum"},
    {"sedtype": "spectrum", "spectrum": {}},
    {"sedtype": "spectrum", "spectrum": {"spectrumtype": "template"}},
    {"sedtype": "spectrum", "spectrum": {"spectrumtype": "template", "params": {}}},
    {"sedtype": "spectrum", "spectrum": {"spectrumtype": "template", "params": {"catalog": "UNKNOWN"}}},
    {"sedtype": "spectrum", "spectrum": {"spectrumtype": "template", "params": {"catalog": "MARCS", "id": "badformat"}}}
])
def test_invalid_templates(bad_input):
    with pytest.raises((KeyError, ValueError, IndexError)):
        SED.from_dict(bad_input)
