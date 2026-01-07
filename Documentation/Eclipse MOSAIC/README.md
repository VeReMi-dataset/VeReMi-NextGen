# Eclipse MOSAIC 

Documentation for the Eclipse MOSAIC V2X simulation for generating CAM communication datasets.

### [Simulation Configuration](./Config)

Configuration of the simulation environment:
- Scenario parameters (duration, seed, projection)
- Federate configuration (OMNeT++, SUMO, Application)
- Network and communication settings (IEEE 802.11p)

### [CamApp](./Application)

ETSI CAM Sending Application:
- CAM trigger logic and sending intervals
- Sensor error models (GPS, speed, heading)
- Driver profiles (Aggressive, Normal, Passive)
- Pseudonym changes (Alias)
- JSON output format
