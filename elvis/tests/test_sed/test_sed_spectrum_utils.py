import pytest
import matplotlib.pyplot as plt
import os
import numpy as np
from synphot import SourceSpectrum
from elvis.targets.sed_spectrum_utils import (
    read_marcs_spectrum,
    read_phoenix_spectrum,
    read_swire_spectrum,
    read_kinney_spectrum,
    read_kurucz_spectrum,
    read_pickles_spectrum,
    read_various_spectrum,
    get_blackbody_spectrum,
    get_powerlaw_spectrum,
)


@pytest.mark.parametrize("func, valid_id, label", [
    (read_marcs_spectrum, "5750:4.5", "MARCS"),
    (read_phoenix_spectrum, "5700:4.50", "PHOENIX"),
    (read_swire_spectrum, "2 Gyr old elliptical", "SWIRE"),
    (read_kinney_spectrum, "Sb Galaxy", "Kinney"),
    (read_kurucz_spectrum, "G:2:V", "Kurucz"),
    (read_pickles_spectrum, "G:2:V", "Pickles"),
    (read_various_spectrum, "Planetary Nebula", "Various")
])
def test_valid_spectrum_readers(func, valid_id, label):
    spectrum = func(valid_id)
    assert isinstance(spectrum, SourceSpectrum)

    if os.getenv("CI") != "true":
        wavelengths = spectrum.waveset
        fluxes = spectrum(wavelengths)
        plt.figure()
        plt.plot(wavelengths, fluxes)
        plt.title(f"Spectrum for {label}")
        plt.xlabel("Wavelength (AA)")
        plt.ylabel("Flux (FLAM)")
        plt.grid(True)
        plt.loglog()
        plt.show()


@pytest.mark.parametrize("func, invalid_id", [
    (read_marcs_spectrum, "bad"),
    (read_phoenix_spectrum, "bad"),
    (read_swire_spectrum, "Not a real ID"),
    (read_kinney_spectrum, "Not a real ID"),
    (read_kurucz_spectrum, "Z:9:X"),
    (read_pickles_spectrum, "Z:9:X"),
    (read_various_spectrum, "Unknown Object")
])
def test_invalid_spectrum_readers(func, invalid_id):
    with pytest.raises((ValueError, FileNotFoundError, IndexError)):
        func(invalid_id)


@pytest.mark.parametrize("temperature", [1000, 5000, 10000])
def test_blackbody_spectrum(temperature):
    spectrum = get_blackbody_spectrum({"temperature": temperature})
    assert isinstance(spectrum, SourceSpectrum)

    if os.getenv("CI") != "true":
        wavelengths = spectrum.waveset
        fluxes = spectrum(wavelengths)
        plt.figure()
        plt.plot(wavelengths, fluxes)
        plt.title(f"Blackbody T={temperature} K")
        plt.xlabel("Wavelength (AA)")
        plt.ylabel("Flux (FLAM)")
        plt.grid(True)
        plt.loglog()
        plt.show()


@pytest.mark.parametrize("params", [
    {"exponent": -1.5},
    {"exponent": 0},
    {"exponent": 2.0}
])
def test_powerlaw_spectrum(params):
    spectrum = get_powerlaw_spectrum(params)
    assert isinstance(spectrum, SourceSpectrum)

    if os.getenv("CI") != "true":
        wavelengths = np.logspace(3,5, 100)
        fluxes = spectrum(wavelengths)
        plt.figure()
        plt.plot(wavelengths, fluxes)
        plt.title(f"Powerlaw exponent={params['exponent']}")
        plt.xlabel("Wavelength (AA)")
        plt.ylabel("Flux (FLAM)")
        plt.grid(True)
        plt.loglog()
        plt.show()


@pytest.mark.parametrize("params", [
    {"temperature": -100},             # Negative temperature
    {"temperature": 200000},           # Too high
    {"temperature": "hot"},           # Non-numeric
    {},                                 # Missing
])
def test_blackbody_spectrum_invalid(params):
    with pytest.raises((ValueError, TypeError, KeyError)):
        get_blackbody_spectrum(params)


@pytest.mark.parametrize("params", [
    {"exponent": "steep"},            # Non-numeric
    {},                                 # Missing
])
def test_powerlaw_spectrum_invalid(params):
    with pytest.raises((ValueError, TypeError, KeyError)):
        get_powerlaw_spectrum(params)
