import os
import requests
import sys
sys.path.append('/usr/src/wifi')
from CoreCommunicator import CoreCommunicator
sys.path.append('/usr/src/shared')
import ConnectionStatus



os.environ["DBUS_SYSTEM_BUS_ADDRESS"] = "unix:path=/run/dbus/system_bus_socket"
import dbus, uuid, sys, NetworkManager as nm, time, json
from dbus.mainloop.glib import DBusGMainLoop
import gobject
'''
NMState={
'0':'STATE_UNKNOWN',#Networking state is unknown. This indicates a daemon error that makes it unable to reasonably assess the state. In such event the applications are expected to assume Internet connectivity might be present and not disable controls that require network access. The graphical shells may hide the network accessibility indicator altogether since no meaningful status indication can be provided.
'10':'STATE_ASLEEP',#Networking is not enabled, the system is being suspended or resumed from suspend.
'20':'STATE_DISCONNECTED',#There is no active network connection. The graphical shell should indicate no network connectivity and the applications should not attempt to access the network.
'30':'STATE_DISCONNECTING',#Network connections are being cleaned up. The applications should tear down their network sessions.
'40':'STATE_CONNECTING',#A network connection is being started The graphical shell should indicate the network is being connected while the applications should still make no attempts to connect the network.
'50':'STATE_CONNECTED_LOCAL',#There is only local IPv4 and/or IPv6 connectivity, but no default route to access the Internet. The graphical shell should indicate no network connectivity.
'60':'STATE_CONNECTED_SITE',#There is only site-wide IPv4 and/or IPv6 connectivity. This means a default route is available, but the Internet connectivity check (see "Connectivity" property) did not succeed. The graphical shell should indicate limited network connectivity.
'70':'STATE_CONNECTED_GLOBAL',#There is global IPv4 and/or IPv6 Internet connectivity This means the Internet connectivity check succeeded, the graphical shell should indicate full network connectivity.
}

NMDeviceState={
'0':'DEVICE_STATE_UNKNOWN',#the device's state is unknown
'10':'DEVICE_STATE_UNMANAGED',#the device is recognized, but not managed by NetworkManager
'20':'DEVICE_STATE_UNAVAILABLE',#the device is managed by NetworkManager, but is not available for use. Reasons may include the wireless switched off, missing firmware, no ethernet carrier, missing supplicant or modem manager, etc.
'30':'DEVICE_STATE_DISCONNECTED',#the device can be activated, but is currently idle and not connected to a network.
'40':'DEVICE_STATE_PREPARE',#the device is preparing the connection to the network. This may include operations like changing the MAC address, setting physical link properties, and anything else required to connect to the requested network.
'50':'DEVICE_STATE_CONFIG',#the device is connecting to the requested network. This may include operations like associating with the Wi-Fi AP, dialing the modem, connecting to the remote Bluetooth device, etc.
'60':'DEVICE_STATE_NEED_AUTH',#the device requires more information to continue connecting to the requested network. This includes secrets like WiFi passphrases, login passwords, PIN codes, etc.
'70':'DEVICE_STATE_IP_CONFIG',#the device is requesting IPv4 and/or IPv6 addresses and routing information from the network.
'80':'DEVICE_STATE_IP_CHECK',#the device is checking whether further action is required for the requested network connection. This may include checking whether only local network access is available, whether a captive portal is blocking access to the Internet, etc.
'90':'DEVICE_STATE_SECONDARIES',#the device is waiting for a secondary connection (like a VPN) which must activated before the device can be activated
'100':'DEVICE_STATE_ACTIVATED',#the device has a network connection, either local or global.
'110':'DEVICE_STATE_DEACTIVATING',#a disconnection from the current network connection was requested, and the device is cleaning up resources used for that connection. The network connection may still be valid.
'120':'DEVICE_STATE_FAILED',#the device failed to connect to the requested network and is cleaning up the connection request
}

NMActiveConnectionState={
'0':'ACTIVE_CONNECTION_STATE_UNKNOWN',#the state of the connection is unknown
'1':'ACTIVE_CONNECTION_STATE_ACTIVATING',#a network connection is being prepared
'2':'ACTIVE_CONNECTION_STATE_ACTIVATED',#there is a connection to the network
'3':'ACTIVE_CONNECTION_STATE_DEACTIVATING',#the network connection is being torn down and cleaned up
'4':'ACTIVE_CONNECTION_STATE_DEACTIVATED',#the network connection is disconnected and will be removed
}


def signal_handler(*args, **kwargs):
    #for i, arg in enumerate(args):
    #    print("arg:%d        %s" % (i, str(arg)))
    #    print(type(arg))
    #print('kwargs:')
    #print(kwargs)
    if len(args) <= 1:
        return
    if not isinstance(args[1],dbus.Dictionary):
        return
    #else:
    #print(args[0])
    if 'State' in args[1] and str(args[0]) == "org.freedesktop.NetworkManager":
        s=str(args[1]['State'])
        print('State', NMState[s] if s in NMState else s)
        print(args[1]['PrimaryConnection'] if 'PrimaryConnection' in args[1] else args[0])
    if 'State' in args[1] and str(args[0]) == "org.freedesktop.NetworkManager.Connection.Active":
        s=str(args[1]['State'])
        print('State', NMActiveConnectionState[s] if s in NMActiveConnectionState else s, args[0])
    #if 'State' in args[1] and str(args[0]) == "org.freedesktop.NetworkManager.Device":
    #    s=str(args[1]['State'])
    #    print('State', NMDeviceState[s] if s in NMDeviceState else s, args[0])
    #else:
    #    return#print(args[0])
    #if 'StateReason' in args[1]:
    #    print('StateReason',args[1]['StateReason'])
    #if 'PrimaryConnection' in args[1]:
    #    print('Primary',args[1]['PrimaryConnection'])
    #    print(args[0])
'''
dbus_loop=DBusGMainLoop(set_as_default=True)
dbus.mainloop.glib.threads_init()

