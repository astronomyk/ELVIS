![ELVIS - The ELT Virtual Instrument Simulator](logos/ELVIS_logo.png)

A common data simulation framework for the ELT instruments

Requirements
------------
- The python package should be able to generate a simulated version of the expected data products for each of the ELT's instruments and their observing modes
- The package should take as input the JSON text from the new ESO exposure time calculator interface
- The package should create FITS files that mirror what is expected after the instrument data reduction pipelines are finished with the observation data
- The software should in future be able to ingest a single ESO Observing Block (OB) and automatically generate the expected raw data files from the instrument
- The instrument model should use, as much as possible, the instrumental characteristics from ESO's own database
- The software should also run as a micro-service command line application such that it can be interfaced with ESO's existing ETC 2.0 infrastructure
- The software should be able to run a million pixel elements in under 10sec, goal 1 sec

User Stories
------------

Michele is the head of ESO instrumentation and has some dedicated time available for testing instruments on the ELT.
He wants to check if MICADO can resolve structure in a z=4 clumpy galaxy using the MCAO mode and the K-band filter.
His motivation is to publish a paper showing how much better the ELT is than JWST.

Ric is the PI of MICADO and is in the middle of commissioning the instrument on the ELT.
He is about to schedule some observations on a globular cluster in order to determine the sensitivity of the real instrument.
He wants to know in advance what to expect in terms of star crowding in the centre of the field of view when using SCAO. 

Gael is the leader of the METIS science team, and he really likes protoplanetary disks for some reason.
His goal is to determine what the smallest gaps are between rings in a HL Tau-like system that can be resolved using the METIS IFU.

Camelle is a PhD Student in Besancon and is looking into the feasibility of using MICADO to detect and track Trans-Neptunian objects (TNOs).
She wants to use the SCAO mode of MICADO and needs to know what the detection limit is for a 10 minute observations, because the TNOs will move more than one pixel in longer observations.
To start with she is just interested in using a standard star as a proxy for her TNO, but will eventually want to use a real TNO spectrum.
Because she is using the SCAO mode, she wants to know how the detection limit changes with distance from the natural guide star.

Reinhard is not enjoying his retirement and wants to get back into science.
He likes watching star whiz around the black hole at the centre of the Milky Way.
In order to get their three-space velocities, he needs to determine their radial velocities with the MICADO Long-Slit spectrographic mode.
He has good connections and so will be able to get enough observing time to point the ELT at each star for 1 hour.
Also he is impatient, and so will accept using MICADO SCAO, rather than waiting 3 years until MCAO is online.

Thomas works at ESO and doesn't care about astronomy. 
But he does want to offer a simulation mode on the ESO 2nd gen ETC.
He wants to be able to pipe the current configuration of the ESO ETC into the software and recieve a FITS file in return.
He doesn't care what is in the FITS file, as Jakob will find a way to display the contents in a meaningful way to the end user.

Olivier was granted 10 hours of observing time on METIS for his asteroid studies.
He has painstakingly put together a set of Observing Blocks to sent to the telescope operators.
Now he has 6 months to wait before he gets any real data. 
In the meantime he wants to simulate the expected raw FITS file when the data finally comes in, so that he can fine-tune his analysis scripts in advance.


Code Structure
--------------

- Input
  - ETC input JSON contains the following fields
    - target : scopesim_targets
    - sky : skycalc effect
    - instrument : scopesim optical train
    - timesnr : OpticalTrain.readout
    - output : which plots to show
    - instrumentName : which inst pkg to use
    - seeingiqao : input params for tiptop?

- Modules
    - a targets translator
    - a opticaltrain generator
    - a readouts runner

- Output
  - FITS file

