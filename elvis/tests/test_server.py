import subprocess
import time
import requests
import json
import os
import pytest
from astropy.io import fits
import io


@pytest.fixture(scope="session", autouse=True)
def flask_server():
    """Start the Flask server for the duration of the test session."""
    server_process = subprocess.Popen(["python", "../server.py"],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)

    # Wait for the server to start
    time.sleep(2)
    for _ in range(10):
        try:
            response = requests.get("http://127.0.0.1:5000/")
            if response.status_code == 404:
                break
        except requests.ConnectionError:
            time.sleep(1)
    else:
        print("❌ Server did not start.")
        server_process.terminate()
        pytest.exit("Server startup failed", returncode=1)

    yield  # Tests run here

    server_process.terminate()
    server_process.wait()
    print("🔴 Server shutdown complete.")


import subprocess
import time
import requests
import json
import os
import pytest


@pytest.fixture(scope="session", autouse=True)
def flask_server():
    """Start the Flask server for the duration of the test session."""
    server_process = subprocess.Popen(["python", "../server.py"],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)

    # Wait for the server to start
    time.sleep(2)
    for _ in range(10):
        try:
            response = requests.get("http://127.0.0.1:5000/")
            if response.status_code == 404:
                break
        except requests.ConnectionError:
            time.sleep(1)
    else:
        print("❌ Server did not start.")
        server_process.terminate()
        pytest.exit("Server startup failed", returncode=1)

    yield  # Tests run here

    server_process.terminate()
    server_process.wait()
    print("🔴 Server shutdown complete.")


def test_fits_content_from_response(flask_server):
    SERVER_URL = "http://127.0.0.1:5000/process"
    JSON_FILENAME = "mocks/eris_nix.json"

    with open(JSON_FILENAME, "r") as file:
        json_data = json.load(file)

    response = requests.post(SERVER_URL, json=json_data)
    assert response.status_code == 200

    # Load response content directly as FITS
    hdul = fits.open(io.BytesIO(response.content))
    header = hdul[0].header

    # Check that a specific header exists
    assert header["HEIRARCH TARGET BRIGHTNESS MAG"] == 10
