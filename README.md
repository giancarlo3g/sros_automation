# Nokia SROS automation lab

## Introduction
This repository provides a quick lab environment to demonstrate automation capabilities of Nokia SROS software using model-driven interfaces via gNMI and pySROS.

## Initial Setup
1. Requirements: 
    - Linux packages
        - Python
        - uv
        - Docker
        - gnmic
        - Containerlab
    - Others
        - Nokia SR-SIM image
        - Nokia SR-SIM license in the parent directory with name `license-srsim25.txt`

2. Start the environment 

    ```
    uv sync
    ```

3. Change mode for shell script

    ```
    chmod +x gnmi/shell_gnmic.sh
    ```

Alternative: run steps below to automate the installation of packages and setting up the Python environment. 
```
make install-all
```

```
make setup-project
```

You still need to load the SR-SIM container image and place the license file in the correct directory.

## Demos
### gNMI demo
Run the following demos from a Linux host with IP connectivity to the device under test.
1. gNMIc
Run commands included in [gnmic_examples.txt](./gnmi/gnmic_examples.txt) on the Linux terminal
2. gNMI with Python

    a. Subscription to port statistics via Telemetry
    
        uv run gnmi/port_stats.py

    b. Subscription to port state with On Change

        uv run gnmi/port_state_onchange.py

### PySROS demo
#### Off-box
Run the following demos from a Linux host with IP connectivity to the device under test.
1. Get info

    ```
    uv run pyrsros/get_info.py
    ```

2. Set hostname

    ```
    uv run pysros/set_hostname.py
    ```

3. Set static route

    ```
    uv run pysros/set_staticroute.py
    ```

4. Custom show command

    ```
    uv run pysros/custom_show.py
    ```

#### On-box
Connect to a router via ssh and run the commands below.
- Copy Python program to the node

    ```
    scp ./pysros/watch.py admin@ixrr6d-a:cf3:/
    ```

- Create alias
    ```
    /environment more false
    /environment command-alias alias "watch" admin-state enable
    /environment command-alias alias "watch" cli-command "pyexec \"cf3:/watch.py\""
    /environment command-alias { alias "watch" mount-point global }
    ```

- Run the command

    ```
    watch "show port 1/1/c1/1 statistics"
    ```
