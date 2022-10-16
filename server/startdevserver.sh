#!/bin/sh

# pipenv shell

# 10.88.88.171 zookeeper.gfsdev zookeeper.gfsdev.localdomain
# 10.88.88.171 broker.gfsdev broker.gfsdev.localdomain
# 10.88.88.171 gremlin.gfsdev gremlin.gfsdev.localdomain
# 10.88.88.171 gfs.gfsdev gfs.gfsdev.localdomain
# 10.88.88.171 gfsui.gfsdev gfsui.gfsdev.localdomain

export LISTEN_ADDR="0.0.0.0"
export LISTEN_PORT="5000"

export GFS_HOST="gfs.botcanics.localdomain"
export GFS_PORT="80"
export GFS_USERNAME="root"
export GFS_PASSWORD="root"

python ./src/py/server.py

