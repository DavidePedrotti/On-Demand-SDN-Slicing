def get_IP_address(host_name: str) -> str:
    """
    Get the IP address for a given host name.

    Args:
        host_name (str): The name of the host (e.g., "h1", "h2", etc.).

    Returns:
        str: The IP address corresponding to the host name.
    """
    ip_mapping = {
        f"h{i}": f"10.0.0.{i}" for i in range(1, 11)
    }
    return ip_mapping.get(host_name)

def get_MAC_address(host_name: str) -> str:
    """
    Get the MAC address for a given host name.

    Args:
        host_name (str): The name of the host (e.g., "h1", "h2", etc.).

    Returns:
        str: The MAC address corresponding to the host name.
    """
    mac_mapping = {
        f"h{i}": f"00:00:00:00:00:{i:02x}" for i in range(1, 11)
    }
    return mac_mapping.get(host_name)

def get_dpid(host_name: str) -> int:
    """
    Get the DPID (Datapath ID) for a given switch name.

    Args:
        host_name (str): The name of the switch (e.g., "s1", "s2", etc.).

    Returns:
        int: The DPID corresponding to the switch name.
    """
    dpid_mapping = {
        f"s{i}": f"{i:016x}" for i in range(1, 5)
    }
    return int(dpid_mapping.get(host_name), 16)

def get_port(src: str, dst: str) -> int:
    """
    Get the port number for a given source and destination.

    Args:
        src (str): The source switch or host.
        dst (str): The destination switch or host.

    Returns:
        int: The port number for the given source and destination.
    """
    link_mapping = {
        "s1": {
            "h1": 1,
            "h2": 2,
            "s2": 3,
            "s4": 4,
        },
        "s2": {
            "h3": 1,
            "h4": 2,
            "h5": 3,
            "s1": 4,
            "s3": 5,
            "s4": 6,
        },
        "s3": {
            "h6": 1,
            "h7": 2,
            "s2": 3,
        },
        "s4": {
            "h8": 1,
            "h9": 2,
            "h10": 3,
            "s1": 4,
            "s2": 5,
        },
    }
    return link_mapping.get(src).get(dst)

def generate_link_entries(src_ip, dst_ips, switch, ports):
    """
    Generate link entries for a given source IP, destination IPs, switch, and ports.

    Args:
        src_ip (str): The source IP address.
        dst_ips (list): A list of destination IP addresses.
        switch (str): The switch name.
        ports (list): A list of ports corresponding to the destination IPs.

    Returns:
        dict: A dictionary representing the link entries.
    """
    return {src_ip: [{dst_ip: get_port(switch, port)} for dst_ip, port in zip(dst_ips, ports)]}

def slice_to_port():
    """
    Generate port mappings for different slicing scenarios.

    Args: None

    Returns:
        dict: A dictionary representing the port mappings for different scenarios.
    """
    first_scenario =  {
        get_dpid("s1"): {
            **generate_link_entries(get_MAC_address("h1"), [get_MAC_address("h6"), get_MAC_address("h7")], "s1", ["s2", "s2"]),
            **generate_link_entries(get_MAC_address("h6"), [get_MAC_address("h1")], "s1", ["h1"]),
            **generate_link_entries(get_MAC_address("h7"), [get_MAC_address("h1")], "s1", ["h1"]),
        },
        get_dpid("s2"): {
            **generate_link_entries(get_MAC_address("h1"), [get_MAC_address("h6"), get_MAC_address("h7")], "s2", ["s3", "s3"]),
            **generate_link_entries(get_MAC_address("h6"), [get_MAC_address("h1")], "s2", ["s1"]),
            **generate_link_entries(get_MAC_address("h7"), [get_MAC_address("h1")], "s2", ["s1"]),
        },
        get_dpid("s3"): {
            **generate_link_entries(get_MAC_address("h1"), [get_MAC_address("h6"), get_MAC_address("h7")], "s3", ["h6", "h7"]),
            **generate_link_entries(get_MAC_address("h6"), [get_MAC_address("h1"), get_MAC_address("h7")], "s3", ["s2", "h7"]),
            **generate_link_entries(get_MAC_address("h7"), [get_MAC_address("h1"), get_MAC_address("h6")], "s3", ["s2", "h6"]),
        },
    }
    second_scenario = {
        get_dpid("s1"): {
            **generate_link_entries(get_MAC_address("h2"), [get_MAC_address("h5"), get_MAC_address("h8")], "s1", ["s2", "s4"]),
            **generate_link_entries(get_MAC_address("h5"), [get_MAC_address("h2"), get_MAC_address("h8")], "s1", ["h2", "s4"]),
            **generate_link_entries(get_MAC_address("h8"), [get_MAC_address("h2"), get_MAC_address("h5")], "s1", ["h2", "s2"]),
        },
        get_dpid("s2"): {
            **generate_link_entries(get_MAC_address("h2"), [get_MAC_address("h5")], "s2", ["h5"]),
            **generate_link_entries(get_MAC_address("h5"), [get_MAC_address("h2"), get_MAC_address("h8")], "s2", ["s1", "s1"]),
            **generate_link_entries(get_MAC_address("h8"), [get_MAC_address("h5")], "s2", ["h5"]),
        },
        get_dpid("s4"): {
            **generate_link_entries(get_MAC_address("h2"), [get_MAC_address("h8")], "s4", ["h8"]),
            **generate_link_entries(get_MAC_address("h5"), [get_MAC_address("h8")], "s4", ["h8"]),
            **generate_link_entries(get_MAC_address("h8"), [get_MAC_address("h2"), get_MAC_address("h5")], "s4", ["s1", "s1"]),
        }
    }
    third_scenario = {
        get_dpid("s2"): {
            **generate_link_entries(get_MAC_address("h3"), [get_MAC_address("h4"), get_MAC_address("h9"), get_MAC_address("h10")], "s2", ["h4", "s4", "s4"]),
            **generate_link_entries(get_MAC_address("h4"), [get_MAC_address("h3"), get_MAC_address("h9"), get_MAC_address("h10")], "s2", ["h3", "s4", "s4"]),
            **generate_link_entries(get_MAC_address("h9"), [get_MAC_address("h3"), get_MAC_address("h4")], "s2", ["h3", "h4"]),
            **generate_link_entries(get_MAC_address("h10"), [get_MAC_address("h3"), get_MAC_address("h4")], "s2", ["h3", "h4"]),
        },
        get_dpid("s4"): {
            **generate_link_entries(get_MAC_address("h3"), [get_MAC_address("h9"), get_MAC_address("h10")], "s4", ["h9", "h10"]),
            **generate_link_entries(get_MAC_address("h4"), [get_MAC_address("h9"), get_MAC_address("h10")], "s4", ["h9", "h10"]),
            **generate_link_entries(get_MAC_address("h9"), [get_MAC_address("h3"), get_MAC_address("h4"), get_MAC_address("h10")], "s4", ["s2", "s2", "h10"]),
            **generate_link_entries(get_MAC_address("h10"), [get_MAC_address("h3"), get_MAC_address("h4"),get_MAC_address("h9")], "s4", ["s2", "s2", "h9"]),
        }
    }
    return {
        0: first_scenario,
        1: second_scenario,
        2: third_scenario
    }
