"""
ERIS ETC Form Builder blueprint.

Provides a web UI to generate JSON input files compatible with the
ESO ETC 2.0 API for the ERIS instrument.
"""

import json
import warnings

from flask import Blueprint, render_template, request, jsonify
import requests as http_requests

from .config import ERIS_FORM_CONFIG

eris_etc_form_bp = Blueprint(
    "eris_etc_form",
    __name__,
    template_folder="../templates",
    static_folder="../static",
)

ETC_API_URL = "https://etc.eso.org/observing/etc/etcapi/Eris/"


@eris_etc_form_bp.route("/eris-etc-form")
def form_page():
    """Serve the ETC JSON form builder page."""
    return render_template("eris_etc_form.html", config=ERIS_FORM_CONFIG,
                           current_instrument="eris")


@eris_etc_form_bp.route("/api/eris-etc-form-config")
def form_config():
    """Return the raw form configuration as JSON (for debugging)."""
    return jsonify(ERIS_FORM_CONFIG)


@eris_etc_form_bp.route("/api/eris-etc-proxy", methods=["POST"])
def etc_proxy():
    """
    Forward an ETC JSON payload to the ESO ETC API and return the response.

    Mirrors the callEtc function in misc/ESO_scripts/etc_cli.py.
    """
    if not request.is_json:
        return jsonify({"error": "Expected JSON payload"}), 400

    payload = request.get_json()

    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="Unverified HTTPS request")
            resp = http_requests.post(
                ETC_API_URL,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                verify=False,
                timeout=60,
            )
        return (resp.content, resp.status_code,
                {"Content-Type": "application/json"})
    except http_requests.RequestException as exc:
        return jsonify({"error": str(exc)}), 502
