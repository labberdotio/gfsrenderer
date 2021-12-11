
import os
import sys

import asyncio

from flask import Flask
from flask import render_template
from flask import request
from flask import Response

from flask_socketio import SocketIO
from flask_socketio import emit
from flask_socketio import disconnect

# from python_graphql_client import GraphqlClient
from gfsgql import GFSGQL

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)

listen_addr = os.environ.get("LISTEN_ADDR", "0.0.0.0")
listen_port = os.environ.get("LISTEN_PORT", "5000")

# gfs_ns = os.environ.get("GFS_NAMESPACE", "gfs1")
gfs_host = os.environ.get("GFS_HOST", "gfsapi")
gfs_port = os.environ.get("GFS_PORT", "5000")
gfs_username = os.environ.get("GFS_USERNAME", "root")
gfs_password = os.environ.get("GFS_PASSWORD", "root")

GRAPHQLQUERY = "query.graphql"

TEMPLATETYPE = "jinja"
MUSTACHETEMPLATE = "template.mustache"
JINJATEMPLATE = "template.jinja"

state = {
    "GFSHOST": gfs_host, 
    "GFSPORT": gfs_port, 
    "GRAPHQLQUERY": GRAPHQLQUERY, 
    "TEMPLATETYPE": TEMPLATETYPE, 
    "MUSTACHETEMPLATE": MUSTACHETEMPLATE, 
    "JINJATEMPLATE": JINJATEMPLATE
}

gqlClient = GFSGQL(
    gfs_host = gfs_host,
    gfs_port = gfs_port,
    gfs_username = gfs_username,
    gfs_password = gfs_password,
)

# 
# 
# 

@app.route('/dhcpquery')
def dhcpquery():
    queryfile = open("./dhcp/" + str(GRAPHQLQUERY), "r")
    query = queryfile.read()
    return Response(
        query, 
        mimetype='application/text'
    )

@app.route('/dhcptemplate')
def dhcptemplate():
    templatefile = open("./dhcp/" + str(MUSTACHETEMPLATE), "r")
    template = templatefile.read()
    return Response(
        template, 
        mimetype='application/text'
    )

@app.route('/rundhcpquery')
def rundhcpquery():
    queryfile = open("./dhcp/" + str(GRAPHQLQUERY), "r")
    query = queryfile.read()
    import simplejson as json
    return Response(
        json.dumps(
            gqlClient.gqlexec(
                query,
                {
                }
            ), 
            indent=2, 
            sort_keys=False
        ), 
        mimetype='application/json'
    )

@app.route('/dhcp')
def dhcp():
    queryfile = open("./dhcp/" + str(GRAPHQLQUERY), "r")
    query = queryfile.read()
    templatefile = open("./dhcp/" + str(MUSTACHETEMPLATE), "r")
    template = templatefile.read()
    import pystache
    return Response(
        pystache.render(
            template,
            gqlClient.gqlexec(
                query,
                {
                }
            ), 
        ), 
        mimetype='application/text'
    )

# 
# 
# 

@app.route('/dnsquery')
def dnsquery():
    queryfile = open("./dns/" + str(GRAPHQLQUERY), "r")
    query = queryfile.read()
    return Response(
        query, 
        mimetype='application/text'
    )

@app.route('/dnstemplate')
def dnstemplate():
    templatefile = open("./dns/" + str(MUSTACHETEMPLATE), "r")
    template = templatefile.read()
    return Response(
        template, 
        mimetype='application/text'
    )

@app.route('/rundnsquery')
def rundnsquery():
    queryfile = open("./dns/" + str(GRAPHQLQUERY), "r")
    query = queryfile.read()
    import simplejson as json
    return Response(
        json.dumps(
            gqlClient.gqlexec(
                query,
                {
                }
            ), 
            indent=2, 
            sort_keys=False
        ), 
        mimetype='application/json'
    )

@app.route('/dns')
def dns():
    queryfile = open("./dns/" + str(GRAPHQLQUERY), "r")
    query = queryfile.read()
    templatefile = open("./dns/" + str(MUSTACHETEMPLATE), "r")
    template = templatefile.read()
    import pystache
    return Response(
        pystache.render(
            template,
            gqlClient.gqlexec(
                query,
                {
                }
            ), 
        ), 
        mimetype='application/text'
    )

