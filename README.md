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
This Integration is configureable via the configuration.yaml. Here is a sample integration:

```yaml
sensor:
  - platform: ventoptimization
    indoor_temp_sensor: sensor.indoor_temp
    indoor_humidity_sensor: sensor.indoor_humidity
    outdoor_temp_sensor: sensor.outdoor_temp
    outdoor_humidity_sensor: sensor.outdoor_humidity
    maximum_wished_humidity: 65.0 # Everything beneath 70% is fine, but i use 65 as a safty buffer
    room_volume: 30.0 # in m³
    total_open_window_surface: 0.75 # in m² (all windows combined)
```

## The optimization
If you want to customize the opimization to adapt to your local situation gather trainingsdata and use either this [jupyter notebook](https://github.com/HrGaertner/vent-optimization/blob/main/model-training.ipynb) or this [webapp](https://hrgaertner.github.io/vent-optimization/) (under "Training" (i am sorry it is currently German only))

To learn about the model and the optimization itself have look at the whole repository dedicated to the development of the model and the webapp


**This integration used the [Mold Indicator Integration](https://www.home-assistant.io/integrations/mold_indicator/) as a minimal template to start from.**
