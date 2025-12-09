#!/bin/bash

echo "-----------------------------------------------"
echo "Getting port statistics using gNMI Subscribe"
router=$(echo "ixr-r6d")
interface=$(echo "toe2c")
port=$(gnmic -a 172.20.20.2 -u admin -p NokiaSros1! --insecure get --format flat --path "/configure/router[router-name=Base]/interface[interface-name=$interface]/port" | awk -F': ' '{print $2}')


echo "    Router: $router" 
echo "    Router Interface: $interface"
echo "    Physical port: $port"
echo "-----------------------------------------------"
echo "Fetching inbound octets for interface $interface on router $router..."
echo "-----------------------------------------------"
gnmic -a 172.20.20.2 -u admin -p NokiaSros1! --insecure subscribe --format flat --path "/state/port[port-id=$port]/ethernet/statistics/in-octets"