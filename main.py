import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.clock import Clock
#from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
# Camera Object[camera.py]
from camera import Camera
# import base64, functools, hashlib, json, os, platform, re, select, socket, subprocess, sys, tempfile, threading, time, tkFileDialog, tkMessageBox, urllib2, webbrowser, zlib
'''
platform.system()
"Windows", "Darwin"
'''
import json, os, threading, time, socket, platform
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

class CamConfigPopup(Popup):
  ip = StringProperty()
  index = NumericProperty()
  apply = BooleanProperty()

class Ponerine(ScreenManager):
  def __init__(self, appexit):  
    super(Ponerine, self).__init__()  
    self.appexit = appexit
    self.iplists = self.ReadConfig()
    self.stopdetect = threading.Event()
    
    sysname = platform.system()
    if sysname == "Windows":
      Window.size = (560,800)
    elif sysname == "Darwin":
      Window.size = (520,700)
  
  def DetectCam(self):
    print "Start DetectCam", len(self.iplists), self.iplists
    i = 0
    for ip in self.iplists:
      if ip <> "":
        print "create detect thread %d" %i
        threading.Thread(target=self.DoDetectCam, args=(i,ip), name="DoDetectCam"+str(i)).start()
        if i == 0:
          self.current_screen.ids.btnCam1.background_normal = 'image/camera_set_down.png'
          self.current_screen.ids.btnCam1.background_down = 'image/camera_set_normal.png'
        else:
          self.current_screen.ids.btnCam2.background_normal = 'image/camera_set_down.png'
          self.current_screen.ids.btnCam2.background_down = 'image/camera_set_normal.png'
      else:
        if i == 0:
          self.current_screen.ids.btnCam1.background_normal = 'image/camera_add_normal.png'
          self.current_screen.ids.btnCam1.background_down = 'image/camera_add_down.png'
        else:
          self.current_screen.ids.btnCam2.background_normal = 'image/camera_add_normal.png'
          self.current_screen.ids.btnCam2.background_down = 'image/camera_add_down.png'
      i += 1
      
  def Connect(self):
    print self.current_screen.ids.btnConnect.background_normal
    self.stopdetect.set()
    if self.current_screen.ids.btnConnect.text == "" or self.current_screen.ids.btnConnect.text == "Error":
      self.cam = []
      print "ip list" ,len(self.iplists), self.iplists
      for ip in self.iplists:
        print "ip list %s" %ip
        if ip <> "":
          self.cam.append(Camera(ip))
      if len(self.cam) > 0:
        self.tconn= threading.Thread(target=self.DoConnect)
        self.tconn.setName('DoConnect')
        self.tconn.start()
      else:
        self.CamConfig(0)
    
  def Disconnect(self):
    self.tconn= threading.Thread(target=self.DoDisconnect)
    self.tconn.setName('DoDisconnect')
    self.tconn.start()
    
  def Control(self):
    if self.current == "setting":
      self.transition = SlideTransition(direction="right")
    self.current = "control"
    self.transition = SlideTransition(direction="left")
    
  def Setting(self):
    self.current = "setting"
  
  def CamConfig(self, index):
    print type(self.parent)
    print "CamConfig index %d" %index, self.iplists
    self.stopdetect.set()
    #camconfigkv = Builder.load_string(open("data/camconfig.kv").read())
    self.camconfigpop = CamConfigPopup(size_hint=(0.8, 0.8), size=self.size, ip=str(self.iplists[index]), index=index)
    self.camconfigpop.bind(on_dismiss=self.CamConfigApply)
    self.camconfigpop.apply = False
    self.camconfigpop.index = int(index)
    #self.camconfigpop.ip = str(self.iplists[index])
    print self.camconfigpop.apply, self.camconfigpop.index, self.camconfigpop.ip
    self.camconfigpop.open()
    #Clock.schedule_once(lambda dt: self.camconfigpop.open())
    #Clock.schedule_once(self.camconfigpop.open())
  
  def CamConfigApply(self, popup):
    if popup.apply:
      print "index %d ip %s" %(popup.index,popup.ip)
      self.iplists[popup.index] = popup.ip
      print self.iplists
      self.WriteConfig()
      #self.iplists = self.ReadConfig()
      #print self.iplists
      self.stopdetect.clear()
      self.DetectCam()
      #Clock.schedule_once(lambda dt: self.camconfigpop.dismiss())
  
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
    
  def DoDetectCam(self, index, ip):
    timewait = 0
    if ip == "":
      return
    self.appexit.wait(1)
    print "start DoDetectCam %d" %index
    socket.setdefaulttimeout(5)
    retry = 0
    while not self.appexit.isSet():
      if timewait > 0:
        self.stopdetect.wait(timewait)
      if self.stopdetect.isSet():
        break 
      retry = retry % 5 + 1
      index = index % 2
      srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      srv.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
      open = srv.connect_ex((ip, 7878))
      srv.close()
      print "Detect Cam IP %s Index %d state %d retry %d" %(ip, index, open, retry)
      if open == 0:
        if index == 0:
          self.current_screen.ids.btnCam1.background_normal = 'image/camera_green.png'
          self.current_screen.ids.btnCam1.background_down = 'image/camera_set_down.png'
        else:
          self.current_screen.ids.btnCam2.background_normal = 'image/camera_green.png'
          self.current_screen.ids.btnCam2.background_down = 'image/camera_set_down.png'
        break
      elif retry >= 5:
        if timewait < 10:
          timewait += 1
        if index == 0:
          self.current_screen.ids.btnCam1.background_normal = 'image/camera_red.png'
          self.current_screen.ids.btnCam1.background_down = 'image/camera_set_down.png'
        else:
          self.current_screen.ids.btnCam2.background_normal = 'image/camera_red.png'
          self.current_screen.ids.btnCam2.background_down = 'image/camera_set_down.png'

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
      self.current_screen.ids.btnConnect.state = "normal"
      self.current_screen.ids.btnConnect.text = ""
      
      #self.current_screen.ids.btnConnect.text = "Connecting"
      self.current = "control"
      i = 0
      for cam in self.cam:
        i +=1
        threading.Thread(target=self.DoWifi, args=(cam.wifioff,), name="DoWifi"+str(i)).start()
  
  def DoDisconnect(self):
