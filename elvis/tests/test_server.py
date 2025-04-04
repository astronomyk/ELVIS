import subprocess
import time
import requests
import json
import os
import unittest


class TestJsonToFitsServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the server for testing."""
        # Step 1: Start the Flask server in a separate process
        cls.server_process = subprocess.Popen(["python", "../server.py"],
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE)

        # Step 2: Wait for the server to start (poll the endpoint)
        time.sleep(2)  # Give it time to start
        for _ in range(10):  # Retry for up to 10 seconds
            try:
                response = requests.get("http://127.0.0.1:5000/")
                if response.status_code == 404:  # Server is running
                    break
            except requests.ConnectionError:
                time.sleep(1)
        else:
            print("Error: Server did not start.")
            cls.server_process.terminate()
            exit(1)

    @classmethod
    def tearDownClass(cls):
        """Shut down the server after testing."""
        cls.server_process.terminate()
        cls.server_process.wait()
        print("🔴 Server shutdown complete.")

    def test_json_to_fits(self):
        """Test the server by sending a POST request and checking the response."""
        # Server details
        SERVER_URL = "http://127.0.0.1:5000/process"
        JSON_FILENAME = "mocks/eris_nix.json"
        FITS_FILENAME = "output.fits"

        # Step 3: Send a test request
        with open(JSON_FILENAME, "r") as file:
            json_data = json.load(file)

        response = requests.post(SERVER_URL, json=json_data)

        # Step 4: Check response and save FITS file
        if response.status_code == 200:
            with open(FITS_FILENAME, "wb") as f:
                f.write(response.content)
            print(f"✅ Test Passed! FITS file saved as {FITS_FILENAME}")
        else:
            print(f"❌ Test Failed! Status Code: {response.status_code}")
            try:
                # Attempt to print JSON content if available
                print(f"Response JSON: {response.json()}")
            except requests.exceptions.JSONDecodeError:
                # If JSON is not found, print raw response content
                print(f"Raw Response: {response.text}")


# if __name__ == '__main__':
#     unittest.main()
