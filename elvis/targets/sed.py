from synphot import SourceSpectrum, units
from synphot.models import BlackBody1D, PowerLawFlux1D
from astropy import units as u
from pathlib import Path
import os

TEMPLATES_PATH = Path("D:/ELVIS/ETC_SED/")  # Update this path as needed


class SED:
    def __init__(self, sed_type):
        self.sed_type = sed_type

    @staticmethod
    def from_dict(sed_dict):
        sed_type = sed_dict.get("sedtype")
        if sed_type == "BlackBody":
            return BlackBodySED.from_dict(sed_dict)
        elif sed_type == "PowerLaw":
            return PowerLawSED.from_dict(sed_dict)
        elif sed_type == "FileSED":
            return FileSED.from_dict(sed_dict)
        elif sed_type == "spectrum":
            spectrum = sed_dict.get("spectrum", {})
            spectrumtype = spectrum.get("spectrumtype")
            if spectrumtype == "template":
                return TemplateSED.from_dict(sed_dict)
            else:
                raise ValueError(f"Unsupported spectrumtype: {spectrumtype}")
        else:
            raise ValueError(f"Unsupported SED type: {sed_type}")

    def get_spectrum(self):
        raise NotImplementedError("Subclasses must implement get_spectrum()")


class BlackBodySED(SED):
    def __init__(self, temperature):
        super().__init__("BlackBody")
        self.temperature = temperature

    @staticmethod
    def from_dict(d):
        temp = d.get("temperature")
        return BlackBodySED(temp)

    def get_spectrum(self):
        bb = BlackBody1D(temperature=self.temperature * u.K)
        return SourceSpectrum(bb)


class PowerLawSED(SED):
    def __init__(self, alpha, amplitude):
        super().__init__("PowerLaw")
        self.alpha = alpha
        self.amplitude = amplitude

    @staticmethod
    def from_dict(d):
        return PowerLawSED(d["alpha"], d["amplitude"])

    def get_spectrum(self):
        model = PowerLawFlux1D(amplitude=self.amplitude, x_0=1*u.AA, alpha=self.alpha)
        return SourceSpectrum(model)


class FileSED(SED):
    def __init__(self, file_path):
        super().__init__("FileSED")
        self.file_path = file_path

    @staticmethod
    def from_dict(d):
        return FileSED(d["file"])

    def get_spectrum(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"SED file not found: {self.file_path}")
        return SourceSpectrum.from_file(self.file_path)


class TemplateSED(SED):
    def __init__(self, catalog, template_id):
        super().__init__("TemplateSED")
        self.catalog = catalog
        self.template_id = template_id

    @staticmethod
    def from_dict(d):
        catalog = d["spectrum"]["params"].get("catalog")
        if catalog == "MARCS":
            return MARCSTemplateSED.from_dict(d)
        elif catalog == "PHOENIX":
            return PhoenixTemplateSED.from_dict(d)
        elif catalog == "SWIRE":
            return SWIRETemplateSED.from_dict(d)
        elif catalog == "Kinney":
            return KinneyTemplateSED.from_dict(d)
        elif catalog == "Kurucz":
            return KuruczTemplateSED.from_dict(d)
        elif catalog == "Pickles":
            return PicklesTemplateSED.from_dict(d)
        elif catalog == "Various":
            return VariousTemplateSED.from_dict(d)
        else:
            raise ValueError(f"Unsupported template catalog: {catalog}")

    def get_template_file(self):
        raise NotImplementedError("Subclasses must implement get_template_file()")

    def get_spectrum(self):
        template_file = self.get_template_file()
        if not os.path.exists(template_file):
            raise FileNotFoundError(f"Template SED file not found: {template_file}")
        return SourceSpectrum.from_file(template_file)


class MARCSTemplateSED(TemplateSED):
    @staticmethod
    def from_dict(d):
        """
        Parse MARCS template ID in the format <temperature>:<logg>.

        Acceptable ranges:
        - temperature: integer in [3000, 8000]
        - logg: float in [3.0, 5.0], formatted to 1 decimal place
        """
        params = d["spectrum"]["params"]
        temp_str, logg_str = params["id"].split(":")
        temp = int(temp_str)
        logg = float(logg_str)
        template_id = f"p{temp}_g+{logg:.1f}_m0.0_t02_st_z+0.00_a+0.00_c+0.00_n+0.00_o+0.00"
        return MARCSTemplateSED("MARCS", template_id)

    def get_template_file(self):
        return os.path.join(TEMPLATES_PATH, "MARCS", f"{self.template_id}.fits")


class PhoenixTemplateSED(TemplateSED):
    @staticmethod
    def from_dict(d):
        """
        Parse PHOENIX template ID in the format <temperature>:<logg>.

        Acceptable ranges:
        - temperature: integer in [2300, 12000], zero-padded to 5 digits
        - logg: float in [0.0, 6.0], formatted to 2 decimal places
        """
        params = d["spectrum"]["params"]
        temp_str, logg_str = params["id"].split(":")
        temp = int(temp_str)
        logg = float(logg_str)
        template_id = f"lte{temp:05d}-{logg:.2f}-PHOENIX"
        return PhoenixTemplateSED("PHOENIX", template_id)

    def get_template_file(self):
        return os.path.join(TEMPLATES_PATH, "PHOENIX", f"{self.template_id}.fits")


