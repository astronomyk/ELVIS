/* ==========================================================
   HAWK-I ETC JSON Builder — Form Logic
   ========================================================== */

const CFG = FORM_CONFIG;   // injected by Jinja2

/* ----------------------------------------------------------
   A.  Initialization
   ---------------------------------------------------------- */
document.addEventListener("DOMContentLoaded", () => {
  populateSelects();
  setDefaults();
  attachListeners();
  updateVisibility();
  updateAOFields();
  showTab("tab-target");
});

/* Populate <select> elements from config data */
function populateSelects() {
  // Magnitude bands (grouped)
  const magSel = document.getElementById("magband");
  for (const grp of CFG.magband_groups) {
    const og = document.createElement("optgroup");
    og.label = grp.label;
    for (const opt of grp.options) {
      og.appendChild(new Option(opt.label, opt.value));
    }
    magSel.appendChild(og);
  }

  // Turbulence category
  const turbSel = document.getElementById("turbulence_category");
  for (const t of CFG.turbulence_categories) {
    turbSel.appendChild(new Option(t.label, t.value));
  }

  // Aperture pixels
  const apSel = document.getElementById("aperturepix");
  for (const v of CFG.aperture_pixels) {
    apSel.appendChild(new Option(v, v));
  }

  // AO modes
  const aoSel = document.getElementById("aoMode");
  for (const m of CFG.hawki_ao_modes) {
    aoSel.appendChild(new Option(m.label, m.value));
  }

  // HAWK-I filters
  const filterSel = document.getElementById("hawki_filter");
  for (const f of CFG.hawki_filters) {
    filterSel.appendChild(new Option(f.label, f.value));
  }

  // SWIRE templates
  const swSel = document.getElementById("swire_template");
  for (const name of CFG.catalogs.SWIRE.templates) {
    swSel.appendChild(new Option(name, name));
  }

  // Populate template Teff/logg for initial catalog (MARCS)
  populateTemplateParams("MARCS");

  // Output checkboxes
  const outDiv = document.getElementById("output-checkboxes");
  for (const grp of CFG.output_groups) {
    const gDiv = document.createElement("div");
    gDiv.className = "output-group";
    const h4 = document.createElement("h4");
    h4.textContent = grp.label;
    gDiv.appendChild(h4);
    for (const opt of grp.options) {
      const lbl = document.createElement("label");
      const cb = document.createElement("input");
      cb.type = "checkbox";
      cb.name = `output_${grp.key}_${opt.key}`;
      cb.checked = opt.default || false;
      lbl.appendChild(cb);
      lbl.appendChild(document.createTextNode(" " + opt.label));
      gDiv.appendChild(lbl);
    }
    outDiv.appendChild(gDiv);
  }
}

/* Populate Teff/logg dropdowns for a given catalog */
function populateTemplateParams(catalog) {
  const catData = CFG.catalogs[catalog];
  const teffLoggDiv = document.getElementById("template-teff-logg");
  const swireDiv = document.getElementById("template-swire");

  if (catalog === "SWIRE") {
    teffLoggDiv.style.display = "none";
    swireDiv.style.display = "";
  } else {
    teffLoggDiv.style.display = "";
    swireDiv.style.display = "none";
    // Populate Teff
    const teffSel = document.getElementById("teff");
    teffSel.innerHTML = "";
    for (const v of catData.params[0].values) {
      teffSel.appendChild(new Option(v, v));
    }
    // Populate logg
    const loggSel = document.getElementById("logg");
    loggSel.innerHTML = "";
    for (const v of catData.params[1].values) {
      loggSel.appendChild(new Option(v, v));
    }
  }
}

/* Set default values */
function setDefaults() {
  const d = CFG.defaults;
  setVal("magband", d.magband);
  setVal("magsys", d.magsys);
  setVal("mag", d.mag);
  setVal("turbulence_category", d.turbulence_category);
  setVal("aperturepix", d.aperturepix);
  setVal("teff", d.teff);
  setVal("logg", d.logg);
  setVal("aoMode", d.aoMode);
  setVal("hawki_filter", d.filter);
}

function setVal(name, value) {
  const el = document.getElementById(name) ||
             document.querySelector(`[name="${name}"]`);
  if (el) el.value = value;
}

