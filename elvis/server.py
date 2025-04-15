from flask import Flask, request, send_file, jsonify
import os
import io

from elvis.simulate import ElvisSimulation

app = Flask(__name__)
PORT = 5000  # Change this to your desired port


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
