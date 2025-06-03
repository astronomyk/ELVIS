import pytest
import json
import io
from pathlib import Path
from astropy.io import fits

from elvis.server import app  # import the Flask app

JSON_FILENAME = Path(__file__).parent / "data/eris_nix.json"


@pytest.fixture
def client():
    app.config["TESTING"] = True  # Optional: Flask runs in testing mode
    with app.test_client() as client:
        yield client


def test_fits_content_from_response(client):
    with open(JSON_FILENAME, "r") as file:
        json_data = json.load(file)

    response = client.post("/process", json=json_data)

    assert response.status_code == 200
    assert response.mimetype == "application/fits"


def test_fits_header_has_keyword_from_input_json(client):
    with open(JSON_FILENAME, "r") as file:
        json_data = json.load(file)

    response = client.post("/process", json=json_data)

    # Load response content directly as FITS
    hdul = fits.open(io.BytesIO(response.data))

    assert hdul[0].header["TARGET BRIGHTNESS MAG"] == 10