#     try:
#       if self.tctrl.isAlive():
#         print "stop tctrl"
#         self.tctrl._Thread__stop()
#     except:
#       pass
    try:
      for cam in self.cam:
        cam.UnlinkCamera()
    except:
      pass
    if self.current == "control":
      self.transition = SlideTransition(direction="right")
      
    self.current = "connect"
    self.stopdetect.clear()
    self.DetectCam()
    self.transition = SlideTransition(direction="left")
    self.current_screen.ids.btnConnect.text = ""

#     cam1 = self.current_screen.ids.btnCam1.background_normal
#     if cam1 == "image/camera_green.png" or cam1 == "image/camera_green.png":
#       self.current_screen.ids.btnCam1.background_normal = "image/camera_set_normal.png"
#
#     cam2 = self.current_screen.ids.btnCam2.background_normal
#     if cam2 == "image/camera_green.png" or cam2 == "image/camera_green.png":
#       self.current_screen.ids.btnCam2.background_normal = "image/camera_set_normal.png"
  
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
  
  def DoWifi(self, wifioff):
    print "wifi wait start"
    wifioff.wait()
    self.current = 'connect'
    self.current_screen.ids.btnConnect.text = ""
  
  def DoControl(self):
    file = ""
    i = 0
    for cam in self.cam:
      i += 1
      while cam.lastjpg == "" and cam.lastmp4 == "":
        if cam.quit.isSet():
          return
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

  def ReadConfig(self, key = "camera_ip", subkey = "ip"):
    print "readcfg"
    cfgfile = __file__.replace(basename(__file__), "data/camera.cfg")
    r = []
    try:
      with open(cfgfile) as file:
        cfg = json.loads(file.read())
        print "readcfg",cfg
      if cfg.has_key(key):
        for item in cfg[key]:
          r.append(item[subkey])
        print "r", r
        if len(r) < 2:
          r.append("")
      else:
        r = ["192.168.42.1",""]
    except StandardError:
      r = ["192.168.42.1",""]
    print r
    return r

  def WriteConfig(self):
    i = 0
    cfg = {}
    camip = []
    for ip in self.iplists:
      if ip <> "":
        i += 1
        camip.append(json.loads('{"camera":%d,"ip":"%s"}'%(i, ip)))
    cfg["camera_ip"] = camip
    print cfg
    cfgfile = __file__.replace(basename(__file__), "data/camera.cfg")
    print __file__
    print cfgfile
    print json.dumps(cfg, indent=2)
    try:
      with open(cfgfile,'w') as file:
        file.write(json.dumps(cfg, indent=2))
    except StandardError:
      pass
    
class PonerineApp(App):
  version = __version__
  def build(self):
    self.appexit = threading.Event()
    ponerine = Ponerine(self.appexit)
    conn = ConnectScreen(name='connect')
    #self.ponerine.iplists = self.readcfg()
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
    self.appexit.set()
    print "app stop"
    for thread in threading.enumerate():
			if thread.isAlive():
				try:
					thread._Thread__stop()
				except:
					pass

if __name__ == '__main__':
  print Window.size
  PonerineApp().run()
