#!/bin/sh

QUEUE_1=$1
QUEUE_2=$2
QUEUE_3=$3

# TODO: Create 3 virtual queues for every link in the network (3*4=12), with max-rate for each services passed as variable



# Switch 3 - eth3
sudo ovs-vsctl set port s3-eth3 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000000 \
queues:123=@1q \
queues:234=@2q \
queues:345=@3q -- \
--id=@1q create queue other-config:min-rate=1 other-config:max-rate=$QUEUE_1 -- \
--id=@2q create queue other-config:min-rate=1 other-config:max-rate=$QUEUE_2 -- \
--id=@3q create queue other-config:min-rate=1 other-config:max-rate=$QUEUE_3

# Switch 2 - eth4
sudo ovs-vsctl set port s2-eth4 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000000 \
queues:123=@1q \
queues:234=@2q \
queues:345=@3q -- \
--id=@1q create queue other-config:min-rate=1 other-config:max-rate=$QUEUE_1 -- \
--id=@2q create queue other-config:min-rate=1 other-config:max-rate=$QUEUE_2 -- \
--id=@3q create queue other-config:min-rate=1 other-config:max-rate=$QUEUE_3

# Switch 2 - eth5
sudo ovs-vsctl set port s2-eth5 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000000 \
queues:123=@1q \
queues:234=@2q \
queues:345=@3q -- \
--id=@1q create queue other-config:min-rate=1 other-config:max-rate=$QUEUE_1 -- \
--id=@2q create queue other-config:min-rate=1 other-config:max-rate=$QUEUE_2 -- \
--id=@3q create queue other-config:min-rate=1 other-config:max-rate=$QUEUE_3

# Switch 1 - eth3
sudo ovs-vsctl set port s1-eth3 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000000 \
queues:123=@1q \
queues:234=@2q \
queues:345=@3q -- \
--id=@1q create queue other-config:min-rate=1 other-config:max-rate=$QUEUE_1 -- \
--id=@2q create queue other-config:min-rate=1 other-config:max-rate=$QUEUE_2 -- \
--id=@3q create queue other-config:min-rate=1 other-config:max-rate=$QUEUE_3

# Switch 1 - eth4
sudo ovs-vsctl set port s1-eth4 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000000 \
queues:123=@1q \
queues:234=@2q \
queues:345=@3q -- \
--id=@1q create queue other-config:min-rate=1 other-config:max-rate=$QUEUE_1 -- \
--id=@2q create queue other-config:min-rate=1 other-config:max-rate=$QUEUE_2 -- \
--id=@3q create queue other-config:min-rate=1 other-config:max-rate=$QUEUE_3


# Switch 4 - eth4
sudo ovs-vsctl set port s4-eth4 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000000 \
queues:123=@1q \
queues:234=@2q \
queues:345=@3q -- \
--id=@1q create queue other-config:min-rate=1 other-config:max-rate=$QUEUE_1 -- \
--id=@2q create queue other-config:min-rate=1 other-config:max-rate=$QUEUE_2 -- \
--id=@3q create queue other-config:min-rate=1 other-config:max-rate=$QUEUE_3



if [ -f "qos_data/old_queues.txt" ]; then
    while read -r uuid
    do
        if [ -n "$uuid" ]; then
            sudo ovs-vsctl --if-exists destroy QoS $uuid
            sudo ovs-vsctl --if-exists destroy Queue $uuid
        fi
    done < "qos_data/old_queues.txt"
fi
