from synphot import SourceSpectrum
from synphot.models import BlackBody1D, PowerLawFlux1D
from synphot import Empirical1D
from synphot.spectrum import SpectralElement
from astropy import units as u
from pathlib import Path
import numpy as np
from dust_extinction.parameter_averages import F99, G23

TEMPLATES_PATH = Path("D:/ELVIS/ETC_SED/")


def get_eso_extinction_element(waveset, a_v=1.0, r_v=3.1):
    """
    Returns a SpectralElement extinction curve using ESO ETC method:
    - Fitzpatrick (1999) for wavelengths <= 2.7 micron
    - Gordon et al. (2021) for wavelengths > 2.7 micron

    Parameters:
    - waveset: Quantity array of wavelengths in microns
    - a_v: Extinction in V band
    - r_v: Ratio of total to selective extinction

    Returns:
    - SpectralElement object representing extinction curve
    """
    wave_micron = waveset.to(u.micron)
    mask_f99 = wave_micron <= 2.7 * u.micron
    mask_g23 = ~mask_f99

    f99 = F99(Rv=r_v)
    g23 = G23(Rv=r_v)

    a_lambda = np.zeros_like(wave_micron.value)
    if np.any(mask_f99):
        a_lambda[mask_f99] = f99(wave_micron[mask_f99]) * a_v
    if np.any(mask_g23):
        a_lambda[mask_g23] = g23(wave_micron[mask_g23]) * a_v

    attenuation = 10 ** (-0.4 * a_lambda)
    return SpectralElement(Empirical1D, points=wave_micron, lookup_table=attenuation)


def read_marcs_spectrum(sed_id):
    """
    Load MARCS template spectrum.

    MARCS spectra use the format <temperature>:<logg>
    - temperature: integer in [3000, 8000]
    - logg: float in [3.0, 5.0], formatted to 1 decimal place
    """
    temp_str, logg_str = sed_id.split(":")
    temp = int(temp_str)
    logg = float(logg_str)
    filename = f"p{temp}_g+{logg:.1f}_m0.0_t02_st_z+0.00_a+0.00_c+0.00_n+0.00_o+0.00.fits"
    path = TEMPLATES_PATH / "MARCS" / filename
    if not path.exists():
        raise FileNotFoundError()
    return SourceSpectrum.from_file(str(path))


def read_phoenix_spectrum(sed_id):
    """
    Load PHOENIX template spectrum.

    PHOENIX spectra use the format <temperature>:<logg>
    - temperature: integer in [2300, 12000], zero-padded to 5 digits
    - logg: float in [0.0, 6.0], formatted to 2 decimal places
    """
    temp_str, logg_str = sed_id.split(":")
    temp = int(temp_str)
    logg = float(logg_str)
    filename = f"lte{temp:05d}-{logg:.2f}-PHOENIX.fits"
    path = TEMPLATES_PATH / "PHOENIX" / filename
    if not path.exists():
        raise FileNotFoundError()
    return SourceSpectrum.from_file(str(path))


def read_swire_spectrum(sed_id):
    """
    Load SWIRE template spectrum by dropdown ID.

    Parameters:
    - sed_id: string key from ETC dropdown menu.
    """
    swire_map = {
        "13 Gyr old elliptical": "Ell13.fits",
        "2 Gyr old elliptical": "Ell2.fits",
        "5 Gyr old elliptical": "Ell5.fits",
        "AGN BQSO1": "BQSO1.fits",
        "AGN QSO1": "QSO1.fits",
        "AGN QSO2": "QSO2.fits",
        "AGN Seyfert 1.8": "Sey18.fits",
        "AGN Seyfert 2.0": "Sey2.fits",
        "AGN TQSO1": "TQSO1.fits",
        "AGN Torus": "Torus.fits",
        "BAL QSO, Seyfert 1, ULIRG Mrk 231": "Mrk231.fits",
        "Spiral 0": "S0.fits",
        "Spiral a": "Sa.fits",
        "Spiral b": "Sb.fits",
        "Spiral c": "Sc.fits",
        "Spiral c4": "Spi4.fits",
        "Spiral dm": "Sdm.fits",
        "Starburst Arp 220": "Arp220.fits",
        "Starburst IRAS 19254-7245 South": "I19254.fits",
        "Starburst IRAS 20551-4250": "I20551.fits"
    }
    filename = swire_map.get(sed_id)
    if not filename:
        raise ValueError(f"Unknown SWIRE template ID: {sed_id}")
    path = TEMPLATES_PATH / "SWIRE" / filename
    if not path.exists():
        raise FileNotFoundError()
    return SourceSpectrum.from_file(str(path))


