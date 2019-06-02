# netatmo wind bucket

Read Netatmo information and store them into bucket in a JSON file

## Installation

### prerequisites:

 * python 3
 * pip

__OR__

 * docker

### installation with python

```shell
pip install --user requirements.txt
```

## How to use

you'll need to set some environment variables before using it:

 * `NETATMO_USERNAME`: the username on netatmo;
 * `NETATMO_PASSWORD`: the password on netatmo;
 * `NETATMO_CLIENT_ID`: the client id of the app created on 
   https://dev.netatmo.com/;
 * `NETATMO_CLIENT_SECRET`: the secret of the app;
 * `NETATMO_DEVICE_ID`: the ID of the main module where you have the wind 
   module (it's its MAC Address);

then you can launch it:

```shell
python netatmo-wind-bucket.py
```

__OR__

```shell
touch buckets.json # only if buckets.json doesn't exist
docker run -d -v ${PWD}/buckets.json:/usr/src/app/buckets.json --env NETATMO_USERNAME=XXX --env NETATMO_PASSWORD=XXX --env NETATMO_CLIENT_ID=XXX --env NETATMO_CLIENT_SECRET=XXX --env NETATMO_DEVICE_ID="70:ee:50:xx:yy:zz" sdesbure/netatmo-wind-bucket:latest
```
