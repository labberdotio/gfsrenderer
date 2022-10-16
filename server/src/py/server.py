
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
# GFS DAO error class
# 
class GFSError(Exception):

    def __init__(self, error):
        self.error = error

    def __str__(self):
        return str(self.error)

# 
# 
# 

# @app.route('/query', methods=['GET', 'POST'])
@app.route('/query', methods=['GET'])
def query():
    from flask import request
    import simplejson as json
    try:
        return Response(
            json.dumps(
                doquery(
                    resolvequery(
                        queryname = request.args.get("query")
                    ), 
                    params = request.args
                ), 
                indent=2, 
                sort_keys=False
            ), 
            mimetype='application/json'
        )
    except Exception as e:
        return Response(
            str(e),
            status=400,
        )

# @app.route('/render', methods=['GET', 'POST'])
@app.route('/render', methods=['GET'])
def render():
    from flask import request
    import simplejson as json
    try:
        # (templatename, template = None, format = "mustache"):
        (template, format) = resolvetemplate(
            templatename = request.args.get("template"), 
            template = None, 
            format = request.args.get("format", "mustache")
        )
        return Response(
            dorender(
                template = template, 
                format = format, 
                data = doquery(
                    query = resolvequery(
                        queryname = request.args.get("query")
                    ), 
                    params = request.args
                ), 
            ), 
            mimetype='application/text'
        )
    except Exception as e:
        return Response(
            str(e),
            status=400,
        )

@app.route('/view', methods=['GET'])
def view():
    from flask import request
    import simplejson as json
    try:
        (query, template, format) = resolveview(
            viewname = request.args.get("view")
        )
        (template, format) = resolvetemplate(
            templatename = template["name"], 
            template = template["template"], 
            format = template["format"], 
        )
        return Response(
            dorender(
                template = template, 
                format = format, 
                data = doquery(
                    query = resolvequery(
                        queryname = query["name"], 
                        query = query["query"]
                    ), 
                    params = request.args
                ), 
            ), 
            mimetype='application/text'
        )
    except Exception as e:
        return Response(
            str(e),
            status=400,
        )

# 
# 
# 
def resolvequery(queryname, query = None):

    if not queryname and not query:
        # return Response(
        #     "Unable to read query, please pass a valid query",
        #     status=400,
        # )
        raise GFSError("Unable to read query, please pass a valid query")

    # File
    if queryname:
        try:
            # queryfile = open("/data/queries/" + str(queryname) + "." + "graphql", "r")
            # queryfile = open("/data/" + str(queryname) + "." + "graphql", "r")
            queryfile = open("/data/" + str(queryname), "r")
            query = queryfile.read()
            return query
        except Exception as e:
            # return Response(
            #     # "Query error: " + str(e.response.json()),
            #     str(e),
            #     status=400,
            # )
            # raise
            pass

    if queryname:
        try:
            queryquery = """
                query queryquery {
                    Querys(
                        name: "%s"
                    ) {
                        name, 
                        query
                    }
                }
            """ % (
                queryname
            )
            querydata = gqlClient.gqlexec(
                queryquery,
                {
                }
            )
            if querydata and \
                "data" in querydata and \
                "Querys" in querydata["data"] and \
                querydata["data"]["Querys"] and len(querydata["data"]["Querys"]) > 0 :
                query = querydata["data"]["Querys"][0]["query"]

        except Exception as e:
            # return Response(
            #     # "Query error: " + str(e.response.json()),
            #     str(e),
            #     status=400,
            # )
            raise

    if not query:
        # return Response(
        #     "Unable to read query, please pass a valid query",
        #     status=400,
        # )
        raise GFSError("Unable to read query, please pass a valid query")

    return query

