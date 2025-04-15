from astropy.io import fits


class ElvisSimulation:
    def __init__(self, data):
        """

        Parameters
        ----------
        data : dict
            JSON format
        """
        # Top-level attributes based on the provided JSON structure
        self.data = data
        self.target = data.get("target", {})
        self.sky = data.get("sky", {})
        self.instrument = data.get("instrument", {})
        self.timesnr = data.get("timesnr", {})
        self.output = data.get("output", {})
        self.instrument_name = data.get("instrumentName", "")
        self.seeingiqao = data.get("seeingiqao", {})

    def simulate(self):
        """Converts the instance data into a FITS HDUList."""
        # Recursive function to add dictionary keys as FITS header values
        def add_to_header(d, prefix=""):
            for key, value in d.items():
                new_key = f"{prefix} {key}".upper().strip()
                if isinstance(value, dict):
                    add_to_header(value, new_key)
                else:
                    try:
                        header[new_key] = value
                    except ValueError:
                        header[new_key] = str(value)

        # Create a primary HDU with header
        hdu = fits.PrimaryHDU()
        header = hdu.header
        add_to_header(self.data)
        # Add the data to the header
        # add_to_header(self.target, "TARGET")
        # add_to_header(self.sky, "SKY")
        # add_to_header(self.instrument, "INSTRUMENT")
        # add_to_header(self.timesnr, "TIMESNR")
        # add_to_header(self.output, "OUTPUT")
        # add_to_header(self.seeingiqao, "SEEINGAO")

        # Create an HDUList with the primary HDU
        hdul = fits.HDUList([hdu])
        return hdul
