#TODO remove this
import time

from connectionManager import ConnectionManager
cm = ConnectionManager()
# cm.connect_client(
#     params={
#         "ssid": "abc12345",
#         "password": "newPassword"
#     }
# )
time.sleep(10)
cm._start_client_wifi_board("testssid")