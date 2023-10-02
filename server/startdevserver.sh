#!/bin/sh

# pipenv shell

# 10.88.88.170 zookeeper.gfsdev zookeeper.gfsdev.localdomain
# 10.88.88.170 broker.gfsdev broker.gfsdev.localdomain
# 10.88.88.170 gremlin.gfsdev gremlin.gfsdev.localdomain
# 10.88.88.170 gfs.gfsdev gfs.gfsdev.localdomain
# 10.88.88.170 gfsui.gfsdev gfsui.gfsdev.localdomain

export LOG_LEVEL="DEBUG"

export LISTEN_ADDR="0.0.0.0"
# export LISTEN_PORT="5000"
export LISTEN_PORT="5001"

# export GFS_NAMESPACE="gfs1"
export GFS_NAMESPACE="labberinfra"
# export GFS_HOST="gfs.labber.io"
# export GFS_PORT="80"
export GFS_HOST="10.88.88.170"
export GFS_PORT="5000"
export GFS_USERNAME=""
export GFS_PASSWORD=""

python ./src/py/server.py
