import requests
import urllib
import json
import enum
import cv2
import numpy as np
from PIL import Image
import time


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
        try:
            res = requests.get(self.base_url).status_code
        except:
            raise RuntimeError("Couldn't resolve request")

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
        self.curr_status_data = res.json()
        # print(self.curr_status_data)

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
            raise RuntimeError("Couldn't resolve connection request")

    def autoOrientation(self):
        self.setOrientation(self.getOrientation())

    def torch(self, state: State):
        if state == State.ON:
            post_url = self.base_url + 'enabletorch'
        elif state == State.OFF:
            post_url = self.base_url + 'disabletorch'
        else:
            raise AttributeError('Invalid State')

        res = requests.post(post_url)
        if res.status_code != 200:  # not OK
            raise RuntimeError("Couldn't resolve request")

    def getBrigthness(self):
        photo_url = self.base_url + 'video'

        vcap = cv2.VideoCapture(photo_url)
        _, image = vcap.read()

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        brithness_val = hsv[..., 2].mean()
        # print(brithness_val)

    def focus(self, state: State):
        if state == State.ON:
            post_url = self.base_url + 'focus'
        elif state == State.OFF:
            post_url = self.base_url + 'nofocus'
        else:
            raise AttributeError('Invalid State')

        res = requests.post(post_url)
        if res.status_code != 200:  # not OK
            raise RuntimeError("Couldn't resolve request")

    def holdFocus(self, hold_duration=2):  # hold_duration in seconds
        self.focus(state=State.ON)
        time.sleep(hold_duration)
        self.focus(state=State.OFF)

    def zoomIn(self):
        self.getAvailStatusVals()
        self.getCurrentStatusVal()

        avail_zoom_data = self.avail_status_data['zoom']
        curr_zoom_data = self.curr_status_data['zoom']
        try:
            curr_zoom_idx = avail_zoom_data.index(curr_zoom_data)
        except ValueError:
            raise AttributeError('Invalid zoom state')

        next_zoom_idx = curr_zoom_idx + 1
        if next_zoom_idx > len(avail_zoom_data) - 1:
            raise ValueError("Already in maximum zoom level")
        post_url = self.base_url + 'ptz?zoom=' + str(next_zoom_idx)

        res = requests.post(post_url)
        if res.status_code != 200:  # not OK
            raise RuntimeError("Couldn't resolve request")

    def zoomOut(self):
        self.getAvailStatusVals()
        self.getCurrentStatusVal()

        avail_zoom_data = self.avail_status_data['zoom']
        curr_zoom_data = self.curr_status_data['zoom']
        try:
            curr_zoom_idx = avail_zoom_data.index(curr_zoom_data)
        except ValueError:
            raise AttributeError('Invalid zoom state')

        next_zoom_idx = curr_zoom_idx - 1
        if next_zoom_idx < 0:
            raise ValueError("Already in minimum zoom level")
        post_url = self.base_url + 'ptz?zoom=' + str(next_zoom_idx)

        res = requests.post(post_url)
        if res.status_code != 200:  # not OK
            raise RuntimeError("Couldn't resolve request")

    
    def zoomSet(self, zoom_value):
        self.getAvailStatusVals()

        avail_zoom_data = self.avail_status_data['zoom']
        if zoom_value not in avail_zoom_data:
            raise AssertionError('Invalid zoom level')
        
        zoom_idx = avail_zoom_data.index(zoom_value)
        post_url = self.base_url + 'ptz?zoom=' + str(zoom_idx)
        if res.status_code != 200:  # not OK
            raise RuntimeError("Couldn't resolve request")

if __name__ == "__main__":
    # help(IPWebcam)

    ip = '192.168.0.104'
    port = '8080'
    cam = IPWebcam(ip, port)