function getVal(name) {
  const el = document.getElementById(name) ||
             document.querySelector(`[name="${name}"]:checked`) ||
             document.querySelector(`[name="${name}"]`);
  if (!el) return undefined;
  if (el.type === "checkbox") return el.checked;
  if (el.type === "radio") {
    const checked = document.querySelector(`[name="${name}"]:checked`);
    return checked ? checked.value : undefined;
  }
  return el.value;
}

/* ----------------------------------------------------------
   B.  Tab Switching
   ---------------------------------------------------------- */
function showTab(tabId) {
  document.querySelectorAll(".tab-panel").forEach(p => {
    p.classList.toggle("active", p.dataset.tab === tabId);
  });
}

/* ----------------------------------------------------------
   C.  Visibility Controller
   ---------------------------------------------------------- */
function updateVisibility() {
  document.querySelectorAll(".conditional").forEach(div => {
    const field = div.dataset.dependsOn;
    const expected = div.dataset.dependsValue;
    if (!field) return;

    let current;
    if (field === "redshiftEnabled") {
      current = document.getElementById("redshiftEnabled").checked ? "true" : "false";
    } else {
      current = getVal(field);
    }

    const visible = current === expected;
    div.style.display = visible ? "" : "none";
  });
}

function updateAOFields() {
  const aoMode = getVal("aoMode");
  const showGuide = aoMode === "tts";
  document.getElementById("ao-params").style.display = showGuide ? "" : "none";
}

/* ----------------------------------------------------------
   D.  Event Listeners
   ---------------------------------------------------------- */
function attachListeners() {
  // Tab switching
  document.querySelectorAll('.tabs input[type="radio"]').forEach(r => {
    r.addEventListener("change", () => showTab(r.id));
  });

  // Conditional visibility triggers
  const triggers = ["morphologytype", "sedtype", "spectrumtype", "extendedtype"];
  for (const name of triggers) {
    document.querySelectorAll(`[name="${name}"]`).forEach(el => {
      el.addEventListener("change", updateVisibility);
    });
  }
  document.getElementById("redshiftEnabled").addEventListener("change", updateVisibility);

  // Catalog change -> repopulate template params
  document.getElementById("catalog").addEventListener("change", (e) => {
    populateTemplateParams(e.target.value);
  });

  // AO mode change -> toggle guide star fields
  document.getElementById("aoMode").addEventListener("change", () => {
    updateAOFields();
  });

  // Action buttons
  document.getElementById("btnPreview").addEventListener("click", doPreview);
  document.getElementById("btnDownload").addEventListener("click", doDownload);
  document.getElementById("btnSend").addEventListener("click", doSendToETC);
  document.getElementById("btnClosePreview").addEventListener("click", () => {
    document.getElementById("preview-panel").style.display = "none";
  });

  // Load JSON file
  document.getElementById("loadFile").addEventListener("change", doLoadJSON);
}

/* ----------------------------------------------------------
   E.  JSON Assembler
   ---------------------------------------------------------- */
