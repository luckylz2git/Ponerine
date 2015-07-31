import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
# Camera Object[camera.py]
from camera import Camera
# import base64, functools, hashlib, json, os, platform, re, select, socket, subprocess, sys, tempfile, threading, time, tkFileDialog, tkMessageBox, urllib2, webbrowser, zlib
import json, os, threading, time, socket
from os.path import basename

__version__='0.0.5'

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
  def __init__(self, exit):  
      super(Ponerine, self).__init__()  
      self.exit = exit
  
  if os.name == "nt":
    Window.size = (560,800)
  
  def DetectCam(self):
    print "Start DetectCam", len(self.iplists), self.iplists
    self.first = threading.Event()
    if len(self.iplists) > 1:
      for i in range(0, len(self.iplists) - 1):
        print i
        threading.Thread(target=self.DoDetectCam, args = (i,), name="DoDetectCam" + str(i)).start()
    else:
      threading.Thread(target=self.DoDetectCam, args = (0,), name="DoDetectCam0").start()
    
  def Connect(self):
    self.first.set()
    if self.current_screen.ids.btnConnect.text == "" or self.current_screen.ids.btnConnect.text == "Error":
      self.cam = []
      print "ip list" ,len(self.iplists), self.iplists
      if len(self.iplists) > 0:
        for ip in self.iplists:
          print "ip list %s" %ip
          self.cam.append(Camera(ip))
        print "Connect", len(self.cam)
        self.tconn= threading.Thread(target=self.DoConnect)
        self.tconn.setName('DoConnect')
        self.tconn.start()
      else:
        self.current_screen.ids.btnConnect.text = "Error"
    
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
    
  def DoDetectCam(self, index):
    time.sleep(5)
    print "start DoDetectCam %d" %index
    socket.setdefaulttimeout(3)
    while not self.first.isSet() and not self.exit.isSet():
      retry = 0
      if len(self.iplists) > index:
        retry += 1
        index = index % 2
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        open = srv.connect_ex((self.iplists[index], 7878))
        print "DoDetectCam Cam %d %d %d" %(index,open,retry)
        if open == 0:
          if index == 0:
            self.current_screen.ids.btnCam1.background_normal = 'image/camera_green.png'
          else:
            self.current_screen.ids.btnCam2.background_normal = 'image/camera_green.png'
          srv.close()
          break
        elif retry >= 1:
          if index == 0:
            self.current_screen.ids.btnCam1.background_normal = 'image/camera_red.png'
          else:
            self.current_screen.ids.btnCam2.background_normal = 'image/camera_red.png'
        srv.close()
      
  def DoConnect(self):
    i = 0
    stop = False
    print "DoConnect", len(self.cam)
    self.current_screen.ids.btnConnect.state = "down"
    self.current_screen.ids.btnConnect.text = ""
    for cam in self.cam:
      quit = cam.quit
      cam.LinkCamera()
      while cam.token == 0:
        i = i % 3 + 1
        time.sleep(0.5)
        #self.current_screen.ids.btnConnect.text = "Connecting %s" %("." * i)
        self.current_screen.ids.btnConnect.text = "%s-%s" %("(" * i,")" * i)
        if quit.isSet():
          stop = True
          break
    if stop:
      self.current_screen.ids.btnConnect.state = "normal"
      self.current_screen.ids.btnConnect.text = "Error"
    else:
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
      
      self.current_screen.ids.btnConnect.state = "normal"
      self.current_screen.ids.btnConnect.text = ""
      
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
    self.current_screen.ids.btnConnect.text = ""
  
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
  version = __version__
  def build(self):
    self.exit = threading.Event()
    ponerine = Ponerine(self.exit)
    conn = ConnectScreen(name='connect')
    ponerine.iplists = self.readcfg()
    #conn.ids.txtCam1.text = cfg[0]
    #conn.ids.txtCam2.text = cfg[1]
    ponerine.add_widget(conn)
    ponerine.add_widget(ControlScreen(name='control'))
    ponerine.add_widget(SettingScreen(name='setting'))
    ponerine.current = 'connect'
    ponerine.DetectCam()
    return ponerine
    
  def on_pause(self):
    return True
    
  def on_stop(self):
    self.exit.set()
    print "app stop"
    #time.sleep(1)
    
  def readcfg(self, key = "camera_ip", subkey = "ip"):
    print "readcfg"
    cfgfile = __file__.replace(basename(__file__), "data/camera.cfg")
    r = []
    try:
      with open(cfgfile) as file:
        cfg = json.loads(file.read())
        #print "readcfg",cfg
      if cfg.has_key(key):
        for item in cfg[key]:
          r.append(item[subkey])
        #print "r", r
        #if len(r) < 2:
          #r.append("")
      else:
        r = ["192.168.42.1"]
    except StandardError:
      r = ["192.168.42.1"]
    print r
    return r

if __name__ == '__main__':
  print Window.size
  PonerineApp().run()
