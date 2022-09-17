
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

@app.route('/query', methods=['POST'])
def query():
    from flask import request
    import simplejson as json

    query = request.form.get("query")

    if not query:
        return Response(
            "Unable to read query, please pass a valid query",
            status=400,
        )

    data = {}
    try:
        data = gqlClient.gqlexec(
            query,
            {
            }
        )
    except Exception as e:
        print(e)
        return Response(
            # "GQL GraphQL error " + str(e.response.json()),
            str(e),
            status=400,
        )

    if not data:
        data = {}

    return Response(
        json.dumps(
            data, 
            indent=2, 
            sort_keys=False
        ), 
        mimetype='application/json'
    )

@app.route('/render', methods=['POST'])
def render():
    from flask import request
    import simplejson as json

    format = request.args.get("format", "mustache")
    if not format:
        format = "mustache"

    query = request.form.get("query")
    template = request.form.get("template")
    context = request.form.get("context")

    if format not in ["mustache", "handlebars", "jinja"]:
        return Response(
            "Invalid format, template formats are mustache, handlebars or jinja",
            status=400,
        )

    if not query:
        return Response(
            "Unable to read query, please pass a valid query",
            status=400,
        )

    if not template:
        return Response(
            "Unable to read template, please pass a valid template, format is set to " + str(format),
            status=400,
        )

    if context:
        try:
            context = json.loads(
                context
            )
        except Exception as e:
            return Response(
                "Unable to read context, if you want to pass an additional render context please pass valid JSON",
                status=400,
            )

    data = {}
    try:
        data = gqlClient.gqlexec(
            query,
            {
            }
        )
    except Exception as e:
        return Response(
            # "GQL GraphQL error " + str(e.response.json()),
            str(e),
            status=400,
        )

    if not data:
        data = {}

    if format == "jinja":
        from jinja2 import Template
        t1 = Template(
            template
        )
        return Response(
            t1.render(
                data
            ), 
            mimetype='application/text'
        )

    elif format == "handlebars":
        pass

    else:
        import pystache
        return Response(
            pystache.render(
                template,
                data, 
            ), 
            mimetype='application/text'
        )

# 
# 
# 

if __name__ == '__main__':
    # socketio.run(app, host=LISTENERADDR, port=LISTENERPORT)
    socketio.run(app, host=str(listen_addr), port=int(listen_port))
