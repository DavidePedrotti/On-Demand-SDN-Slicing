def get_IP_address(host_name: str) -> str:
    """
    Get the IP address for a given host name.

    Args:
        host_name (str): The name of the host (e.g., "h1", "h2", etc.).

    Returns:
        str: The IP address corresponding to the host name.
    """
    ip_mapping = {
        f"h{i}": f"192.168.0.{i}" for i in range(1, 11)
    }
    return ip_mapping.get(host_name)

def get_MAC_address (host_name: str) -> str:
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

def get_dpid (host_name: str) -> int:
    """
    Get the DPID (Datapath ID) for a given switch name.

    Args:
        host_name (str): The name of the switch (e.g., "s1", "s2", etc.).

    Returns:
        int: The DPID corresponding to the switch name.
    """
    dpid_mapping = {
        f"s{i}": f"{i:016x}" for i in range(1, 6)
    }
    return int(dpid_mapping.get(host_name), 16)


def get_port (src: str, dst: str) -> int:
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
            "h1": 3,
            "h10": 4,
            "s2": 1,
            "s4": 2,
        },
        "s2": {
            "h5": 4,
            "s1": 1,
            "s3": 2,
            "s4": 3,
        },
        "s3": {
            "h2": 3,
            "h3": 4,
            "h4": 5,
            "s2": 1,
            "s4": 2,
        },
        "s4": {
            "h6": 2,
            "h7": 3,
            "h8": 4,
            "s1": 1,
            "s2": 2,
            "s3": 3,
            "s5": 4,
        },
        "s5": {
            "h6": 2,
            "h7": 3,
            "h8": 4,
            "h9": 5,
            "s4": 1,
        }
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

