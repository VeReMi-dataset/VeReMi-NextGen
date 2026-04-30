# Getting Started

Documentation of how to recreate the VeReMi NextGen Dataset and to run it on your own machine.
> [!NOTE]
> For running the simulation directly on you own machine, Eclipse MOSAIC specific questions or regarding the development or extension of any kind, pls refer to the official [Eclipse MOSAIC documentation](https://eclipse.dev/mosaic/docs/)

## Run the simulation with via docker

For an easy recreation or extension of VeReMi NextGen, we provide the following two Docker image, which contains everything you need, to 
get the simulation started.

**1. ghcr.io/vs-uulm/veremi-nextgen:recreation**
    
The image with the `recreation` tag runs with the same versions as VeReMi NextGen was created with. This
enables you to run the simulation in the exactly same environment as we did. 

**2. ghcr.io/vs-uulm/veremi-nextgen:latest**

The image with the `latest` tag represents the latest versions of Eclipse MOSAIC, Eclipse SUMO and 
OmNET++ available at the time the image was build. You can build your Image, selecting the versions you need, with the Dockerfile provided
under `Generator/docker`. Detailed documentation on how to build your own Image can be found down below.

### Step-by-Step instruction

1. Create a new folder for the simulation, containing the subfolders `logs`, `json` and `scenarios`
2. Copy the scenarios from `Generator/docker/scenarios` to the created `scenarios` folder 
>   [!NOTE]
>   You can add whichever scenario you want to simulate. In this case you just have to copy the application folder into your scenario 
>   and adjust the config in the `EtsiApplication.json` regarding `simulation time` and `simulation area` 
3. If needed, make adjustments to the configs defined in the scenario itself
4. To start the simulation, open a terminal in the simulation folder and run the following command:

    ```bash
    docker run --rm -it \
    --user $(id -u):$(id -g) \
    -v $(pwd)/scenarios:/opt/mosaic/scenarios \
    -v $(pwd)/logs:/opt/mosaic/logs \
    -v $(pwd)/json:/opt/mosaic/output \
    ghcr.io/vs-uulm/veremi-nextgen:<tag> \
    <scenario-name>
    ```
    | Parameter                                   | Description                                                                            |
    |---------------------------------------------|----------------------------------------------------------------------------------------|
    | `--rm`                                      | Automatically removes the container after the simulation ends.                         |
    | `-it`                                       | Runs the container in interactive mode (output visible, stop with `Ctrl+C`).           |
    | `--user $(id -u):$(id -g)`                  | Runs the container with your local user and group ID so generated files belong to you. |
    | `-v $(pwd)/scenarios:/opt/mosaic/scenarios` | Mounts local scenario files into the simulation environment.                           |
    | `-v $(pwd)/logs:/opt/mosaic/logs`           | Mounts the directory used to store simulation logs.                                    |
    | `-v $(pwd)/json:/opt/mosaic/output`         | Maps the output directory where Java writes JSON files to your local `./json` folder.  |

## Build your own image

In case the provided image is outdated, or you need specific versions in your simulation of one of the simulators, you can simply build you own image. To do so follow these steps:

### Case 1: Updating to the newest versions

In this case it is pretty straight forward. The only thing you have to do is to look up which the newest Eclipse MOSAIC version is and adjust the version
in the `dockerfile`. The other dependency, namely Eclipse SUMO and OmNET++/Inet will be automatically be downloaded in the newest version. In case the download of
Eclipse MOSAIC fails, the URL schema has changed and has to be adjusted. To build the image simply execute the following command:

```bash
docker build -t <image-name> .
```

### Case 2: Updating to specific versions

> [!NOTE]
> You have to make sure the chosen versions are compatible and supported by Eclipse MOSAIC.

In this case you have to observe more things. In the beginning you can follow the instruction of Case 1. The following adjustments have to be implemented to change the version of a specific simulator: 

**Eclipse SUMO:**
Change the sumo installation to the following code and replace <version> with the version needed

```dockerfile
RUN add-apt-repository -y ppa:sumo/stable && \
    apt-get update && \
    apt-get install -y \
        sumo=<version>* \
        sumo-tools=<version>* \
        sumo-doc=<version>* && \
    rm -rf /var/lib/apt/lists/*
```

**Eclipse MOSAIC:** Change the OmNET++ installation to the following code and adjust the paths and filenames.

```dockerfile
COPY <path to the omnet++ .tgz folder> /opt/sources/
COPY <path to the inet .tgz folder> /opt/sources/
COPY <path to the omnetpp-federate .zip folder> /opt/sources/


RUN cd bin/fed/omnetpp && \
    chmod +x omnet_installer.sh && \
    yes y | ./omnet_installer.sh \
    --installation-type USER \
    --omnetpp /opt/sources/<filename> \
    --inet /opt/sources/<filename> \
    --federate /opt/sources/<filename>
```

The files can be downloaded under the following links:
- [OmNET++](https://omnetpp.org/download/)
- [Inet](https://inet.omnetpp.org/Download.html)
- [Omnetpp-federate](https://www.dcaiti.tu-berlin.de/research/simulation/download/)


## Run the attack integration

The post-processing script is located in `Generator/attackGenerator/attackGenerator.py`.
This script injects misbehavior/attack patterns into V2X message datasets stored as JSON files. It reads all JSON files from an input folder, selects a subset of vehicles as attackers, modifies their messages according to the selected misbehavior, and writes the manipulated dataset to a new output folder.


### Usage
To create attack datasets, run the attack generator with the desired input folder, misbehavior type, and SUMO scenario configuration:
```
python attackGenerator.py <input_folder> <misbehavior> <sumoConf>
```

| Argument | Description |
|---|---|
| `input_folder` | Path to the folder containing the input JSON files |
| `misbehavior` | Misbehavior/attack type to inject |
| `sumoConf` | Path to the SUMO scenario configuration file (`.sumocfg`) |

The script reads all JSON files from the given input folder, selects a subset of vehicles as attackers, applies the specified misbehavior to their messages, and stores the resulting files in a new output folder. The output folder is created next to the input folder and follows the naming scheme `<input_folder>_<misbehavior>`.

For ```sumoConf```, use the `InTAS_full_poly.sumocfg` from the directory  
`Generator/simulation/mosaic/scenarios/<scenario>/sumo`.

The attack ratio can be adjusted in the `attackGenerator.py` file using the ```ATTACK_RATIO```variable.

Example: 
```
python inject_misbehavior.py ./Dataset/urban_2 constantPositionOffset .Generator/simulation/mosaic/scenarios/InTAS_urban_2_4/sumo/InTAS_full_poly.sumocfg
```


