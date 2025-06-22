# 📕 Book *Introduction to SAR Satellite Data Analysis* GitHub Repository

[Japanese](https://github.com/syu-tan/sar-python-book/blob/main/README.md) | [English](doc/READM_en.md)

TODO: Add book  
![img]()

This is the official repository that hosts the Python source code for the book *Introduction to SAR Satellite Data Analysis*.  
Under the terms of the [license](./LICENSE), the code may be used **free of charge for commercial purposes**.


# 🚀 Book Overview

- The book is published by **Kōdansha Scientific** (link coming soon).
- The author’s introductory article on the book is available [here](TODO).



# 🔍 Related Posts

A list of commemorative articles published in conjunction with the book release.


# 💻 Code–Chapter Correspondence

| Chapter                                                      | Section                           | Description                             | Notebook File                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------------------------ | --------------------------------- | --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Chapter 1 Fundamentals of SAR and Observation Principles** |                                   |                                         |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|                                                              | *Synthetic Aperture*              | Basics of synthetic aperture            | <ul><li>[1_1_3_impulse_response.ipynb](./src/1_1_3_impulse_response.ipynb)</li><li>[1_1_6_migration.ipynb](./src/1_1_6_migration.ipynb)</li><li>[1_1_7_999_synthetic_aperture.ipynb](./src/1_1_7_999_synthetic_aperture.ipynb)</li><li>[1_1_7_focus.ipynb](./src/1_1_7_focus.ipynb)</li></ul>                                                                                                                                                                                                                                                              |
|                                                              | *Intensity Images*                | Multilooking, etc.                      | <ul><li>[1_3_3_multilooking.ipynb](./src/1_3_3_multilooking.ipynb)</li></ul>                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
|                                                              | *Radar-Specific Phenomena*        | Ambiguity, RFI, and more                | <ul><li>[1_3_7_ambiguity_azimuth.ipynb](./src/1_3_7_ambiguity_azimuth.ipynb)</li><li>[1_3_7_ambiguity_range.ipynb](./src/1_3_7_ambiguity_range.ipynb)</li><li>[1_3_9_radio_frequency_interference.ipynb](./src/1_3_9_radio_frequency_interference.ipynb)</li></ul>                                                                                                                                                                                                                                                                                         |
|                                                              | *SAR Performance*                 | Polarimetry, antenna beam, orbit        | <ul><li>[1_3_1_polarimetry.ipynb](./src/1_3_1_polarimetry.ipynb)</li><li>[1_3_2_antena_pattarn.ipynb](./src/1_3_2_antena_pattarn.ipynb)</li><li>[1_3_2_beam.ipynb](./src/1_3_2_beam.ipynb)</li><li>[1_3_2_orbit.ipynb](./src/1_3_2_orbit.ipynb)</li></ul>                                                                                                                                                                                                                                                                                                  |
|                                                              | *InSAR*                           | Interferometric processing              | <ul><li>[1_5_1-2-3-5-6-7_insar.ipynb](./src/1_5_1-2-3-5-6-7_insar.ipynb)</li><li>[1_5_3_coregistolation.ipynb](./src/1_5_3_coregistolation.ipynb)</li><li>[1_5_4_wrap_phase.ipynb](./src/1_5_4_wrap_phase.ipynb)</li><li>[1_5_6_insar_2pass.ipynb](./src/1_5_6_insar_2pass.ipynb)</li><li>[1_5_9_baseline.ipynb](./src/1_5_9_baseline.ipynb)</li><li>[1_5_999_insar_topo.ipynb](./src/1_5_999_insar_topo.ipynb)</li></ul>                                                                                                                                  |
|                                                              | *Advanced SAR Processing*         | High-level SAR techniques               | <ul><li>[1_6_1_chirp_scaling.ipynb](./src/1_6_1_chirp_scaling.ipynb)</li><li>[1_6_1_stolt_interpolation.ipynb](./src/1_6_1_stolt_interpolation.ipynb)</li><li>[1_6_2_speckle_noise.ipynb](./src/1_6_2_speckle_noise.ipynb)</li><li>[1_6_2_subaperture_capella_eiffel.ipynb](./src/1_6_2_subaperture_capella_eiffel.ipynb)</li><li>[1_6_2_subaperture_umbra_haneda.ipynb](./src/1_6_2_subaperture_umbra_haneda.ipynb)</li><li>[1_6_3_moving_target.ipynb](./src/1_6_3_moving_target.ipynb)</li><li>[1_6_999_cphd.ipynb](./src/1_6_999_cphd.ipynb)</li></ul> |
| **Chapter 2 Preparing for SAR Data Analysis**                |                                   |                                         |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|                                                              | *Acquisition & Visualization*     | Basic visualization and data download   | <ul><li>[2_2_sar_georeference.ipynb](./src/2_2_sar_georeference.ipynb)</li></ul>                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
|                                                              | *Geospatial Processing*           | Orthorectification, etc.                | <ul><li>[2_2_sar_georeference.ipynb](./src/2_2_sar_georeference.ipynb)</li></ul>                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| **Chapter 3 Analyzing SAR Data**                             |                                   |                                         |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|                                                              | *Forestry & Agriculture*          | Segmentation & time series              | <ul><li>[3_2_forest.ipynb](./src/3_2_forest.ipynb)</li><li>[3_3_2-3_crop_paz-s2_time-seriess.ipynb](./src/3_3_2-3_crop_paz-s2_time-seriess.ipynb)</li><li>[3_3_2_999_crop_paz.ipynb](./src/3_3_2_999_crop_paz.ipynb)</li><li>[3_3_2_999_crop_paz_time-seriese.ipynb](./src/3_3_2_999_crop_paz_time-seriese.ipynb)</li><li>[3_3_3_999_crop_sentinel-2.ipynb](./src/3_3_3_999_crop_sentinel-2.ipynb)</li><li>[3_3_4_model.ipynb](./src/3_3_4_model.ipynb)</li></ul>                                                                                          |
|                                                              | *Flooding*                        | Statistical models                      | <ul><li>[3_1_2_simple_thresholding.ipynb](./src/3_1_2_simple_thresholding.ipynb)</li><li>[3_1_3_local_thresholding.ipynb](./src/3_1_3_local_thresholding.ipynb)</li><li>[3_1_4_s1_flood_extraction.ipynb](./src/3_1_4_s1_flood_extraction.ipynb)</li></ul>                                                                                                                                                                                                                                                                                                 |
|                                                              | *Earthquakes*                     | InSAR, pixel offset, 2.5 D              | <ul><li>[3_4_4_insar_higashinihon.ipynb](./src/3_4_4_insar_higashinihon.ipynb)</li><li>[3_4_5_insar_alos2.ipynb](./src/3_4_5_insar_alos2.ipynb)</li><li>[3_4_5_pixeloffset.ipynb](./src/3_4_5_pixeloffset.ipynb)</li><li>[3_4_6_2.5d.ipynb](./src/3_4_6_2.5d.ipynb)</li></ul>                                                                                                                                                                                                                                                                              |
|                                                              | *Maritime*                        | Object detection & signal processing    | <ul><li>[3_5_1_ship_signal_distribution.ipynb](./src/3_5_1_ship_signal_distribution.ipynb)</li><li>[3_5_2_cfar.ipynb](./src/3_5_2_cfar.ipynb)</li><li>[3_5_2_ssdd.ipynb](./src/3_5_2_ssdd.ipynb)</li><li>[3_5_3_mmrotate.ipynb](./src/3_5_3_mmrotate.ipynb)</li></ul>                                                                                                                                                                                                                                                                                      |
| **Chapter 4 The Present and Future of SAR**                  |                                   |                                         |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|                                                              | *SAR Providers*                   | —                                       | *(no code)*                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|                                                              | *Future Prospects*                | —                                       | *(no code)*                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **Appendix**                                                 |                                   |                                         |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|                                                              | *Fourier Transform & Correlation* | Mathematical background & visualization | <ul><li>[Appendix_Fourier_Transform_%20Correlation_%20Processing.ipynb](./src/Appendix_Fourier_Transform_%20Correlation_%20Processing.ipynb)</li></ul>                                                                                                                                                                                                                                                                                                                                                                                                     |



# ⚙️ Environment Setup

Instructions for setting up the Python environment for this book can be found [here](doc/develop.md).

> All sample code and explanations in this book were verified to run as of the time of writing.  
> However, behavior may differ depending on your environment and software versions.  
> **Always validate on your own responsibility.** Each piece of code comes with its own license terms.  
> When redistributing or using commercially, be sure to comply with the license conditions and the book’s disclaimer, and to provide proper attribution or obtain the necessary permissions.  
> Sections that combine open-source libraries are also subject to the licenses of those libraries.  
> Before use, review each license in full; if unclear, consult a professional or contact the author (Yasui).



# 📃 License

### 🛰 Data License

When using satellite data, follow the license terms of each provider.  
Some valuable datasets used in this book are licensed specifically for use **within the book only**.  
Public datasets that readers obtain directly from the providers are not subject to these restrictions; links are provided where applicable.

### 🤖 Code License

Refer to the [license](./LICENSE) for details on using the code.  
If you have customization or usage requests, feel free to contact us—flexible arrangements are possible.

Although not bundled with this repository, we gratefully build upon the following libraries:

- **mmdetection**  
  <https://github.com/open-mmlab/mmdetection>
- **mmrotate**  
  <https://github.com/open-mmlab/mmrotate>
- **SNAPHU**  
  `Copyright 2002-2024 Board of Trustees, Leland Stanford Jr. University`  
  <https://web.stanford.edu/group/radar/softwareandlinks/sw/snaphu/README>
- **SNAPHU-PY**  
  `Copyright © 2023 California Institute of Technology ("Caltech"). U.S. Government`  
  <https://github.com/isce-framework/snaphu-py/blob/main/LICENSE-BSD-3-Clause>

In addition, the following Java and C codebases were referenced:

- **ESA SNAP (polarimetric analysis)**  
  <https://github.com/senbox-org>
- **GMTSAR (slant-range computation)**  
  <https://github.com/gmtsar/gmtsar>



# 🙏 Acknowledgments

We express deep gratitude to **ESA, ICEYE, JAXA, and Synspective** for graciously permitting the use of valuable data.  
We also thank **Capella Space, CSA, Hisdesat, and the Geospatial Information Authority of Japan** for providing open data.  
Institutions are listed in alphabetical order.


# 🤝 Contributors

<a href="https://github.com/syu-tan/sar-python-book">
  <img src="https://github.com/syu-tan.png" width="100px;" alt="syu-tan" style="border-radius:50%;"/>
  <img src="https://github.com/koichisato-dev.png" width="100px;" alt="koichisato-dev" style="border-radius:50%;"/>
</a>

We welcome additional contributors—feel free to reach out!


# 📩 Contact

- For code issues, please open a GitHub Issue.  
- For questions about the book, use the Q&A channel in the [Japan Satellite Data Community](https://zenn.dev/syu_tan/articles/593d27ec7f2de3).  
- For business inquiries, contact us via [X](https://x.com/emmyeil) or through the [author’s profile](https://syu-tan.github.io/).  
  TODO: Add contact for Mr. Satō

---

## *We hope this repository advances the development and practical use of SAR.*

