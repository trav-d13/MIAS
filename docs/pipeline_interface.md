## Pipeline (Interface)
This file provides the framework for the transformation pipeline from raw track data
located in `data/tracks.csv` through to features used for similarity calculations.
Each pipeline must inherent from the pipeline interface. 

**Note:** Different pipelines may result in varied features, hence the need for a pipeline interface, such
that there exists a common method for the front-end to make use of.

## Pipeline Interface Documentation
::: src.pipeline_interface