dbus.set_default_main_loop(dbus_loop)

WIRELESS = "802-11-wireless"
WIRELESS_SECURITY = "802-11-wireless-security"

bus =dbus.SystemBus()
'''
#register your signal callback
bus.add_signal_receiver(signal_handler,
                        bus_name='org.freedesktop.NetworkManager')#,
                        #interface_keyword='interface',
                        #member_keyword='member',
                        #path_keyword='path',
                        #message_keyword='msg')
#proxy =bus.get_object("org.freedesktop.NetworkManager","/org/freedesktop/NetworkManager")
#nm.NetworkManager.interface=dbus.Interface(proxy,"org.freedesktop.NetworkManager")
loop=GLib.MainLoop()
loop.run()
'''
class ConnectionManager:
    def __init__(self, debug=False):
        self.debug = debug
        self._device = self._get_device()

        self.core_communicator = CoreCommunicator()

        # this uuid is used for the hotspot profile
        self._hotspot_uuid = "cf88afd3-f429-4647-8c87-0b0175251237"
        self._hotspot_connection = self.find_connection_from_uuid(self._hotspot_uuid)

        # this uuid is used for the client wifi profile (only one is allowed)
        self._client_uuid = "72804d5a-82ce-4d96-a514-2ce7b68a378d"
        self._client_connection = self.find_connection_from_uuid(self._client_uuid)
        if self._client_connection is None:
            self.generate_base_client_profile()

            # double check
            self._client_connection = self.find_connection_from_uuid(self._client_uuid)
            assert self._client_connection is not None
        self._client_connection_settings = self._client_connection.GetSettings()

    # client mode specific

    def connect_client(self, params):
        print("Attempting to connect to client network")
        ssid = params.get("ssid")
        password = params.get("password")

        # make changes if necessary
        if ssid is not None:
            print("New SSID provided: {}".format(ssid))
            self.update_client_ssid(ssid)
        if password is not None:
            print("New password provided")
            self.update_client_password(password)
        if ssid is not None or password is not None:
            print("Saving connection")
            self.save_client_connection()

        # nm.NetworkManager.ActivateConnection(self._client_connection, self._device, "/")
        print("Activating connection")
        self.core_communicator.start_client_wifi_board(ssid)
        self.start_connection(self._client_connection)

    def update_client_ssid(self, new_ssid):
        self._client_connection_settings[WIRELESS]["ssid"] = new_ssid

    def update_client_password(self, new_password):
        if new_password is None or len(new_password) == 0:
            if self._client_connection_settings.get(WIRELESS_SECURITY, None) is not None:
                # Delete the security settings since the network is not protected
                del self._client_connection_settings[WIRELESS_SECURITY]
            else:
                # There is no security setting to remove, which means that the last network us not protected
                pass
        else:
            self._client_connection_settings[WIRELESS_SECURITY] = {}
            self._client_connection_settings[WIRELESS_SECURITY]['key-mgmt'] = "wpa-psk"
            self._client_connection_settings[WIRELESS_SECURITY]["auth-alg"] = "open"
            self._client_connection_settings[WIRELESS_SECURITY]["psk"] = new_password


    def save_client_connection(self):
        self._client_connection.Update(self._client_connection_settings)

    def generate_base_client_profile(self):
        # connection object
        con = {
            "type": "802-11-wireless",
            "uuid": self._client_uuid,
            "id": "client_connection",
            "autoconnect": False,
            "autoconnect-priority": 0  # must be LOWER than hotspot priority (1)
        }
        wifi = {
            "ssid": "blank_ssid",
            "mode": "infrastructure",
            "hidden": True
        }
        security = {
            "key-mgmt": "wpa-psk",
            "auth-alg": "open",
            "psk": "blank_password"
        }
        ip4 = {
            "method": "auto"
        }
        ip6 = {
            "method": "auto"
        }
        connection = {
            "connection": con,
            "802-11-wireless": wifi,
            "802-11-wireless-security": security,
            "ipv4": ip4,
            "ipv6": ip6
        }
        # dev = self._device
        nm.Settings.AddConnection(connection)

    # end client-mode specific

    # hotspot specific

    # TODO fixup so it works, could be useful if we encounter problems
    def create_hotspot(self, ssid, password):
        conn_info = {
            "type": "802-11-wireless",
            "uuid": str(uuid.uuid4()),
            "id": "Lederbord Hotspot"
        }

        wifi = {
            "ssid": ssid,
            "mode": "ap",
            "band": "bg",
            "channel": 1
        }

        wifi_security = {
            "key-mgmt": "wpa-psk",
            "psk": password
        }

        ipv4 = {
            "method": "shared",
            "address1": ["10.0.0.5", "24", "10.0.0.5"]
        }
        ipv6 = {"method": "ignore"}

        con = {
            "connection": conn_info,
            "802-11-wireless": wifi,
            "802-11-wireless-security": wifi_security,
            "ipv4": ipv4,
            "ipv6": ipv6
        }

        # create connection
        hotspot_connection = nm.Settings.AddConnection(con)
        return hotspot_connection

    def start_hotspot(self):
        conn_profile = self.find_connection_from_uuid(self._hotspot_uuid)
        if (conn_profile == None):
            return
        self.start_connection(conn_profile)

    # end hotspot specific

    # general connection
    def find_connection_from_uuid(self, uuid):
        for connection in nm.Settings.ListConnections():
            config = connection.GetSettings()
            if config["connection"]["uuid"] == uuid:
                return connection

    def start_connection(self, connection):
        active_connection = nm.NetworkManager.ActivateConnection(connection, self._device, "/")

        # check connection
        settled = False
        start = time.time()
        while (time.time() < start + 30) and not settled:
            try:
                if self._device.ActiveConnection.State == nm.NM_ACTIVE_CONNECTION_STATE_ACTIVATED:
                    # TODO log this somehow? Maybe the phone could get it and send it to us?
                    # print("Connection running with SSID: {} and Password: {}".format(ssid, password))
                    self.core_communicator.set_client_wifi_status(ConnectionStatus.CONNECTED)
                    settled = True
            except:
                pass
            time.sleep(1)

        if not settled:
            print("Failed to start connection")
            self.core_communicator.set_client_wifi_status(ConnectionStatus.FAILED)

    def _get_device(self):
        devices = nm.NetworkManager.GetDevices()
        print(devices)
        for device in devices:
            if (device.DeviceType == nm.NM_DEVICE_TYPE_WIFI):
                if self.debug:
                    print(device.Interface)
                return device

    # end general connection

if __name__ == '__main__':
    connManager = ConnectionManager(debug=True)
