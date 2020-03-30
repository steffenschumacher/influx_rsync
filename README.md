# influx_rsync
Tool to copy data from one influxdb to another incrementally with each run

## Requirements.

Python 3.6+

## Installation & Usage
### pip install


```sh
pip install influx_rsync
```
(you may need to run `pip` with root permission: `sudo pip install git+https://github.com//.git`)

Then import the package:
```python
import influx_rsync
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

Then import the package:
```python
from influx_rsync import InfluxRSync
```

## Getting Started
Install and then run the following:

```python
from influx_rsync import InfluxRSync
from influxdb import InfluxDBClient
from influx_rsync import InfluxRSync

src = InfluxDBClient(host='localhost')
dst = InfluxDBClient(host='remote.influxdb.com', verify_ssl=True, username='xxx', password='yyy')
irs = InfluxRSync(src, dst)
print(irs.sync())  # will copy whatever data in source which is newer than the latest found in destination

```

## Author

ssch@wheel.dk

