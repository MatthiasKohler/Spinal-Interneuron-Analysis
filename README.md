# Spinal interneuron data analysis

Software to analyze synaptic responses of *in vivo* patch clamp recordings from spinal interneurons.

This paper describes how the data was obtained and the results of the analysis.

[Kohler, M.,  Bengtsson, F., Stratmann, P., Spanne, A., Röhrbein, F., Knoll, A., Albu-Schäffer, A., Jörntell, H.
Diversified physiological sensory input connectivity questions the existence of distinct classes of spinal interneurons in the adult cat in vivo Bioarxiv 2021.](https://bioarxiv.org)


## Contact

Matthias Kohler 
lastname (at) in (dot) tum (dot) de.

## Data

Post synaptic potential (PSP) latency times with corresponding PSP amplitudes for each neuron
are located in  `data_raw`. Synaptology data is located in `data_synaptology`.

## Compiling and running

The software is written in C++, Python, R and bash. The software has been tested on
Ubuntu 18.04 and the C++ part with clang++-7. 

### Parallelization:

The analysis core is multithreaded to speed up the analysis. The number of threads is hard coded
into `analysis_core/main.cpp` in the variable `n_threads`. The value is set to twelve.

### Compiling

We put the cmake build directory into the source directory. This is generally not recommended.
Change if necessary and adapt the `analysis_loops.sh` and `analysis_association_rules.sh` scripts to find
the analysis core executable `analysis_core`. If necessary adapt the number of threads `make` uses to compile.

    cd analysis_core
    cmake -DCMAKE_CXX_COMPILER=/usr/bin/clang++-7 .
    make -j8

### Usage

The software is composed of several scripts which perform one part of the analysis.
All scripts below are run in the directory containing this README without any arguments.
Output directories and names of generated files are hardcoded.

Script | Output | Purpose
------ | ------------- | -------
`convert_data.sh` |  | Converts data from human writable format to tidy format.
`reduce_data.py`  |  | Synaptology data shows over how many synapses a signal was transmitted to a neurons. This script reduces data from information on multisynaptic responses to response no response data from a modality.
`analysis_clusterability.R` | `results_clusterability/` | Runs the Sigclust and Gap-Statistics algorithm to determine clusterability.
`analysis_loops.sh` | `results_loops/` | Counts excitatory loops on the dataset and compares is to the swap randomized dataset.
`analysis_association_rules.sh` | `results_association_rules/` | Computes association rules and compares them to the swap randomized dataset.
`plot_clusterability.py` | `results_clusterability/` | Generates plots for the GapStatistics and the SigClust algorithm.
`plot_loops.py` | `plots_loops/` | Generates plots in  from results written to `results_loops`.
`plot_association_rules.py` | `plots_association_rules/` | Generates plots from results written to `results_association_rules`.
`plot_latencies.py` | `plots_latencies/` | Generates plots of the latency distribution of the PSPs.
`plot_weights.py` | `plots_weights/` | Generates plots of weight distributions.
