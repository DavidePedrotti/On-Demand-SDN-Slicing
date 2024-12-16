#!/bin/sh

# TODO: Create 3 virtual queues for every link in the network (3*4=12), with max-rate for each services passed as variable

# Switch 3 - eth3
sudo ovs-vsctl set port s3-eth3 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000000 \
queues:123=@1q \
queues:234=@2q -- \
--id=@1q create queue other-config:min-rate=10000 other-config:max-rate=50000 -- \
--id=@2q create queue other-config:min-rate=100000 other-config:max-rate=50000

# Switch 2 - eth5
sudo ovs-vsctl set port s2-eth5 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000 \
queues:123=@1q \
queues:234=@2q -- \
--id=@1q create queue other-config:min-rate=10000 other-config:max-rate=50000 -- \
--id=@2q create queue other-config:min-rate=10000 other-config:max-rate=50000



