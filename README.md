# UART → InfluxDB → Grafana Stack

This repo spins up InfluxDB + Grafana with Docker Compose and a Python script that sends mock data into Influx so you can visualize it in Grafana.

* [InfluxDB](https://github.com/influxdata/influxdb) - time series database
* [Chronograf](https://github.com/influxdata/chronograf) - admin UI for InfluxDB
* [Grafana](https://github.com/grafana/grafana) - visualization UI for InfluxDB

## Setup
Clone this repo, create your python environment and install all requirements.
```
bash
python -m venv .venv
. ./.venv/bin/activate
pip install -r bridge/requirements.txt
```

You'll need a `.env` file. I haven't pushed an example one yet.

Next just start InfluxDB + Grafana
```bash
docker-compose up -d
# or docker compose up -d, depending on your system
```

To stop the app:

1. Run the following command from the root of the cloned repo:
```
docker-compose down
```

Finally, run the bridge to get mock data. This will soon be replaced by reading an actual UART port or a mock tty device.
```
bash
python3 bridge/send_mock_influx.py
```

## Ports

The services in the app run on the following ports:

| Host Port | Service |
| - | - |
| 3000 | Grafana |
| 8086 | InfluxDB |
| 127.0.0.1:8888 | Chronograf |

Note that Chronograf does not support username/password authentication. Anyone who can connect to the service has full admin access. Consequently, the service is not publically exposed and can only be access via the loopback interface on the same machine that runs docker.

If docker is running on a remote machine that supports SSH, use the following command to setup an SSH tunnel to securely access Chronograf by forwarding port 8888 on the remote machine to port 8888 on the local machine:

```
ssh [options] <user>@<docker-host> -L 8888:localhost:8888 -N
```

## Volumes

The app creates the following named volumes (one for each service) so data is not lost when the app is stopped:

* influxdb-storage
* chronograf-storage
* grafana-storage

## Users

The app creates two admin users - one for InfluxDB and one for Grafana. By default, the username and password of both accounts is `admin`. To override the default credentials, set the following environment variables before starting the app:

* `INFLUXDB_USERNAME`
* `INFLUXDB_PASSWORD`
* `GRAFANA_USERNAME`
* `GRAFANA_PASSWORD`

## Database

The app creates a default InfluxDB database called `db0`.

## Data Sources

The app creates a Grafana data source called `InfluxDB` that's connected to the default IndfluxDB database (e.g. `db0`).

To provision additional data sources, see the Grafana [documentation](http://docs.grafana.org/administration/provisioning/#datasources) and add a config file to `./grafana-provisioning/datasources/` before starting the app.

