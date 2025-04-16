import os
import numpy as np
import pytest

from astropy.io.fits import ImageHDU
from elvis.etc_parser.targets import SersicExtendedMorphology  # Adjust import as needed


def show_image(hdu: ImageHDU, title: str):
    """Show image if not on GitHub Actions (CI = true)"""
    if os.getenv("CI") != "true":
        from matplotlib import pyplot as plt
        plt.imshow(hdu.data, origin="lower", cmap="viridis", norm="log")
        plt.title(title)
        plt.colorbar(label="Normalized Flux")
        plt.show()


@pytest.mark.parametrize("index,radius,ellipticity,angle,title", [
    (2.0, 0.5, 0.0, 0, "Circular Sersic (n=2.0)"),
    (3.5, 0.8, 0.5, 30, "Elliptical Sersic (e=0.5, θ=30°)"),
    (1.0, 1.0, 0.99, 0, "Edge Case: High Ellipticity (e=0.99)")
])
def test_sersic_profiles(index, radius, ellipticity, angle, title):
    sersic = SersicExtendedMorphology(index=index, radius=radius)
    hdu = sersic.make_field(
        pixel_scale=0.05,
        fov_diameter=5.0,
        ellipticity=ellipticity,
        angle=angle
    )

    assert isinstance(hdu, ImageHDU)
    assert hdu.data.shape[0] == hdu.data.shape[1]  # image should be square
    assert np.isclose(np.sum(hdu.data), 1.0, atol=1e-3)  # flux normalized
    assert not np.isnan(hdu.data).any()

    show_image(hdu, title)
