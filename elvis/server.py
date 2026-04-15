from flask import Flask, request, send_file, jsonify, render_template
import os
import io

from elvis.simulate import ElvisSimulation
from elvis.eris_etc_form import eris_etc_form_bp
from elvis.hawki_etc_form import hawki_etc_form_bp

app = Flask(__name__)
app.register_blueprint(eris_etc_form_bp)
app.register_blueprint(hawki_etc_form_bp)
PORT = 5000  # Change this to your desired port

# Instrument registry — each ETC form blueprint adds an entry here.
# Templates read this via the INSTRUMENTS Jinja2 global.
INSTRUMENTS = [
    {
        "id": "eris",
        "name": "ERIS",
        "url": "/eris-etc-form",
        "description": "Enhanced Resolution Imager and Spectrograph (VLT)",
    },
    {
        "id": "hawki",
        "name": "HAWK-I",
        "url": "/hawki-etc-form",
        "description": "High Acuity Wide-field K-band Imager (VLT)",
    },
]

app.jinja_env.globals["INSTRUMENTS"] = INSTRUMENTS


@app.route("/")
def index():
    """Splash page listing all available instrument ETC forms."""
    return render_template("index.html", current_instrument=None)


@app.route('/process', methods=['POST'])
def process_json():
    if not request.is_json:
        return jsonify({"error": "Invalid input, expected JSON"}), 400

    data = request.get_json()
    sim = ElvisSimulation(data)
    hdul = sim.simulate()

    # Check optional flag: use disk or memory
    use_disk = data.get("output", {}).get("use_disk", False)

    if use_disk:
        fits_filename = os.path.join(os.getcwd(), "output.fits")
        hdul.writeto(fits_filename, overwrite=True)
        return jsonify({"filepath": fits_filename})

    else:
        mem_buf = io.BytesIO()
        hdul.writeto(mem_buf)
        mem_buf.seek(0)
        return send_file(mem_buf, as_attachment=True,
                         download_name="output.fits",
                         mimetype="application/fits")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
