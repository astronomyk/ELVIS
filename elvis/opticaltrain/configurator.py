"""
Step 3: Apply ETC JSON settings to a ScopeSim OpticalTrain.

Translates the ``instrument``, ``sky``, ``seeing``, and ``timesnr``
sections of an ETC JSON dict into OpticalTrain property updates.
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def configure_optical_train(opt_train, etc_json: dict) -> None:
    """
    Apply ETC configuration to an OpticalTrain in-place.

    Parameters
    ----------
    opt_train : scopesim.OpticalTrain
        The OpticalTrain to configure.
    etc_json : dict
        The full ETC JSON dict.
    """
    _apply_instrument(opt_train, etc_json.get("instrument", {}))
    _apply_sky(opt_train, etc_json.get("sky", {}))
    _apply_seeing(opt_train, etc_json.get("seeing", {}))
    _apply_timesnr(opt_train, etc_json.get("timesnr", {}))


def _apply_instrument(opt_train, inst: dict) -> None:
    """Apply instrument-section settings (filter, grating, etc.)."""
    # TODO: map ins_configuration and instrument keys to OpticalTrain
    #       effects once the IRDB effect names are confirmed.
    log.info("Instrument config: %s (not yet applied)", inst)


def _apply_sky(opt_train, sky: dict) -> None:
    """Apply sky-section settings via skycalc parameters."""
    # TODO: wire elvis.sky.converter.etc_sky_to_skycalc() into the
    #       OpticalTrain atmosphere/sky-background effects.
    log.info("Sky config: %s (not yet applied)", sky)


def _apply_seeing(opt_train, seeing: dict) -> None:
    """Apply seeing/AO settings to the PSF effects."""
    # TODO: map turbulence_category, AO mode, separation to PSF effects.
    log.info("Seeing config: %s (not yet applied)", seeing)


def _apply_timesnr(opt_train, timesnr: dict) -> None:
    """Apply DIT/NDIT to the detector readout effects."""
    # TODO: set DIT and NDIT on the detector effect.
    log.info("Timesnr config: %s (not yet applied)", timesnr)
