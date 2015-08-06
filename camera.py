from Queue import Queue
import json, socket, threading, time, select, os

class Camera():
  def __init__(self, ip="192.168.42.1", port=7878):
    self.ip = ip
    self.port = port
    self.socketopen = -1
    self.qsend = Queue()
    self.token = 0
    self.recv = ""
    self.link = False
    self.jsonon = False
    self.jsonoff = 0
    self.msgbusy = 0
    self.cambusy = False
    self.showtime = True
    self.status = {}
    self.filetaken = ""
    self.recording = False
    self.rectime = "00:00:00"
    self.settings = ""
    self.taken = threading.Event()
    self.quit = threading.Event()
    self.wifioff = threading.Event()
    self.lsdir = threading.Event()
    
  def __str__(self):
    info = dict()
    info["ip"] = self.ip
    info["port"] = self.port
    info["link"] = self.link
    return str(info)

  def LinkCamera(self):
    self.socketopen = -1
    self.qsend = Queue()
    self.token = 0
    self.recv = ""
    self.link = False
    #self.wifi = True
    self.taken.clear()
    self.wifioff.clear()
    self.lsdir.clear()
    self.jsonon = False
    self.jsonoff = 0
    self.msgbusy = 0
    self.cambusy = False
    self.showtime = True
    self.status = {}
    self.filetaken = ""
    self.recording = False
    self.rectime = "00:00:00"
    self.settings = ""
    threading.Thread(target=self.ThreadSend, name="ThreadSend").start()
#     self.tsend= threading.Thread(target=self.ThreadSend)
#     self.tsend.setDaemon(True)
#     self.tsend.setName('ThreadSend')
#     self.tsend.start()
    threading.Thread(target=self.ThreadRecv, name="ThreadRecv").start()
