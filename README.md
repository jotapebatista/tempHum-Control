# Monitoring Service Application

This is a Python application for monitoring temperature and humidity levels of a room and controlling a dehumidifier accordingly. It makes API requests to a device that reads temperature and humidity data and writes it to an InfluxDB database. The application then checks if the humidity level exceeds a threshold and toggles the dehumidifier on or off accordingly.

## Prerequisites

To use this application, you must have the following installed:

- Python 3.6 or higher
- InfluxDB 2.0 or higher
- Requests library
- Requests-futures library
- InfluxDB client library

## Configuration

The application requires a configuration file, `config.json`, which should contain the following fields:

```
{
    "influxdb": {
        "url": "[IFLUXDB_URL]",
        "org": "[INFLUXDB_ORG]",
        "bucket": "[INFLUXDB_BUCKET]"
    },
    "device": {
        "api_url": "[API_URL]",
        "auth_key": "[SHELLY_AUTH_KEY]",
        "id": "[DEVICE_ID]",
        "max_workers": 10,
        "max_retries": 3,
        "delay": 3,
        "temperature_lower_threshold" : 45,
        "temperature_upper_threshold": 55
    },
    "plug": {
        "url": ""
    }
}
```

- `influxdb`: This field contains the URL, organization, and bucket information for your InfluxDB instance.
- `device`: This field contains the URL, authentication key, device ID, and other settings for the device that reads temperature and humidity data.
- `plug`: This field contains the URL for the dehumidifier API.

## Usage

To use the application, simply run the `app.py` file with Python:

```
python3 app.py
```

The application will run indefinitely, reading temperature and humidity data and toggling the dehumidifier on or off as necessary.

## Logging

The application logs to a file located at `logs/app.log`. If the directory does not exist, it will be created automatically. The logging level can be set to either `INFO` or `ERROR`.

## License

This application is made available under the [MIT License](https://opensource.org/licenses/MIT).