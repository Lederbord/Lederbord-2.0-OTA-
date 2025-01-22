from flask import Flask, request
import sys

sys.path.append('wifi/')

from connectionManager import *

class ConnectionManagerServer(object):

    def __init__(self):
        super().__init__()
        self.app = self.create_app()
        self.connMgr = ConnectionManager()

    def create_app(self):
        app = Flask(__name__)

        @app.route('/', methods=['GET', 'POST'])
        def index():
            data = ''
            if request.method == 'GET':
                data = request.args.get('r', '')
            elif request.method == 'POST':
                if 'r' in request.form:
                    data = request.form['r']
                    print(data)
                else:
                    data = request.data

            # Convert bytes to string if appropriate
            try:
                data = data.decode('utf-8')
            except AttributeError:
                pass

            # Convert data to the json format
            try:
                req = json.loads(data)
            except ValueError:
                return '{"Error":"Could not decode request json"}'

            # Get data from the request
            try:
                method = req['method']
                params = req['params']
                uid = req['id']
            except KeyError:
                return '{"Error":"Missing required entries in request json"}'

            # Call the method
            try:
                # Call the class/obj method is there is a '.'
                if '.' in method:
                    obj = self
                    while '.' in method:
                        # print(method)
                        # print(obj, obj.__dict__)
                        comps = method.split('.')
                        # print(comps[0])
                        obj = getattr(obj, comps[0])
                        method = '.'.join(comps[1:])
                    # print('END OF WHILE', obj, obj.__dict__)
                    resp = getattr(obj, method)(params)
                else:  # Call the local method
                    resp = getattr(self, method)(params)
            except KeyError:
                return '{"Error":"Could not find the requested method"}'

            # ret = {"id": uid, "response": resp}
            return '{"id":"%s", "response":%s}' % (uid, resp)

        return app

    def start_server(self):
        self.app.run(host='0.0.0.0', port=80, debug=False, ssl_context=('/usr/src/app/secrets/lederbord_local.cer', '/usr/src/app/secrets/lederbord_local.key'))

    def checkParams(self, params):
        if type(params) == dict:
            return params
        if type(params) == str:
            return json.loads(params)
        else:
            return None

    def connectClient(self, dataStr=None):
        params = self.checkParams(dataStr)
        self.connMgr.connect_client(params)


if __name__ == "__main__":
    server = ConnectionManagerServer()
    server.start_server()