#     self.trecv= threading.Thread(target=self.ThreadRecv)
#     self.trecv.setDaemon(True)
#     self.trecv.setName('ThreadRecv')
#     self.trecv.start()

  def UnlinkCamera(self):
    if self.link:
      self.SendMsg('{"msg_id":258}')
    else:
      self.Disconnect()

  def SendMsg(self, msg):
    self.qsend.put(msg)

  def ThreadSend(self):
    i = 0
    #print "ThreadSend Starts\n"
    if self.socketopen <> 0:
      while self.socketopen <> 0 and i < 4:
        i += 1
        print "try to connect socket %d" %i
        self.Connect()
      if self.socketopen <> 0:
        self.quit.set()
        self.taken.set()
        print "socket time out"
        return
    print "socket connected"
    if self.socketopen == 0:
      #print "wait for token from camera"
      while not self.link:
        if self.quit.isSet():
          break
      #print "start sending loop"
      while self.socketopen == 0:
        if self.quit.isSet():
          break
        if self.msgbusy == 0:
          data = json.loads(self.qsend.get())
          allowsendout = True
          if data["msg_id"] == 515 and not self.recording:
            allowsendout = False
          if allowsendout:
            data["token"] = self.token
            print "sent out:", json.dumps(data, indent=2)
            self.msgbusy = data["msg_id"]
            self.srv.send(json.dumps(data))

  def JsonHandle(self, data):
    print "received:", json.dumps(data, indent=2)
    # confirm message: rval = 0
    if data.has_key("rval"):
      self.JsonRval(data)
    # status message: msg_id = 7
    elif data["msg_id"] == 7:
      self.JsonStatus(data)
      print "camera status:", json.dumps(self.status, indent=2)

  # status message: 7
  def JsonStatus(self, data):
    #if "param" in data.keys():
    if data.has_key("param"):
      if data["type"] == "battery":
        self.status["battery"] = data["param"]
        self.status["adapter_status"] = "0"
      elif data["type"] == "adapter":
        self.status["battery"] = data["param"]
        self.status["adapter_status"] = "1"
      #elif data["type"] == "start_photo_capture":
        #self.cambusy = True
      elif data["type"] == "photo_taken":
        self.cambusy = False
        self.status[data["type"]] = data["param"]
        self.filetaken = data["param"].replace("/tmp/fuse_d/DCIM","")
        print self.filetaken
        self.taken.set()
      elif data["type"] == "video_record_complete":
        self.cambusy = False
        self.status[data["type"]] = data["param"]
        self.filetaken = data["param"].replace("/tmp/fuse_d/DCIM","")
        print self.filetaken
        self.taken.set()
      else:
        self.status[data["type"]] = data["param"]
    else:
      if data["type"] == "start_video_record":
        self.cambusy = False
        self.recording = True
        if self.showtime:
          self.SendMsg('{"msg_id":515}')
      elif data["type"] == "piv_complete":
        self.cambusy = False
        self.filetaken = "piv_complete"
        self.taken.set()
      elif data["type"] == "wifi_will_shutdown":
        self.wifioff.set()
        self.link = False
        self.UnlinkCamera()

  '''
  normal rval = 0
  other rval:
   -4: token lost
   -9: msg 2 need more options
  -14: msg 515 not available,
       setting remain unchanged
  '''
  # rval message
  def JsonRval(self, data):
    # allow next msg send out
    if self.msgbusy == data["msg_id"] and data["msg_id"] <> 258:
        self.msgbusy = 0
    # token lost, need to re-new token
    if data["rval"] == -4:
      self.token = 0
      self.link = False
      self.srv.send('{"msg_id":257,"token":0}')
      self.SendMsg('{"msg_id":%d}' %data["msg_id"])
    # error rval < 0, clear msg_id
    elif data["rval"] < 0:
      if data["msg_id"] == 1283:
        self.status["pwd"] = ""
        self.status["listing"] = []
        self.lsdir.set()
      data["msg_id"] = 0
    # get token
    if data["msg_id"] == 257:
      self.token = data["param"]
      self.link = True
    # drop token
    elif data["msg_id"] == 258:
      self.token = 0
      self.link = False
      self.UnlinkCamera()
    # all config information
    elif data["msg_id"] == 3:
      self.settings = json.dumps(data["param"], indent=0).replace("{\n","{").replace("\n}","}")
      #self.status["config"] = data["param"]
    # battery status
    elif data["msg_id"] == 13:
      self.status["battery"] = data["param"]
      if data["type"] == "batterty":
        self.status["adapter_status"] = "0"
      else:
        self.status["adapter_status"] = "1"
      print "camera status:\n", json.dumps(self.status, indent=2)
    # take photo
    elif data["msg_id"] == 769:
      self.cambusy = True
    # start record
    elif data["msg_id"] == 513:
      self.recordtime = self.RecordTime(0)
      self.cambusy = True
    # stop record
    elif data["msg_id"] == 514:
      self.recording = False
      self.cambusy = True
    # recording time
    elif data["msg_id"] == 515:
      self.recordtime = self.RecordTime(data["param"])
      if self.showtime and self.recording:
        self.SendMsg('{"msg_id":515}')
    # change dir
    elif data["msg_id"] == 1283:
      self.status["pwd"] = data["pwd"]
    # get file listing
    elif data["msg_id"] == 1282:
      self.status["listing"] = self.CreateFileList(data["listing"])
      self.lsdir.set()

  def RecvMsg(self):
    try:
      if self.socketopen == 0:
        ready = select.select([self.srv], [], [])
        if ready[0]:
          byte = self.srv.recv(1)
          if byte == "{":
            self.jsonon = True
            self.jsonoff += 1
          elif byte == "}":
            self.jsonoff -= 1
          self.recv += byte
          if self.jsonon and self.jsonoff == 0:
            #print "RecvMsg self.recv",self.recv
            self.JsonHandle(json.loads(self.recv))
            self.recv = ""
    except Exception as err:
      self.link = False
      print "RecvMsg error", err, self.recv
      self.recv = ""

  def ThreadRecv(self):
    #print "ThreadRecv Starts\n"
    while self.socketopen: 
      if self.quit.isSet():
        break
    while self.socketopen == 0:
      if self.quit.isSet():
        break
      self.RecvMsg()

  def Connect(self):
    socket.setdefaulttimeout(5)
    #create socket
    self.srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.srv.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    self.socketopen = self.srv.connect_ex((self.ip, self.port))
    print "socket status: %d" %self.socketopen
    if self.socketopen == 0:
      #print 'sent out: {"msg_id":257,"token":0}'
      self.msgbusy = 257
      self.srv.send('{"msg_id":257,"token":0}')
      self.srv.setblocking(0)

  def Disconnect(self):
    if self.socketopen == 0:
      self.socketopen = -1
      try:
        self.srv.close()
      except:
        pass
      finally:
        self.quit.set()
        self.taken.set()

  def RecordTime(self, seconds):
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
      
  def TakePhoto(self, type="precise quality"):
    if type == "precise quality":
      self.SendMsg('{"msg_id":769}')

  def StartRecord(self, showtime=True):
    self.showtime = showtime
    self.SendMsg('{"msg_id":513}')

  def StopRecord(self):
    self.SendMsg('{"msg_id":514}')

  def RefreshFile(self, dir="/tmp/fuse_d/DCIM", ext="", sort="date desc"):
    self.lsdir.clear()
    self.status["ext"] = ext.lower()
    self.status["sort"] = sort
    self.status["pwd"] = ""
    self.status["listing"] = []
    if dir == "":
      self.lsdir.set()
      return
    self.SendMsg('{"msg_id":1283,"param":"%s"}' %dir)
    while True:
      if self.quit.isSet():
        return
      if self.wifioff.isSet():
        return
      if self.lsdir.isSet():
        return
      if self.status["pwd"] <> "":
        break
    if self.status["pwd"] <> "":
      self.SendMsg('{"msg_id":1282,"param":" -D -S"}')
      while not self.lsdir.isSet():
        if self.quit.isSet():
          break
        if self.wifioff.isSet():
          break
          
  def CreateFileList(self, rvalfilelist):
    #print "rvalfilelist", rvalfilelist
    r = []
    if len(rvalfilelist) > 0:
      i = 0
      for item in rvalfilelist:
        add = True
        #if self.status["ext"] in ("jpg","mp4","raw") and (self.status["ext"] not in item.keys()[0].lower() or "_thm" in item.keys()[0].lower()):
        if self.status["ext"] in ("jpg","mp4","raw") and self.status["ext"] not in item.keys()[0].lower():
          add = False
        if add:
          i += 1
          print i, item.keys()[0], item[item.keys()[0]]
          r.append(item.keys()[0])
    #print "create file list", r
    return r
    
  def FormatCard(self):
    self.SendMsg('{"msg_id":4}')

  def Reboot(self):
    self.SendMsg('{"msg_id":2,"type":"dev_reboot","param":"on"}')

  def RestoreFactory(self):
    self.SendMsg('{"msg_id":2,"type":"restore_factory_settings","param":"on"}')
