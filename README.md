# Global comparison of urban bike-sharing accessibility across 40 cities

This GitHub repository contains the code and resources used in the research paper "Global comparison of urban bike-sharing accessibility across 40 cities," published in [Scientific Reports](https://www.nature.com/articles/s41598-024-70706-x). 

## Overview

This study introduces a comprehensive global comparison of bike-sharing systems by aggregating data from 40 cities worldwide. By integrating this data with population metrics and urban characteristics, we classified bike-sharing networks and assessed their effective coverage in relation to the population served and existing public transit systems. We introduce the "Bike-Share Service Accessibility Index" (BSAI), a new metric to evaluate and compare the performance of bike-sharing networks. Our findings offer valuable insights for urban planners and policymakers, providing data-driven strategies to enhance sustainable urban mobility through better-integrated and more spatially equitable bike-sharing systems.

The code in this repository, primarily written in Python, facilitates the replication of our analyses. It includes processes for downloading and processing bike station data using the pybikes library and obtaining city network and boundary data from OpenStreetMap (OSM). The spatial distribution of bike-sharing stations is analyzed using the Nearest Neighbor Index (NNI), and the integration of these systems with public transit is evaluated through spatial analysis of median distances between bike stations and the nearest transit stops.

Data sources for this study include bike-sharing data from official websites and the pybikes library, city network and boundary data from OSM, and population data from the Global Human Settlement Layer (GHSL). The GHSL provides a detailed estimation of the population in each 100x100 m cell, which is crucial for assessing bike-sharing accessibility in relation to urban demographics.

Through this research, we uncover varied spatial distribution patterns of bike-sharing stations across cities, reflecting different urban planning strategies and geographic characteristics. Our evaluation of the integration between bike-sharing systems and public transit reveals significant variations in efficiency and accessibility, highlighting areas for potential improvement and investment. The introduction of the BSAI offers a holistic evaluation of urban bike-share infrastructure, providing a comprehensive metric for city planners to gauge and enhance the performance of their bike networks.

All code and data used in this study are made available in this repository to ensure transparency and reproducibility.