# 
# 
# 
def resolvetemplate(templatename, template = None, format = "mustache"):

    if not templatename and not template:
        # return Response(
        #     "Unable to read template, please pass a valid template, format is set to " + str(format),
        #     status=400,
        # )
        raise GFSError("Unable to read template, please pass a valid template, format is set to " + str(format))

        # File
    if templatename:
        try:
            # templatefile = open("/data/templates/" + str(templatename) + "." + format, "r")
            # templatefile = open("/data/" + str(templatename) + "." + format, "r")
            templatefile = open("/data/" + str(templatename), "r")
            template = templatefile.read()
            return (template, format)
        except Exception as e:
            # return Response(
            #     # "Query error: " + str(e.response.json()),
            #     str(e),
            #     status=400,
            # )
            # raise
            pass

    if templatename:
        try:
            templatequery = """
                query templatequery {
                    Templates(
                        name: "%s"
                    ) {
                        name, 
                        template, 
                        format
                    }
                }
            """ % (
                templatename
            )
            templatedata = gqlClient.gqlexec(
                templatequery,
                {
                }
            )
            if templatedata and \
                "data" in templatedata and \
                "Templates" in templatedata["data"] and \
                templatedata["data"]["Templates"] and len(templatedata["data"]["Templates"]) > 0 :
                template = templatedata["data"]["Templates"][0]["template"]
                format = templatedata["data"]["Templates"][0]["format"]
                if not format:
                    format = "mustache"

        except Exception as e:
            # return Response(
            #     # "Query error: " + str(e.response.json()),
            #     str(e),
            #     status=400,
            # )
            raise

    if not template:
        # return Response(
        #     "Unable to read template, please pass a valid template, format is set to " + str(format),
        #     status=400,
        # )
        raise GFSError("Unable to read template, please pass a valid template, format is set to " + str(format))

    return (template, format)

# 
# 
# 
def resolveview(viewname):

    query = None
    template = None
    partials = []

    if viewname:
        try:
            viewquery = """
                query viewquery {
                    Views(
                        name: "%s"
                    ) {
                        name,
                        query {
                            name,
                            query
                        },
                        template {
                            name,
                            template,
                            format
                        }
                    }
                }
            """ % (
                viewname
            )
            querydata = gqlClient.gqlexec(
                viewquery,
                {
                }
            )
            if querydata and \
                "data" in querydata and \
                "Views" in querydata["data"] and \
                querydata["data"]["Views"] and len(querydata["data"]["Views"]) > 0 :
                view = querydata["data"]["Views"][0]
                query = querydata["data"]["Views"][0]["query"]
                template = querydata["data"]["Views"][0]["template"]
                partials = [] # querydata["data"]["Views"][0]["partials"]

        except Exception as e:
            # return Response(
            #     # "Query error: " + str(e.response.json()),
            #     str(e),
            #     status=400,
            # )
            raise

    return (query, template, partials)

# 
# 
# 
def doquery(query, params = {}):

    data = {}
    try:
        data = gqlClient.gqlexec(
            query,
            params
        )
    except Exception as e:
        # return Response(
        #     # "Query error: " + str(e.response.json()),
        #     str(e),
        #     status=400,
        # )
        raise

    if not data:
        data = {}

    # 
    # BIND DNS serial
    # 
    context = data

    import datetime
    from datetime import datetime

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

    # return data
    return context

# 
# 
# 
def dorender(template, format = "mustache", data = {}):

    if format not in ["mustache", "handlebars", "jinja"]:
        # return Response(
        #     "Invalid format, template formats are mustache, handlebars or jinja",
        #     status=400,
        # )
        raise GFSError("Invalid format, template formats are mustache, handlebars or jinja")

    if format == "jinja":
        from jinja2 import Template
        t1 = Template(
            template
        )
        # return Response(
        return t1.render(
            data
        )
        # , 
        #     mimetype='application/text'
        # )

    elif format == "handlebars":
        from pybars import Compiler
        compiler = Compiler()
        template = compiler.compile(template)
        # return Response(
        return template(data)
        # , 
        #     mimetype='application/text'
        # )

    else:

        import pystache
        # return Response(
        return pystache.render(
            template,
            data, 
        )
        # , 
        #     mimetype='application/text'
        # )

        # 
        # This seemed to have issues
        # 
        # I'm cheating here, I believe the handlebars syntax is a derivative of mustache, 
        # which should mean that mustache templates should be renderable by a handlebars renderer.
        # I have too many mustache templates that need handlebars looping to handle Item1,Item2 type
        # of output
        # 
        # from pybars import Compiler
        # compiler = Compiler()
        # template = compiler.compile(template)
        # # return Response(
        # return template(data)
        # # , 
        # #     mimetype='application/text'
        # # )

# 
# 
# 

if __name__ == '__main__':
    # socketio.run(app, host=LISTENERADDR, port=LISTENERPORT)
    # 
    # TODO: I need to fix this
    # RuntimeError: The Werkzeug web server is not designed to run in production. Pass allow_unsafe_werkzeug=True to the run() method to disable this error.
    # 
    socketio.run(
        app, 
        host=str(listen_addr), 
        port=int(listen_port), 
        # allow_unsafe_werkzeug=True
    )