# 
# 
# 

@app.route('/bindconfquery')
def bindconfquery():
    queryfile = open("./bindconf/" + str(GRAPHQLQUERY), "r")
    query = queryfile.read()
    return Response(
        query, 
        mimetype='application/text'
    )

@app.route('/bindconftemplate')
def bindconftemplate():
    templatefile = open("./bindconf/" + str(MUSTACHETEMPLATE), "r")
    template = templatefile.read()
    return Response(
        template, 
        mimetype='application/text'
    )

@app.route('/runbindconfquery')
def runbindconfquery():
    queryfile = open("./bindconf/" + str(GRAPHQLQUERY), "r")
    query = queryfile.read()
    import simplejson as json
    return Response(
        json.dumps(
            gqlClient.gqlexec(
                query,
                {
                }
            ), 
            indent=2, 
            sort_keys=False
        ), 
        mimetype='application/json'
    )

@app.route('/bindconf')
def bindconf():
    queryfile = open("./bindconf/" + str(GRAPHQLQUERY), "r")
    query = queryfile.read()
    templatefile = open("./bindconf/" + str(MUSTACHETEMPLATE), "r")
    template = templatefile.read()
    import pystache
    return Response(
        pystache.render(
            template,
            gqlClient.gqlexec(
                query,
                {
                }
            ), 
        ), 
        mimetype='application/text'
    )

# 
# 
# 

@app.route('/bindzonequery')
def bindzonequery():
    queryfile = open("./bindzone/" + str(GRAPHQLQUERY), "r")
    query = queryfile.read()
    return Response(
        query, 
        mimetype='application/text'
    )

@app.route('/bindzonetemplate')
def bindzonetemplate():
    templatefile = open("./bindzone/" + str(MUSTACHETEMPLATE), "r")
    template = templatefile.read()
    return Response(
        template, 
        mimetype='application/text'
    )

@app.route('/runbindzonequery')
def runbindzonequery():
    queryfile = open("./bindzone/" + str(GRAPHQLQUERY), "r")
    query = queryfile.read()
    import simplejson as json
    return Response(
        json.dumps(
            gqlClient.gqlexec(
                query,
                {
                }
            ), 
            indent=2, 
            sort_keys=False
        ), 
        mimetype='application/json'
    )

@app.route('/bindzone')
def bindzone():
    queryfile = open("./bindzone/" + str(GRAPHQLQUERY), "r")
    query = queryfile.read()
    templatefile = open("./bindzone/" + str(MUSTACHETEMPLATE), "r")
    template = templatefile.read()
    import datetime
    from datetime import datetime
    import pystache
    context = gqlClient.gqlexec(
        query,
        {
        }
    )
    # now = datetime.date.today()
    now = datetime.now() # current date and time
    # year = now.year
    year = now.strftime("%Y")
    # year = now.strftime("%y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    hour = now.strftime("%H")
    min = now.strftime("%M")
    sec = now.strftime("%S")
    context["year"] = str(year)
    context["month"] = str(month)
    context["day"] = str(day)
    context["hour"] = str(hour)
    context["min"] = str(min)
    context["sec"] = str(sec)
    # serial can not go above 32bit, so we get an overflow with the below
    # context["incr"] = str( (int(hour) * 60 * 60) + (int(min) * 60) + int(sec) )
    # we have 2 digits for the increment, lets condense hour and mins into 0 to 99
    # 23 * 60 + 60 = 1440 minutes per day
    # 0 to 99 max -> 1440 / 1440 * 99 = 99
    # serial = ( h * 60 + s ) / 1440 * 99
    # serial ( 11 * 60 + 25 ) / 1440 * 99 = 47
    context["incr"] = str(int((((int(hour) * 60) + int(min)) / 1440) * 90))
    return pystache.render(
        template,
        # gqlClient.gqlexec(
        #     query,
        #     {
        #     }
        # ),
        context
    )

# 
# 
# 

@app.route('/hostsquery')
def hostsquery():
    queryfile = open("./hosts/" + str(GRAPHQLQUERY), "r")
    query = queryfile.read()
    return Response(
        query, 
        mimetype='application/text'
    )

@app.route('/hoststemplate')
def hoststemplate():
    templatefile = open("./hosts/" + str(JINJATEMPLATE), "r")
    template = templatefile.read()
    return Response(
        template, 
        mimetype='application/text'
    )

