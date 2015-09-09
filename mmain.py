import kivy
# Ponerine Multi-Cam Controller
kivy.require('1.9.0')

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager , SlideTransition
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ObjectProperty

from kivy.adapters.dictadapter import DictAdapter
from kivy.uix.listview import ListView, ListItemButton, ListItemLabel, CompositeListItem
from kivy.adapters.models import SelectableDataItem

from kivy.config import Config,ConfigParser
from kivy.uix.settings import SettingsWithNoMenu,SettingOptions,SettingBoolean,SettingString

# Camera Object[camera.py]
from camera import Camera
from camerasetting import CameraSetting
# import base64, functools, hashlib, json, os, platform, re, select, socket, subprocess, sys, tempfile, threading, time, tkFileDialog, tkMessageBox, urllib2, webbrowser, zlib
'''
platform.system()
"Windows", "Darwin"
'''
import json, os, threading, time, socket, platform, inspect
from os.path import basename

Builder.load_file('data/mconnectscreen.kv')
Builder.load_file('data/mpopupconfig.kv')

#print "Clock.max_iteration", Clock.max_iteration
Clock.max_iteration = 100
__version__='0.0.1'

class MConnectScreen(Screen):
  pass

class ConfigPopup(Popup):
  cfg = ObjectProperty()
  apply = BooleanProperty()
  
