
import logging

# logging.basicConfig(level=logging.WARNING)
# logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.DEBUG)

from python_graphql_client import GraphqlClient



# 
# GFS GraphQL client error class
# 
class GFSGQLError(Exception):

    def __init__(self, error):
        pass



# 
# GFS GraphQL client
# 
class GFSGQL():

    logger = logging.getLogger("GFSGQL")

    def __init__(
        self,

        gfs_host,
        gfs_port,
        gfs_username,
        gfs_password,

        **kwargs):

        self.gfs_host = gfs_host
        self.gfs_port = gfs_port
        self.gfs_username = gfs_username
        self.gfs_password = gfs_password

        self.api_namespace = "gfs1"

        self.gfs_gqlurl = "http://" + self.gfs_host + ":" + self.gfs_port + "/" + self.api_namespace + "/" + "graphql"

        self.gfs_gqlclient = GraphqlClient(
            endpoint=self.gfs_gqlurl
        )

    def gqlencodedict(self, data = {}):
        _list = []
        for key in data:
            val = data.get(key)
            _list.append(key + ":" + str(self.gqlencode(val)))
        return "{" + ", ".join(_list) + "}"

    def gqlencodelist(self, data = []):
        _list = []
        for val in data:
            _list.append(str(self.gqlencode(val)))
        return "[" + ", ".join(_list) + "]"

    def gqlencode(self, data):
        if isinstance(data, list):
            return self.gqlencodelist(data)
        elif isinstance(data, dict):
            return self.gqlencodedict(data)
        elif isinstance(data, int):
            return str(data)
        else:
            # return "\"" + str(data) + "\""
            return str(data)

    def gqlargs(self, match = {}):
        return str(self.gqlencode({
            "$" + key: value for key, value in match.items()
        }))[1:-1]

    def gqlvars(self, match = {}):
        return str(self.gqlencode({
            key: "$" + key for key, value in match.items()
        }))[1:-1]

    def gqldata(self, data = {}):
        return str(self.gqlencode(data))[1:-1]

    def gqlfields(self, fields = {}):
        # return str(self.gqlencode(fields))[1:-1]
        # return ", ".join(fields)

        ret = ""
        if isinstance(fields, list):
            for val in fields:
                # val = fields.get(key)
                if isinstance(val, dict):
                    ret += val + " {" + self.gqlfields(val) + "}" + ", "
                elif val:
                    ret += val + ", "

        elif isinstance(fields, dict):
            for key in fields:
                val = fields.get(key)
                if isinstance(val, dict):
                    ret += key + " {" + self.gqlfields(val) + "}" + ", "
                elif val:
                    ret += key + ", "

        else:
            pass

        return ret

    #
    #
    #

    def gqlexec(self, query, variables = {}):

        self.logger.debug("Running GQL query: ")
        self.logger.debug(query)
        self.logger.debug("with variables: ")
        self.logger.debug(variables)

        data = {}
        try:
            # Synchronous request
            data = self.gfs_gqlclient.execute(
                query=query, 
                variables=variables
            )

        except Exception as e:
            raise GFSGQLError("GQL GraphQL error " + str(
                e.response.json())
            )

        self.logger.debug("GQL query result")
        self.logger.debug(data)

        if data and "errors" in data:
            raise GFSGQLError("GQL GraphQL error " + str(
                data)
            )

        return data

    def gqlquery(self, resource, arguments = {}, variables = {}, fields = {}):

        self.logger.debug("")
        self.logger.debug("GQL query of resource: " + resource)
        self.logger.debug("arguments: " + str(arguments))
        self.logger.debug("variables: " + str(variables))
        self.logger.debug("fields: " + str(fields))

        query = """
            query %s {
                %s {
                    %s
                }
            }
        """ % (
            "%ss" % (resource),
            "%ss" % (resource),
            self.gqlfields(fields)
        )

        if arguments:
            query = """
                query %s(%s) {
                    %s(%s) {
                        %s
                    }
                }
            """ % (
                "%ss" % (resource),
                self.gqlargs(arguments),
                "%ss" % (resource),
                self.gqlvars(variables),
                self.gqlfields(fields)
            )

        self.logger.debug("Running GQL query: ")
        self.logger.debug(query)
        self.logger.debug("with variables: ")
        self.logger.debug(variables)

        data = {}
        try:
            # Synchronous request
            data = self.gfs_gqlclient.execute(
                query=query, 
                variables=variables
            )

        except Exception as e:
            raise GFSGQLError("GQL GraphQL error " + str(
                e.response.json())
            )

        self.logger.debug("GQL query result")
        self.logger.debug(data)

        if data and "errors" in data:
            raise GFSGQLError("GQL GraphQL error " + str(
                data)
            )

        return data.get(
            "data", {}
        ).get(
            "%ss" % (resource), []
        )

    def gqlget(self, resource, arguments = {}, variables = {}, fields = {}):

        self.logger.debug("")
        self.logger.debug("GQL get of resource: " + resource)
        self.logger.debug("arguments: " + str(arguments))
        self.logger.debug("variables: " + str(variables))
        self.logger.debug("fields: " + str(fields))

        query = """
            query %s(%s) {
                %s(%s) {
                    %s
                }
            }
        """ % (
            resource,
            self.gqlargs(arguments),
            resource,
            self.gqlvars(variables),
            self.gqlfields(fields)
        )

        self.logger.debug("Running GQL query: ")
        self.logger.debug(query)
        self.logger.debug("with variables: ")
        self.logger.debug(variables)

        data = {}
        try:
            # Synchronous request
            data = self.gfs_gqlclient.execute(
                query=query, 
                variables=variables
            )

        except Exception as e:
            raise GFSGQLError("GQL GraphQL error " + str(
                e.response.json())
            )

        self.logger.debug("GQL query result")
        self.logger.debug(data)

        if data and "errors" in data:
            raise GFSGQLError("GQL GraphQL error " + str(
                data)
            )

        return data.get(
            "data", {}
        ).get(
            resource, []
        )

    def gqlcreate(self, resource, arguments = {}, variables = {}, fields = {}):

        self.logger.debug("")
        self.logger.debug("GQL create of resource: " + resource)
        self.logger.debug("arguments: " + str(arguments))
        self.logger.debug("variables:")
        self.logger.debug(variables)
        self.logger.debug("fields: " + str(fields))

        resource = resource.replace(":", "").replace("@", "").replace("-", "")

        query="""
            mutation %s(%s) {
                %s(%s) {
                    instance {
                        %s
                    },
                    ok,
                    error
                }
            }
        """ % (
            "create%s" % ((resource[0].upper() + resource[1:])),
            self.gqlargs(arguments),
            "create%s" % ((resource[0].upper() + resource[1:])),
            self.gqlvars(variables),
            self.gqlfields(fields)
        )

        self.logger.debug("Running GQL mutation: ")
        self.logger.debug(query)
        self.logger.debug("with variables: ")
        self.logger.debug(variables)

        data = {}
        try:
            # Synchronous request
            data = self.gfs_gqlclient.execute(
                query=query, 
                variables=variables
            )

        except Exception as e:
            raise GFSGQLError("GQL GraphQL error " + str(
                e.response.json())
            )

        self.logger.debug("GQL mutation result")
        self.logger.debug(data)

        if data and "errors" in data:
            raise GFSGQLError("GQL GraphQL error " + str(
                data)
            )

        if data and "error" in data.get("data", {}).get("create%s" % ((resource[0].upper() + resource[1:])), {}):
            if data.get("data", {}).get("create%s" % ((resource[0].upper() + resource[1:])), {}).get("error", None):
                raise GFSGQLError("GQL GraphQL error " + str(
                    data.get("data", {}).get("create%s" % ((resource[0].upper() + resource[1:])), {}).get("error", None))
                )

        return data.get(
            "data", {}
        ).get(
            "create%s" % ((resource[0].upper() + resource[1:])), {}
        )
        # .get(
        #     "instance", {}
        # )

    def gqlupdate(self, resource, arguments = {}, variables = {}, fields = {}):

        self.logger.debug("")
        self.logger.debug("GQL update of resource: " + resource)
        self.logger.debug("arguments: " + str(arguments))
        self.logger.debug("variables:")
        self.logger.debug(variables)
        self.logger.debug("fields: " + str(fields))

        query="""
            mutation %s(%s) {
                %s(%s) {
                    instance {
                        %s
                    },
                    ok
                }
            }
        """ % (
            "update%s" % ((resource[0].upper() + resource[1:])),
            self.gqlargs(arguments),
            "update%s" % ((resource[0].upper() + resource[1:])),
            self.gqlvars(variables),
            self.gqlfields(fields)
        )

        self.logger.debug("Running GQL mutation: ")
        self.logger.debug(query)
        self.logger.debug("with variables: ")
        self.logger.debug(variables)

        data = {}
        try:
            # Synchronous request
            data = self.gfs_gqlclient.execute(
                query=query, 
                variables=variables
            )

        except Exception as e:
            raise GFSGQLError("GQL GraphQL error " + str(
                e.response.json())
            )

        self.logger.debug("GQL mutation result")
        self.logger.debug(data)

        if data and "errors" in data:
            raise GFSGQLError("GQL GraphQL error " + str(
                data)
            )

        if data and "error" in data.get("data", {}).get("update%s" % ((resource[0].upper() + resource[1:])), {}):
            if data.get("data", {}).get("update%s" % ((resource[0].upper() + resource[1:])), {}).get("error", None):
                raise GFSGQLError("GQL GraphQL error " + str(
                    data.get("data", {}).get("update%s" % ((resource[0].upper() + resource[1:])), {}).get("error", None))
                )

        return data.get(
            "data", {}
        ).get(
            "update%s" % ((resource[0].upper() + resource[1:])), {}
        )
        # .get(
        #     "instance", {}
        # )

    def gqldelete(self, resource, arguments = {}, variables = {}):

        self.logger.debug("")
        self.logger.debug("GQL delete of resource: " + resource)
        self.logger.debug("arguments: " + str(arguments))
        self.logger.debug("variables: " + str(variables))

        query="""
            mutation %s(%s) {
                %s(%s) {
                    ok
                }
            }
        """ % (
            "delete%s" % ((resource[0].upper() + resource[1:])),
            self.gqlargs(arguments),
            "delete%s" % ((resource[0].upper() + resource[1:])),
            self.gqlvars(variables)
        )

        self.logger.debug("Running GQL mutation: ")
        self.logger.debug(query)
        self.logger.debug("with variables: ")
        self.logger.debug(variables)

        data = {}
        try:
            # Synchronous request
            data = self.gfs_gqlclient.execute(
                query=query, 
                variables=variables
            )

        except Exception as e:
            raise GFSGQLError("GQL GraphQL error " + str(
                e.response.json())
            )

        self.logger.debug("GQL mutation result")
        self.logger.debug(data)

        if data and "errors" in data:
            raise GFSGQLError("GQL GraphQL error " + str(
                data)
            )

        if data and "error" in data.get("data", {}).get("delete%s" % ((resource[0].upper() + resource[1:])), {}):
            if data.get("data", {}).get("delete%s" % ((resource[0].upper() + resource[1:])), {}).get("error", None):
                raise GFSGQLError("GQL GraphQL error " + str(
                    data.get("data", {}).get("delete%s" % ((resource[0].upper() + resource[1:])), {}).get("error", None))
                )

        return data.get(
            "data", {}
        ).get(
            "delete%s" % ((resource[0].upper() + resource[1:])), {}
        )

    #
    #
    #

    def exec(self, query, variables = {}):
        return self.gqlexec(query, variables)

    def query(self, resource, arguments = {}, variables = {}, fields = {}):
        return self.gqlquery(resource, arguments, variables, fields)

    def get(self, resource, arguments = {}, variables = {}, fields = {}):
        return self.gqlget(resource, arguments, variables, fields)

    def create(self, resource, arguments = {}, variables = {}, fields = {}):
        return self.gqlcreate(resource, arguments, variables, fields)

    def update(self, resource, arguments = {}, variables = {}, fields = {}):
        return self.gqlupdate(resource, arguments, variables, fields)

    def delete(self, resource, arguments = {}, variables = {}):
        return self.gqldelete(resource, arguments, variables)


# 
# Main
# 
# if __name__ == '__main__':
# 
#     gfs_host = "localhost"
#     gfs_port = "5000"
#     gfs_username = None
#     gfs_password = None
# 
#     gqlClient = GFSGQL(
#         gfs_host = gfs_host,
#         gfs_port = gfs_port,
#         gfs_username = gfs_username,
#         gfs_password = gfs_password,
#     )
# 
#     gqlClient.gqlexec(
#         """
#             mutation updateIp($id:String!, $name:String, $address:String, ) {
#                 updateIp(id:$id, name:$name, address:$address, ) {
#                     instance {
#                         id, name, address,
#                     },
#                     ok
#                 }
#             }
#         """,
#         {
#             "id": "5202",
#             "name": "myname",
#             "address": "myaddress"
#         }
#     )
# 