def read_kinney_spectrum(sed_id):
    """
    Load Kinney template spectrum by dropdown ID.

    Parameters:
    - sed_id: string key from ETC dropdown menu.
    """
    kinney_map = {
        "Elliptical Galaxy": "Kinney_ell.fits",
        "S0 Galaxy": "Kinney_s0.fits",
        "Sa Galaxy": "Kinney_sa.fits",
        "Sb Galaxy": "Kinney_sb.fits",
        "Starburst Galaxy 1": "Kinney_starb1.fits",
        "Starburst Galaxy 2": "Kinney_starb2.fits",
        "Starburst Galaxy 3": "Kinney_starb3.fits",
        "Starburst Galaxy 4": "Kinney_starb4.fits",
        "Starburst Galaxy 5": "Kinney_starb5.fits",
        "Starburst Galaxy 6": "Kinney_starb6.fits"
    }
    filename = kinney_map.get(sed_id)
    if not filename:
        raise ValueError(f"Unknown Kinney template ID: {sed_id}")
    path = TEMPLATES_PATH / "Kinney" / filename
    if not path.exists():
        raise FileNotFoundError()
    return SourceSpectrum.from_file(str(path))


def read_kurucz_spectrum(sed_id):
    """
    Load Kurucz template spectrum.

    Kurucz spectra use the format <spec_type>:<spec_sub_type>:<lum_class>
    - spec_type: O, B, A, F, G, K, M
    - spec_sub_type: 2, 5, 8
    - lum_class: I, V
    """
    spec_type, spec_sub_type, lum_class = sed_id.split(":")
    filename = f"{spec_type}{spec_sub_type}{lum_class}.fits"
    path = TEMPLATES_PATH / "Kurucz" / filename
    if not path.exists():
        raise FileNotFoundError()
    return SourceSpectrum.from_file(str(path))


def read_pickles_spectrum(sed_id):
    """
    Load Pickles template spectrum.

    Pickles spectra use the format <spec_type>:<spec_sub_type>:<lum_class>
    - spec_type: O, B, A, F, G, K, M
    - spec_sub_type: 0, 2, 5, 8
    - lum_class: I, II, III, IV, V
    """
    spec_type, spec_sub_type, lum_class = sed_id.split(":")
    filename = f"{spec_type}{spec_sub_type}{lum_class}.fits"
    path = TEMPLATES_PATH / "Pickles" / filename
    if not path.exists():
        raise FileNotFoundError()
    return SourceSpectrum.from_file(str(path))


def read_various_spectrum(sed_id):
    """
    Load spectrum from "Various" template group by name.

    Parameters:
    - sed_id: name from dropdown
    """
    various_map = {
        "HII region (Orion)": "orion.fits",
        "Planetary Nebula": "pn.fits"
    }
    filename = various_map.get(sed_id)
    if not filename:
        raise ValueError(f"Unknown Various template ID: {sed_id}")
    path = TEMPLATES_PATH / "Various" / filename
    if not path.exists():
        raise FileNotFoundError()
    return SourceSpectrum.from_file(str(path))


def get_template_spectrum(params):
    catalog = params.get("catalog")
    sed_id = params.get("id")

    if catalog == "MARCS":
        return read_marcs_spectrum(sed_id)
    elif catalog == "PHOENIX":
        return read_phoenix_spectrum(sed_id)
    elif catalog == "SWIRE":
        return read_swire_spectrum(sed_id)
    elif catalog == "Kinney":
        return read_kinney_spectrum(sed_id)
    elif catalog == "Kurucz":
        return read_kurucz_spectrum(sed_id)
    elif catalog == "Pickles":
        return read_pickles_spectrum(sed_id)
    elif catalog == "Various":
        return read_various_spectrum(sed_id)
    else:
        raise ValueError(f"Unsupported catalog: {catalog}")


def get_blackbody_spectrum(params):
    temp = params.get("temperature")
    if temp is None:
        raise ValueError("Blackbody spectrum requires 'temperature' parameter.")
    if not isinstance(temp, (int, float)):
        raise ValueError(f"Blackbody 'temperature' must be int or float: f{type(temp)=}, {temp}")
    if temp < 0 or temp > 1e5:
        raise ValueError(f"Blackbody 'temperature' outside acceptable range [0, 1e5]: f{temp}")
    return SourceSpectrum(BlackBody1D(temperature=temp * u.K))


def get_powerlaw_spectrum(params):
    alpha = params.get("exponent")
    if alpha is None:
        raise ValueError("Power-law spectrum requires 'exponent' parameter.")
    model = PowerLawFlux1D(amplitude=1, x_0=1 * u.um, alpha=alpha)
    return SourceSpectrum(model)