class MPonerine(ScreenManager):
  def __init__(self, appexit):
    super(MPonerine, self).__init__()

    self.applyconfig = False
    self.appexit = appexit
    self.cfglist = []
    self.cfglist = self.ReadConfig()
    self.stopdetect = threading.Event()
    self.resizecam = threading.Event()
    self.connect = threading.Event()
    self.recordstart = threading.Event()
    self.recordstop = threading.Event()
    sysname = platform.system()
    self.totaldownloadsize = 0
    self.currentdownloadsize = 0
    if sysname == "Windows":
      Window.size = (560,800)
    elif sysname == "Darwin":
      Window.size = (520,700)
    
  def InitialCamIcon(self):
    self.btncameras = []
    self.btncameras.append(self.current_screen.ids.btnCam0)
    self.btncameras.append(self.current_screen.ids.btnCam1)
    self.btncameras.append(self.current_screen.ids.btnCam2)
    self.btncameras.append(self.current_screen.ids.btnCam3)
    self.btncameras.append(self.current_screen.ids.btnCam4)
    self.btncameras.append(self.current_screen.ids.btnCam5)
    self.btncameras.append(self.current_screen.ids.btnCam6)
    self.btncameras.append(self.current_screen.ids.btnCam7)
    self.btncameras.append(self.current_screen.ids.btnCam8)
    self.btnphoto = self.current_screen.ids.btnphoto
    self.btnconnect = self.current_screen.ids.btnconnect
    self.btnrecord = self.current_screen.ids.btnrecord
    for i in range(self.cameras):
      btn = self.btncameras[i]
      if self.cfglist[i]["ip"] <> "":
        btn.text = "CAM%s\n%s" %(self.cfglist[i]["camera"], self.cfglist[i]["name"])
        btn.background_normal = 'image/mcamera_normal.png'
      else:
        btn.text = ""
        btn.background_normal = 'image/mcamera_noip.png'
      if self.cfglist[i]["enabled"] == 1:
        btn.color = (0,0,0,1)
        threading.Thread(target=self.DoDetectCam, name="DoDetectCam%d" %i,
                         args=(i, self.cfglist[i]["ip"], 1,)).start()
      else:
        btn.color = (0,0,0,0.5)
  
  def DetectCam(self):
    for i in range(self.cameras):
      btn = self.btncameras[i]
      btn.disabled = False
      btn.color = (0,0,0,1)
      if self.cfglist[i]["ip"] <> "":
        btn.text = "CAM%s\n%s" %(self.cfglist[i]["camera"], self.cfglist[i]["name"])
        btn.background_normal = 'image/mcamera_normal.png'
      else:
        btn.text = ""
        btn.background_normal = 'image/mcamera_noip.png'
      if self.cfglist[i]["enabled"] == 1:
        btn.color = (0,0,0,1)
      else:
        btn.color = (0,0,0,0.5)
      # Detect Thread
      if self.cfglist[i]["enabled"] == 1:
        threading.Thread(target=self.DoDetectCam, name="DoDetectCam%d" %i,
                       args=(i, self.cfglist[i]["ip"], 1,)).start()

  def DoDetectCam(self, index, ip, timewait = 1):
    if ip == "":
      return
    self.appexit.wait(timewait)
    timewait = 0
    print "start DoDetectCam %d" %index
    socket.setdefaulttimeout(5)
    retry = 0
    btn = self.btncameras[index]
    while not self.appexit.isSet():
      #print timewait
      if timewait > 0:    
        self.stopdetect.wait(timewait)
      if self.stopdetect.isSet():
        return 
      retry = retry % 5 + 1
      #index = index % 2
      srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      srv.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
      open = srv.connect_ex((ip, 7878))
      srv.close()
      print "Detect Cam IP %s Index %d state %d retry %d" %(ip, index, open, retry)
      if self.stopdetect.isSet():
        return
      if open == 0:
        #btn.color = (0.72,0.95,0.65,1)
        btn.background_normal = 'image/mcamera_linked.png'
        print 'image/mcamera_linked.png'
        return
      elif retry >= 5:
        if timewait < 10:
          timewait += 1
        #btn.color = (0.94,0.46,0.7,1)
        btn.background_normal = 'image/mcamera_disconnect.png'
  
  def Connect(self):
    btn = self.btnconnect
    if btn.text == "CONNECT":
      #btn.text = "CONNECTING"
      btn.disabled = True
      btn.disabled_color = (0,0,0,0.5)
      btn.background_disabled_normal = 'image/mcamera_normal.png'

      self.stopdetect.set()
      self.connect.clear()
      self.recordstart.clear()
      self.recordstop.clear()
      self.cam = []
      idx = 0
      num = 0
      self.linked = 0
      self.error = 0
      self.retry = []
      self.firstcam = 0
      for cfg in self.cfglist:
        self.btncameras[num].disabled = True
        if cfg["enabled"] == 1 and cfg["ip"] <> "":
          self.cam.append(Camera(cfg["ip"]))
          threading.Thread(target=self.DoConnect, args=(idx,num,), name="DoConnect%d" %idx).start()
          idx += 1
          self.btncameras[num].background_disabled_normal = 'image/mcamera_normal.png'
        else:
          self.btncameras[num].text = ""
          self.btncameras[num].background_disabled_normal = 'image/mcamera_noip.png'
        num += 1
      self.connect.set()
      threading.Thread(target=self.DoShowConnect, args=(0,), name="DoShowConnect").start()
    elif btn.text == "RETRY": # Retry connect to rest of the camera
      btn.disabled = True
      btn.disabled_color = (0,0,0,0.5)
      btn.background_disabled_normal = 'image/mcamera_normal.png'
      self.connect.clear()
      self.error = 0
      for itm in self.retry:
        idx = itm["index"]
        num = itm["number"]
        self.cam[idx].quit.clear()
        threading.Thread(target=self.DoConnect, args=(idx,num,), name="DoConnect%d" %idx).start()
        self.btncameras[num].background_disabled_normal = 'image/mcamera_normal.png'
      self.retry = []
      self.connect.set()
      threading.Thread(target=self.DoShowConnect, args=(2,), name="DoShowConnect").start()
    elif btn.text == "DISCONNECT":
      btn.disabled = True
      btn.disabled_color = (0,0,0,0.5)
      btn.background_disabled_normal = 'image/mcamera_normal.png'
      self.btnphoto.disabled = True
      self.btnrecord.disabled = True
      threading.Thread(target=self.DoDisconnect, name="DoDisconnect").start()
      self.connect.set()
      threading.Thread(target=self.DoShowConnect, args=(1,), name="DoShowConnect").start()
      
  def DoShowConnect(self, type):
    i = 0
    self.btnconnect.disabled_color = (0,0,0,1)
    #self.btnconnect.background_disabled_normal = 'image/mcamera_normal.png'
    #self.btnconnect.disabled = True
    while self.connect.isSet():
      if i == 0:
        i = 1
        self.btnconnect.background_disabled_normal = 'image/mcamera_linked.png'
      else:
        i = 0
        if type in (0,2): #connect
          self.btnconnect.background_disabled_normal = 'image/mcamera_connect.png'
          if self.linked == len(self.cam):
            self.connect.clear()
            self.btnphoto.disabled = False
            self.btnphoto.background_normal = 'image/mcamera_normal.png'
            self.btnphoto.background_down = 'image/mcamera_down.png'
            self.btnphoto.color = (0,0,0,1)
            
            self.btnrecord.disabled = False
            self.btnrecord.background_normal = 'image/mcamera_normal.png'
            self.btnrecord.background_down = 'image/mcamera_down.png'
            self.btnrecord.color = (0,0,0,1)
            threading.Thread(target=self.ButtonText, args=(self.btnconnect,"DISCONNECT",1,), name="ButtonText").start()
            i = 0
            for cfg in self.cfglist:
              if cfg["enabled"] == 1 and cfg["ip"] <> "":
                self.btncameras[i].background_disabled_normal = 'image/mcamera_connect.png'
                print "Link All %d" %i, self.btncameras[i].background_disabled_normal
              i += 1
            self.btnconnect.disabled = False
            self.btnconnect.color = (0,0,0,1)
            break
          elif (self.linked + self.error) == len(self.cam):
            self.connect.clear()
            if type == 0:
              self.btnconnect.disabled = False
              self.btnconnect.color = (1,0,0,1)
              self.btnconnect.text = "ERR %d / %d" %(self.error, len(self.cam))
              self.btnconnect.background_normal = 'image/mcamera_normal.png'
              threading.Thread(target=self.ButtonText, args=(self.btnconnect,"RETRY",1,), name="ButtonText").start()
              break
            else: #retry
              self.btnconnect.disabled_color = (1,0,0,1)
              self.btnconnect.text = "ERR %d / %d" %(self.error, len(self.cam))
              time.sleep(1.5)
              self.btnconnect.color = (0,0,0,1)
              self.btnconnect.disabled_color = (0,0,0,0.5)
              self.btnconnect.text = "DISCONNECT"
              threading.Thread(target=self.Connect, name="Disconnect").start()
              break
        else: #disconnect
          self.btnconnect.background_disabled_normal = 'image/mcamera_disconnect.png'
      time.sleep(1)
    
  def DoConnect(self, index, number):
    self.connect.wait()
    
    cam = self.cam[index]
    btn = self.btncameras[number]
    quit = cam.quit
    cam.LinkCamera()
    while True:
      if cam.link:
        break
      btn.disabled_color = (0,0,0,1)
      quit.wait(1)
      if quit.isSet():
        self.error += 1
        self.retry.append(json.loads('{"index":%d,"number":%d}' %(index,number)))
        #btn.disabled = False
        btn.background_disabled_normal = 'image/mcamera_disconnect.png'
        print "Fail to connect camera %d" %number
        return
    # Listen Start Record Command
    threading.Thread(target=self.DoStartRecord, args=(index,), name="DoStartRecord%d" %index).start()
    #print 'image/mcamera_connect.png'
    self.linked += 1
    self.btnconnect.text = 'CAM %d / %d' %(self.linked, len(self.cam))
    #cam.StartViewfinder()
    print "Linked Camera %d" %number
    # if self.linked == len(self.cam):
      # self.connect.clear()
      # self.btnphoto.disabled = False
      # self.btnphoto.background_normal = 'image/mcamera_normal.png'
      # self.btnphoto.background_down = 'image/mcamera_down.png'
      # self.btnphoto.color = (0,0,0,1)
      # self.btnrecord.disabled = False
      # self.btnrecord.background_normal = 'image/mcamera_normal.png'
      # self.btnrecord.background_down = 'image/mcamera_down.png'
      # self.btnrecord.color = (0,0,0,1)
      # threading.Thread(target=self.ButtonText, args=(self.btnconnect,"DISCONNECT",1.5,), name="ButtonText").start()
      # i = 0
      # for cfg in self.cfglist:
        # if cfg["enabled"] == 1 and cfg["ip"] <> "":
          # self.btncameras[i].background_disabled_normal = 'image/mcamera_connect.png'
          # print "Link All %d" %i, self.btncameras[i].background_disabled_normal
        # i += 1
      # self.btnconnect.disabled = False
    cam.SendMsg('{"msg_id":2,"type":"buzzer_volume", "param":"mute"}')
    #threading.Thread(target=self.DoWifi, args=(cam.wifioff,), name="DoWifi"+str(i)).start()
    #threading.Thread(target=self.DoFileTaken, args=(i,), name="DoFileTaken"+str(i)).start()
    
  def DoDisconnect(self):
    try:
      for cam in self.cam:
        if cam.link:
          cam.UnlinkCamera()
          cam.quit.wait(10)
    except:
      pass
    self.connect.clear()
    self.stopdetect.clear()    
    self.DetectCam()
    self.btnconnect.disabled = False
    self.btnconnect.text = "CONNECT"
    self.btnconnect.background_normal = 'image/mcamera_normal.png'
    
  def DoStartRecord(self, index):
    retry = False
    while True:
      self.recordstart.wait()
      cam = self.cam[index]
      cam.StartRecord(False)
      cam.recording.wait(15)
      if cam.recording.isSet():
        retry = False
        print "\nDoStartRecord", index
        if self.linked == 0:
          self.firstcam = index
          print "self.firstcam", self.firstcam
        self.linked += 1
        self.btnrecord.text = 'CAM %d / %d' %(self.linked, len(self.cam))
        threading.Thread(target=self.DoStopRecord, args=(index,), name="DoStopRecord%d" %index).start()
        if self.linked == len(self.cam):
          self.cam[self.firstcam].SendMsg('{"msg_id":2,"type":"buzzer_ring", "param":"on"}')
          time.sleep(1.5)
          self.cam[self.firstcam].SendMsg('{"msg_id":2,"type":"buzzer_ring", "param":"off"}')
          threading.Thread(target=self.ButtonText, args=(self.btnrecord,"STOP",1,), name="ButtonText").start()
          threading.Thread(target=self.DoShowRecord, name="DoShowRecord").start()
          self.recordstart.clear()
          self.btnrecord.disabled = False
        self.recordstop.wait()
      elif retry:
        retry = False
        self.recordstart.clear()
        self.btnrecord.disabled_color = (1,0,0,1)
        self.btnrecord.text = "ERROR"
        time.sleep(2)
        self.btnrecord.disabled_color = (0,0,0,1)
        self.btnrecord.text == "STOP"
        self.Record() #STOP
        self.recordstop.wait()
      else:
        retry = True
  
  def DoShowRecord(self):
    i = 0
    while True:
      if self.btnrecord.text == "STOP":
        if i == 0:
          i = 1
          self.btnrecord.background_normal = 'image/mcamera_disconnect.png'
        else:
          i = 0
          self.btnrecord.background_normal = 'image/mcamera_normal.png'
        print self.btnrecord.text, self.btnrecord.background_normal, i
      self.recordstop.wait(1)
      if self.recordstop.isSet() or self.btnrecord.text in ("RECORD", "STOPPING", "ERROR"):
        self.btnrecord.background_normal = 'image/mcamera_normal.png'
        return
    
  def DoStopRecord(self, index):
    self.recordstop.wait()
    cam = self.cam[index]
    cam.taken.clear()
    if cam.recording.isSet():
      cam.StopRecord()
    print "DoStopRecord", index
    print cam.filetaken
    self.linked += 1
    self.btnrecord.text = 'CAM %d / %d' %(self.linked, len(self.cam))
    if self.linked == len(self.cam):
      threading.Thread(target=self.ButtonText, args=(self.btnrecord,"RECORD",1.5,), name="ButtonText").start()
      self.recordstop.clear()
      self.btnrecord.background_normal = 'image/mcamera_normal.png'
      self.btnrecord.disabled = False
      
  def ButtonText(self, button, text, timewait=1):
    #print "timewait",type(timewait)
    time.sleep(timewait)
    button.text = text
  
  def ButtonBackground(self, button, type, imagefilepath):
    if type == "background_normal":
      button.background_normal = imagefilepath
    elif type == "background_down":
      button.background_down = imagefilepath
    elif type == "background_disabled_normal":
      button.background_disabled_normal = imagefilepath
    elif type == "background_disabled_down":
      button.background_disabled_normal = imagefilepath
  
  def Record(self):
    btn = self.btnrecord
    if btn.text == "RECORD":
      self.linked = 0
      self.firstcam = 0
      self.recordstart.set()
      self.recordstop.clear()
      btn.text == "STARTING"
      btn.disabled = True
    elif btn.text == "STOP":
      self.linked = 0
      btn.text == "STOPPING"
      btn.disabled = True
      self.cam[self.firstcam].SendMsg('{"msg_id":2,"type":"buzzer_ring", "param":"on"}')
      time.sleep(1.5)
      self.cam[self.firstcam].SendMsg('{"msg_id":2,"type":"buzzer_ring", "param":"off"}')
      self.recordstop.set()
      self.recordstart.clear()

  def CamerasPopupOpen(self):
    print type(self.parent)
    print "Connection Config - Camera Count"
    self.stopdetect.set()
    self.cameraspopup = CamerasPopup(title='Connection Config - Camera Count', size_hint=(0.8, 0.4), size=self.size)
    self.cameraspopup.bind(on_dismiss=self.CamerasPopupApply)
    self.cameraspopup.apply = False
    self.cameraspopup.cameras = str(self.cameras)
    #print self.configpop.apply, self.configpop.index, self.configpop.cfg
    self.cameraspopup.open()
    
  def CamerasPopupApply(self, popup):
    cnt = 6
    if popup.apply:
      print "Set Camera Count %s" %(popup.cameras)
      try:
        cnt = int(popup.cameras)
      except:
        cnt = 6
      if cnt < 1:
        cnt = 1
      elif cnt > 9:
        cnt = 9
      self.cameras = cnt
      self.WriteConfig()
      self.cfglist = self.ReadConfig()
    self.stopdetect.clear()
    self.DetectCam()
      
  def ConfigPopupOpen(self, index):
    #index = int(cambtn.id)
    #print type(self.parent)
    #print "Config Popup Open index %s" %index, self.cfglist
    self.stopdetect.set()
    self.configpop = ConfigPopup(title='Connection Config - Camera', size_hint=(0.8, 0.6), size=self.size, cfg=self.cfglist[index], index=index)
    self.configpop.bind(on_dismiss=self.ConfigPopupApply)
    self.configpop.apply = False
    self.configpop.index = index
    print self.configpop.apply, self.configpop.index, self.configpop.cfg
    self.configpop.open()
  
  def ConfigPopupApply(self, popup):
    if popup.apply:
      print "index %d ip %s" %(popup.index,popup.cfg)
      self.cfglist[popup.index] = popup.cfg
      self.WriteConfig()
      self.cfglist = self.ReadConfig()
    self.stopdetect.clear()
    self.DetectCam()
  
  def Buzzer(self, sec=1.5):
    self.cam[self.firstcam].SendMsg('{"msg_id":2,"type":"buzzer_ring", "param":"on"}')
    time.sleep(sec)
    self.cam[self.firstcam].SendMsg('{"msg_id":2,"type":"buzzer_ring", "param":"off"}')
    
  def Photo(self):
    self.tphoto= threading.Thread(target=self.DoPhoto)
    self.tphoto.setName('DoPhoto')
    self.tphoto.start()
  
  def Second2Time(self, seconds):
    rectime = "00:00:00"
    ihour = 0
    iminute = 0
    isecond = 0
    if seconds <> 0:
      ihour = seconds / 3600
      seconds = seconds % 3600
      iminute = seconds / 60
      isecond = seconds % 60
      rectime = "%02d:%02d:%02d" %(ihour, iminute, isecond)
    return rectime
    
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
    
  def DoStartRecord_old(self):
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
      print recording, "Record Time: ", rectime
      if len(rectime) > 1:
        self.current_screen.ids.lblCam1.text = "CAM 1 [ " + rectime[0] + " ]"
        self.current_screen.ids.lblCam2.text = "CAM 2 [ " + rectime[1] + " ]"
      else:
        self.current_screen.ids.lblCam1.text = "CAM 1 [ " + rectime[0] + " ]"
        self.current_screen.ids.lblCam2.text = "CAM 2 [ --:--:-- ]"
    self.current_screen.ids.lblCam1.text = "CAM 1 [ --:--:-- ]"
    self.current_screen.ids.lblCam2.text = "CAM 2 [ --:--:-- ]"
    
  def DoStopRecord_old(self):
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
    print "DoWifi wait start"
    wifioff.wait()
    self.transition = SlideTransition(direction = "right")
    self.stopdetect.clear()
    self.switch_to(self.screen[0],direction="right")
    self.current_screen.ids.btnConnect.text = ""
    self.DetectCam(45)
    time.sleep(15)
    wifioff.clear()
  
  def DoFileTaken(self, index):
    print "DoFileTaken start %d" %index
    self.cam[index].setallok.wait(30)
    if self.cam[index].setallok.isSet() and len(self.cam[index].settings) > 0:
      debugtxt = self.current_screen.ids.txtDebug.text
      for item in self.cam[index].settings:
        for key,value in item.items():
          if key in ["video_resolution","timelapse_video_resolution","capture_mode"]:
            debugtxt += "\nCAM %d %s: %s" %(index+1,key,value)
      self.current_screen.ids.txtDebug.text = debugtxt + "\n"
    while not self.cam[index].quit.isSet():
      self.cam[index].taken.wait(1)
      if self.cam[index].taken.isSet() and self.current_screen.name == "camera":
        debugtxt = self.current_screen.ids.txtDebug.text
        if self.cam[index].filetaken <> "":
          debugtxt += "\nCAM %d : " %(index+1) + self.cam[index].filetaken
          self.current_screen.ids.txtDebug.text = debugtxt
        self.cam[index].taken.clear()
    print "DoFileTaken stop %d" %index
    
  def ReadConfig(self):
    self.cameras = 9 #default 6 cameras
    cfgfile = __file__.replace(basename(__file__), "data/mcamera.cfg")
    initstr = '''
    {
      "camera": "0",
      "ip": "",
      "enabled": 0,
      "name": ""
    }
    '''
    r = []
    try:
      with open(cfgfile) as file:
        readstr = file.read()
        #print "readstr", readstr
        cfg = json.loads(readstr)
