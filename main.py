import kivy

kivy.require('1.9.0')

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager , SlideTransition
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ObjectProperty
# Camera Object[camera.py]
from camera import Camera
# import base64, functools, hashlib, json, os, platform, re, select, socket, subprocess, sys, tempfile, threading, time, tkFileDialog, tkMessageBox, urllib2, webbrowser, zlib
'''
platform.system()
"Windows", "Darwin"
'''
import json, os, threading, time, socket, platform
from os.path import basename


#print "Clock.max_iteration", Clock.max_iteration
Clock.max_iteration = 500
__version__='0.0.7'

class ConfigPopup(Popup):
  cfg = ObjectProperty()
  apply = BooleanProperty()

class Ponerine(ScreenManager):
  
  def RefreshFile(self, text):
    print text.upper()
    print text.lower()
    str = self.current_screen.ids.lstCamera.text.replace("Camera","").replace(" ","")
    index = -1
    if str.isdigit():
      index = int(str) - 1
    if index > -1 and text <> "File Type":
      self.current_screen.ids.boxFileList.clear_widgets()
      lbl = Label(text="Loading File List ...", size_hint=(1, 1), font_size=self.width/20)
      self.current_screen.ids.boxFileList.add_widget(lbl)
      threading.Thread(target=self.DoRefreshFile, args=(text[0:3],index,), name="DoRefreshFile").start()
  
  def SelectCamera(self, instance):
    print instance.text
    #if instance.text <> "Camera":
    #  instance.text = "Camera"
  
  def SelectFile(self, instance):
    print instance.text
    if instance.text <> "Selection":
      instance.text = "Selection"
    
    
  def __init__(self, appexit):  
    super(Ponerine, self).__init__()  
    self.appexit = appexit
    self.cfglist = []
    self.cfglist = self.ReadConfig()
    self.stopdetect = threading.Event()
    
    sysname = platform.system()
    if sysname == "Windows":
      Window.size = (560,800)
    elif sysname == "Darwin":
      Window.size = (520,700)
  
  def DetectCam(self, timewait = 1):
    print "Start DetectCam", len(self.cfglist), self.cfglist
    i = 0
    for cfg in self.cfglist:
      if cfg["ip"] <> "":
        print "create detect thread %d" %i
        threading.Thread(target=self.DoDetectCam, args=(i,cfg["ip"],timewait,), name="DoDetectCam"+str(i)).start()
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
      print "ip list" ,len(self.cfglist), self.cfglist
      for cfg in self.cfglist:
        print "ip list %s" %cfg["ip"]
        if cfg["ip"] <> "":
          self.cam.append(Camera(cfg["ip"]))
      if len(self.cam) > 0:
        self.tconn= threading.Thread(target=self.DoConnect)
        self.tconn.setName('DoConnect')
        self.tconn.start()
      else:
        self.ConfigPopupOpen(0)
    
  def Disconnect(self):
    self.transition = SlideTransition(direction = "right")
    self.switch_to(Builder.load_file('data/connectscreen.kv'))
    self.current_screen.ids.btnConnect.text = ""
    threading.Thread(target=self.DoDisconnect, name="DoDisconnect").start()
    # self.tconn= threading.Thread(target=self.DoDisconnect)
    # self.tconn.setName('DoDisconnect')
    # self.tconn.start()

  def FileManager(self):
    self.transition = SlideTransition(direction = "right")
    self.switch_to(Builder.load_file('data/filemanagerscreen.kv'))
    self.current_screen.ids.lstCamera.text = "Camera"
    camlist = []
    for i in range(len(self.cam)):
      camlist.append('Camera %d'%(i+1))
    if len(camlist) > 0:
      self.current_screen.ids.lstCamera.values = camlist
    self.current_screen.ids.lstFileType.text = "File Type"
    self.current_screen.ids.lstSelection.text = "Selection"
    
  def Camera(self):
    if self.current == "setting":
      self.transition = SlideTransition(direction = "right")
    elif self.current == "filemanager":
      self.transition = SlideTransition(direction = "left")
    self.switch_to(Builder.load_file('data/camerascreen.kv'))
    
  def Setting(self):
    #if self.current == "camera":
    self.transition = SlideTransition(direction = "left")
    self.switch_to(Builder.load_file('data/settingscreen.kv'))
  
  def ConfigPopupOpen(self, index):
    print type(self.parent)
    print "Config Popup Open index %d" %index, self.cfglist
    self.stopdetect.set()
    self.configpop = ConfigPopup(title='Connection Config - Camera %d' %(index+1), size_hint=(0.8, 0.8), size=self.size, cfg=self.cfglist[index], index=index)
    self.configpop.bind(on_dismiss=self.ConfigPopupApply)
    self.configpop.apply = False
    self.configpop.index = int(index)
    print self.configpop.apply, self.configpop.index, self.configpop.cfg
    self.configpop.open()
  
  def ConfigPopupApply(self, popup):
    if popup.apply:
      print "index %d ip %s" %(popup.index,popup.cfg)
      self.cfglist[popup.index] = popup.cfg
      self.WriteConfig()
      self.stopdetect.clear()
      self.DetectCam()
    
  def Photo(self):
    self.tphoto= threading.Thread(target=self.DoPhoto)
    self.tphoto.setName('DoPhoto')
    self.tphoto.start()
    
  def Record(self):
    if self.current_screen.ids.btnRecord.text == "Start Record":
      self.tstart= threading.Thread(target=self.DoStartRecord)
      self.tstart.setName('DoStartRecord')
      self.tstart.start()
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
    
  def DoDetectCam(self, index, ip, timewait = 1):
    if ip == "":
      return
    self.appexit.wait(timewait)
    timewait = 0
    print "start DoDetectCam %d" %index
    socket.setdefaulttimeout(5)
    retry = 0
    while not self.appexit.isSet():
      print timewait
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
      if self.stopdetect.isSet():
        break
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
        quit.wait(0.5)
        if quit.isSet():
          stop = True
          break
        self.current_screen.ids.btnConnect.text = "%s-%s" %("(" * i,")" * i)
        
    if stop:
      self.current_screen.ids.btnConnect.state = "normal"
      self.current_screen.ids.btnConnect.text = "Error"
    else:
      #self.current_screen.ids.btnConnect.state = "normal"
      #self.current_screen.ids.btnConnect.text = ""
      self.transition = SlideTransition(direction = "left")
      self.current = 'camera'
      #self.switch_to(Builder.load_file('data/camerascreen.kv'))
      i = 0
      for cam in self.cam:
        threading.Thread(target=self.DoWifi, args=(cam.wifioff,), name="DoWifi"+str(i)).start()
        threading.Thread(target=self.DoFileTaken, args=(i,), name="DoFileTaken"+str(i)).start()
        i +=1
  
  def DoDisconnect(self):
    try:
      for cam in self.cam:
        cam.UnlinkCamera()
    except:
      pass
    self.stopdetect.clear()
    self.DetectCam()
  
  def DoRefreshFile(self, text, index):
    list = []
    cam = self.cam[index]
    cam.RefreshFile()
    cam.lsdir.wait()
    if len(cam.status["listing"]) > 0:
      print "file extention: %s" %text
      cam.RefreshFile(cam.status["pwd"] + "/" + cam.status["listing"][0], text)
      cam.lsdir.wait()
    if len(cam.status["listing"]) > 0:
      #print "media list: ", cam.status["listing"]
      for item in cam.status["listing"]:
        list.append(item)
    
    layout = GridLayout(cols=3, padding=self.width/40, spacing=self.width/40, size_hint=(None, None), width = self.width)
    layout.bind(minimum_height=layout.setter('height'))

    buttons = []
    for item in list:
      ext = item[len(item)-3:len(item)].lower()
      if ext in ("jpg","mp4","raw"):
        buttons.append(ToggleButton(text=item, halign="center",valign="bottom",padding=(self.width/80,self.width/80),text_size=((self.width-self.width/10)/3, (self.width-self.width/10)/5),
                         background_normal="image/file%s-2.png"%ext,background_down="image/file%s-1.png"%ext,
                         size=((self.width-self.width/10)/3, (self.width-self.width/10)/5), size_hint=(None, None), font_size=self.width/50, color=(1,1,0,1)))
      else:
        buttons.append(ToggleButton(text=item, halign='center',valign='bottom',padding=(self.width/80,self.width/80),text_size=((self.width-self.width/10)/3, (self.width-self.width/10)/5),size=((self.width-self.width/10)/3, (self.width-self.width/10)/5), size_hint=(None, None), font_size=self.width/50, color=(1,1,0,1)))
    i = 0
    for btn in buttons:
      layout.add_widget(btn, index=i)
      i += 1
      #print "No. %d children len" %i,len(layout.children[:])
    sv = ScrollView(size_hint=(None, None), size=(self.current_screen.ids.boxFileList.width,
                    self.current_screen.ids.boxFileList.height), pos_hint={'center_x': .5, 'center_y': .5}, do_scroll_x=False)
    sv.add_widget(layout)
    self.current_screen.ids.boxFileList.clear_widgets()
    self.current_screen.ids.boxFileList.add_widget(sv)   

  def DoRefreshFile2(self, text):
    i = 0
    list = []
    for i in range(30):
      list.append("Cam 1: YDXJ%04d.jpg" %i)
    self.current_screen.ids.boxFileList.clear_widgets()
    layout = GridLayout(cols=3, padding=self.width/40, spacing=self.width/40, size_hint=(None, None), width = self.width)
    layout.bind(minimum_height=layout.setter('height'))

    sv = ScrollView(size_hint=(None, None), size=(self.current_screen.ids.boxFileList.width,
                    self.current_screen.ids.boxFileList.height), pos_hint={'center_x': .5, 'center_y': .5}, do_scroll_x=False)
    sv.add_widget(layout)
    self.current_screen.ids.boxFileList.add_widget(sv) 
    
    for item in list:
      ext = item[len(item)-3:len(item)].lower()
      if ext in ("jpg","mp4","raw"):
        btn = ToggleButton(text=item, halign="center",valign="bottom",padding=(self.width/80,self.width/80),text_size=((self.width-self.width/10)/3, (self.width-self.width/10)/5),
                         background_normal="image/file%s-2.png"%ext,background_down="image/file%s-1.png"%ext,
                         size=((self.width-self.width/10)/3, (self.width-self.width/10)/5), size_hint=(None, None), font_size=self.width/50, color=(1,1,0,1))
      else:
        btn = ToggleButton(text=item, halign='center',valign='bottom',padding=(self.width/80,self.width/80),text_size=((self.width-self.width/10)/3, (self.width-self.width/10)/5),size=((self.width-self.width/10)/3, (self.width-self.width/10)/5), size_hint=(None, None), font_size=self.width/50, color=(1,1,0,1))
      layout.add_widget(btn, index=i)
    
  def DoRefreshFile1(self, text):
    i = 0
    list = []
    for i in range(30):
      list.append("Cam 1: YDXJ%04d.jpg" %i)
    print list
    self.current_screen.ids.boxFileList.clear_widgets()
    layout = Builder.load_string(self.BuildFileList(list))
    layout.bind(minimum_height=layout.setter('height'))

    sv = ScrollView(size_hint=(None, None), size=(self.current_screen.ids.boxFileList.width,
                    self.current_screen.ids.boxFileList.height), pos_hint={'center_x': .5, 'center_y': .5}, do_scroll_x=False)
    sv.add_widget(layout)
    self.current_screen.ids.boxFileList.add_widget(sv)
    for child in self.current_screen.ids.boxFileList.children[:]:
      print child
      
  def BuildFileList(self, list):
    buildstr = '''
GridLayout:
    padding: root.width/40, root.width/40, root.width/40, root.width/40
    spacing: root.width/40
    size_hint: None, None
    width: root.width
    cols: 3
    #size: root.width, (root.width-root.width/10)/5*1 + root.width/40
'''
    for item in list:
      ext = item[len(item)-3:len(item)].lower()
      buildstr += '''
    ToggleButton:
        text: '''
      buildstr += '"%s"' %item
      buildstr += '''
        size_hint: None, None
        size: (root.width-root.width/10)/3,(root.width-root.width/10)/5
        text_size: self.size
        font_size: root.width/50
        color: 1,1,0,1
        halign: "center"
        valign: "bottom"
        background_normal: '''
      buildstr += '"image/file%s-2.png"' %ext
      buildstr += '''
        background_down: '''
      buildstr += '"image/file%s-1.png"' %ext
    
    buildstr += '''
'''
    print buildstr
    return buildstr.replace("root.width",str(self.width))
      
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
    print "DoWifi wait start"
    wifioff.wait()
    self.transition = SlideTransition(direction = "right")
    wifioff.clear()
    self.stopdetect.clear()
    self.switch_to(Builder.load_file('data/connectscreen.kv'))
    self.current_screen.ids.btnConnect.text = ""
    self.DetectCam(45)
    print "DoWifi wait stop"
  
  def DoFileTaken(self, index):
    print "DoFileTaken start %d" %index
    while not self.cam[index].quit.isSet():
      self.cam[index].taken.wait()
      debugtxt = self.get_screen("camera").ids.txtDebug.text
      if self.cam[index].filetaken <> "":
        debugtxt += "\nCAM %d : " %(index+1) + self.cam[index].filetaken
        self.get_screen("camera").ids.txtDebug.text = debugtxt
      self.cam[index].taken.clear()
    print "DoFileTaken stop %d" %index

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

  def ReadConfig(self):
    print "readcfg"
    cfgfile = __file__.replace(basename(__file__), "data/camera.cfg")
    initstr = '''
    {
      "ip": "", 
      "camera": 0,
      "wifimode": 0,
      "defaultip": "",
      "stationip": "",
      "gateway": "",
      "ssid": "",
      "password": ""
    }
    '''
    r = []
    try:
      with open(cfgfile) as file:
        readstr = file.read()
        print "readstr", readstr
        cfg = json.loads(readstr)
        print "readcfg",cfg
      if cfg.has_key("config"):
        for item in cfg["config"]:
          cfginit = json.loads(initstr)
          cfginit.update(item)
          r.append(cfginit)
        print "r", r
        if len(r) < 2:
          cfginit = json.loads(initstr)
          cfginit["camera"] = 2
          r.append(cfginit)
      else:
        cfginit = json.loads(initstr)
        cfginit["camera"] = 1
        cfginit["ip"] = "192.168.42.1"
        cfginit["defaultip"] = "192.168.42.1"
        r.append(cfginit)
        cfginit = json.loads(initstr)
        cfginit["camera"] = 2
        r.append(cfginit)
    except StandardError:
      cfginit = json.loads(initstr)
      cfginit["camera"] = 1
      cfginit["ip"] = "192.168.42.1"
      cfginit["defaultip"] = "192.168.42.1"
      r.append(cfginit)
      cfginit = json.loads(initstr)
      cfginit["camera"] = 2
      r.append(cfginit)
    print r
    return r

  def WriteConfig(self):
    cfg = {}
    cfg["config"] = self.cfglist
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
    ponerine.duration = 0.7
    
    ConnectScreen = Builder.load_file('data/connectscreen.kv')
    ConnectScreen.name = 'connect'
    
    #FileManagerScreen = Builder.load_file('data/filemanagerscreen.kv')
    #FileManagerScreen.name = 'filemanager'
    
    CameraScreen = Builder.load_file('data/camerascreen.kv')
    CameraScreen.name = 'camera'
    
    #SettingScreen = Builder.load_file('data/settingscreen.kv')
    #SettingScreen.name = 'setting'
    
    ponerine.add_widget(ConnectScreen)
    #ponerine.add_widget(FileManagerScreen)
    ponerine.add_widget(CameraScreen)
    #ponerine.add_widget(SettingScreen)
    ponerine.current = 'connect'
    ponerine.DetectCam()
    #ponerine.switch_to(Builder.load_file('data/connectscreen.kv'))
    #ponerine.DetectCam()
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
