from flask import Flask, request, send_file, jsonify
from astropy.io import fits
import json
import os

app = Flask(__name__)
PORT = 5000  # Change this to your desired port


@app.route('/process', methods=['POST'])
def process_json():
    if not request.is_json:
        return jsonify({"error": "Invalid input, expected JSON"}), 400

    data = request.get_json()

    # Create a primary HDU (empty data, just a header)
    hdu = fits.PrimaryHDU()

    # Convert JSON data to hierarchical FITS header keywords
    header = hdu.header

    # Create an HDU list and write to FITS file
    hdul = fits.HDUList([hdu])
    fits_filename = os.path.join(os.getcwd(), "output.fits")
    hdul.writeto(fits_filename, overwrite=True)

    return send_file(fits_filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