class SWIRETemplateSED(TemplateSED):
    dropdown_to_file = {
        "13 Gyr old elliptical": "Ell13.fits",
        "2 Gyr old elliptical": "Ell2.fits",
        "5 Gyr old elliptical": "Ell5.fits",
        "AGN BQSO1": "BQSO1.fits",
        "AGN QSO1": "QSO1.fits",
        "AGN QSO2": "QSO2.fits",
        "AGN Seyfert 1.8": "Sey18.fits",
        "AGN Seyfert 2.0": "Sey2.fits",
        "AGN TQSO1": "TQSO1.fits",
        "AGN Torus": "Torus.fits",
        "BAL QSO, Seyfert 1, ULIRG Mrk 231": "Mrk231.fits",
        "Spiral 0": "S0.fits",
        "Spiral a": "Sa.fits",
        "Spiral b": "Sb.fits",
        "Spiral c": "Sc.fits",
        "Spiral c4": "Spi4.fits",
        "Spiral dm": "Sdm.fits",
        "Starburst Arp 220": "Arp220.fits",
        "Starburst IRAS 19254-7245 South": "I19254.fits",
        "Starburst IRAS 20551-4250": "I20551.fits"
    }

    @staticmethod
    def from_dict(d):
        params = d["spectrum"]["params"]
        display_id = params["id"]
        filename = SWIRETemplateSED.dropdown_to_file.get(display_id)
        if filename is None:
            raise ValueError(f"Unknown SWIRE template ID: {display_id}")
        return SWIRETemplateSED("SWIRE", filename.replace(".fits", ""))

    def get_template_file(self):
        return os.path.join(TEMPLATES_PATH, "SWIRE", f"{self.template_id}.fits")


class KinneyTemplateSED(TemplateSED):
    dropdown_to_file = {
        "Elliptical Galaxy": "Kinney_ell.fits",
        "S0 Galaxy": "Kinney_s0.fits",
        "Sa Galaxy": "Kinney_sa.fits",
        "Sb Galaxy": "Kinney_sb.fits",
        "Starburst Galaxy 1": "Kinney_starb1.fits",
        "Starburst Galaxy 2": "Kinney_starb2.fits",
        "Starburst Galaxy 3": "Kinney_starb3.fits",
        "Starburst Galaxy 4": "Kinney_starb4.fits",
        "Starburst Galaxy 5": "Kinney_starb5.fits",
        "Starburst Galaxy 6": "Kinney_starb6.fits"
    }

    @staticmethod
    def from_dict(d):
        params = d["spectrum"]["params"]
        display_id = params["id"]
        filename = KinneyTemplateSED.dropdown_to_file.get(display_id)
        if filename is None:
            raise ValueError(f"Unknown Kinney template ID: {display_id}")
        return KinneyTemplateSED("Kinney", filename.replace(".fits", ""))

    def get_template_file(self):
        return os.path.join(TEMPLATES_PATH, "Kinney", f"{self.template_id}.fits")


class KuruczTemplateSED(TemplateSED):
    @staticmethod
    def from_dict(d):
        """
        Parse Kurucz template ID in the format <spec_type>:<spec_sub_type>:<lum_class>.

        Acceptable values:
        - spec_type: O, B, A, F, G, K, M
        - spec_sub_type: 2, 5, 8
        - lum_class: I, V
        """
        params = d["spectrum"]["params"]
        spec_type, spec_sub_type, lum_class = params["id"].split(":")
        template_id = f"{spec_type}{spec_sub_type}{lum_class}"
        return KuruczTemplateSED("Kurucz", template_id)

    def get_template_file(self):
        return os.path.join(TEMPLATES_PATH, "Kurucz", f"{self.template_id}.fits")


class PicklesTemplateSED(TemplateSED):
    @staticmethod
    def from_dict(d):
        """
        Parse Pickles template ID in the format <spec_type>:<spec_sub_type>:<lum_class>.

        Acceptable values:
        - spec_type: O, B, A, F, G, K, M
        - spec_sub_type: 0, 2, 5, 8
        - lum_class: I, II, III, IV, V
        """
        params = d["spectrum"]["params"]
        spec_type, spec_sub_type, lum_class = params["id"].split(":")
        template_id = f"{spec_type}{spec_sub_type}{lum_class}"
        return PicklesTemplateSED("Pickles", template_id)

    def get_template_file(self):
        return os.path.join(TEMPLATES_PATH, "Pickles", f"{self.template_id}.fits")


class VariousTemplateSED(TemplateSED):
    dropdown_to_file = {
        "HII region (Orion)": "orion.fits",
        "Planetary Nebula": "pn.fits"
    }

    @staticmethod
    def from_dict(d):
        params = d["spectrum"]["params"]
        display_id = params["id"]
        filename = VariousTemplateSED.dropdown_to_file.get(display_id)
        if filename is None:
            raise ValueError(f"Unknown Various template ID: {display_id}")
        return VariousTemplateSED("Various", filename.replace(".fits", ""))

    def get_template_file(self):
        return os.path.join(TEMPLATES_PATH, "Various", f"{self.template_id}.fits")
