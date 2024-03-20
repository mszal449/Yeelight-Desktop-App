from yeelight import discover_bulbs, Bulb


# Device controller class used to manage devices
class DeviceController:
    devices = {}

    def __init__(self):
        print('Initializing device controller module.')

    def find_devices(self):
        """Search for devices and update the devices list"""

        print('Searching for devices...')
        result = discover_bulbs()
        self.devices = {}

        # reset _devices table
        for device in result:
            # add device instance to list
            device['instance'] = Bulb(device['ip'])
            self.devices[device['ip']] = device
            print(device)

        return result
