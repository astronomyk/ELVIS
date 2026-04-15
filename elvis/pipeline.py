"""
ELVIS simulation pipeline.

Orchestrates the 5-step workflow from the architecture diagram::

    ESO ETC  --JSON-->  ELVIS  --.FITS-->  ESO ETC

    Step 1: ETC JSON target  →  scopesim Source object
    Step 2: Create default OpticalTrain for instrument (from IRDB)
    Step 3: Update OpticalTrain with ETC instrument/sky/seeing config
    Step 4: OpticalTrain.observe(source)
    Step 5: OpticalTrain.readout()  →  FITS HDUList
"""

from __future__ import annotations

import logging

from astropy.io import fits

from elvis.source.converter import etc_target_to_scopesim_yaml, to_scopesim_target
from elvis.opticaltrain import create_optical_train, configure_optical_train

log = logging.getLogger(__name__)


def run_simulation(etc_json: dict) -> fits.HDUList:
    """
    Full ELVIS pipeline: ETC JSON in, FITS HDUList out.

    Parameters
    ----------
    etc_json : dict
        Complete ETC JSON payload (with ``instrumentName``, ``target``,
        ``sky``, ``instrument``, ``timesnr``, etc.).

    Returns
    -------
    astropy.io.fits.HDUList
    """
    instrument_name = etc_json.get("instrumentName", "")

    # --- Step 1: Target → scopesim Source ---
    source = _create_source(etc_json)

    # --- Step 2: Create default OpticalTrain from IRDB ---
    try:
        opt_train = create_optical_train(instrument_name)
    except ValueError:
        log.warning("Unknown or missing instrumentName '%s' — "
                    "returning header-only FITS.", instrument_name)
        return _fallback_header_only(etc_json)

    if opt_train is None:
        log.warning("No OpticalTrain available — returning header-only FITS.")
        return _fallback_header_only(etc_json)

    # --- Step 3: Configure OpticalTrain from ETC JSON ---
    configure_optical_train(opt_train, etc_json)

    # --- Step 4: Observe ---
    opt_train.observe(source)

    # --- Step 5: Readout → FITS ---
    readout = opt_train.readout()

    # ScopeSim readout() returns a list of detector readouts, each being
    # a list of HDUs: [[PrimaryHDU, ImageHDU], ...].  Merge into one HDUList.
    hdul = _readout_to_hdulist(readout)

    return hdul


def _create_source(etc_json: dict):
    """
    Step 1: Convert the ETC JSON target section to a scopesim Source.

    Falls back to ``None`` if the conversion fails (e.g. unsupported
    morphology type), letting the caller decide how to handle it.
    """
    target = etc_json.get("target")
    if target is None:
        log.warning("No 'target' section in ETC JSON.")
        return None

    try:
        yaml_dict = etc_target_to_scopesim_yaml(etc_json)
        source_target = to_scopesim_target(yaml_dict)
        source = source_target.to_source()
        log.info("Created scopesim Source: %s", yaml_dict.get("target_class"))
        return source
    except Exception as exc:
        log.warning("Could not create Source from ETC JSON: %s", exc)
        return None


def _readout_to_hdulist(readout) -> fits.HDUList:
    """
    Convert the ScopeSim readout() return value to a proper HDUList.

    ``OpticalTrain.readout()`` returns a list of detector readouts,
    where each readout is a list of HDUs (typically [PrimaryHDU, ImageHDU]).
    This function merges them: the first detector's PrimaryHDU leads,
    followed by each detector's ImageHDU extensions.
    """
    if isinstance(readout, fits.HDUList):
        return readout

    hdus = []
    for i, detector_hdus in enumerate(readout):
        if isinstance(detector_hdus, fits.HDUList):
            detector_hdus = list(detector_hdus)
        for hdu in detector_hdus:
            if isinstance(hdu, fits.PrimaryHDU) and i == 0:
                hdus.append(hdu)
            elif isinstance(hdu, fits.PrimaryHDU):
                # Convert additional PrimaryHDUs to ImageHDUs
                hdus.append(fits.ImageHDU(data=hdu.data, header=hdu.header))
            else:
                hdus.append(hdu)

    if not hdus:
        hdus.append(fits.PrimaryHDU())

    # Ensure the first HDU is a PrimaryHDU
    if not isinstance(hdus[0], fits.PrimaryHDU):
        hdus.insert(0, fits.PrimaryHDU())

    return fits.HDUList(hdus)


# -------------------------------------------------------------------------
#  Fallback: JSON → FITS headers (current behaviour while stubs exist)
# -------------------------------------------------------------------------

def _fallback_header_only(etc_json: dict) -> fits.HDUList:
    """
    Fallback pipeline: dump the ETC JSON into FITS header keywords.

    This preserves the original ``ElvisSimulation.simulate()`` behaviour
    so the ``/process`` endpoint stays functional while OpticalTrain
    integration is being wired up.
    """
    def _add_to_header(d, header, prefix=""):
        for key, value in d.items():
            new_key = f"{prefix} {key}".upper().strip()
            if isinstance(value, dict):
                _add_to_header(value, header, new_key)
            else:
                try:
                    header[new_key] = value
                except ValueError:
                    header[new_key] = str(value)

    hdu = fits.PrimaryHDU()
    _add_to_header(etc_json, hdu.header)
    return fits.HDUList([hdu])
