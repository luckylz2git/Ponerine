import kivy
# config ref
# http://www.cnblogs.com/sitemanager/p/4117687.html
# ConfigParser - Configuration file parser
# https://docs.python.org/2/library/configparser.html
kivy.require('1.9.0')

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager , SlideTransition
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
#from kivy.uix.progressbar import ProgressBar
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
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

Builder.load_file('data/connectscreen.kv')
Builder.load_file('data/filemanagerscreen.kv')
Builder.load_file('data/camerascreen.kv')
Builder.load_file('data/settingscreen.kv')
Builder.load_file('data/injectionscreen.kv')

#print "Clock.max_iteration", Clock.max_iteration
Clock.max_iteration = 100
__version__='0.1.2'

class ConnectScreen(Screen):
  pass

class FileManagerScreen(Screen):
  pass
  
class CameraScreen(Screen):
  pass

class SettingScreen(Screen):
  pass
  
class InjectionScreen(Screen):
  pass

class ConfigPopup(Popup):
  cfg = ObjectProperty()
  apply = BooleanProperty()

class DeletePopup(Popup):
  apply = BooleanProperty()

class RebootPopup(Popup):
  apply = BooleanProperty()
  index = NumericProperty()

class Ponerine(ScreenManager):
  def __init__(self, appexit):
    super(Ponerine, self).__init__()
    
    #self.config = ConfigParser()
    #self.BuildConfig(self.config)
    #print "__init__",self.config
    #self.cfgtoken = cfgtoken
    #self.cfgevent = cfgevent
    self.applyconfig = False
    self.settings = "" #SettingsWithNoMenu
    self.injectsetting = "" #SettingsWithNoMenu
    self.appexit = appexit
    self.screen = []
    self.cfglist = []
    self.cfglist = self.ReadConfig()
    self.stopdetect = threading.Event()
    sysname = platform.system()
    self.totaldownloadsize = 0
    self.currentdownloadsize = 0
    self.showfiletotal = threading.Event()
    self.showfiletotal.set()
    if sysname == "Windows":
      Window.size = (560,800)
    elif sysname == "Darwin":
      Window.size = (520,700)
      
  def GetFileSize(self, sizebyte, unit=""):
    pres = ["B", "KB", "MB", "GB", "TB"]
    value = float(sizebyte)
    option = 0
    if unit == "":
      while value > 1024:
        value = value/float(1024)
        option += 1
      
      return("%.2f %s" %(value, pres[option]))
    else:
      i = 0
      for u in pres:
        if u.lower() == unit.lower():
          break
        i += 1
      while True:
        if option > 4 or i == option:
          return ("%.2f %s" %(value, pres[option]))
        value = value/float(1024)
        option += 1
        
  def DownloadFile(self):
    str = self.current_screen.ids.lstCamera.text.replace("Camera","").replace(" ","")
    index = -1
    if str.isdigit():
      index = int(str) - 1
      threading.Thread(target=self.DoDownloadFile, args=(index,), name="DoDownloadFile").start()
      self.current_screen.ids.btnDownload.text = "Download"
      self.current_screen.ids.btnDownload.disabled = True
      self.current_screen.ids.btnDelete.text = "Delete"
      self.current_screen.ids.btnDelete.disabled = True
      #self.DoDownloadFile(index)

  def DeleteFile(self):
    str = self.current_screen.ids.lstCamera.text.replace("Camera","").replace(" ","")
    index = -1
    if str.isdigit():
      index = int(str) - 1
      threading.Thread(target=self.DoDeleteFile, args=(index,), name="DoDeleteFile").start()
      self.current_screen.ids.btnDownload.text = "Download"
      self.current_screen.ids.btnDownload.disabled = True
      self.current_screen.ids.btnDelete.text = "Delete"
      self.current_screen.ids.btnDelete.disabled = True
      
  def FilterFile(self, text):
    if text <> "File Type" and self.showfiletotal.isSet():
      self.current_screen.ids.glFileList.clear_widgets()
      threading.Thread(target=self.DoFilterFile, args=(text[0:3].lower(),), name="DoFilterFile").start()
  
  def SelectCamera(self, instance):
    str = self.current_screen.ids.lstCamera.text.replace("Camera","").replace(" ","")
    index = -1
    if str.isdigit():
      self.current_screen.ids.btnDownload.disabled = True
      self.current_screen.ids.btnDelete.disabled = True
      #self.current_screen.ids.lstSelection.text = "Selection"
      self.current_screen.ids.lstSelection.disabled = True
      index = int(str) - 1
      if isinstance(self.current_screen.ids.boxProgress.children[0], Label):
        self.current_screen.ids.boxProgress.children[0].text = ""
      self.current_screen.ids.glFileList.clear_widgets()
      threading.Thread(target=self.DoRefreshFile, args=(index,), name="DoRefreshFile").start()
      
  def SelectFile(self, instance):
    if instance.text == "Clear All":
      #Loop Clear
      while len(self.file_dict_adapter.selection) > 0:
        self.file_dict_adapter.deselect_list(self.file_dict_adapter.selection)
    elif instance.text == "Select All":
      #Loop Clear
      while len(self.file_dict_adapter.selection) > 0:
        self.file_dict_adapter.deselect_list(self.file_dict_adapter.selection)
      #Select All
      list = []
      ln = self.file_dict_adapter.get_count()
      for i in range(ln):
        for child in self.file_dict_adapter.get_view(i).children[:]:
          if isinstance(child, ListItemButton):
            list.append(child)
      self.file_dict_adapter.select_list(list)
    elif instance.text == "Invert Select":
      oldlist = []
      #Get File Name
      if len(self.file_dict_adapter.selection) > 0:
        for item in self.file_dict_adapter.selection:
          oldlist.append(item.text)
        print oldlist
        #Loop Clear
        while len(self.file_dict_adapter.selection) > 0:
          self.file_dict_adapter.deselect_list(self.file_dict_adapter.selection)
      #Select All
      list = []
      ln = self.file_dict_adapter.get_count()
      for i in range(ln):
        for child in self.file_dict_adapter.get_view(i).children[:]:
          if isinstance(child, ListItemButton):
            if len(oldlist) == 0:
              list.append(child)
            elif child.text not in oldlist:
              list.append(child)
      self.file_dict_adapter.select_list(list)
    elif instance.text == "Undownload":
      #Loop Clear
      while len(self.file_dict_adapter.selection) > 0:
        self.file_dict_adapter.deselect_list(self.file_dict_adapter.selection)
      #Select All
      list = []
      ln = self.file_dict_adapter.get_count()
      for i in range(ln):
        for child in self.file_dict_adapter.get_view(i).children[:]:
          if isinstance(child, ListItemButton):
            for item in self.filelist:
              if item["name"] == child.text:
                if not self.CheckDownloadHistory(item["name"],item["date"],item["size"]):
                  list.append(child)
      self.file_dict_adapter.select_list(list)
    elif instance.text == "Downloaded":
      #Loop Clear
      while len(self.file_dict_adapter.selection) > 0:
        self.file_dict_adapter.deselect_list(self.file_dict_adapter.selection)
      #Select All
      list = []
      ln = self.file_dict_adapter.get_count()
      for i in range(ln):
        for child in self.file_dict_adapter.get_view(i).children[:]:
          if isinstance(child, ListItemButton):
            for item in self.filelist:
              if item["name"] == child.text:
                if self.CheckDownloadHistory(item["name"],item["date"],item["size"]):
                  list.append(child)
      self.file_dict_adapter.select_list(list)
    instance.text = "Selection"

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
    #print self.current_screen.ids.btnConnect.background_normal
    self.stopdetect.set()
    if self.current_screen.ids.btnConnect.text == "" or self.current_screen.ids.btnConnect.text == "Error":
      self.cam = []
      self.config = []
      print "ip list" ,len(self.cfglist), self.cfglist
      i = 0
      for cfg in self.cfglist:
        print "ip list %s" %cfg["ip"]
        if cfg["ip"] <> "":
          self.cam.append(Camera(cfg["ip"]))
          self.config.append(ConfigParser(name='cam%d'%i))
          i += 1
      if len(self.cam) > 0:
        self.tconn= threading.Thread(target=self.DoConnect)
        self.tconn.setName('DoConnect')
        self.tconn.start()
      else:
        self.ConfigPopupOpen(0)
    
  def Disconnect(self):
    #self.transition = SlideTransition(direction = "right")
    self.switch_to(self.screen[0],direction = "right")
    self.current_screen.ids.btnConnect.text = ""
    threading.Thread(target=self.DoDisconnect, name="DoDisconnect").start()

  def FileManager(self):
    if self.current_screen.name in ("camera","setting","injection"):
      dirct = "right"
    else:
      dirct = "left"
    self.switch_to(self.screen[1],direction = dirct)
    self.current_screen.ids.lstCamera.text = "Camera"
    self.filelist = []
    self.selectlist = []
    camlist = []
    for i in range(len(self.cam)):
      camlist.append('Camera %d'%(i+1))
    self.current_screen.ids.lstFileType.text = "File Type"
    self.current_screen.ids.lstSelection.text = "Selection"
    self.current_screen.ids.lstSelection.disabled = True
    self.current_screen.ids.btnDownload.disabled = True
    self.current_screen.ids.btnDelete.disabled = True
    if len(camlist) > 0:
      self.current_screen.ids.lstCamera.values = camlist
      self.current_screen.ids.lstCamera.text = camlist[0]
    
  def Camera(self):
    if self.current_screen.name in ("setting","injection"):
      dirct = "right"
    else:
      dirct = "left"
    self.switch_to(self.screen[2],direction = dirct)

  def Setting(self):
    if self.current_screen.name in ("injection"):
      dirct = "right"
    else:
      dirct = "left"
    self.switch_to(self.screen[3],direction = dirct)
    camlist = []
    for i in range(len(self.cam)):
      camlist.append('Camera %d Setting'%(i+1))
    if len(camlist) > 0:
      self.current_screen.ids.lstCamera.values = camlist
      self.current_screen.ids.lstCamera.text = camlist[0]
  
  def Injection(self):
    self.switch_to(self.screen[4],direction = "left")
    camlist = []
    for i in range(len(self.cam)):
      camlist.append('Camera %d Injection'%(i+1))
    if len(camlist) > 0:
      self.current_screen.ids.lstCamera.values = camlist
      self.current_screen.ids.lstCamera.text = camlist[0]
  
  def InjectCamera(self, instance):
    camtext = instance.text
    if camtext == "Camera Injection":
      return
    index = int(camtext.replace('Camera ','').replace(' Injection','')) - 1
    
    threading.Thread(target=self.DoInjection, args=(index,), name="DoInjection"+str(index)).start()
    instance.text = "Camera Injection"
  
  def InjectApply(self):
    pass
  
  def DoInjection(self, index):
    self.BuildConfig("injection", self.config[index], {})
    self.applyconfig = False
    self.BuildInjection(index, self.config[index])
    self.current_screen.ids.boxInjectSetting.clear_widgets()
    self.current_screen.ids.boxInjectSetting.add_widget(self.injectsetting)
    self.applyconfig = True
  
  def BuildInjection(self, index, config):
    if isinstance(self.injectsetting, SettingsWithNoMenu):
      return
    else:
      jsondata = '['
      c = CameraSetting()
      jsondata += c.BuildSetting("hack_wifi_mode") + ","
      jsondata += c.BuildSetting("enable_info_display") + ","
      jsondata += c.BuildSetting("hack_video_resolution") + ","
      jsondata += c.BuildSetting("hack_timelapse_video_resolution") + ","
      jsondata += c.BuildSetting("hack_video_bitrate") + ","
      jsondata += c.BuildSetting("hack_raw_photo")
      jsondata += ']'
      self.injectsetting = SettingsWithNoMenu(size_hint=(1,1))
      self.injectsetting.add_json_panel('Camera %d Injection, needs reboot.' %(index+1), config, data = jsondata)
    
  def RebootPopupOpen(self, index):
    self.rebootpop = RebootPopup(title='Reboot Confirmation', size_hint=(0.8, 0.35), size=self.size)
    self.rebootpop.bind(on_dismiss=self.RebootPopupApply)
    self.rebootpop.apply = False
    self.rebootpop.index = index
    self.rebootpop.open()
    
  def RebootPopupApply(self, popup):
    if popup.apply:
      self.cam[popup.index].Reboot()
  
  def DeletePopupOpen(self):
    self.deletepop = DeletePopup(title='Delete Confirmation', size_hint=(0.8, 0.35), size=self.size)
    self.deletepop.bind(on_dismiss=self.DeletePopupApply)
    self.deletepop.apply = False
    self.deletepop.open()
    
  def DeletePopupApply(self, popup):
    if popup.apply:
      self.DeleteFile()
  
  def ConfigPopupOpen(self, index):
    print type(self.parent)
    print "Config Popup Open index %d" %index, self.cfglist
    self.stopdetect.set()
    self.configpop = ConfigPopup(title='Connection Config - Camera %d' %(index+1), size_hint=(0.8, 0.85), size=self.size, cfg=self.cfglist[index], index=index)
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
      self.cfglist = self.ReadConfig()
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
      while not cam.link:
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
      self.Camera()
      i = 0
      for cam in self.cam:
        #time.sleep(1)
        threading.Thread(target=self.DoWifi, args=(cam.wifioff,), name="DoWifi"+str(i)).start()
        #time.sleep(1)
        threading.Thread(target=self.DoFileTaken, args=(i,), name="DoFileTaken"+str(i)).start()
        #time.sleep(1)
        #threading.Thread(target=self.DoConfig, args=(self.cfgevent,i,), name="DoConfig"+str(i)).start()
        if cam.cfgdict == {}:
          cam.SendMsg('{"msg_id":3}')
        i +=1
  
  def DoDisconnect(self):
    try:
      for cam in self.cam:
        cam.UnlinkCamera()
    except:
      pass
    self.stopdetect.clear()
    self.DetectCam()
  
  # fun DoFilterFile0(self, filter):
    # layout = GridLayout(cols=4, padding=self.width/60, spacing=self.width/60, size_hint=(None, None), width = self.width)
    # layout.bind(minimum_height=layout.setter('height'))

    # bshow = False
    # if len(self.filelist) > 0:
      # i = 0
      # for item in self.filelist:
        # if filter == "all":
          # ext = "all"
        # else:
          # ext = item[len(item)-3:len(item)].lower()
        # if filter == ext:
          # bshow = True
          # btn = ToggleButton(text=item, size=((self.width-self.width/12)/4, (self.width-self.width/12)/10), size_hint=(None, None))
          # layout.add_widget(btn,index=i)
          # i += 0
    # if bshow:
      # sv = ScrollView(size_hint=(None, None), size=(self.current_screen.ids.glFileList.width,self.current_screen.ids.glFileList.height), 
                    # pos_hint={'center_x': .5, 'center_y': .5}, do_scroll_x=False)
      # sv.add_widget(layout)
      # self.current_screen.ids.glFileList.clear_widgets()
      # self.current_screen.ids.glFileList.add_widget(sv)
    # else:
      # self.current_screen.ids.glFileList.clear_widgets()
      # if filter == "all":
        # lbl = Label(text="No Files In Camera !", font_size=self.width/30)
      # else:
        # lbl = Label(text="No %s Files In Camera !"%(filter.upper()), font_size=self.width/30)
      # self.current_screen.ids.glFileList.add_widget(lbl)
  def GetDownloadDir(self, index):
    r = ""
    if index >= len(self.cfglist):
      return r
    if "download" in self.cfglist[index].keys():
      r = self.cfglist[index]["download"]
    if r == "":
      r = "/mnt/sdcard/pronerine/download/camera%d"%(index+1)
    else:
      r = r + "/camera%d"%(index+1)
    if os.path.isdir(r):
      return r
    try:
      os.makedirs(r,0o777)
      return r
    except StandardError as err:
      print err
      return ""
    
  def DoDownloadFile(self, index):
    downdir = self.GetDownloadDir(index)
    #print "downdir",downdir
    if downdir == "" and isinstance(self.current_screen.ids.boxProgress.children[0], Label):
      self.current_screen.ids.boxProgress.children[0].text = "error: can not create download dir"
      self.current_screen.ids.btnDownload.text = "Download"
      return
      
    cam = self.cam[index]

    glProgress = GridLayout(cols=4, size_hint=(None,None),size=(self.width,self.width/10))
    lblFileName = Label(size_hint=(None,None),size=(self.width*0.4,self.width/10),color=(1,1,0,1),font_size=self.width/40,text_size=(self.width*0.4,self.width/10),halign='center',valign='middle')
    lblFilePercent = Label(size_hint=(None,None),size=(self.width*0.1,self.width/10),color=(1,1,0,1),font_size=self.width/40,text_size=(self.width*0.2,self.width/10),halign='center',valign='middle')
    lblFileSize = Label(size_hint=(None,None),size=(self.width*0.3,self.width/10),color=(1,1,0,1),font_size=self.width/40,text_size=(self.width*0.2,self.width/10),halign='center',valign='middle')
    lblFileTime = Label(size_hint=(None,None),size=(self.width*0.2,self.width/10),color=(1,1,0,1),font_size=self.width/40,text_size=(self.width*0.2,self.width/10),halign='center',valign='middle')

    glProgress.add_widget(lblFileName)
    glProgress.add_widget(lblFilePercent)
    glProgress.add_widget(lblFileSize)
    glProgress.add_widget(lblFileTime)
    
    self.current_screen.ids.boxProgress.clear_widgets()
    self.current_screen.ids.boxProgress.add_widget(Label(text='start to download',size_hint=(1,1),color=(1,1,0,1),font_size=self.width/40))

    i = 0
    e = 0
    ln = len(self.selectlist)
    self.currentdownloadsize = 0
    total = 0
    for file in self.selectlist:
      #lblFileTotal.text = "status:  %d downloaded  %d remains"%(i,ln-i) if e == 0 else "status:  %d downloaded  %d remains  %d error"%(i,ln-i-e,e)
      #lblFileName.text = "{0}\n".format(file)
      #lblFileName.text += "d%d/e%d/t%d" %(i,ln-i-e,e)
      #pct = "%0.2f" %cam.dlstatus["percent"]
      #lblFilePercent.text = "\n{0} %".format()
      cam.StartWebDownload(file, downdir)
      cam.dlstart.wait()
      self.currentdownloadsize += total
      fetchall = self.currentdownloadsize
      #print "self.currentdownloadsize" ,self.currentdownloadsize
      if i+e == 0:
        self.current_screen.ids.boxProgress.clear_widgets()
        self.current_screen.ids.boxProgress.height = self.width / 10
        self.current_screen.ids.boxProgress.add_widget(glProgress)
      while True:
        #print cam.dlstatus
        
        if cam.dlerror.isSet():
          lblFileName.text = "%s ( error )" %file
          e += 1
          time.sleep(5)
          break
        if cam.dlstop.isSet():
          i += 1
          if ln > 1:
            pct = "100.00 %\n"
            pct += "%0.2f" %(float(fetch)/self.totaldownloadsize*100)
            pct += " %"
            lblFilePercent.text = pct
          else:
            lblFilePercent.text = "100.00 %"
          self.WriteDownloadHistory(file, downdir)
          break
        
        speed = cam.dlstatus["speed"]
        fname = "{0}\n".format(file)
        fname += "%d/%d @ %s/s" %(i+1,ln,self.GetFileSize(speed)) if e==0 else "%d/%d(e%d) @ %s/s" %(i+1,ln,e,self.GetFileSize(speed))
        pct = ""
        fsize = ""
        ftime = ""
        lblFileName.text = fname
        total = int(cam.dlstatus["total"])
        #print "total" ,total
        if total > 0:
          fetch = cam.dlstatus["fetch"]
          pct = "%0.2f" %(float(fetch)/total*100)
          #print "lblFilePercent", lblFilePercent.text
          pct += " %"
          totalsize = self.GetFileSize(total)
          ext = totalsize[len(totalsize)-2:len(totalsize)]
          #print "ext",ext
          fetchsize = self.GetFileSize(fetch,ext).replace(ext,"").replace(" ","")
          #print "fetchsize" ,fetchsize
          fsize = "%s/%s" %(fetchsize,totalsize)
          if speed > 0:
            remain = total - fetch
            ftime = "%s" %(self.Second2Time(remain/speed))
            #print "lblFileTime",lblFileTime.text
            
        if ln >1 and self.totaldownloadsize > 0:
          fetch = fetchall + cam.dlstatus["fetch"]
          pct += "\n%0.2f" %(float(fetch)/self.totaldownloadsize*100)
          #print "lblFilePercent", lblFilePercent.text
          pct += " %"
          totalsize = self.GetFileSize(self.totaldownloadsize)
          ext = totalsize[len(totalsize)-2:len(totalsize)]
          fetchsize = self.GetFileSize(fetch,ext).replace(ext,"").replace(" ","")
          fsize += "\n%s/%s" %(fetchsize,totalsize)
          if speed > 0:
            remain = self.totaldownloadsize - fetch
            ftime += "\n%s" %(self.Second2Time(remain/speed))
            #print "lblFileTime",lblFileTime.text
        
        if pct <> "":
          lblFilePercent.text = pct
        if fsize <> "":
          lblFileSize.text = fsize
        if ftime <> "":
          lblFileTime.text = ftime
        cam.dlstop.wait(1)
      
    #cam.DisconnectData()
    self.current_screen.ids.boxProgress.clear_widgets()
    self.current_screen.ids.boxProgress.height = self.width / 20
    self.current_screen.ids.boxProgress.add_widget(Label(color=(1,1,0,1),font_size=self.width/40))
    self.showfiletotal.clear()
    oldtext = self.current_screen.ids.lstFileType.text[0:3].lower()
    #self.current_screen.ids.lstFileType.text = "File Type"
    if oldtext == "fil":
      oldtext = "all"
    #self.current_screen.ids.btnDownload.text = "Download"
    #self.current_screen.ids.btnDownload.disabled = True
    self.DoFilterFile(oldtext)
    #self.showfiletotal.wait()
    self.current_screen.ids.btnDownload.text = "Download"
    self.showfiletotal.set()
    if isinstance(self.current_screen.ids.boxProgress.children[0], Label):
      self.current_screen.ids.boxProgress.children[0].text = "status:  %d downloaded"%i if e == 0 else "status:  %d downloaded  %d error"%(i,e)

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
      
  def DoDeleteFile(self, index):
    cam = self.cam[index]

    lblFileTotal = Label(size_hint=(None,None),size=(self.width,self.width/20),color=(1,1,0,1),font_size=self.width/40)

    self.current_screen.ids.boxProgress.clear_widgets()
    self.current_screen.ids.boxProgress.add_widget(lblFileTotal,index=0)

    i = 0
    e = 0
    ln = len(self.selectlist)
    for file in self.selectlist:
      lblFileTotal.text = "status:  %d deleted  %d remains"%(i,ln-i) if e == 0 else "status:  %d deleted  %d remains  %d error"%(i,ln-i-e,e)
      cam.StartDelete(file)
      cam.dlstop.wait()
      if cam.dlerror.isSet():
        e += 1
      else:
        i += 1

    self.current_screen.ids.boxProgress.clear_widgets()
    self.current_screen.ids.boxProgress.height = self.width / 20
    self.current_screen.ids.boxProgress.add_widget(Label(color=(1,1,0,1),font_size=self.width/40))
    self.showfiletotal.clear()
    oldtext = self.current_screen.ids.lstFileType.text
    print oldtext
    self.current_screen.ids.glFileList.clear_widgets()
    self.DoRefreshFile(index) #, False)
    if oldtext[0:3].lower() in ("jpg","mp4","raw"):
      self.DoFilterFile(oldtext[0:3].lower())
    self.showfiletotal.clear()
    self.current_screen.ids.lstFileType.text = oldtext
    self.current_screen.ids.btnDelete.text = "Delete"
    self.showfiletotal.set()
    if isinstance(self.current_screen.ids.boxProgress.children[0], Label):
      self.current_screen.ids.boxProgress.children[0].text = "status:  %d deleted"%i if e == 0 else "status:  %d deleted  %d error"%(i,e)
    
  def SelectTest(self, instance, *args):
    #return
    for item in instance.selection:
      print "SelectTest", type(item), item.text
    
  def SelectChange(self, instance):
    #print type(instance)
    self.selectlist = []
    i = len(instance.selection)
    ln = len(self.file_dict_adapter.data)
    if i > 0:
      self.totaldownloadsize = 0
      for item in instance.selection:
        self.selectlist.append(item.text)
        for file in self.filelist:
          if item.text == file["name"]:
            #print file["size"]
            self.totaldownloadsize += file["size"]
      #print self.totaldownloadsize
      self.current_screen.ids.btnDownload.disabled = False
      self.current_screen.ids.btnDelete.disabled = False
      if self.showfiletotal.isSet() and isinstance(self.current_screen.ids.boxProgress.children[0], Label):
        self.current_screen.ids.boxProgress.children[0].text = "%d of %d selected" %(i,ln)
    else:
      self.totaldownloadsize = 0
      self.current_screen.ids.btnDownload.disabled = True
      self.current_screen.ids.btnDelete.disabled = True
      if self.showfiletotal.isSet() and isinstance(self.current_screen.ids.boxProgress.children[0], Label):
        self.current_screen.ids.boxProgress.children[0].text = "1 file" if ln == 1 else "%d files"%ln
    
  def DoRefreshFile(self, index, showlabel = True):
    downdir = self.GetDownloadDir(index)
    if downdir <> "":
      self.ReadDownloadHistory(downdir)
      
    if showlabel:
      info = "Loading Camera %d File List "%(index+1)
      #print info
      lbl = Label(text=info, font_size=self.width/30)
      self.current_screen.ids.glFileList.add_widget(lbl)
      i = 0
    
    self.filelist = []
    self.current_screen.ids.lstFileType.text = "File Type"
    cam = self.cam[index]
    cam.RefreshFile()
    while True:
      cam.lsdir.wait(1)
      if cam.lsdir.isSet():
        #print "break first"
        break
      #print info + "."*i
      if showlabel:
        lbl.text = info + "."*i
        i = (i+1) % 4
    if len(cam.listing) > 0:
      cam.RefreshFile(cam.status["pwd"] + "/" + cam.listing[0]["name"])
      while True:
        cam.lsdir.wait(1)
        if cam.lsdir.isSet():
          #print "break second"
          break
        #print info + "."*i
        if showlabel:
          lbl.text = info + "."*i
          i = (i+1) % 4
    if len(cam.listing) > 0:
      self.filelist = cam.listing
      #print "self.filelist",self.filelist
      if showlabel:
        self.DoFilterFile("all")
    else:
      self.current_screen.ids.lstSelection.disabled = True
      self.current_screen.ids.glFileList.clear_widgets()
      lbl = Label(text="No Files In Camera !", font_size=self.width/30)
      self.current_screen.ids.glFileList.add_widget(lbl)

  def DoFilterFile(self, filter):
    fdict = {}
    i = 0
    for item in self.filelist:
      #print item
      if filter == "all":
        ext = "all"
      else:
        ext = item["name"][len(item["name"])-3:len(item["name"])].lower()
      if filter == ext:
        i += 1
        #item["index"] = str(i)
        #item["is_selected"] = True #False
        fdict[str(i)] = {}
        fdict[str(i)].update(item)
        if self.CheckDownloadHistory(item["name"],item["date"],item["size"]):
          fdict[str(i)]["index"] = "*%s*" %str(i)
        else:
          fdict[str(i)]["index"] = str(i)
        fdict[str(i)]["is_selected"] = True
        #print i
        #print item
    if i == 0:
      self.current_screen.ids.glFileList.clear_widgets()
      if self.showfiletotal.isSet() and isinstance(self.current_screen.ids.boxProgress.children[0], Label):
        self.current_screen.ids.boxProgress.children[0].text = "0 file"
      return
    #print fdict
    #return
    file_args_converter = lambda row_index, rec: {
         'text': rec['name'],
         'size_hint_y': None,
         'height': self.width/15,
         'cls_dicts':[{'cls': ListItemLabel,'kwargs': {'text': rec['index'],'size_hint_x': 0.2,'deselected_color':[0,0,0,1],'selected_color':[0.8,0.8,0.8,0.8]}},
                    {'cls': ListItemButton,'kwargs': {'text': rec['name'],'is_representing_cls': True,'size_hint_x': 0.5,'deselected_color':[0,0,0,1],'selected_color':[0.8,0.8,0.8,0.8] }},
                    {'cls': ListItemLabel,'kwargs': {'text': self.GetFileSize(rec['size']),'size_hint_x': 0.3,'deselected_color':[0,0,0,1],'selected_color':[0.8,0.8,0.8,0.8]}},
                    {'cls': ListItemLabel,'kwargs': {'text': rec['date'],'size_hint_x': 0.5,'deselected_color':[0,0,0,1],'selected_color':[0.8,0.8,0.8,0.8]}}
                    ]}
    #file_sorted = sorted(fdict.keys())
    file_sorted = ["{0}".format(index+1) for index in range(i)]
    #selection_mode='single'/'multiple'
    self.file_dict_adapter = DictAdapter(sorted_keys=file_sorted,data=fdict,args_converter=file_args_converter,
                                selection_mode='multiple',allow_empty_selection=True,cls=CompositeListItem)
    #self.file_dict_adapter.bind(selection=self.SelectChange)
    self.file_dict_adapter.bind(on_selection_change=self.SelectChange)
    self.file_list_view = ListView(adapter=self.file_dict_adapter)
    self.current_screen.ids.glFileList.clear_widgets()
    self.current_screen.ids.glFileList.add_widget(self.file_list_view)
    if self.showfiletotal.isSet() and isinstance(self.current_screen.ids.boxProgress.children[0], Label):
      self.current_screen.ids.boxProgress.children[0].text = "1 file" if i == 1 else "%d files"%i
    self.current_screen.ids.lstSelection.disabled = False
    self.showfiletotal.set()
    
  # fun DoRefreshFile2(self, text):
    # i = 0
    # list = []
    # for i in range(30):
      # list.append("Cam 1: YDXJ%04d.jpg" %i)
    # self.current_screen.ids.glFileList.clear_widgets()
    # layout = GridLayout(cols=3, padding=self.width/40, spacing=self.width/40, size_hint=(None, None), width = self.width)
    # layout.bind(minimum_height=layout.setter('height'))

    # sv = ScrollView(size_hint=(None, None), size=(self.current_screen.ids.glFileList.width,
                    # self.current_screen.ids.glFileList.height), pos_hint={'center_x': .5, 'center_y': .5}, do_scroll_x=False)
    # sv.add_widget(layout)
    # self.current_screen.ids.glFileList.add_widget(sv) 
    
    # for item in list:
      # ext = item[len(item)-3:len(item)].lower()
      # if ext in ("jpg","mp4","raw"):
        # btn = ToggleButton(text=item, halign="center",valign="bottom",padding=(self.width/80,self.width/80),text_size=((self.width-self.width/10)/3, (self.width-self.width/10)/5),
                         # background_normal="image/file%s-2.png"%ext,background_down="image/file%s-1.png"%ext,
                         # size=((self.width-self.width/10)/3, (self.width-self.width/10)/5), size_hint=(None, None), font_size=self.width/50, color=(1,1,0,1))
      # else:
        # btn = ToggleButton(text=item, halign='center',valign='bottom',padding=(self.width/80,self.width/80),text_size=((self.width-self.width/10)/3, (self.width-self.width/10)/5),size=((self.width-self.width/10)/3, (self.width-self.width/10)/5), size_hint=(None, None), font_size=self.width/50, color=(1,1,0,1))
      # layout.add_widget(btn, index=i)
    
  # fun DoRefreshFile1(self, text):
    # i = 0
    # list = []
    # for i in range(30):
      # list.append("Cam 1: YDXJ%04d.jpg" %i)
    # print list
    # self.current_screen.ids.glFileList.clear_widgets()
    # layout = Builder.load_string(self.BuildFileList(list))
    # layout.bind(minimum_height=layout.setter('height'))

    # sv = ScrollView(size_hint=(None, None), size=(self.current_screen.ids.glFileList.width,
                    # self.current_screen.ids.glFileList.height), pos_hint={'center_x': .5, 'center_y': .5}, do_scroll_x=False)
    # sv.add_widget(layout)
    # self.current_screen.ids.glFileList.add_widget(sv)
    # for child in self.current_screen.ids.glFileList.children[:]:
      # print child
      
  # fun BuildFileList(self, list):
    # buildstr = '''
