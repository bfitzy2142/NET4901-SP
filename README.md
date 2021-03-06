# NET4901-Senior Project: SDLENS

## Application Overview
SDLens is a software defined network (SDN) monitoring web application designed to operate with the OpenDaylight controller. It provides real-time telemetry from OpenFlow switches, provides an interactive topology of the network, and many more intuitive features.

This entire application was built using the web-framework Flask.

## Architecture of SDLENS
![SDLens Architecture](https://user-images.githubusercontent.com/44167644/55921299-314a8700-5bca-11e9-9a3e-d80d6294686c.png)
- Primarily developed in Python​3
- JavaScript on the front-end​
- Three main components of our application​
    - Web App​
    - Monitoring Agents​
    - MySQL Database​
- Web App and Agents interact with both the Database and the controller's Northbound interface​
- Designed with modularity in mind​

## Installation Steps
The following instructions will discribe how to install and run our web application, **SDLENS**.

### Prerequisites
This application makes uses the following services:
- MySql Server
- Nmap
- OpenDaylight Controller
  - The following packages for the controller:
    - odl-restconf
    - odl-l2switch-switch
    - odl-dlux-core
    - odl-dluxapps-nodes
    - odl-dluxapps-topology
    - odl-dluxapps-yangui
    - odl-dluxapps-yangvisualizer
    - odl-dluxapps-yangman
- Python 3
  - python-pip

#### Optional
- Mininet
    - The Mininet VM was used to emulate SDN networks in the development of SDLENS.
    - Any SDN can be used provided it uses an OpenDaylight controller.

### Installing
Preface: All commands will assuem a linux or other Unix based operating system (MacOS).

#### MySql Server
Installing the MySql Server is easy, as it can be accomplished with Aptitude.

```
$ apt install mysql-server
$ apt install libmysqlclient-dev
```

#### OpenDaylight
The OpenDaylight controller can be downloaded from the [OpenDaylight](https://www.opendaylight.org/) website. This application was developed using OpenDaylight version: `0.8.3`

Once OpenDaylight has been extracted, you can start the program with:

```bash
$ karaf-version/bin/./karaf clean
```

When starting the program, run the `clean` option. This ensures that any previously installed packages are removed and allows for more continuity at the cost of an extra step. 

Use the following command to install required ODL features:

```
> feature:install odl-restconf odl-l2switch-switch odl-dlux-core odl-dluxapps-nodes odl-dluxapps-topology odl-dluxapps-yangui odl-dluxapps-yangvisualizer odl-dluxapps-yangman
```

#### Mininet (Optional)
If you are using Mininet to emulate an SDN network, you can download the Mininet virtual machine from Mininet's website: [Download](https://github.com/mininet/mininet/wiki/Mininet-VM-Images)

Once downloaded and opperational, you can create a new topology with the following command. **Note: Add your controller IP**.

```bash
$ sudo mn --controller=remote,ip=`controller IP` --switch ovsk,protocols=OpenFLow13 --topo Topology of your choice
```

A mesh topology is included with this repository called 'basicMesh' under the mininet directory. Copy this file to your Mininet VM and place it within ~/scripts. Create ~/scripts if that directory does not already exist. To create the mesh topology, add your controller's IP address and run the following:

```sh
sudo mn --custom scripts/basicMesh.py --topo dcharoot --controller=remote,ip='controller IP' --switch ovsk,protocols=OpenFlow13
```

Once mininet is running issue the following:

```sh
pingall
```

This will generate traffic throughout the network and allow the contoller to populate the openflow switches with flowrules.

## Authors
- Bradley Fitzgerald - Carleton University, Canada (far left)
- Samuel Cook - Carleton University, Canada (inner left)
- Samuel Robillard - Carleton University, Canada (inner right)
- Josh Nelson - Carleton University, Canada (far right)

![SDLens_Group](https://user-images.githubusercontent.com/44167644/55919797-47097d80-5bc5-11e9-9967-34752b6e1f3d.jpg)
