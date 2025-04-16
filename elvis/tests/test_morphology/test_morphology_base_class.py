import json
from pathlib import Path
from astropy.table import Table
from astropy.io.fits import ImageHDU
import pytest

from elvis.targets import Morphology, PointSourceMorphology, SersicExtendedMorphology, InfiniteExtendedMorphology


def test_point_source_from_dict():
    morph = Morphology.from_dict({"morphologytype": "point"})
    assert isinstance(morph, PointSourceMorphology)

def test_infinite_extended_from_dict():
    morph = Morphology.from_dict({
        "morphologytype": "extended",
        "extendedtype": "infinite"
    })
    assert isinstance(morph, InfiniteExtendedMorphology)

def test_sersic_extended_from_dict_with_defaults():
    morph = Morphology.from_dict({
        "morphologytype": "extended",
        "extendedtype": "sersic",
        "index": 2.0,
        "radius": 1.5
    })
    assert isinstance(morph, SersicExtendedMorphology)
    assert morph.index == 2.0
    assert morph.radius == 1.5
    assert morph.ellipticity == 0.0
    assert morph.angle == 0.0

def test_sersic_extended_from_dict_with_optional():
    morph = Morphology.from_dict({
        "morphologytype": "extended",
        "extendedtype": "sersic",
        "index": 3.0,
        "radius": 1.0,
        "ellipticity": 0.3,
        "angle": 45
    })
    assert isinstance(morph, SersicExtendedMorphology)
    assert morph.ellipticity == 0.3
    assert morph.angle == 45

def test_invalid_extended_type_raises():
    with pytest.raises(ValueError, match="Unknown extendedtype: weirdshape"):
        Morphology.from_dict({
            "morphologytype": "extended",
            "extendedtype": "weirdshape"
        })

def test_invalid_morphologytype_raises():
    with pytest.raises(ValueError, match="Unknown morphologytype: blob"):
        Morphology.from_dict({
            "morphologytype": "blob"
        })



# Path to your test JSON file

TEST_FILE = Path(__file__).parent.parent / "data" / "eris_nix.json"
def test_parse_morphology_from_json():
    with open(TEST_FILE, "r") as f:
        data = json.load(f)

    morph_data = data["target"]["morphology"]
    morph = Morphology.from_dict(morph_data)

    assert morph is not None
    assert hasattr(morph, "make_field")

    # Call make_field() with dummy params if needed
    result = morph.make_field(pixel_scale=0.05, fov_diameter=5.0)
    assert isinstance(result, (Table, ImageHDU))
