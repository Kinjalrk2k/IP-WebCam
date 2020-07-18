import requests
import urllib.request
import json
import enum


class Orientation(enum.Enum):
    Landscape = 'landscape'
    Portrait = 'portrait'
    AntiLandscape = 'upsidedown'
    AntiPortrait = 'upsidedown_portrait'


class State(enum.Enum):
    ON = 'on'
    OFF = 'off'


class IPWebcam:
    def __init__(self, ip, port, username='', password=''):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password

        self.base_url = f'http://{self.username}:{self.password}@{self.ip}:{self.port}/'
        # print(self.base_url)
        res = requests.post(self.base_url)

    def getCurrentStatusVal(self):
        sta_url = self.base_url + 'status.json'
        res = requests.get(sta_url)
        self.curr_status_data = res.json()['curvals']
        # print(self.curr_status_data)

    def getAvailStatusVals(self):
        sta_url = self.base_url + 'status.json?show_avail=1'
        res = requests.get(sta_url)
        self.avail_status_data = res.json()['avail']
        # print(self.avail_status_data)

    def getSensorData(self):
        sen_url = self.base_url + 'sensors.json'
        res = requests.get(sen_url)
        self.curr_sensor_data = res.json()
        # print(self.curr_sensor_data)

    def getOrientation(self):
        self.getSensorData()
        data_vals = self.curr_sensor_data['accel']['data']
        Ax = data_vals[-1][1][0]
        Ay = data_vals[-1][1][1]

        if Ay > 5:
            return Orientation.Portrait
        elif Ay < -5:
            return Orientation.AntiPortrait
        elif Ax > 5:
            return Orientation.Landscape
        elif Ax < 5:
            return Orientation.AntiLandscape

    def setOrientation(self, orientation: Orientation):
        if orientation not in Orientation:
            raise AttributeError('Invalid Orientation')

        post_url = self.base_url + 'settings/orientation?set=' + orientation.value
        res = requests.post(post_url)
        if res.status_code != 200:  # not OK
            raise RuntimeError("Couldn't resolve request")

    def autoOrientation(self):
        self.setOrientation(self.getOrientation())

    def Torch(self, state: State):
        if state == State.ON:
            post_url = self.base_url + 'enabletorch'
        elif state == State.OFF:
            post_url = self.base_url + 'disabletorch'
        else:
            raise AttributeError('Invalid State')

        res = requests.post(post_url)
        if res.status_code != 200:  # not OK
            raise RuntimeError("Couldn't resolve request")
    

if __name__ == "__main__":
    ip = '192.168.0.104'
    port = '8080'
    cam = IPWebcam(ip, port)

    cam.Torch(state=State.OFF)
