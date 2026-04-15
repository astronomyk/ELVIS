"""
Step 2: Create a default ScopeSim OpticalTrain for an instrument.

Maps the ETC ``instrumentName`` to an IRDB instrument package and
instantiates a ScopeSim OpticalTrain with default settings.
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

# ETC instrumentName → IRDB package name
INSTRUMENT_MAP = {
    "eris": "ERIS",
    "hawki": "HAWKI_new",
}


def create_optical_train(instrument_name: str):
    """
    Create a default OpticalTrain for the given instrument.

    Parameters
    ----------
    instrument_name : str
        The ``instrumentName`` field from the ETC JSON (e.g. ``"eris"``).

    Returns
    -------
    scopesim.OpticalTrain or None
        A ready-to-configure OpticalTrain, or ``None`` if ScopeSim / the
        IRDB package is not available (fallback mode).

    Raises
    ------
    ValueError
        If ``instrument_name`` is not in ``INSTRUMENT_MAP``.
    """
    if instrument_name not in INSTRUMENT_MAP:
        raise ValueError(
            f"Unknown instrument '{instrument_name}'. "
            f"Available: {list(INSTRUMENT_MAP)}"
        )

    pkg = INSTRUMENT_MAP[instrument_name]

    try:
        import scopesim
        cmd = scopesim.UserCommands(use_instrument=pkg)
        opt = scopesim.OpticalTrain(cmd)
        log.info("Created OpticalTrain for %s (IRDB: %s)", instrument_name, pkg)
        return opt
    except Exception as exc:
        log.warning(
            "Could not create OpticalTrain for %s: %s. "
            "Falling back to header-only mode.", instrument_name, exc
        )
        return None
