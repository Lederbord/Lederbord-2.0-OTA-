import requests
import json

CORE_SERVER_ADDRESS = "http://core:80"

class CoreCommunicator:

    def start_client_wifi_board(self, m_ssid):
        self._execute_RPC(method="createClientConnect",
                          params={"ssid": m_ssid})

    def set_client_wifi_status(self, new_status):
        self._execute_RPC(method="setClientConnectStatus",
                          params={"status": new_status.name})
        

    def _execute_RPC(self, method, params):
        headers = {
            "Content-Type": "text/plain"
        }
        data = {
            "method": method,
            "params": params,
            "id": "wifi-container"
        }
        data_str = json.dumps(data)

        print(f"Making request to: {CORE_SERVER_ADDRESS} with data {data_str}")
        resp = requests.post(CORE_SERVER_ADDRESS, headers=headers, data=data_str)
        print("Response: {}".format(resp))


