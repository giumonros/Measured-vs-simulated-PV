# Measured PV data

For now, the measured pv data are collected manually using high quality measurements from universities. The normalized hourly timeseries and high resolution data for some specific days are stored in an excel format in this [folder](https://github.com/giumonros/Measured-vs-simulated-PV/tree/main/src/simeasren/data/measured_PV)

More details can be found in [this publication](https://www.sciencedirect.com/science/article/pii/S1364032124007706).

## Contribute
To contribute and provide additional shareable data please contact please contact us at [giulia.montanari@polito.it](mailto:giulia.montanari@polito.it) or [njbca@dtu.dk](mailto:njbca@dtu.dk).

Otherwise it is also possible to do it manually following these steps:

1. Go in the ``src/simeasren/data/measured_PV`` folder and download one of the existing excel file (for example the one called "Utrecht"): click on the file > click on the three dots on the top right of your screen > click download

2. Rename the excel file to your location and replace the required informations with yours

3. Fork this repository (Top right of the screen, you need to create a GitHub account)

4. Go inside the ``src/simeasren/data/measured_PV`` folder ; Click on "Add files" and "Upload files" ; Upload your new excel file

5. Commit the changes, create a pull request, we will review it and after a while your data will be shared on the repository!


## PV plants characteristics
The characteristics of the sites currently available are described in the following table:

| Parameter | Turin, Italy | Utrecht, The Netherlands | Almería, Spain |
|------------|---------------|---------------------------|----------------|
| **Available years** | 2019–2020 | 2014–2017 | 2023ᵃ |
| **Latitude** | 45.065 | 51.970°ᵇ | 36.931 |
| **Longitude** | 7.659 | 5.329°ᵇ | −2.472 |
| **Tiltᶜ** | 26° | 30° | 22° |
| **Azimuthᶜ** | 206° | 170° | 178° |
| **System loss** | 10 %ᵈ | 5 % | 9.75 % |
| **Building integration** | Yes | Yes | No |
| **Installed peak capacity (kWp)** | 604.6 kWp | 1.90 kWp | 3992 kWp |
| **Inverter nominal capacity (kW), inlet/outlet** | 635ᵉ | 2.0 | 3.8 MVA/3.67 MVA |
| **Inverter model** | Sunny Tripower | Confidential | Freesun FS3670KH000015 |
| **Module manufacturer** | Benq | Confidential | Longi |
| **Module model** | SunForte PM096B00 | Confidential | LR4-72HBD-440M |
| **PV cell technology** | Mono c-Si | Mono c-Si | Mono c-Siᶠ |

---

ᵃ Year available only in Renewable ninja.  
ᵇ Midpoint of the area reported in [Visser et al.](https://pubs.aip.org/aip/jrse/article/14/4/043501/2848635), values are based on system with ID002.  
ᶜ In all cases there is no tracking system.  
ᵈ Estimated.  
ᵉ Multiple inverters.  
ᶠ Bifacial PV panels.