@app.route('/runhostsquery')
def runhostsquery():
    queryfile = open("./hosts/" + str(GRAPHQLQUERY), "r")
    query = queryfile.read()
    import simplejson as json
    return Response(
        json.dumps(
            gqlClient.gqlexec(
                query,
                {
                }
            ), 
            indent=2, 
            sort_keys=False
        ), 
        mimetype='application/json'
    )

@app.route('/hosts')
def hosts():
    queryfile = open("./hosts/" + str(GRAPHQLQUERY), "r")
    query = queryfile.read()
    templatefile = open("./hosts/" + str(JINJATEMPLATE), "r")
    template = templatefile.read()
    # import pystache
    # return pystache.render(
    #     template,
    #     gqlClient.gqlexec(
    #         query,
    #         {
    #         }
    #     ), 
    # )
    from jinja2 import Template
    t1 = Template(
       template
    )
    return Response(
        t1.render(
            gqlClient.gqlexec(
                query,
                {
                }
            )
        ), 
        mimetype='application/text'
    )

# 
# 
# 

@app.route('/sshquery')
def sshquery():
    queryfile = open("./ssh/" + str(GRAPHQLQUERY), "r")
    query = queryfile.read()
    return Response(
        query, 
        mimetype='application/text'
    )

@app.route('/sshtemplate')
def sshtemplate():
    templatefile = open("./ssh/" + str(JINJATEMPLATE), "r")
    template = templatefile.read()
    return Response(
        template, 
        mimetype='application/text'
    )

@app.route('/runsshsquery')
def runsshquery():
    queryfile = open("./ssh/" + str(GRAPHQLQUERY), "r")
    query = queryfile.read()
    import simplejson as json
    return Response(
        json.dumps(
            gqlClient.gqlexec(
                query,
                {
                }
            ), 
            indent=2, 
            sort_keys=False
        ), 
        mimetype='application/json'
    )

@app.route('/ssh')
def ssh():
    queryfile = open("./ssh/" + str(GRAPHQLQUERY), "r")
    query = queryfile.read()
    templatefile = open("./ssh/" + str(JINJATEMPLATE), "r")
    template = templatefile.read()
    # import pystache
    # return pystache.render(
    #     template,
    #     gqlClient.gqlexec(
    #         query,
    #         {
    #         }
    #     ), 
    # )
    from jinja2 import Template
    t1 = Template(
       template
    )
    return Response(
        t1.render(
            gqlClient.gqlexec(
                query,
                {
                }
            )
        ), 
        mimetype='application/text'
    )

# 
# 
# 

@app.route('/httpquery')
def httpquery():
    queryfile = open("./http/" + str(GRAPHQLQUERY), "r")
    query = queryfile.read()
    return Response(
        query, 
        mimetype='application/text'
    )

@app.route('/httptemplate')
def httptemplate():
    templatefile = open("./http/" + str(JINJATEMPLATE), "r")
    template = templatefile.read()
    return Response(
        template, 
        mimetype='application/text'
    )

@app.route('/httpquery')
def runhttpquery():
    queryfile = open("./http/" + str(GRAPHQLQUERY), "r")
    query = queryfile.read()
    import simplejson as json
    return Response(
        json.dumps(
            gqlClient.gqlexec(
                query,
                {
                }
            ), 
            indent=2, 
            sort_keys=False
        ), 
        mimetype='application/json'
    )

@app.route('/http')
def http():
    queryfile = open("./http/" + str(GRAPHQLQUERY), "r")
    query = queryfile.read()
    templatefile = open("./http/" + str(JINJATEMPLATE), "r")
    template = templatefile.read()
    # import pystache
    # return pystache.render(
    #     template,
    #     gqlClient.gqlexec(
    #         query,
    #         {
    #         }
    #     ), 
    # )
    from jinja2 import Template
    t1 = Template(
       template
    )
    return Response(
        t1.render(
            gqlClient.gqlexec(
                query,
                {
                }
            )
        ), 
        mimetype='application/text'
    )

# 
# 
# 

if __name__ == '__main__':
    # socketio.run(app, host=LISTENERADDR, port=LISTENERPORT)
    socketio.run(app, host=str(listen_addr), port=int(listen_port))
