import httplib
import base64
import ConfigParser
import io
import json

class CouchConnection(httplib.HTTPConnection):
    """docstring for CouchConnection"""
    def __init__(self, host="127.0.0.1", port=5984, username="", password=""):
        httplib.HTTPConnection.__init__(self, host, port)
        self.username = username
        self.password = password

    def request(self, method, path, body="", header={}):
        if self.username != "" and self.password != "":
            creds = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
            header["Authorization"] = "Basic %s" % creds
        httplib.HTTPConnection.request(self, method, path, body, header)

    def get(self, path, header={}):
        self.request("GET", path, "", header)
        return self.getresponse()

    def post(self, path, body=None, header={}):
        self.request("POST", path, body, header)
        return self.getresponse()

    def json_post(self, path, body=None, header={}):
        h = { "Content-Type": "application/json" }
        self.request("POST", path, body, dict(h.items() + header.items()))
        return self.getresponse()

    def put(self, path, body, header={}):
        self.request("PUT", path, body, header)
        return self.getresponse()

    def json_put(self, path, body, header={}):
        h = { "Content-Type": "application/json" }
        self.request("PUT", path, body, dict(h.items() + header.items()))
        return self.getresponse()

    def delete(self, path, body=None, header={}):
        self.request("GET", path)
        res = self.getresponse()
        doc = json.loads(res.read())
        if "_rev" in doc:
            self.request("DELETE", path + "?rev=" + doc["_rev"], body, header)
            res = self.getresponse()
            return res.read()
        else:
            return False

    def temp_view(self, path, body, header={}):
        return self.json_post(path + "/_temp_view", body, header)

    def temp_view_with_params(self, path, params, body, header={}):
        return self.json_post(path + "/_temp_view" + params, body, header)


def arsnova_connection(propertypath):
    f = open(propertypath, "r")
    properties = f.read()
    f.close()

    config = ConfigParser.RawConfigParser()
    config.readfp(io.BytesIO("[arsnova]" + properties))
    host = config.get("arsnova", "couchdb.host")
    port = config.get("arsnova", "couchdb.port")
    db = config.get("arsnova", "couchdb.name")
    username = config.get("arsnova", "couchdb.username")
    password = config.get("arsnova", "couchdb.password")
    return (db, CouchConnection(host, port, username, password))
