import pytest
from astropy.io import fits

from elvis.simulate import ElvisSimulation


# Standalone setup function to create the simulation instance
def mock_json():
    """Set up the simulation with mock JSON data."""
    sample_json = {
        "target": {
            "brightness": {
                "mag": 10
            }
        },
        "sky": {
            "airmass": 1.1,
            "moon_fli": 0.5
        },
        "instrument": {
            "ins_configuration": "nixIMG"
        },
        "timesnr": {
            "DET.NDIT": 1,
            "DET.DIT": 2
        },
        "output": {},
        "instrumentName": "eris",
        "seeingiqao": {
            "mode": "aolgs",
            "params": {
                "gsmag": 12,
                "separation": 0,
                "turbulence_category": 50
            },
            "aperturepix": 9
        }
    }
    # Return the simulation instance
    return sample_json

# Test class that uses the setup fixtur

class TestElvisSimulationInit:
    def test_all_top_level_json_keys_are_initialised_attributes(self):
        """Test if all top-level attributes are correctly assigned."""
        # Check the top-level attributes
        sim = ElvisSimulation(mock_json())

        assert sim.target["brightness"]["mag"] == 10
        assert sim.sky["airmass"] == 1.1
        assert sim.instrument["ins_configuration"] == "nixIMG"
        assert sim.timesnr["DET.NDIT"] == 1
        assert sim.instrument_name == "eris"
        assert sim.seeingiqao["mode"] == "aolgs"

    def test_throws_error_if_no_json_dict_passed(self):
        with pytest.raises(TypeError):
            ElvisSimulation()


class TestElvisSimulationSimulate:

    def test_simulate(self):
        """Test if the simulation produces a valid FITS HDUList with the expected header."""
        sim = ElvisSimulation(mock_json())
        hdul = sim.simulate()

        # Test if the FITS header contains the expected keywords
        header = hdul[0].header

        # Check if some specific HEIRARCH keywords are in the header
        assert header["TARGET BRIGHTNESS MAG"] == 10
        assert header["SKY AIRMASS"] == 1.1
        assert header["INSTRUMENT INS_CONFIGURATION"] == "nixIMG"
        assert header["TIMESNR DET.NDIT"] == 1

    def test_simulate_returns_fits_object(self):
        """Test if simulate() returns a valid HDUList."""
        sim = ElvisSimulation(mock_json())
        hdul = sim.simulate()

        # Check if hdul is an instance of fits.HDUList
        assert isinstance(hdul, fits.HDUList)
        assert len(hdul) == 1  # There should be only one HDU

    def test_simulate_returns_empty_header_for_empty_json(self):
        """Test simulate() with an empty JSON input."""
        sim = ElvisSimulation({})
        hdul = sim.simulate()

        # Check if the HDUList is still created, even for an empty input
        assert isinstance(hdul, fits.HDUList)
        assert len(hdul) == 1  # There should be only one HDU

        # Check if the header is empty or contains minimal data
        header = hdul[0].header
        assert "TIMESNR DET.NDIT" not in header
