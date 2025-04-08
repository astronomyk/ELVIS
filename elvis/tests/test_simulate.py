import pytest
from astropy.io import fits
from elvis.simulate import simulate_from_json


class TestSimulateFromJson:
    def test_returns_hdulist(self):
        sample_json = {
            "target": {
                "brightness": {
                    "mag": 10
                }
            },
            "output": {
                "use_disk": False
            }
        }
        hdul = simulate_from_json(sample_json)
        assert isinstance(hdul, fits.HDUList)
        assert isinstance(hdul[0], fits.PrimaryHDU)

    def test_fits_header_contains_hierarchy(self):
        sample_json = {
            "target": {
                "brightness": {
                    "mag": 10
                }
            }
        }
        hdul = simulate_from_json(sample_json)
        header = hdul[0].header
        assert "HEIRARCH.TARGET.BRIGHTNESS.MAG" in header
        assert header["HEIRARCH.TARGET.BRIGHTNESS.MAG"] == 10

    def test_string_value_conversion(self):
        json_input = {
            "metadata": {
                "description": "Test simulation"
            }
        }
        hdul = simulate_from_json(json_input)
        header = hdul[0].header
        assert "HEIRARCH.METADATA.DESCRIPTION" in header
        assert header["HEIRARCH.METADATA.DESCRIPTION"] == "Test simulation"

    def test_nested_structure_is_flattened(self):
        json_input = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": 42
                    }
                }
            }
        }
        hdul = simulate_from_json(json_input)
        header = hdul[0].header
        assert "HEIRARCH.LEVEL1.LEVEL2.LEVEL3.VALUE" in header
        assert header["HEIRARCH.LEVEL1.LEVEL2.LEVEL3.VALUE"] == 42

    def test_non_serializable_types_are_converted_to_string(self):
        json_input = {
            "observation": {
                "timestamp": "2024-04-08T12:00:00Z"
            }
        }
        hdul = simulate_from_json(json_input)
        header = hdul[0].header
        assert header["HEIRARCH.OBSERVATION.TIMESTAMP"] == "2024-04-08T12:00:00Z"
