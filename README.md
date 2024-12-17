# On-Demand-SDN-Slicing

## Commands for testing
list all queues: `sudo ovs-vsctl list queue`
remove all queues: `sudo ovs-vsctl -- --all destroy QoS -- --all destroy Queue`

## Endpoints
The endpoints for the first controller are exposed on URL `http://localhost:8081/controller/first` and are:
- `always_on`
- `listener`
- `no_guest`
- `speaker`

The endpoints for the second controller are exposed on URL `http://localhost:8081/controller/second` and are:
- TODO


## Running the Application in the GUI
This section contains all the necessary commands to run and test the application inside the GUI
1. Running the controller:
    - navigate to either `first_topology/` or `second_topology/`
    - execute `ryu-manager --wsapi-port 8081 controller.py`
2. Running the gui
    - navigate to the `gui/` directory
    - execute `python3 -m http.server 8080`
3. Running mininet
    - navigate to either `first_topology/` or `second_topology/`
    - execute `sudo python3 topology.py`

## Running the Application in the terminal
This section contains all the necessary commands to run and test the application inside the terminal
1. Running the controller:
    - navigate to either `first_topology/` or `second_topology/`
    - execute `ryu-manager --wsapi-port 8081 controller.py`
2. Running mininet
    - navigate to either `first_topology/` or `second_topology/`
    - execute `sudo python3 topology.py`
3. Making requests to the controller:
    - execute `curl http://localhost:8081/controller/{option}/{slice_name}`
    - `{option}`: the accepted options are either `first` or `second`
    - `{slice_name}`: the accepted slices are defined in the [endpoints](#endpoints) section