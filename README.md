![ELVIS - The ELT Virtual Instrument Simulator](logos/ELVIS_logo.png)

A common data simulation framework for the ELT instruments

Requirements
------------
- The python package should be able to generate a simulated version of the expected data products for each of the ELT's instruments and their observing modes
- The package should take as input the JSON text from the new ESO exposure time calculator interface
- The package should create FITS files that mirror what is expected after the instrument data reduction pipelines are finished with the observation data
- The sotware should in future be able to ingest a single ESO Observing Block (OB) and automatically generate the expected raw data files from the instrument
- The instrument model should use, as much as possible, the instrumental characteristics from ESO's own database
- The software should run as a micro-service such that it can be interfaced with ESO's existing ETC 2.0 infrastructure
- 