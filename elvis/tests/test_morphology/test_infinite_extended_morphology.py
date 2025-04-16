import os
import pytest
import numpy as np

from astropy.io.fits import ImageHDU
from elvis.targets import InfiniteExtendedMorphology


def show_image(hdu: ImageHDU, title: str):
    """Show image if not on GitHub Actions (CI = true)"""
    if os.getenv("CI") != "true":
        from matplotlib import pyplot as plt
        plt.imshow(hdu.data, origin="lower", cmap="plasma", norm="log")
        plt.title(title)
        plt.colorbar(label="Flux/pixel")
        plt.show()


def extract_patch_sum(hdu, pixel_scale):
    """Sum flux over closest integer-sized 1 arcsec² square patch centered on image"""
    pixels_per_arcsec = 1.0 / pixel_scale
    npix = int(np.round(pixels_per_arcsec))  # pixel width for ~1 arcsec

    center = hdu.data.shape[0] // 2
    half = npix // 2
    patch = hdu.data[center - half:center + half + 1, center - half:center + half + 1]
    return np.sum(patch)


@pytest.mark.parametrize("pixel_scale", [
    0.02,   # much smaller than 1 arcsec (high resolution)
    0.999,  # just below 1 arcsec
    1.0,    # exactly 1 arcsec per pixel
    1.001,  # just above 1 arcsec
])
def test_uniform_flux_scaling_for_values_up_to_1_arcsec(pixel_scale):
    fov_diameter = pixel_scale * 100  # large enough to fit several 1 arcsec patches

    morph = InfiniteExtendedMorphology()
    hdu = morph.make_field(pixel_scale=pixel_scale, fov_diameter=fov_diameter)

    assert isinstance(hdu, ImageHDU)
    assert not np.isnan(hdu.data).any()

    patch_sum = extract_patch_sum(hdu, pixel_scale)

    # Allow looser tolerance for coarse pixelation cases
    assert np.isclose(patch_sum, 1.0, rtol=0.05), \
        f"Patch sum {patch_sum:.3f} != 1.0 for pixel scale {pixel_scale}"

    show_image(hdu, f"Infinite Uniform Source (pix={pixel_scale:.3f} arcsec)")


def test_uniform_flux_scaling_for_values_above_1_arcsec():
    pixel_scale = 2
    fov_diameter = pixel_scale * 10  # large enough to fit several 1 arcsec patches

    morph = InfiniteExtendedMorphology()
    hdu = morph.make_field(pixel_scale=pixel_scale, fov_diameter=fov_diameter)
    patch_sum = hdu.data[0,0] / pixel_scale**2

    assert np.isclose(patch_sum, 1.0, rtol=0.05), \
        f"Patch sum {patch_sum:.3f} != 1.0 for pixel scale {pixel_scale}"

    show_image(hdu, f"Infinite Uniform Source (pix={pixel_scale:.3f} arcsec)")
