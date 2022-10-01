
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
            queryfile = open("/data/" + str(queryname) + "." + "graphql", "r")
            query = queryfile.read()
            return query
        except Exception as e:
            # return Response(
            #     # "Query error: " + str(e.response.json()),
            #     str(e),
            #     status=400,
            # )
            raise

    if queryname:
        try:
            queryquery = """
                query queryquery {
                    queries(
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
                "queries" in querydata["data"] and \
                querydata["data"]["queries"] and len(querydata["data"]["queries"]) > 0 :
                query = querydata["data"]["queries"][0]["query"]

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
            templatefile = open("/data/" + str(templatename) + "." + format, "r")
            template = templatefile.read()
            return (template, format)
        except Exception as e:
            # return Response(
            #     # "Query error: " + str(e.response.json()),
            #     str(e),
            #     status=400,
            # )
            raise

    if templatename:
        try:
            templatequery = """
                query templatequery {
                    templates(
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
                "templates" in templatedata["data"] and \
                templatedata["data"]["templates"] and len(templatedata["data"]["templates"]) > 0 :
                template = templatedata["data"]["templates"][0]["template"]
                format = templatedata["data"]["templates"][0]["format"]
                if not format:
                    format = "mustache"

        except Exception as e:
            # return Response(
            #     # "Query error: " + str(e.response.json()),
            #     str(e),
            #     status=400,
            # )
            raise

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
                    views(
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
                        partials {
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
                "views" in querydata["data"] and \
                querydata["data"]["views"] and len(querydata["data"]["views"]) > 0 :
                view = querydata["data"]["views"][0]
                query = querydata["data"]["views"][0]["query"]
                template = querydata["data"]["views"][0]["template"]
                partials = querydata["data"]["views"][0]["partials"]

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

    return data

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
        pass

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
