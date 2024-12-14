# On-Demand-SDN-Slicing

## Running the Application
This section contains all the necessary commands to run and test the application
1. Running the controller:
    - navigate to either `first_topology/` or `second_topology/`
    - execute `ryu-manager --wsapi-port 8081 controller.py`
2. Running the gui
    - navigate to the `gui/` directory
    - execute `python3 -m http.server 8080`
3. Running mininet
    - navigate to either `first_topology/` or `second_topology/`
    - execute `sudo python3 topology.py`