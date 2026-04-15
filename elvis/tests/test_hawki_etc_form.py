"""Tests for the HAWK-I ETC form builder blueprint."""

import json
import pytest

from elvis.server import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_form_page_loads(client):
    """GET /hawki-etc-form returns 200 with the form page."""
    response = client.get("/hawki-etc-form")
    assert response.status_code == 200
    assert b"HAWK-I" in response.data


def test_instrument_nav_present(client):
    """The page contains the instrument navigation bar."""
    response = client.get("/hawki-etc-form")
    assert b"instrument-nav" in response.data
    assert b"ERIS" in response.data


def test_form_config_injected(client):
    """The page contains the FORM_CONFIG JavaScript variable."""
    response = client.get("/hawki-etc-form")
    assert b"FORM_CONFIG" in response.data
    assert b"MARCS" in response.data
    assert b"hawki_filters" in response.data


def test_config_api_endpoint(client):
    """GET /api/hawki-etc-form-config returns valid JSON config."""
    response = client.get("/api/hawki-etc-form-config")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "catalogs" in data
    assert "MARCS" in data["catalogs"]
    assert "hawki_filters" in data
    assert len(data["hawki_filters"]) == 11


def test_etc_proxy_rejects_non_json(client):
    """POST /api/hawki-etc-proxy without JSON returns 400."""
    response = client.post("/api/hawki-etc-proxy", data="not json",
                           content_type="text/plain")
    assert response.status_code == 400


def test_etc_proxy_returns_501(client):
    """POST /api/hawki-etc-proxy returns 501 (no v2.0 API for HAWK-I)."""
    payload = {"instrumentName": "hawki", "target": {}}
    response = client.post("/api/hawki-etc-proxy",
                           data=json.dumps(payload),
                           content_type="application/json")
    assert response.status_code == 501
    data = json.loads(response.data)
    assert "error" in data
    assert "HAWK-I" in data["error"]
    assert "hint" in data