def slice_to_port(scenario = 0):
    """
    Generate port mappings for different slicing scenarios.

    Args:
        scenario (int): The scenario number (0, 1, 2, or 3). Defaults to 0.

    Returns:
        dict: A dictionary representing the port mappings for the given scenario.
    """
    if scenario == 0:
        return {
            get_dpid("s1"): {
                **generate_link_entries(get_IP_address("h10"), [get_IP_address("h9")], "s1", ["s4"]),
                **generate_link_entries(get_IP_address("h9"), [get_IP_address("h10")], "s1", ["h10"]),
            },
            get_dpid("s4"): {
                **generate_link_entries(get_IP_address("h10"), [get_IP_address("h9")], "s4", ["s5"]),
                **generate_link_entries(get_IP_address("h9"), [get_IP_address("h10")], "s4", ["s1"]),
            },
            get_dpid("s5"): {
                **generate_link_entries(get_IP_address("h10"), [get_IP_address("h9")], "s5", ["h9"]),
                **generate_link_entries(get_IP_address("h9"), [get_IP_address("h10")], "s5", ["s4"]),
            },
        }
    elif scenario == 1:
        return {
            get_dpid("s1"): {
                **generate_link_entries(get_IP_address("h2"), [get_IP_address("h10")], "s1", ["h10"]),
                **generate_link_entries(get_IP_address("h3"), [get_IP_address("h10")], "s1", ["h10"]),
                **generate_link_entries(get_IP_address("h4"), [get_IP_address("h10")], "s1", ["h10"]),
                **generate_link_entries(get_IP_address("h5"), [get_IP_address("h10")], "s1", ["h10"]),
                **generate_link_entries(get_IP_address("h6"), [get_IP_address("h10")], "s1", ["h10"]),
                **generate_link_entries(get_IP_address("h9"), [get_IP_address("h10")], "s1", ["h10"]),
                **generate_link_entries(get_IP_address("h10"), [get_IP_address("h2"), get_IP_address("h3"), get_IP_address("h4"), get_IP_address("h5"), get_IP_address("h6"), get_IP_address("h9")], "s1", ["s4"] * 6),
            },
            get_dpid("s2"): {
                **generate_link_entries(get_IP_address("h2"), [get_IP_address("h5")], "s2", ["h5"]),
                **generate_link_entries(get_IP_address("h3"), [get_IP_address("h5")], "s2", ["h5"]),
                **generate_link_entries(get_IP_address("h4"), [get_IP_address("h5")], "s2", ["h5"]),
                **generate_link_entries(get_IP_address("h5"), [get_IP_address("h2"), get_IP_address("h3"), get_IP_address("h4"), get_IP_address("h6"), get_IP_address("h10")], "s2", ["s4"] * 5),
                **generate_link_entries(get_IP_address("h6"), [get_IP_address("h5")], "s2", ["h5"]),
                **generate_link_entries(get_IP_address("h10"), [get_IP_address("h5")], "s2", ["h5"]),
            },
            get_dpid("s3"): {
                **generate_link_entries(get_IP_address("h2"), [get_IP_address("h3"), get_IP_address("h4"), get_IP_address("h5"), get_IP_address("h6"), get_IP_address("h10")], "s3", ["h3", "h4"] + ["s4"] * 3),
                **generate_link_entries(get_IP_address("h3"), [get_IP_address("h2"), get_IP_address("h4"), get_IP_address("h5"), get_IP_address("h6"), get_IP_address("h10")], "s3", ["h2", "h4"] + ["s4"] * 3),
                **generate_link_entries(get_IP_address("h4"), [get_IP_address("h2"), get_IP_address("h3"), get_IP_address("h5"), get_IP_address("h6"), get_IP_address("h10")], "s3", ["h2", "h3"] + ["s4"] * 3),
                **generate_link_entries(get_IP_address("h5"), [get_IP_address("h2"), get_IP_address("h3"), get_IP_address("h4")], "s3", ["h2", "h3", "h4"]),
                **generate_link_entries(get_IP_address("h6"), [get_IP_address("h2"), get_IP_address("h3"), get_IP_address("h4")], "s3", ["h2", "h3", "h4"]),
                **generate_link_entries(get_IP_address("h10"), [get_IP_address("h2"), get_IP_address("h3"), get_IP_address("h4")], "s3", ["h2", "h3", "h4"]),
            },
            get_dpid("s4"): {
                **generate_link_entries(get_IP_address("h2"), [get_IP_address("h5"), get_IP_address("h6"), get_IP_address("h10")], "s4", ["s2", "s5", "s1"]),
                **generate_link_entries(get_IP_address("h3"), [get_IP_address("h5"), get_IP_address("h6"), get_IP_address("h10")], "s4", ["s2", "s5", "s1"]),
                **generate_link_entries(get_IP_address("h4"), [get_IP_address("h5"), get_IP_address("h6"), get_IP_address("h10")], "s4", ["s2", "s5", "s1"]),
                **generate_link_entries(get_IP_address("h5"), [get_IP_address("h2"), get_IP_address("h3"), get_IP_address("h4"), get_IP_address("h6"), get_IP_address("h10")], "s4", ["s3"] * 3 + ["s5", "s1"]),
                **generate_link_entries(get_IP_address("h6"), [get_IP_address("h2"), get_IP_address("h3"), get_IP_address("h4"), get_IP_address("h5"), get_IP_address("h10")], "s4", ["s3"] * 3 + ["s2", "s1"]),
                **generate_link_entries(get_IP_address("h9"), [get_IP_address("h10")], "s4", ["s1"]),
                **generate_link_entries(get_IP_address("h10"), [get_IP_address("h2"), get_IP_address("h3"), get_IP_address("h4"), get_IP_address("h5"), get_IP_address("h6"), get_IP_address("h9")], "s4", ["s3"] * 3 + ["s2", "s5", "s5"]),
            },
            get_dpid("s5"): {
                **generate_link_entries(get_IP_address("h2"), [get_IP_address("h6")], "s5", ["h6"]),
                **generate_link_entries(get_IP_address("h3"), [get_IP_address("h6")], "s5", ["h6"]),
                **generate_link_entries(get_IP_address("h4"), [get_IP_address("h6")], "s5", ["h6"]),
                **generate_link_entries(get_IP_address("h5"), [get_IP_address("h6")], "s5", ["h6"]),
                **generate_link_entries(get_IP_address("h6"), [get_IP_address("h2"), get_IP_address("h3"), get_IP_address("h4"), get_IP_address("h5"), get_IP_address("h7"), get_IP_address("h8"), get_IP_address("h9"), get_IP_address("h10")], "s5", ["s4"] * 4 + ["h7", "h8", "h9", "s4"]),
                **generate_link_entries(get_IP_address("h7"), [get_IP_address("h6")], "s5", ["h6"]),
                **generate_link_entries(get_IP_address("h8"), [get_IP_address("h6")], "s5", ["h6"]),
                **generate_link_entries(get_IP_address("h9"), [get_IP_address("h6"), get_IP_address("h10")], "s5", ["h6", "s4"]),
                **generate_link_entries(get_IP_address("h10"), [get_IP_address("h6"), get_IP_address("h9")], "s5", ["h6", "h9"]),
            },
        }
    elif scenario == 2:
        return {
            get_dpid("s1"): {
                **generate_link_entries(get_IP_address("h10"), [get_IP_address("h9"), get_IP_address("h6")], "s1", ["s4", "s4"]),
                **generate_link_entries(get_IP_address("h9"), [get_IP_address("h10")], "s1", ["h10"]),
                **generate_link_entries(get_IP_address("h6"), [get_IP_address("h10")], "s1", ["h10"]),
            },
            get_dpid("s4"): {
                **generate_link_entries(get_IP_address("h10"), [get_IP_address("h9"), get_IP_address("h6")], "s4", ["s5", "s5"]),
                **generate_link_entries(get_IP_address("h9"), [get_IP_address("h10")], "s4", ["s1"]),
                **generate_link_entries(get_IP_address("h6"), [get_IP_address("h10")], "s4", ["s1"]),
            },
            get_dpid("s5"): {
                **generate_link_entries(get_IP_address("h10"), [get_IP_address("h9"), get_IP_address("h6")], "s5", ["h9", "h6"]),
                **generate_link_entries(get_IP_address("h9"), [get_IP_address("h6"), get_IP_address("h10")], "s5", ["h6", "s4"]),
                **generate_link_entries(get_IP_address("h6"), [get_IP_address("h9"), get_IP_address("h10")], "s5", ["h9", "s4"]),
            },
        }
    elif scenario == 3:
        return {
            get_dpid("s1"): {
                **generate_link_entries(get_IP_address("h1"), [get_IP_address("h2"), get_IP_address("h3"), get_IP_address("h4"), get_IP_address("h5"), get_IP_address("h6"), get_IP_address("h9"), get_IP_address("h10")], "s1", ["s2"] * 4 + ["s4"] * 2 + ["h10"]),
                **generate_link_entries(get_IP_address("h2"), [get_IP_address("h1")], "s1", ["h1"]),
                **generate_link_entries(get_IP_address("h3"), [get_IP_address("h1")], "s1", ["h1"]),
                **generate_link_entries(get_IP_address("h4"), [get_IP_address("h1")], "s1", ["h1"]),
                **generate_link_entries(get_IP_address("h5"), [get_IP_address("h1")], "s1", ["h1"]),
                **generate_link_entries(get_IP_address("h6"), [get_IP_address("h1"), get_IP_address("h2"), get_IP_address("h3"), get_IP_address("h4"), get_IP_address("h5"), get_IP_address("h10")], "s1", ["h1"] + ["s2"] * 4 + ["h10"]),
                **generate_link_entries(get_IP_address("h9"), [get_IP_address("h1"), get_IP_address("h2"), get_IP_address("h3"), get_IP_address("h4"), get_IP_address("h5"), get_IP_address("h10")], "s1", ["h1"] + ["s2"] * 4 + ["h10"]),
                **generate_link_entries(get_IP_address("h10"), [get_IP_address("h1"), get_IP_address("h6"), get_IP_address("h9")], "s1", ["h1"] + ["s4"] * 2),
            },
            get_dpid("s2"): {
                **generate_link_entries(get_IP_address("h1"), [get_IP_address("h2"), get_IP_address("h3"), get_IP_address("h4"), get_IP_address("h5")], "s2", ["s3"] * 3 + ["h5"]),
                **generate_link_entries(get_IP_address("h2"), [get_IP_address("h1")], "s2", ["s1"]),
                **generate_link_entries(get_IP_address("h3"), [get_IP_address("h1")], "s2", ["s1"]),
                **generate_link_entries(get_IP_address("h4"), [get_IP_address("h1")], "s2", ["s1"]),
                **generate_link_entries(get_IP_address("h5"), [get_IP_address("h1")], "s2", ["s1"]),
            },
            get_dpid("s3"): {
                **generate_link_entries(get_IP_address("h1"), [get_IP_address("h2"), get_IP_address("h3"), get_IP_address("h4")], "s3", ["h2", "h3", "h4"]),
                **generate_link_entries(get_IP_address("h2"), [get_IP_address("h1")], "s3", ["s2"]),
                **generate_link_entries(get_IP_address("h3"), [get_IP_address("h1")], "s3", ["s2"]),
                **generate_link_entries(get_IP_address("h4"), [get_IP_address("h1")], "s3", ["s2"]),
            },
            get_dpid("s4"): {
                **generate_link_entries(get_IP_address("h1"), [get_IP_address("h6"), get_IP_address("h9")], "s4", ["s5", "s5"]),
                **generate_link_entries(get_IP_address("h6"), [get_IP_address("h1"), get_IP_address("h10")], "s4", ["s1", "s1"]),
                **generate_link_entries(get_IP_address("h9"), [get_IP_address("h1"), get_IP_address("h10")], "s4", ["s1", "s1"]),
                **generate_link_entries(get_IP_address("h10"), [get_IP_address("h6"), get_IP_address("h9")], "s4", ["s5", "s5"]),
            },
            get_dpid("s5"): {
                **generate_link_entries(get_IP_address("h1"), [get_IP_address("h6"), get_IP_address("h9")], "s5", ["h6", "h9"]),
                **generate_link_entries(get_IP_address("h6"), [get_IP_address("h1"), get_IP_address("h9"), get_IP_address("h10")], "s5", ["s4", "h9", "s4"]),
                **generate_link_entries(get_IP_address("h9"), [get_IP_address("h1"), get_IP_address("h6"), get_IP_address("h10")], "s5", ["s4", "h6", "s4"]),
                **generate_link_entries(get_IP_address("h10"), [get_IP_address("h6"), get_IP_address("h9")], "s5", ["h6", "h9"]),
            },
        }