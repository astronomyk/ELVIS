"""
HAWK-I ETC Form Builder blueprint.

Provides a web UI to generate JSON input files compatible with the
ESO ETC 2.0 schema for the HAWK-I instrument.
"""

from flask import Blueprint, render_template, request, jsonify

from .config import HAWKI_FORM_CONFIG

hawki_etc_form_bp = Blueprint(
    "hawki_etc_form",
    __name__,
    template_folder="../templates",
    static_folder="../static",
)


@hawki_etc_form_bp.route("/hawki-etc-form")
def form_page():
    """Serve the HAWK-I ETC JSON form builder page."""
    return render_template("hawki_etc_form.html", config=HAWKI_FORM_CONFIG,
                           current_instrument="hawki")


@hawki_etc_form_bp.route("/api/hawki-etc-form-config")
def form_config():
    """Return the raw form configuration as JSON (for debugging)."""
    return jsonify(HAWKI_FORM_CONFIG)


@hawki_etc_form_bp.route("/api/hawki-etc-proxy", methods=["POST"])
def etc_proxy():
    """
    HAWK-I has no ESO ETC v2.0 API.

    Returns a helpful message directing users to the v1.0 ETC or to
    download the JSON for use with ScopeSim / ELVIS.
    """
    if not request.is_json:
        return jsonify({"error": "Expected JSON payload"}), 400

    return jsonify({
        "error": "No ESO ETC v2.0 API available for HAWK-I",
        "hint": (
            "Use 'Download JSON' to save the configuration for use with "
            "ScopeSim / ELVIS, or visit the HAWK-I ETC v1.0 at "
            "https://www.eso.org/observing/etc/bin/gen/form?"
            "INS.NAME=HAWK-I+INS.MODE=imaging"
        ),
    }), 501
