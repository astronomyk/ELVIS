from abc import ABC, abstractmethod
from astropy.table import Table
from astropy.io.fits import ImageHDU
import numpy as np


class Morphology(ABC):
    def __init__(self, params: dict = None):
        self.params = params or {}      # Store all morphology-level options

    @staticmethod
    def from_dict(data: dict):
        morph_type = data.get("morphologytype")

        if morph_type == "point":
            return PointSourceMorphology(**data)

        elif morph_type == "extended":
            ext_type = data.get("extendedtype")
            if ext_type == "infinite":
                return InfiniteExtendedMorphology(**data)
            elif ext_type == "sersic":
                return SersicExtendedMorphology(**data)
            else:
                raise ValueError(f"Unknown extendedtype: {ext_type}")

        else:
            raise ValueError(f"Unknown morphologytype: {morph_type}")

    @abstractmethod
    def make_field(self, **kwargs):
        pass


class PointSourceMorphology(Morphology):
    def __init__(self, **params):
        super().__init__(params)

    def make_field(self, **kwargs):
        # Use kwargs if passed; fall back to self.params
        p = {**self.params, **kwargs}

        x = p.get("x")
        y = p.get("y")
        ref = p.get("ref")
        weight = p.get("weight")
        spec_type = p.get("spec_type")

        if x is None and y is None:
            table = Table()
            table["x"] = [0.0]
            table["y"] = [0.0]
            table["ref"] = [0]
            table["weight"] = [1.0]
            table["spec_type"] = [None]
            return table

        if (x is None) != (y is None):
            raise ValueError("Both 'x' and 'y' must be provided together.")

        x = list(x)
        y = list(y)
        n = len(x)

        def validate_or_default(name, arr, default):
            if arr is None:
                return [default] * n
            arr = list(arr)
            if len(arr) != n:
                raise ValueError(f"Length mismatch: '{name}' has length {len(arr)}, expected {n}.")
            return arr

        ref = validate_or_default("ref", ref, 0)
        weight = validate_or_default("weight", weight, 1.0)
        spec_type = validate_or_default("spec_type", spec_type, None)

        table = Table()
        table["x"] = x
        table["y"] = y
        table["ref"] = ref
        table["weight"] = weight
        table["spec_type"] = spec_type

        return table


class InfiniteExtendedMorphology(Morphology):
    def __init__(self, **params):
        super().__init__(params)

    def make_field(self, **kwargs):
        self.params.update(**kwargs)
        pixel_scale = kwargs.get("pixel_scale")
        fov_diameter = kwargs.get("fov_diameter")

        if pixel_scale is None or fov_diameter is None:
            raise ValueError("pixel_scale and fov_diameter must be provided for extended sources")

        # Define grid size (same logic as Sersic)
        npix = int(np.ceil(fov_diameter / pixel_scale))
        if npix % 2 == 0:
            npix += 1  # keep center pixel at center

        # Total flux within 1 arcsec^2 should be 1, ergo each pixel has a value of pixel_scale**2
        data = np.ones((npix, npix)) * pixel_scale**2

        hdu = ImageHDU(data=data, name="INFINITE_EXTENDED")
        hdu.header["PIXSCALE"] = pixel_scale
        hdu.header["FOV_DIAM"] = fov_diameter
        return hdu


class SersicExtendedMorphology(Morphology):
    def __init__(self, index, radius, **params):

        super().__init__(params)
        self.index = index
        self.radius = radius
        self.ellipticity = self.params.get("ellipticity", 0.0)
        self.angle = self.params.get("angle", 0.0)

    def make_field(self, **kwargs):
        pixel_scale = kwargs.get("pixel_scale")
        fov_diameter = kwargs.get("fov_diameter")
        ellipticity = kwargs.get("ellipticity", 0.0)  # optional, default circular
        angle_deg = kwargs.get("angle", 0.0)  # in degrees

        if pixel_scale is None or fov_diameter is None:
            raise ValueError("pixel_scale and fov_diameter must be provided for extended sources")

        if not (0 <= ellipticity <= 0.95):
            raise ValueError("ellipticity must be in [0, 0.95)")

        # Convert angle to radians
        theta = np.radians(angle_deg)

        # Compute pixel grid
        npix = int(np.ceil(fov_diameter / pixel_scale))
        if npix % 2 == 0:
            npix += 1  # ensure center pixel

        axis = (np.arange(npix) - npix // 2) * pixel_scale
        x, y = np.meshgrid(axis, axis)

        # Rotate coordinates
        x_rot = x * np.cos(theta) + y * np.sin(theta)
        y_rot = -x * np.sin(theta) + y * np.cos(theta)

        # Ellipticity scaling
        q = 1 - ellipticity  # axis ratio
        r = np.sqrt(x_rot**2 + (y_rot / q) ** 2)

        # Sersic profile
        n = self.index
        re = self.radius
        bn = 2 * n - 1/3

        with np.errstate(over='ignore'):
            image = np.exp(-bn * ((r / re) ** (1/n) - 1))

        image /= np.sum(image)

        hdu = ImageHDU(data=image, name="SERSIC_MODEL")
        hdu.header["SINDEX"] = self.index
        hdu.header["SRADIUS"] = self.radius
        hdu.header["PIXSCALE"] = pixel_scale
        hdu.header["FOV_DIAM"] = fov_diameter
        hdu.header["ELLIPTIC"] = ellipticity
        hdu.header["ANGLE"] = angle_deg

        return hdu
