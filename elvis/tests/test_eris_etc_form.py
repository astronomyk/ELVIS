"""Tests for the ERIS ETC form builder blueprint."""

import json
import pytest
from unittest.mock import patch, MagicMock

from elvis.server import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_form_page_loads(client):
    """GET /eris-etc-form returns 200 with the form page."""
    response = client.get("/eris-etc-form")
    assert response.status_code == 200
    assert b"ERIS" in response.data


def test_form_config_injected(client):
    """The page contains the FORM_CONFIG JavaScript variable."""
    response = client.get("/eris-etc-form")
    assert b"FORM_CONFIG" in response.data
    assert b"MARCS" in response.data
    assert b"turbulence_categories" in response.data


def test_config_api_endpoint(client):
    """GET /api/eris-etc-form-config returns valid JSON config."""
    response = client.get("/api/eris-etc-form-config")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "catalogs" in data
    assert "MARCS" in data["catalogs"]
    assert "nix_filters" in data
    assert len(data["nix_filters"]) == 17


def test_etc_proxy_rejects_non_json(client):
    """POST /api/eris-etc-proxy without JSON returns 400."""
    response = client.post("/api/eris-etc-proxy", data="not json",
                           content_type="text/plain")
    assert response.status_code == 400


@patch("elvis.eris_etc_form.http_requests.post")
def test_etc_proxy_forwards_json(mock_post, client):
    """POST /api/eris-etc-proxy forwards payload to ESO ETC API."""
    mock_response = MagicMock()
    mock_response.content = json.dumps({"status": "ok"}).encode()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    payload = {"instrumentName": "eris", "target": {}}
    response = client.post("/api/eris-etc-proxy",
                           data=json.dumps(payload),
                           content_type="application/json")
    assert response.status_code == 200
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert "Eris" in call_args[0][0]


def test_index_page_loads(client):
    """GET / returns the splash page listing instruments."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"ELVIS" in response.data
    assert b"ERIS" in response.data
    assert b"HAWK-I" in response.data
