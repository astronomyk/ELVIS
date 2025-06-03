from astropy import units as u
import numpy as np
from synphot import Gaussian1D, SourceSpectrum

from elvis.targets.sed_spectrum_utils import (
    get_template_spectrum,
    get_blackbody_spectrum,
    get_powerlaw_spectrum,
    get_eso_extinction_element
)


def get_spectrum(sed_dict):
    sedtype = sed_dict.get("sedtype")
    spectrum = sed_dict.get("spectrum", {})
    spectrumtype = spectrum.get("spectrumtype")
    params = spectrum.get("params", {})

    if sedtype == "spectrum" and spectrumtype == "template":
        spec = get_template_spectrum(params)
    elif sedtype == "spectrum" and spectrumtype == "blackbody":
        spec = get_blackbody_spectrum(params)
    elif sedtype == "spectrum" and spectrumtype == "powerlaw":
        spec = get_powerlaw_spectrum(params)
    elif sedtype == "spectrum" and spectrumtype == "upload":
        raise NotImplementedError("'upload' spectrum type is not yet supported.")
    else:
        raise ValueError(f"Unsupported sedtype/spectrumtype: {sedtype}/{spectrumtype}")

    # Apply extinction if present
    extinction_av = sed_dict.get("extinctionav")
    if extinction_av:
        ext_element = get_eso_extinction_element(spec.waveset, a_v=extinction_av)
        spec = spec * ext_element

    # Apply redshift if present
    redshift_info = sed_dict.get("redshift", {})
    redshift = redshift_info.get("redshift")
    if redshift:
        spec.z = redshift

    # Warn if baryvelcor is present
    if "baryvelcor" in redshift_info:
        import warnings
        warnings.warn("'baryvelcor' was detected, but has no effect on the spectrum")

    return spec


def get_emission_line(sed_dict):
    """
    Create a SourceSpectrum representing a single emission line.

    Parameters:
    - sed_dict:

    Returns:
    - synphot.SourceSpectrum representing the emission line

    Raises:
    - ValueError if required parameters are missing or invalid
    """
    if sed_dict.get("sedtype") != "emissionline":
        raise ValueError("Expected sedtype to be 'emissionline'")

    params = sed_dict.get("emissionline", {}).get("params", {})

    lam = params.get("lambda")
    fwhm = params.get("fwhm")

    if lam is None or fwhm is None:
        raise ValueError("Emission line parameters must include 'lambda' and 'fwhm'")

    try:
        lam = float(lam)
        fwhm = float(fwhm)
    except ValueError:
        raise ValueError("'lambda' and 'fwhm' must be numeric")

    if lam <= 0 or fwhm <= 0:
        raise ValueError("'lambda' and 'fwhm' must be positive")

    sigma = fwhm / (2 * (2 * np.log(2))**0.5)
    gauss = Gaussian1D(amplitude=1, mean=lam * u.AA, stddev=sigma * u.AA)
    return SourceSpectrum(gauss)