# GridLayout:
    # padding: root.width/40, root.width/40, root.width/40, root.width/40
    # spacing: root.width/40
    # size_hint: None, None
    # width: root.width
    # cols: 3
#    size: root.width, (root.width-root.width/10)/5*1 + root.width/40
# '''
    # for item in list:
      # ext = item[len(item)-3:len(item)].lower()
      # buildstr += '''
    # ToggleButton:
        # text: '''
      # buildstr += '"%s"' %item
      # buildstr += '''
        # size_hint: None, None
        # size: (root.width-root.width/10)/3,(root.width-root.width/10)/5
        # text_size: self.size
        # font_size: root.width/50
        # color: 1,1,0,1
        # halign: "center"
        # valign: "bottom"
        # background_normal: '''
      # buildstr += '"image/file%s-2.png"' %ext
      # buildstr += '''
        # background_down: '''
      # buildstr += '"image/file%s-1.png"' %ext
    
    # buildstr += '''
# '''
    # print buildstr
    # return buildstr.replace("root.width",str(self.width))
      
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
  
  #def DoConfig(self, cfgevent, index):
  def DoConfig(self):
    return
    while not self.appexit.isSet():
      print "start cfgevent wait"
      cfgevent.wait()
      print "get cfgevent set"
      if self.applyconfig:
        global cfgtoken
        print "changesetting", cfgtoken
        token = (cfgtoken[0],cfgtoken[1])
        if token == ('setting', 'video_resolution'):
          self.cam[index].ChangeSetting(cfgtoken[1],cfgtoken[2])
        cfgevent.clear()
        while not self.appexit.isSet():
          self.cam[index].setok.wait(1)
          if self.cam[index].setok.isSet():
            break
          self.cam[index].seterror.wait(1)
          if self.cam[index].seterror.isSet():
            break
      else:
        cfgevent.clear()
        
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
    self.cam[index].setallok.wait(15)
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

  def ReadSetting(self, instance):
    camtext = instance.text
    if camtext == "Camera Setting":
      return
    index = int(camtext.replace('Camera ','').replace(' Setting','')) - 1
    
    threading.Thread(target=self.DoReadSetting, args=(index,), name="DoReadSetting"+str(index)).start()
    instance.text = "Camera Setting"
  
  def DoReadSetting(self, index):
    self.current_screen.ids.boxCameraSetting.clear_widgets()
    settings = []
    cam = self.cam[index]
    if cam.cfgdict == {}:
      cam.ReadAllStatus()
      while True:
        cam.setok.wait(1)
        if cam.setok.isSet():
          break
        if cam.seterror.isSet():
          print "DoReadSetting ReadAllStatus Error"
          return
      settings = cam.settings
      cam.settings = []
      if cam.webportopen:
        cam.RenewToken()

    self.BuildConfig("setting", self.config[index], cam.cfgdict)
    self.applyconfig = False
    #debugtxt += "\nCAM %d Settings :\n" %i + settings
    #print "Camera %d" %(index+1), settings
    if cam.webportopen:
      cam.RenewToken()
      
    self.BuildSetting(index, self.config[index], settings)
          
    self.current_screen.ids.boxCameraSetting.add_widget(self.settings)
    self.applyconfig = True
    #print "key:",key,"value:",value
    #self.current_screen.ids.txtDebug.text = debugtxt
    
  def BuildSetting(self, index, config, camsetting):
    if isinstance(self.settings, SettingsWithNoMenu):
      return
      
    print "start to build setting"
    vstand = ""
    for item in camsetting:
      for key,value in item.items():
        if key == "video_standard":
          vstand = "_" + value
          break

    jsondata = '['
    c = CameraSetting()
    # Add Video Sections
    jsondata += c.BuildSetting("rec_mode") + ","
    jsondata += c.BuildSetting("rec_default_mode") + ","
    jsondata += c.BuildSetting("video_standard") + ","
    jsondata += c.BuildSetting("video_resolution" + vstand) + ","
    jsondata += c.BuildSetting("timelapse_video_resolution" + vstand) + ","
    jsondata += c.BuildSetting("timelapse_video") + ","
    jsondata += c.BuildSetting("video_quality") + ","
    jsondata += c.BuildSetting("video_stamp") + ","
    jsondata += c.BuildSetting("video_rotate") + ","
    jsondata += c.BuildSetting("loop_record") + ","
    jsondata += c.BuildSetting("emergency_file_backup") + ","
    jsondata += c.BuildSetting("record_photo_time") + ","
    # Add Photo Sections
    jsondata += c.BuildSetting("capture_mode") + ","
    jsondata += c.BuildSetting("capture_default_mode") + ","
    jsondata += c.BuildSetting("photo_size") + ","
    jsondata += c.BuildSetting("photo_quality") + ","
    jsondata += c.BuildSetting("photo_stamp") + ","
    jsondata += c.BuildSetting("precise_cont_time") + ","
    jsondata += c.BuildSetting("precise_selftime") + ","
    jsondata += c.BuildSetting("precise_self_running") + ","
    jsondata += c.BuildSetting("burst_capture_number") + ","
    # Add System Sections
    jsondata += c.BuildSetting("system_mode") + ","
    jsondata += c.BuildSetting("system_default_mode") + ","
    jsondata += c.BuildSetting("meter_mode") + ","
    jsondata += c.BuildSetting("preview_status") + ","
    jsondata += c.BuildSetting("start_wifi_while_booted") + ","
    jsondata += c.BuildSetting("auto_low_light") + ","
    jsondata += c.BuildSetting("auto_power_off") + ","
    jsondata += c.BuildSetting("buzzer_volume") + ","
    jsondata += c.BuildSetting("buzzer_ring") + ","
    jsondata += c.BuildSetting("led_mode") + ","
    jsondata += c.BuildSetting("osd_enable") + ","
    jsondata += c.BuildSetting("rc_button_mode") + ","
    jsondata += c.BuildSetting("video_output_dev_type") + ","
    # Add System Readonly
    jsondata += c.BuildSetting("camera_clock") + ","
    jsondata += c.BuildSetting("wifi_ssid") + ","
    jsondata += c.BuildSetting("wifi_password") + ","
    jsondata += c.BuildSetting("serial_number") + ","
    jsondata += c.BuildSetting("hw_version") + ","
    jsondata += c.BuildSetting("sw_version") #+ ","
    #jsondata += c.BuildSetting("dev_functions") + ","
    #jsondata += c.BuildSetting("app_status") + ","
    #jsondata += c.BuildSetting("sd_card_status") + ","
    #jsondata += c.BuildSetting("sdcard_need_format") + ","
    #jsondata += c.BuildSetting("streaming_status") + ","
    #jsondata += c.BuildSetting("dual_stream_status") + ","
    #jsondata += c.BuildSetting("support_auto_low_light") + ","
    #jsondata += c.BuildSetting("piv_enable") + ","
    #jsondata += c.BuildSetting("timelapse_photo") + ","
    #jsondata += c.BuildSetting("quick_record_time") + ","
    #jsondata += c.BuildSetting("precise_cont_capturing") + ","
    #jsondata += c.BuildSetting("precise_self_remain_time")
    jsondata += ']'
    #print jsondata
    
    self.settings = SettingsWithNoMenu(size_hint=(1,1))
    self.settings.add_json_panel('Camera %d Settings' %(index+1), config, data = jsondata)
    #for child in self.settings.children[0].children[0].children[0].children[:]:
      #print child,type(child)
      #if isinstance(child, SettingOptions):
        #print "SettingOptions", child.key
        # directly change options
        #if child.key == "video_resolution":
          #child.options = ["2304x1296 30P 16:9","2304x1296 29P 16:9", "2304x1296 28P 16:9"]
      #elif isinstance(child, Label):
        #print "title: ", child.text
        #self.settingtitle = child
        # directly change setting title
        #child.text = 'Camera 2 Settings'
    
  def BuildConfig(self, section, config, camcfgdict):
    # this is hacking function
    if section == "injection":
      config.setdefaults(section,{
        "hack_wifi_mode": "Camera Default",
        "enable_info_display": "Camera Default",
        "hack_video_resolution": "Camera Default",
        "hack_timelapse_video_resolution": "Camera Default",
        "hack_video_bitrate": "Camera Default",
        "hack_raw_photo": "Camera Default"
        })
    elif section == "setting":
      if camcfgdict <> {}:
        config.setdefaults(section, camcfgdict)
      else:      
        config.setdefaults(section, {
          "camera_clock": "",
          "video_standard": "",
          "app_status": "",
          "video_resolution": "",
          "video_stamp": "",
          "video_quality": "",
          "timelapse_video": "",
          "capture_mode": "",
          "photo_size": "",
          "photo_stamp": "",
          "photo_quality": "",
          "timelapse_photo": "",
          "preview_status": "",
          "buzzer_volume": "",
          "buzzer_ring": "",
          "capture_default_mode": "",
          "precise_cont_time": "",
          "burst_capture_number": "",
          "wifi_ssid": "",
          "wifi_password": "",
          "led_mode": "",
          "meter_mode": "",
          "sd_card_status": "",
          "video_output_dev_type": "",
          "sw_version": "",
          "hw_version": "",
          "dual_stream_status": "",
          "streaming_status": "",
          "precise_cont_capturing": "",
          "piv_enable": "",
          "auto_low_light": "",
          "loop_record": "",
          "warp_enable": "",
          "support_auto_low_light": "",
          "precise_selftime": "",
          "precise_self_running": "",
          "auto_power_off": "",
          "serial_number": "",
          "system_mode": "",
          "system_default_mode": "",
          "start_wifi_while_booted": "",
          "quick_record_time": "",
          "precise_self_remain_time": "",
          "sdcard_need_format": "",
          "video_rotate": "",
          "emergency_file_backup": "",
          "osd_enable": "",
          "rec_default_mode": "",
          "rec_mode": "",
          "record_photo_time": "",
          "dev_functions": "",
          "rc_button_mode": "",
          "timelapse_video_duration": "",
          "timelapse_video_resolution": ""
          })
    config.add_callback(self.ConfigChange)
    
  def ConfigChange(self, section, key, value):
    if not self.applyconfig:
      return
    if section == "setting" and isinstance(self.settings, SettingsWithNoMenu):
      threading.Thread(target=self.DoConfigChange, args=(section,key,value,),name="DoConfigChange").start()
    elif section == "injection" and isinstance(self.injectsetting, SettingsWithNoMenu):
      threading.Thread(target=self.DoInjectChange, args=(section,key,value,),name="DoInjectChange").start()
      
  def DoInjectChange(self, section, key, value):
    for child in self.injectsetting.children[0].children[0].children[0].children[:]:
      if isinstance(child, Label):
        camtext = child.text #Camera 1 Injection, needs reboot.
        break
    index = int(camtext.replace('Camera ','').replace(' Injection, needs reboot.','')) - 1
    print "DoInjectChange", index, key, value
    if key == "hack_wifi_mode":
      pass
    elif key == "enable_info_display":
      pass
    elif key == "hack_video_resolution":
      pass
    elif key == "hack_video_resolution":
      pass
    elif key == "hack_timelapse_video_resolution":
      pass
    elif key == "hack_video_bitrate":
      pass
    elif key == "hack_raw_photo":
      pass

  def DoRefreshTitle(self, title, text):
    print "DoRefreshTitle"
    time.sleep(2)
    title.text = text
    
  def DoConfigChange(self, section, key, value):
    booloptions = ["video_rotate", "emergency_file_backup", "loop_record", "precise_self_running",
                 "preview_status", "auto_low_light", "buzzer_ring", "osd_enable", "start_wifi_while_booted"]
    readonlyopts = ["streaming_status",
                  "piv_enable",
                  "app_status",
                  "sdcard_need_format",
                  "precise_cont_capturing",
                  "timelapse_photo",
                  "quick_record_time",
                  "serial_number",
                  "sd_card_status",
                  "precise_self_remain_time",
                  "dual_stream_status",
                  "sw_version",
                  "hw_version",
                  "support_auto_low_light",
                  "dev_functions",
                  "camera_clock"]
    for child in self.settings.children[0].children[0].children[0].children[:]:
      if isinstance(child, Label):
        title = child
        camtext = child.text.replace(' OK','').replace(' ERROR','').replace('-SET','').replace('-GET','') #Camera 1 Settings
        break
    index = int(camtext.replace('Camera ','').replace(' Settings','')) - 1
    if key not in readonlyopts:
      self.cam[index].ChangeSetting(key, value)
      while True:
        self.cam[index].setok.wait(1)
        if self.cam[index].setok.isSet():
          title.text = camtext + ' OK-SET'
          break
        if self.cam[index].seterror.isSet():
          #title.text = "DoConfigChange %s %s ChangeSetting Error" %(key,value)
          print "DoConfigChange %s %s ChangeSetting Error" %(key,value)
          #time.sleep(30)
          title.text = camtext + ' ERROR-SET'
          return
    
    # NTSC or PAL
    if key == "video_standard":
      self.cam[index].ReadAllStatus()
      while True:
        self.cam[index].setallok.wait(1)
        if self.cam[index].setallok.isSet():
          title.text = camtext + ' OK-GET'
          break
        if self.cam[index].setallerror.isSet():
          #title.text = "DoConfigChange ReadAllStatus Error"
          print "DoConfigChange ReadAllStatus Error"
          #time.sleep(30)
          title.text = camtext + ' ERROR-GET'
          return
      c = CameraSetting()
      print "video_resolution_%s" %value
      r = c.BuildSetting("video_resolution_%s"%value)
      opt = []
      for item in json.loads(r)["options"]:
        opt.append(json.dumps(item).replace('"',''))
      #applycfg = self.applyconfig
      self.applyconfig = False
      ## Solution 1
      #for item in self.cam[index].settings:
      #  for itemkey,itemvalue in item.items():
          #print item,json.dumps(itemkey),json.dumps(itemvalue)
          #self.config[index].set("setting",itemkey,itemvalue)
          #if itemkey == "video_resolution":
          #  self.config[index].set("setting",itemkey,itemvalue)
          #elif itemkey == "timelapse_video_resolution":
          #  self.config[index].set("setting",itemkey,itemvalue)
      
      ## Solution 2
      for child in self.settings.children[0].children[0].children[0].children[:]:
        if isinstance(child, (SettingOptions,SettingBoolean,SettingString)):
          for item in self.cam[index].settings:
            for itmkey, itmvalue in item.items():
              if child.key == itmkey:
                child.value = itmvalue
              if child.key in ["video_resolution","timelapse_video_resolution"]:
                child.options = opt
                
      self.applyconfig = True
    # Set WiFi SSID or Password
    elif key in ["wifi_ssid", "wifi_password"]:
      self.RebootPopupOpen(index)

    threading.Thread(target=self.DoRefreshTitle, args=(title,camtext,),name="DoRefreshTitle").start()
    
  def CheckDownloadHistory(self, name, date, size):
    if len(self.downloadhistory) > 0:
      for item in self.downloadhistory:
        if item["name"] == name and item["date"] == date and item["size"] == size:
          return True
    return False
    
  def WriteDownloadHistory(self, file, downdir):
    #print "WriteDownloadHistory",downdir, file
    saveitem = {}
    history = {}
    for item in self.filelist:
      if item["name"] == file:
        saveitem.update(item)
        break
    if len(self.downloadhistory) > 0:
      bfound = False
      for item in self.downloadhistory:
        if item["name"] == saveitem["name"]:
          bfound = True
          item.update(saveitem)
          break
      if not bfound:
        self.downloadhistory.append(saveitem)
    else:
      self.downloadhistory.append(saveitem)
    
    history["downloaded"] = self.downloadhistory
    #print "WriteDownloadHistory",json.dumps(history, indent=2)
    try:
      with open(downdir + "/download.list",'w') as file:
        file.write(json.dumps(history, indent=2))
    except StandardError:
      pass
    self.ReadDownloadHistory(downdir)
    
  def ReadDownloadHistory(self, downdir):
    self.downloadhistory = []
    try:
      with open(downdir + "/download.list") as file:
        readstr = file.read()
      #print "ReadDownloadHistory",readstr
      history = json.loads(readstr)
      if history.has_key("downloaded"):
        for item in history["downloaded"]:
          self.downloadhistory.append(item)
    except StandardError:
      pass
    
  def ReadConfig(self):
    #print "readcfg"
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
      "password": "",
      "download": "",
      "upload": ""
    }
    '''
    r = []
    try:
      with open(cfgfile) as file:
        readstr = file.read()
        #print "readstr", readstr
        cfg = json.loads(readstr)
        #print "readcfg",cfg
      if cfg.has_key("config"):
        for item in cfg["config"]:
          cfginit = json.loads(initstr)
          cfginit.update(item)
          r.append(cfginit)
        #print "r", r
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
    for item in r:
      if item["download"] == "":
        item["download"] = "/mnt/sdcard/ponerine/download"
      if item["upload"] == "":
        item["upload"] = "/mnt/sdcard/ponerine/upload"
    #print r
    return r

  def WriteConfig(self):
    cfg = {}
    cfg["config"] = self.cfglist
    #print cfg
    cfgfile = __file__.replace(basename(__file__), "data/camera.cfg")
    #print __file__
    #print cfgfile
    #print json.dumps(cfg, indent=2)
    try:
      with open(cfgfile,'w') as file:
        file.write(json.dumps(cfg, indent=2))
    except StandardError:
      pass
    
class PonerineApp(App):
  #use_kivy_settings = False
  version = __version__
  def build(self):
    global cfgtoken
    cfgtoken = ()
    self.cfgevent = threading.Event()
    self.appexit = threading.Event()
    #ponerine = Ponerine(self.config, self.cfgevent, self.appexit)
    ponerine = Ponerine(self.appexit)
    ponerine.duration = 0.7
    #ConnectScreen = Builder.load_file('data/connectscreen.kv')
    #ConnectScreen.name = 'connect'
    
    #FileManagerScreen = Builder.load_file('data/filemanagerscreen.kv')
    #FileManagerScreen.name = 'filemanager'
    
    #CameraScreen = Builder.load_file('data/camerascreen.kv')
    #CameraScreen.name = 'camera'
    
    #SettingScreen = Builder.load_file('data/settingscreen.kv')
    #SettingScreen.name = 'setting'
    
    #ponerine.add_widget(ConnectScreen)
    #ponerine.add_widget(FileManagerScreen)
    #ponerine.add_widget(CameraScreen)
    #ponerine.add_widget(SettingScreen)
    #ponerine.current = 'connect'
    #ponerine.DetectCam()
    ponerine.screen = [ConnectScreen(name="connect"),FileManagerScreen(name="filemanager"),CameraScreen(name="camera"),SettingScreen(name="setting"),InjectionScreen(name="injection")]
    ponerine.switch_to(ponerine.screen[0])
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
  #print Window.size
  PonerineApp().run() 
