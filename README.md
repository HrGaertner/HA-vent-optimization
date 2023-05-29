# HA-vent-optimization
[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/HrGaertner/HA-vent-optimization/actions.yaml?label=HA%20compatible&style=for-the-badge)

A integration for Home-Assistant that predicts how long you have to open your windows (specially optimized for bathrooms, but should work for any other room too) in order to prevent mold and other nasty things. You can use it for example to get notification how long you should vent if it is necessary.

## Installation
Install [HACS](https://hacs.xyz)

Use this link:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=HrGaertner&repository=HA-vent-optimization&category=integration)

And install the configuration

## Configuration
You can configure and setup this integration via a Config Flow. Thanks a lot to [Alexwijn](https://github.com/Alexwijn)
![image](https://github.com/HrGaertner/HA-vent-optimization/assets/53614377/d1e04abb-b06d-4407-89e2-3754c54de6bf)
```

## The optimization
If you want to customize the opimization to adapt to your local situation gather trainingsdata and use either this [jupyter notebook](https://github.com/HrGaertner/vent-optimization/blob/main/code/model%7Ctraining/model-training.ipynb) or this [webapp](https://hrgaertner.github.io/vent-optimization/) (under "Training" (i am sorry it is currently German only))

To learn about the model and the optimization itself have look at the whole repository dedicated to the development of the model and the webapp


**This integration used the [Mold Indicator Integration](https://www.home-assistant.io/integrations/mold_indicator/) as a minimal template to start from.**
