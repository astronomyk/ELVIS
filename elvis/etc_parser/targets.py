from abc import ABC, abstractmethod
from astropy.table import Table
from astropy.io.fits import ImageHDU
import numpy as np


class Morphology(ABC):
    @staticmethod
    def from_dict(data: dict):
        morph_type = data.get("morphologytype")

        if morph_type == "point":
            return PointSourceMorphology()

        elif morph_type == "extended":
            ext_type = data.get("extendedtype")
            if ext_type == "infinite":
                return InfiniteExtendedMorphology()
            elif ext_type == "sersic":
                index = data.get("index", 1)
                radius = data.get("radius", 0.5)
                return SersicExtendedMorphology(index=index, radius=radius)
            else:
                raise ValueError(f"Unknown extendedtype: {ext_type}")

        else:
            raise ValueError(f"Unknown morphologytype: {morph_type}")

    @abstractmethod
    def make_field(self, **kwargs):
        pass


class PointSourceMorphology(Morphology):
    def make_field(self, **kwargs):
        """Returns an astropy Table with a single point source at (0, 0)"""
        table = Table()
        table['x'] = [0.0]
        table['y'] = [0.0]
        table['ref'] = [0]      # refers to first SED in the scene
        table['weight'] = [1.0] # total flux
        return table


class InfiniteExtendedMorphology(Morphology):
    def make_field(self, **kwargs):
        """Returns a placeholder FITS image for infinite source"""
        pixel_scale = kwargs.get("pixel_scale")
        fov_diameter = kwargs.get("fov_diameter")

        if pixel_scale is None or fov_diameter is None:
            raise ValueError("pixel_scale and fov_diameter must be provided for extended sources")

        # Placeholder image, actual model not needed (uniform)
        data = np.zeros((1, 1))
        hdu = ImageHDU(data=data, name="INFINITE_EXTENDED")
        hdu.header["PIXSCALE"] = pixel_scale
        hdu.header["FOV_DIAM"] = fov_diameter
        return hdu


class SersicExtendedMorphology(Morphology):
    def __init__(self, index=1.0, radius=0.5):
        self.index = index  # Sersic index n
        self.radius = radius  # effective radius in arcsec

    def make_field(self, **kwargs):
        pixel_scale = kwargs.get("pixel_scale")
        fov_diameter = kwargs.get("fov_diameter")
        ellipticity = kwargs.get("ellipticity", 0.0)  # optional, default circular
        angle_deg = kwargs.get("angle", 0.0)  # in degrees

        if pixel_scale is None or fov_diameter is None:
            raise ValueError("pixel_scale and fov_diameter must be provided for extended sources")

        if not (0 <= ellipticity < 1):
            raise ValueError("ellipticity must be in [0, 1)")

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
