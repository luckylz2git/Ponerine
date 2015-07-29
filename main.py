import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
# Camera Object[camera.py]
from camera import Camera
# import base64, functools, hashlib, json, os, platform, re, select, socket, subprocess, sys, tempfile, threading, time, tkFileDialog, tkMessageBox, urllib2, webbrowser, zlib
import json, os, threading, time
from os.path import basename

__version__='0.0.2'

class ConnectScreen(Screen):
  #config in ponerine.kv
  pass

class ControlScreen(Screen):
  #config in ponerine.kv
  pass

class SettingScreen(Screen):
  #config in ponerine.kv
  pass

class Ponerine(ScreenManager):
  if os.name == "nt":
    Window.size = (560,800)
  
  def Connect(self):
    self.cam = []
    if self.current_screen.ids.txtCam1.text <> "":
      self.cam.append(Camera(self.current_screen.ids.txtCam1.text))
    if self.current_screen.ids.txtCam2.text <> "":
      self.cam.append(Camera(self.current_screen.ids.txtCam2.text))
    print "Connect", len(self.cam)
    self.tconn= threading.Thread(target=self.DoConnect)
    self.tconn.setName('DoConnect')
    self.tconn.start()
    
  def Disconnect(self):
    self.tconn= threading.Thread(target=self.DoDisconnect)
    self.tconn.setName('DoDisconnect')
    self.tconn.start()
    
  def Control(self):
    self.current = "control"
    
  def Setting(self):
    self.current = "setting"

  def Photo(self):
    self.tphoto= threading.Thread(target=self.DoPhoto)
    self.tphoto.setName('DoPhoto')
    self.tphoto.start()
    self.tctrl= threading.Thread(target=self.DoControl)
    self.tctrl.setName('DoControl')
    self.tctrl.start()
    
  def Record(self):
    if self.current_screen.ids.btnRecord.text == "Start Record":
      self.tstart= threading.Thread(target=self.DoStartRecord)
      self.tstart.setName('DoStartRecord')
      self.tstart.start()
      self.tctrl= threading.Thread(target=self.DoControl)
      self.tctrl.setName('DoControl')
      self.tctrl.start()
    elif self.current_screen.ids.btnRecord.text == "Stop Record":
      self.tstop= threading.Thread(target=self.DoStopRecord)
      self.tstop.setName('DoStopRecord')
      self.tstop.start()
      
  def ReadSetting(self):
    for cam in self.cam:
      cam.SendMsg('{"msg_id":3}')
    self.tread= threading.Thread(target=self.DoSetting)
    self.tread.setName('DoSetting')
    self.tread.start()

  def DoConnect(self):
    i = 0
    print "DoConnect", len(self.cam)
    #self.current_screen.ids.btnConnect.state = "down"
    self.current_screen.ids.btnConnect.text = "Connecting"
    for cam in self.cam:
      cam.LinkCamera()
      while cam.token == 0:
        i = i % 3 + 1
        time.sleep(0.5)
        self.current_screen.ids.btnConnect.text = "Connecting %s" %("." * i)
    #save camera ip to camera.cfg
    i = 0
    cfg = {}
    ip = []
    for cam in self.cam:
      i += 1
      ip.append(json.loads('{"camera":%d,"ip":"%s"}'%(i,cam.ip)))
    cfg["camera_ip"] = ip
    print cfg
    self.savecfg(cfg)

    #self.current_screen.ids.btnConnect.state = "normal"
    #self.current_screen.ids.btnConnect.text = "Connecting"
    self.current = "control"
    #print "tctrl start"
  
  def DoDisconnect(self):
    try:
      if self.tctrl.isAlive():
        print "stop tctrl"
        self.tctrl._Thread__stop()
    except:
      pass
    try:
      for cam in self.cam:
        cam.UnlinkCamera()
    except:
      pass
    self.current = "connect"
    self.current_screen.ids.btnConnect.text = "Connect"
  
  def DoPhoto(self):
    i = 0
    #self.current_screen.ids.btnPhoto.state = "down"
    self.current_screen.ids.btnPhoto.text = "Taking Photo"
    for cam in self.cam:
      cam.TakePhoto()
    for cam in self.cam:
      while cam.cambusy:
        i = i % 3 + 1
        time.sleep(0.5)
        self.current_screen.ids.btnPhoto.text = "Taking Photo %s" %("." * i)
    #self.current_screen.ids.btnPhoto.state = "normal"
    self.current_screen.ids.btnPhoto.text = "Take Photo"
    
  def DoStartRecord(self):
    i = 0
    #self.current_screen.ids.btnRecord.state = "down"
    self.current_screen.ids.btnRecord.text = "Starting Record"
    for cam in self.cam:
      cam.StartRecord()
    for cam in self.cam:
      while cam.cambusy:
        i = i % 3 + 1
        time.sleep(0.5)
        self.current_screen.ids.btnRecord.text = "Starting Record %s" %("." * i)
    #self.current_screen.ids.btnRecord.state = "normal"
    self.current_screen.ids.btnRecord.text = "Stop Record"
    time.sleep(1)
    recording = True
    while recording:
      time.sleep(0.8)
      rectime = []
      for cam in self.cam:
        recording = recording and cam.recording
        rectime.append(cam.recordtime)
      print "Record Time: ", rectime
      if len(rectime) > 1:
        self.current_screen.ids.lblCam1.text = "CAM 1 [ " + rectime[0] + " ]"
        self.current_screen.ids.lblCam2.text = "CAM 2 [ " + rectime[1] + " ]"
      else:
        self.current_screen.ids.lblCam1.text = "CAM 1 [ " + rectime[0] + " ]"
        self.current_screen.ids.lblCam2.text = "CAM 2 [ --:--:-- ]"
    self.current_screen.ids.lblCam1.text = "CAM 1 [ --:--:-- ]"
    self.current_screen.ids.lblCam2.text = "CAM 2 [ --:--:-- ]"
    
  def DoStopRecord(self):
    i = 0
    self.current_screen.ids.btnRecord.state = "down"
    self.current_screen.ids.btnRecord.text = "Stopping Record"
    for cam in self.cam:
      cam.StopRecord()
    for cam in self.cam:
      while cam.cambusy:
        i = i % 3 + 1
        time.sleep(0.5)
        self.current_screen.ids.btnRecord.text = "Stopping Record %s" %("." * i)
    self.current_screen.ids.btnRecord.state = "normal"
    self.current_screen.ids.btnRecord.text = "Start Record"
  
  def DoWifi(self):
    wifi = True
    while wifi:
      for cam in self.cam:
        wifi = wifi and cam.wifi
    self.current = 'connect'
    self.current_screen.ids.btnConnect.text = "Connect"
  
  def DoControl(self):
    file = ""
    i = 0
    for cam in self.cam:
      i += 1
      while cam.lastjpg == "" and cam.lastmp4 == "":
        pass
      debugtxt = self.get_screen("control").ids.txtDebug.text
      file = cam.lastjpg
      cam.lastjpg = ""
      if file <> "":
        debugtxt += "\nCAM %d : " %i + file
      file = cam.lastmp4
      cam.lastmp4 = ""
      if file <> "":
        debugtxt += "\nCAM %d : " %i + file
    self.get_screen("control").ids.txtDebug.text = debugtxt

  def DoSetting(self):
    debugtxt = self.get_screen("setting").ids.txtDebug.text
    settings = ""
    i = 0
    for cam in self.cam:
      i += 1
      while cam.settings == "":
        pass
      settings = cam.settings
      cam.settings = ""
      debugtxt += "\nCAM %d Settings :\n" %i + settings
    self.get_screen("setting").ids.txtDebug.text = debugtxt

  def savecfg(self, data):
    cfgfile = __file__.replace(basename(__file__), "data/camera.cfg")
    try:
      with open(cfgfile,'w') as file:
        file.write(json.dumps(data, indent=2))
    except StandardError:
      pass
    
class PonerineApp(App):

  def build(self):
    ponerine = Ponerine()
    conn = ConnectScreen(name='connect')
    cfg = self.readcfg()
    conn.ids.txtCam1.text = cfg[0]
    conn.ids.txtCam2.text = cfg[1]
    ponerine.add_widget(conn)
    ponerine.add_widget(ControlScreen(name='control'))
    ponerine.add_widget(SettingScreen(name='setting'))
    ponerine.current = 'connect'
    return ponerine
    
  def on_pause(self):
    return True

  def readcfg(self):
    cfgfile = __file__.replace(basename(__file__), "data/camera.cfg")
    r = []
    try:
      with open(cfgfile) as file:
        cfg = json.loads(file.read())
        #print "readcfg",cfg
      if cfg.has_key("camera_ip"):
        for item in cfg["camera_ip"]:
          r.append(item["ip"])
        #print "r", r
        if len(r) < 2:
          r.append("")
      else:
        r = ["192.168.42.1",""]
    except StandardError:
      r = ["192.168.42.1",""]
    return r

if __name__ == '__main__':
  print Window.size
  PonerineApp().run()
