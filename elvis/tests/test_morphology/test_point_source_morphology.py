import pytest
from astropy.table import Table
from elvis.targets import PointSourceMorphology


def test_default_single_point():
    morph = PointSourceMorphology()
    table = morph.make_field()

    assert isinstance(table, Table)
    assert len(table) == 1
    assert table["x"][0] == 0.0
    assert table["y"][0] == 0.0
    assert table["ref"][0] == 0
    assert table["weight"][0] == 1.0
    assert table["spec_type"][0] is None


def test_full_input_all_columns_equal_length():
    morph = PointSourceMorphology()
    table = morph.make_field(
        x=[1.0, 2.0],
        y=[1.0, 2.0],
        ref=[0, 1],
        weight=[0.5, 0.8],
        spec_type=["star", "galaxy"]
    )

    assert len(table) == 2
    assert table["x"][1] == 2.0
    assert table["ref"][1] == 1
    assert table["weight"][1] == 0.8
    assert table["spec_type"][1] == "galaxy"


def test_missing_spec_type_column_fills_with_none():
    morph = PointSourceMorphology()
    table = morph.make_field(
        x=[0.1, 0.2],
        y=[0.3, 0.4],
        ref=[0, 1],
        weight=[1.0, 0.9]
    )

    assert all(spt is None for spt in table["spec_type"])


def test_missing_weight_column_fills_with_ones():
    morph = PointSourceMorphology()
    table = morph.make_field(
        x=[0.1, 0.2],
        y=[0.3, 0.4],
        ref=[0, 1],
        spec_type=["star", "galaxy"]
    )

    assert all(weight == 1. for weight in table["weight"])


def test_missing_ref_column_fills_with_zeros():
    morph = PointSourceMorphology()
    table = morph.make_field(
        x=[0.1, 0.2],
        y=[0.3, 0.4],
        weight=[0.5, 0.6],
        spec_type=["quasar", "galaxy"]
    )

    assert all(ref == 0 for ref in table["ref"])


def test_only_x_provided_raises_error():
    morph = PointSourceMorphology()
    with pytest.raises(ValueError, match="Both 'x' and 'y' must be provided together."):
        morph.make_field(x=[0.1, 0.2])


def test_mismatched_column_lengths_raises_error():
    morph = PointSourceMorphology()
    with pytest.raises(ValueError, match="Length mismatch: 'ref' has length 1, expected 2."):
        morph.make_field(
            x=[0.1, 0.2],
            y=[0.3, 0.4],
            ref=[0],  # Length mismatch
            weight=[1.0, 1.0]
        )