function buildJSON() {
  const json = { instrumentName: "hawki" };

  // --- Target ---
  const morphtype = getVal("morphologytype");
  const morph = { morphologytype: morphtype };
  if (morphtype === "extended") {
    morph.extendedtype = getVal("extendedtype");
    if (morph.extendedtype === "sersic") {
      morph.index = parseFloat(getVal("sersic_index")) || 1;
      morph.radius = parseFloat(getVal("sersic_radius")) || 0.5;
    }
  }

  const sedtype = getVal("sedtype");
  const sed = { sedtype: sedtype, extinctionav: parseFloat(getVal("extinctionav")) || 0 };

  if (sedtype === "spectrum") {
    const stype = getVal("spectrumtype");
    const spectrum = { spectrumtype: stype };

    if (stype === "template") {
      const catalog = getVal("catalog");
      let id;
      if (catalog === "SWIRE") {
        id = getVal("swire_template");
      } else {
        id = getVal("teff") + ":" + getVal("logg");
      }
      spectrum.params = { catalog: catalog, id: id };
    } else if (stype === "blackbody") {
      spectrum.params = { temperature: parseFloat(getVal("bb_temperature")) || 1000 };
    } else if (stype === "powerlaw") {
      spectrum.params = { exponent: parseFloat(getVal("pl_exponent")) || 0 };
    }

    sed.spectrum = spectrum;
  } else {
    // emissionline
    sed.emissionline = {
      params: {
        lambda: parseFloat(getVal("em_lambda")) || 1000,
        fwhm: parseFloat(getVal("em_fwhm")) || 1,
      }
    };
  }

  // Redshift
  if (document.getElementById("redshiftEnabled").checked) {
    sed.redshift = {
      redshift: parseFloat(getVal("redshift")) || 0,
      baryvelcor: parseFloat(getVal("baryvelcor")) || 0,
    };
  }

  json.target = {
    morphology: morph,
    sed: sed,
    brightness: {
      brightnesstype: "mag",
      magband: getVal("magband"),
      mag: parseFloat(getVal("mag")) || 10,
      magsys: getVal("magsys"),
    },
  };

  // --- Sky ---
  json.sky = {
    airmass: parseFloat(getVal("airmass")) || 1.2,
    fli: parseFloat(getVal("fli")) || 0.5,
    waterVapour: parseFloat(getVal("waterVapour")) || 2.5,
    moonDistance: parseFloat(getVal("moonDistance")) || 30,
  };

  // --- Seeing ---
  const aoMode = getVal("aoMode");
  json.seeing = {
    turbulence_category: parseInt(getVal("turbulence_category")) || 50,
    separation: parseFloat(getVal("separation")) || 0,
    aperturepix: parseInt(getVal("aperturepix")) || 9,
  };
  if (aoMode === "tts") {
    json.seeing["SEQ.TTS.MAG"] = parseFloat(getVal("tts_mag")) || 0;
  }

  // --- Instrument ---
  const insConfig = "img_" + aoMode;
  json.instrument = {
    ins_configuration: insConfig,
    "INS.FILT.NAME": getVal("hawki_filter"),
  };

  // --- Time / S/N ---
  json.timesnr = {
    "DET.DIT": parseFloat(getVal("dit")) || 10,
    "DET.NDIT": parseInt(getVal("ndit")) || 6,
  };

  // --- Output ---
  const output = {};
  for (const grp of CFG.output_groups) {
    const gObj = {};
    for (const opt of grp.options) {
      const cb = document.querySelector(`[name="output_${grp.key}_${opt.key}"]`);
      gObj[opt.key] = cb ? cb.checked : false;
    }
    output[grp.key] = gObj;
  }
  json.output = output;

  return json;
}

/* ----------------------------------------------------------
   F.  Action Handlers
   ---------------------------------------------------------- */
function doPreview() {
  const json = buildJSON();
  document.getElementById("jsonPreview").textContent = JSON.stringify(json, null, 2);
  document.getElementById("preview-title").textContent = "JSON Preview";
  document.getElementById("preview-panel").style.display = "";
}

function doDownload() {
  const json = buildJSON();
  const blob = new Blob([JSON.stringify(json, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "hawki_etc_input.json";
  a.click();
  URL.revokeObjectURL(url);
}

async function doSendToETC() {
  const json = buildJSON();
  const btn = document.getElementById("btnSend");
  btn.disabled = true;
  btn.textContent = "Sending...";

  try {
    const resp = await fetch("/api/hawki-etc-proxy", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(json),
    });
    const data = await resp.json();
    document.getElementById("jsonPreview").textContent = JSON.stringify(data, null, 2);
    document.getElementById("preview-title").textContent =
      resp.ok ? "ETC Response (success)" : `ETC Response (${resp.status})`;
    document.getElementById("preview-panel").style.display = "";
  } catch (err) {
    document.getElementById("jsonPreview").textContent = "Error: " + err.message;
    document.getElementById("preview-title").textContent = "ETC Response (error)";
    document.getElementById("preview-panel").style.display = "";
  } finally {
    btn.disabled = false;
    btn.textContent = "Send to ETC";
  }
}

function doLoadJSON(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const json = JSON.parse(e.target.result);
      loadFormFromJSON(json);
    } catch (err) {
      alert("Invalid JSON file: " + err.message);
    }
  };
  reader.readAsText(file);
  // Reset file input so the same file can be loaded again
  event.target.value = "";
}

/* ----------------------------------------------------------
   G.  Load JSON into Form
   ---------------------------------------------------------- */
