# On-Demand-SDN-Slicing
TODO: there are many duplicated descriptions, try to unify them if possible

## Project structure
The structure of the project is as follows:
```
├── gui
│   ├── images
│   ├── index.html
│   ├── script.js
│   └── style.css
└── topologies
    ├── first_topology
    │   ├── controller.py
    │   ├── topology.py
    │   └── utils.py
    └── second_topology
        ├── controller.py
        ├── createQueue.sh
        ├── qos.py
        ├── qos_data
        │   ├── current_queues.txt
        │   ├── old_queues.txt
        │   └── stderr.txt
        ├── topology.py
        └── utils.p
```
- `gui/` contains the files to run the web interface
- `topologies/` contains the two topologies: `first_topology/` and `second_topology/`
    - each topology contains the following files
        - `controller.py`: contains the controller logic to handle the requests from the GUI and to interact with the mininet topology
        - `topology.py`: contains the mininet topology
        - `utils.py`: contains the utility functions used in the controller
    - `second_topology/` contains files related to QoS
        - `createQueue.sh`: script to create and delete queues
        - `qos.py`: calls `createQueue.sh`
        - `qos_data/`: contains the files to store the current and old queues, as well as the stderr output of the script

## Endpoints
The endpoints for the first controller are exposed on URL `http://localhost:8081/controller/first` and are:
- `always_on_mode`
- `listener_mode`
- `no_guest_mode`
- `speaker_mode`

The endpoints for the second controller are exposed on URL `http://localhost:8081/controller/second` and are:
- `first_mode`
- `second_mode`
- `third_mode`


## Running the Application in the GUI
This section contains all the necessary commands to run and test the application inside the GUI
1. Running mininet
    - navigate to either `first_topology/` or `second_topology/`
    - execute `sudo python3 topology.py`
2. Running the controller:
    - navigate to either `first_topology/` or `second_topology/`
    - execute `sudo ryu-manager --wsapi-port 8081 controller.py`
3. Running the gui
    - navigate to the `gui/` directory
    - execute `python3 -m http.server 8080`

If you want to terminate the session, execute the following commands in the terminal with mininet:
1. `quit` to terminate the session
2. `sudo mn -c` to clean up

## Running the Application in the terminal
This section contains all the necessary commands to run and test the application inside the terminal
1. Running mininet
    - navigate to either `first_topology/` or `second_topology/`
    - execute `sudo python3 topology.py`
2. Running the controller:
    - navigate to either `first_topology/` or `second_topology/`
    - execute `sudo ryu-manager --wsapi-port 8081 controller.py`
3. Making requests to the controller:
    - execute `curl http://localhost:8081/controller/{option}/{slice_name}`
    - `{option}`: the accepted options are either `first` or `second`
    - `{slice_name}`: the accepted slices are defined in the [endpoints](#endpoints) section

If you want to terminate the session, execute the following commands in the terminal with mininet:
1. `quit` to terminate the session
2. `sudo mn -c` to clean up

## Testing QoS (second topology)

In the second topology there are 3 queues for each link:
- TCP traffic on port 80
- UDP traffic on port 53
- TODO: add missing one

To test TCP run:
1. `h5 iperf -s -p 80 &` to run a server `h5` on port 80
2. `h6 iperf -c h5 -p 80` to run a client `h6` that will connect to `h5`

To test UDP run:
1. `h5 iperf -s -u -p 53 &`
2. `h6 iperf -c h5 -u -b 10m -p 53`
- Note: it is necessary to specify the bandwidth with `-b` for UDP traffic because it defaults to 1Mbps

To list all queues run: `sudo ovs-vsctl list queue`

Note: the queues are automatically deleted whenever the new queues are created

TODO: add screenshots of the GUI and the terminal commands
