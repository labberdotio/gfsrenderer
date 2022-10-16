
import os
import sys

import logging
logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.DEBUG)

import traceback

import time
from datetime import datetime

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



class GFSLogger():

    @classmethod
    def getLogger(self, name):
        return GFSLogger(name)

    @classmethod
    def getLogLevel(self):
        return None

    def __init__(self, name, **kwargs):
        self._name = name
        self._logger = logging.getLogger(name)

    def enter(self, message):
        start = time.time() # datetime.now()
        # self._logger.debug("ENTER: " + message)
        return start
        # pass

    def exit(self, message, start):
        end = time.time()
        diff = ( end - start ) * 1000
        # addstat(self._name + ": " + message, diff)
        # if diff > 250.0:
        #     self._logger.warning("EXIT: " + message + " AFTER " + str( diff ) + " MS " )
        #     for nme in allcalls:
        #         if alltimes[nme] > 1000.0:
        #             # print(" >> STAT: " + nme + ", calls: " + str(allcalls[nme]) + ", time: " + str(alltimes[nme]))
        #             self._logger.warning(" >> STAT: " + nme + ", calls: " + str(allcalls[nme]) + ", time: " + str(alltimes[nme]))
        # 
        # else:
        self._logger.debug("EXIT: " + message + " AFTER " + str( diff ) + " MS " )
        return diff
        # pass

    def debug(self, *args, **kwargs):
        self._logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        self._logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        self._logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        self._logger.error(*args, **kwargs)

    def critical(self, *args, **kwargs):
        self._logger.critical(*args, **kwargs)

    def exception(self, *args, **kwargs):
        self._logger.exception(*args, **kwargs)

    def log(self, lvl, *args, **kwargs):
        self._logger.log(lvl, *args, **kwargs)

# 
# 
# 

logger = GFSLogger.getLogger("GFSRenderer")

# @app.route('/query', methods=['GET', 'POST'])
@app.route('/query', methods=['GET'])
def query():
    from flask import request
    import simplejson as json
    etime = logger.enter("query")
    try:
        # return 
        ret = Response(
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
        logger.exit("models", etime)
        return ret
    except Exception as e:
        logger.exit("models", etime)
        return Response(
            str(e),
            status=400,
        )

# @app.route('/render', methods=['GET', 'POST'])
@app.route('/render', methods=['GET'])
def render():
    from flask import request
    import simplejson as json
    etime = logger.enter("render")
    try:
        # (templatename, template = None, format = "mustache"):
        (template, format, mime) = resolvetemplate(
            templatename = request.args.get("template"), 
            template = None, 
            format = request.args.get("format", "mustache")
        )
        if not mime:
            mime = 'application/text'
        # return 
        ret = Response(
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
            mimetype=mime # 'application/text'
        )
        logger.exit("render", etime)
        return ret
    except Exception as e:
        logger.exit("render", etime)
        return Response(
            str(e),
            status=400,
        )

@app.route('/view', methods=['GET'])
@app.route('/view/<path:view>', methods=['GET'])
def view(view = None):
    from flask import request
    import simplejson as json
    etime = logger.enter("query")
    if not view:
        view = request.args.get("view")
    try:
        (query, template, format, viewmime) = resolveview(
            viewname = view # request.args.get("view")
        )
        if not viewmime:
            viewmime = 'application/text'
        (template, format, templatemime) = resolvetemplate(
            templatename = template["name"], 
            template = template["template"], 
            format = template["format"], 
            # mime = template["mime"], 
        )
        if not templatemime:
            templatemime = 'application/text'
        # return 
        ret = Response(
            dorender(
                template = template, 
                format = format, 
                data = doquery(
                    query = resolvequery(
                        queryname = query["name"], 
                        query = query["query"]
                    ), 
                    params = request.args.to_dict() # flat=False)
                ), 
            ), 
            mimetype=viewmime # 'application/text'
        )
        logger.exit("view", etime)
        return ret
    except Exception as e:
        logger.exit("view", etime)
        return Response(
            str(e),
            status=400,
        )

# 
# 
# 
def resolvequery(queryname, query = None):
    etime = logger.enter("resolvequery")

    if not queryname and not query:
        # return Response(
        #     "Unable to read query, please pass a valid query",
        #     status=400,
        # )
        raise GFSError("Unable to read query, please pass a valid query")

    if query:
        return query

    # File
    if queryname:
        try:
            # queryfile = open("/data/queries/" + str(queryname) + "." + "graphql", "r")
            # queryfile = open("/data/" + str(queryname) + "." + "graphql", "r")
            queryfile = open("/data/" + str(queryname), "r")
            query = queryfile.read()
            logger.exit("resolvequery", etime)
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

    logger.exit("resolvequery", etime)
    return query

# 
# 
# 
def resolvetemplate(templatename, template = None, format = "mustache", mime = 'application/text'):
    etime = logger.enter("resolvetemplate")

    if not templatename and not template:
        # return Response(
        #     "Unable to read template, please pass a valid template, format is set to " + str(format),
        #     status=400,
        # )
        raise GFSError("Unable to read template, please pass a valid template, format is set to " + str(format))

    if template and format:
       return (template, format, mime) 

    # File
    if templatename:
        try:
            # templatefile = open("/data/templates/" + str(templatename) + "." + format, "r")
            # templatefile = open("/data/" + str(templatename) + "." + format, "r")
            templatefile = open("/data/" + str(templatename), "r")
            template = templatefile.read()
            logger.exit("resolvetemplate", etime)
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
                        format, 
                        mime
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
                mime = templatedata["data"]["Templates"][0]["mime"] 
                if not format:
                    format = "mustache"
                if not mime:
                    mime = 'application/text'
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

    logger.exit("resolvetemplate", etime)
    return (template, format, mime)

# 
# 
# 
def resolveview(viewname):
    etime = logger.enter("resolveview")

    query = None
    template = None
    partials = []
    mime = 'application/text'

    if viewname:
        try:
            viewquery = """
                query viewquery {
                    Views(
                        name: "%s"
                    ) {
                        name,
                        mime,
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
                mime = querydata["data"]["Views"][0]["mime"]
                query = querydata["data"]["Views"][0]["query"]
                template = querydata["data"]["Views"][0]["template"]
                partials = [] # querydata["data"]["Views"][0]["partials"]

            if not mime:
                mime = 'application/text'

        except Exception as e:
            # return Response(
            #     # "Query error: " + str(e.response.json()),
            #     str(e),
            #     status=400,
            # )
            raise

    logger.exit("resolveview", etime)
    return (query, template, partials, mime)

# 
# 
# 
def doquery(query, params = {}):
    etime = logger.enter("doquery")

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

    logger.exit("doquery", etime)
    # return data
    return context

# 
# 
# 
def dorender(template, format = "mustache", data = {}):
    etime = logger.enter("dorender")

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
        # return 
        ret = t1.render(
            data
        )
        # , 
        #     mimetype='application/text'
        # )

        logger.exit("dorender", etime)
        return ret

    elif format == "handlebars":
        from pybars import Compiler
        compiler = Compiler()
        template = compiler.compile(template)
        # return Response(
        # return 
        ret = template(data)
        # , 
        #     mimetype='application/text'
        # )

        logger.exit("dorender", etime)
        return ret

    else:

        import pystache
        # return Response(
        # return 
        ret = pystache.render(
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

        logger.exit("dorender", etime)
        return ret

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
