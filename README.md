# netatmo wind bucket

Read Netatmo information and store them into bucket in a JSON file

[![Maintainability](https://api.codeclimate.com/v1/badges/48f8e53a77a3a8ff4dd2/maintainability)](https://codeclimate.com/github/sdesbure/netatmo-wind-bucket/maintainability)
|
[![](https://images.microbadger.com/badges/image/sdesbure/netatmo-wind-bucket.svg)](https://microbadger.com/images/sdesbure/netatmo-wind-bucket "Get your own image badge on microbadger.com")
|
[![](https://images.microbadger.com/badges/version/sdesbure/netatmo-wind-bucket.svg)](https://microbadger.com/images/sdesbure/netatmo-wind-bucket "Get your own version badge on microbadger.com")
|
[![](https://images.microbadger.com/badges/commit/sdesbure/netatmo-wind-bucket.svg)](https://microbadger.com/images/sdesbure/netatmo-wind-bucket "Get your own commit badge on microbadger.com")
|
[![](https://images.microbadger.com/badges/license/sdesbure/netatmo-wind-bucket.svg)](https://microbadger.com/images/sdesbure/netatmo-wind-bucket "Get your own license badge on microbadger.com")


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