#       if cfg.has_key("cameras"):
#         self.cameras = cfg["cameras"]
#         if self.cameras < 1:
#           self.cameras = 6
      if cfg.has_key("config"):
        for item in cfg["config"]:
          cfginit = json.loads(initstr)
          cfginit.update(item)
          r.append(cfginit)
        print "config read len %d of %d" %(len(r), self.cameras)
        if len(r) < self.cameras:
          for i in range(len(r), self.cameras):
            cfginit = json.loads(initstr)
            cfginit["camera"] = str(i+1)
            r.append(cfginit)
      else:
        for i in range(self.cameras):
          cfginit = json.loads(initstr)
          cfginit["camera"] = str(i+1)
          r.append(cfginit)
    except StandardError:
      for i in range(self.cameras):
        cfginit = json.loads(initstr)
        cfginit["camera"] = str(i+1)
        r.append(cfginit)
    #for item in r:
    #  print "ReadConfig", item
    return r

  def WriteConfig(self):
    cfg = {}
    #cfg["cameras"] = self.cameras
    cfg["config"] = self.cfglist
    cfgfile = __file__.replace(basename(__file__), "data/mcamera.cfg")
    try:
      with open(cfgfile,'w') as file:
        file.write(json.dumps(cfg, indent=2))
    except StandardError:
      pass
    
class MPonerineApp(App):
  version = __version__
  def build(self):
    self.appexit = threading.Event()

    mponerine = MPonerine(self.appexit)
    mponerine.duration = 0.7

    mponerine.screen = [MConnectScreen(name="mconnect")]
    mponerine.switch_to(mponerine.screen[0])
    mponerine.InitialCamIcon()
    return mponerine
    
  def on_pause(self):
    return True
    
  def on_stop(self):
    self.appexit.set()
    for thread in threading.enumerate():
      if thread.isAlive():
        try:
          thread._Thread__stop()
        except:
          pass

if __name__ == '__main__':
  MPonerineApp().run() 
