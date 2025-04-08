from astropy.io import fits


def simulate_from_json(data):
    # Create a primary HDU with header
    hdu = fits.PrimaryHDU()
    header = hdu.header

    def add_to_header(d, prefix="HEIRARCH"):
        for key, value in d.items():
            new_key = f"{prefix}.{key}".upper()
            if isinstance(value, dict):
                add_to_header(value, new_key)
            else:
                try:
                    header[new_key] = value
                except ValueError:
                    header[new_key] = str(value)

    add_to_header(data)
    hdul = fits.HDUList([hdu])
    return hdul