function loadFormFromJSON(json) {
  const t = json.target || {};
  const morph = t.morphology || {};
  const sed = t.sed || {};
  const bright = t.brightness || {};
  const sky = json.sky || {};
  const seeing = json.seeing || json.seeingiqao || {};
  const inst = json.instrument || {};
  const ts = json.timesnr || {};

  // Morphology
  setRadio("morphologytype", morph.morphologytype || "point");
  if (morph.extendedtype) setVal("extendedtype", morph.extendedtype);
  if (morph.index != null) setVal("sersic_index", morph.index);
  if (morph.radius != null) setVal("sersic_radius", morph.radius);

  // SED
  setRadio("sedtype", sed.sedtype || "spectrum");
  setVal("extinctionav", sed.extinctionav || 0);

  if (sed.spectrum) {
    setVal("spectrumtype", sed.spectrum.spectrumtype || "template");
    if (sed.spectrum.params) {
      if (sed.spectrum.params.catalog) {
        setVal("catalog", sed.spectrum.params.catalog);
        populateTemplateParams(sed.spectrum.params.catalog);
      }
      if (sed.spectrum.params.id) {
        const catalog = sed.spectrum.params.catalog || "MARCS";
        if (catalog === "SWIRE") {
          setVal("swire_template", sed.spectrum.params.id);
        } else {
          const parts = sed.spectrum.params.id.split(":");
          if (parts.length === 2) {
            setVal("teff", parts[0]);
            setVal("logg", parts[1]);
          }
        }
      }
      if (sed.spectrum.params.temperature != null) {
        setVal("bb_temperature", sed.spectrum.params.temperature);
      }
      if (sed.spectrum.params.exponent != null) {
        setVal("pl_exponent", sed.spectrum.params.exponent);
      }
    }
  }

  if (sed.emissionline && sed.emissionline.params) {
    setVal("em_lambda", sed.emissionline.params.lambda);
    setVal("em_fwhm", sed.emissionline.params.fwhm);
  }

  // Redshift
  if (sed.redshift) {
    document.getElementById("redshiftEnabled").checked = true;
    setVal("redshift", sed.redshift.redshift || 0);
    setVal("baryvelcor", sed.redshift.baryvelcor || 0);
  }

  // Brightness
  setVal("magband", bright.magband || "K");
  setVal("mag", bright.mag || 10);
  setVal("magsys", bright.magsys || "vega");

  // Sky
  setVal("airmass", sky.airmass || 1.2);
  setVal("fli", sky.fli || sky.moon_fli || 0.5);
  setVal("waterVapour", sky.waterVapour || sky.pwv || 2.5);
  setVal("moonDistance", sky.moonDistance || 30);

  // Seeing / AO
  const turbCat = seeing.turbulence_category ||
                  (seeing.params && seeing.params.turbulence_category) || 50;
  setVal("turbulence_category", turbCat);
  setVal("aperturepix", seeing.aperturepix || 9);
  const sep = seeing.separation ||
              (seeing.params && seeing.params.separation) || 0;
  setVal("separation", sep);
  const ttsMag = seeing["SEQ.TTS.MAG"] ||
                 (seeing.params && seeing.params.gsmag) || 12;
  setVal("tts_mag", ttsMag);

  // AO mode from ins_configuration
  const insConf = inst.ins_configuration || "img_noao";
  const parts = insConf.split("_");
  const aoMode = parts[1] || "noao";
  setVal("aoMode", aoMode);
  updateAOFields();

  // HAWK-I filter
  if (inst["INS.FILT.NAME"]) setVal("hawki_filter", inst["INS.FILT.NAME"]);

  // Timesnr
  setVal("dit", ts["DET.DIT"] || ts["DET1.DIT"] || 10);
  setVal("ndit", ts["DET.NDIT"] || ts["DET1.NDIT"] || 6);

  // Output checkboxes
  const output = json.output || {};
  for (const grp of CFG.output_groups) {
    const gObj = output[grp.key] || {};
    for (const opt of grp.options) {
      const cb = document.querySelector(`[name="output_${grp.key}_${opt.key}"]`);
      if (cb) cb.checked = gObj[opt.key] || false;
    }
  }

  // Update all visibility
  updateVisibility();
  updateAOFields();
}

function setRadio(name, value) {
  const el = document.querySelector(`[name="${name}"][value="${value}"]`);
  if (el) el.checked = true;
}
