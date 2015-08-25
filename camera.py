from Queue import Queue
import json, socket, threading, time, select, os, urllib2, hashlib
from os.path import basename #, getsize

class Camera():
  def __init__(self, ip="192.168.42.1", port=7878, dataport=8787, webport=80):
    self.ip = ip
    self.port = port
    self.dataport = dataport
    self.webport = webport
    self.webportopen = False
    self.socketopen = -1
    self.datasocketopen = -1
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
    self.recordtime = "00:00:00"
    self.settings = []
    self.cfgdict = {}
    self.optcount = 0
    self.settable = {}
    self.readonly = ["app_status",
                   "dev_functions",
                   "dual_stream_status",
                   "hw_version",
                   "piv_enable",
                   "precise_cont_capturing",
                   "precise_self_remain_time",
                   "quick_record_time",
                   "sd_card_status",
                   "sdcard_need_format",
                   "serial_number",
                   "streaming_status",
                   "support_auto_low_light",
                   "sw_version",
                   "timelapse_photo"]
    self.taken = threading.Event()
    self.quit = threading.Event()
    self.wifioff = threading.Event()
    self.lsdir = threading.Event()
    self.dlstart = threading.Event()
    self.dlcomplete = threading.Event()
    self.dlstop = threading.Event()
    self.dlerror = threading.Event()
    self.dlopen = threading.Event()
    self.setok = threading.Event()
    self.seterror = threading.Event()
    self.optok = threading.Event()
    self.opterror = threading.Event()
    
  def __str__(self):
    info = dict()
    info["ip"] = self.ip
    info["port"] = self.port
    info["link"] = self.link
    return str(info)

  def LinkCamera(self):
    self.socketopen = -1
    self.datasocketopen = -1
    self.qsend = Queue()
    self.token = 0
    self.recv = ""
    self.link = False
    #self.wifi = True
    self.taken.clear()
    self.wifioff.clear()
    self.lsdir.clear()
    self.dlstart.clear()
    self.dlcomplete.clear()
    self.dlstop.clear()
    self.dlerror.clear()
    self.dlopen.clear()
    
    self.setok.clear()
    self.seterror.clear()
    self.optok.clear()
    self.opterror.clear()
    
    self.jsonon = False
    self.jsonoff = 0
    self.msgbusy = 0
    self.cambusy = False
    self.showtime = True
    self.status = {}
    self.filetaken = ""
    self.recording = False
    self.recordtime = "00:00:00"
    self.settings = []
    self.settable = {}
    self.readonly = ["app_status",
                   "dev_functions",
                   "dual_stream_status",
                   "hw_version",
                   "piv_enable",
                   "precise_cont_capturing",
                   "precise_self_remain_time",
                   "quick_record_time",
                   "sd_card_status",
                   "sdcard_need_format",
                   "serial_number",
                   "streaming_status",
                   "support_auto_low_light",
                   "sw_version",
                   "timelapse_photo"]
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
    self.Disconnect()
  
  def RenewToken():
    self.SendMsg('{"msg_id":258}')
    self.SendMsg('{"msg_id":257}')
    
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
      #self.SendMsg('{"msg_id":259,"param":"none_force"}')
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
            #print "sent out:", json.dumps(data, indent=2)
            print "sent out:", json.dumps(data)
            self.msgbusy = data["msg_id"]
            self.srv.send(json.dumps(data))
            #{"token":1,"msg_id":2,"type": "dev_reboot","param":"on"}
            if data["msg_id"] == 2 and data["type"] == "dev_reboot" and data["param"] == "on":
              time.sleep(5)
              self.wifioff.set()

  def JsonHandle(self, data):
    print "received:", json.dumps(data, indent=2)
    #print "received:", json.dumps(data)
    # confirm message: rval = 0
    if data.has_key("rval"):
      self.JsonRval(data)
    # status message: msg_id = 7
    elif data["msg_id"] == 7:
      self.JsonStatus(data)
      #print "camera status:", json.dumps(self.status, indent=2)
    elif data["msg_id"] == 1793:
      print "change different app msg_id: 1793"
      self.wifioff.set()
      self.link = False
      self.UnlinkCamera()

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
        #print self.filetaken
        self.taken.set()
      elif data["type"] == "video_record_complete":
        self.cambusy = False
        self.status[data["type"]] = data["param"]
        self.filetaken = data["param"].replace("/tmp/fuse_d/DCIM","")
        print self.filetaken
        self.taken.set()
      elif data["type"] == "get_file_complete":
        self.dlcomplete.set()
      elif data["type"] == "get_file_fail":
        self.status["offset"] = data["param"]
        self.dlerror.set()
        #self.StartDownload(self.status["file"], self.status["size"], self.status["offset"])
        #threading.Thread(target=self.ThreadDownload, args=(self.status["file"],self.status["size"],self.status["offset"],),name="ThreadDownload").start()
        #self.SendMsg('{"msg_id": 1285,"fetch_size":%d,"param": "%s", "offset": %d}'%(self.status["size"],self.status["file"],data["param"]))

      #{"md5sum":"e9976d54a00d136813565bfaa56f2e1b","msg_id":7,"type":"put_file_complete","param":15109422}
      elif data["type"] == "put_file_complete":
        self.dlcomplete.set()
      #{"msg_id":7,"type":"put_file_fail","param": 0}
      elif data["type"] == "put_file_fail":
        self.dlerror.set()
      else:
        self.status[data["type"]] = data["param"]
    else:
      print data
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
      elif data["type"] == "put_file_complete":
        self.dlcomplete.set()
      elif data["type"] == "vf_start":
        print "webport open"
        self.webportopen = True

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
    # token lost, need to re-new token
    if data["msg_id"] == 257 and data["rval"] < 0:
      self.token = 0
      self.link = False
      self.srv.send('{"msg_id":257,"token":0}')
      self.SendMsg('{"msg_id":%d}' %data["msg_id"])
    # allow next msg send out
    if self.msgbusy == data["msg_id"] and data["msg_id"] <> 258:
        self.msgbusy = 0
    # error rval < 0, clear msg_id
    if data["rval"] < 0:
      if data["msg_id"] == 1283:
        self.status["pwd"] = ""
        self.listing = []
        self.lsdir.set()
      elif data["msg_id"] == 1281:
        self.dlerror.set()
        self.dlstop.set()
      elif data["msg_id"] == 1285:
        self.dlerror.set()
        self.dlstop.set()
      elif data["msg_id"] == 1286:
        self.dlerror.set()
        self.dlstop.set()
      elif data["msg_id"] == 2:
        self.seterror.set()
      elif data["msg_id"] == 3:
        self.seterror.set()
      data["msg_id"] = 0
    # get token
    if data["msg_id"] == 257:
      self.token = data["param"]
      self.link = True
    # drop token
    elif data["msg_id"] == 258:
      self.token = 0
      #self.link = False
      #self.UnlinkCamera()
    # open webport
    elif data["msg_id"] == 259:
      self.webportopen = True
    elif data["msg_id"] == 2:
      self.setok.set()
    # all config information
    elif data["msg_id"] == 3:
      #self.settings = json.dumps(data["param"], indent=0).replace("{\n","{").replace("\n}","}")
      #if self.cfgdict == {}:
      #print "first time msg_id 3"
      for item in data["param"]:
        self.cfgdict.update(item)
      self.settings = data["param"]
      self.setok.set()
      #print json.dumps(self.cfgdict,indent=2)
      #self.status["config"] = data["param"]
    # battery status
    elif data["msg_id"] == 9:
      if data["permission"] == "settable":
        self.settable[data["param"]] = data["options"]
        #print json.dumps(data["param"]), json.dumps(data["permission"]), json.dumps(data["options"])
      self.optcount -= 1
      if self.optcount == 0:
        print "read all options"
        self.optok.set()
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
      #print "I need the pwd %s" %self.status["pwd"]
    elif data["msg_id"] == 1281:
      self.dlstop.set()
    # get file listing
    elif data["msg_id"] == 1282:
      self.listing = self.CreateFileList(data["listing"])
      self.lsdir.set()
    # download file size
    elif data["msg_id"] == 1285:
      self.status["size"] = data["size"]
      self.status["rem_size"] = data["rem_size"]
      self.status["offset"] = data["size"] - data["rem_size"]
      self.dlstart.set()
    # upload file
    elif data["msg_id"] == 1286:
      self.dlstart.set()
      
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

  def ConnectData(self):
    socket.setdefaulttimeout(5)
    #create socket
    self.datasrv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.datasrv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.datasrv.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    self.datasocketopen = self.datasrv.connect_ex((self.ip, self.dataport))
    print "socket status: %d" %self.datasocketopen
    if self.datasocketopen == 0:
      #self.datasrv.setblocking(0)
      self.dlopen.set()
      
  def DisconnectData(self):
    if self.datasocketopen == 0:
      self.datasocketopen == -1
      try:
        self.datasrv.close()
      except:
        pass
        
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
  
  def StartDelete(self, file):
    self.dlstop.clear()
    self.dlerror.clear()
    self.SendMsg('{"msg_id":1281,"param":"%s"}'%file)
  
  def ReadAllStatus(self):
    self.setok.clear()
    self.seterror.clear()
    self.SendMsg('{"msg_id":3}')
    threading.Thread(target=self.ThreadChangeSetting, name="ReadAllStatus").start()
    
  def ReadSetting(self, type=""):
    self.optcount = 0
    self.optok.clear()
    self.opterror.clear()
    if self.cfgdict <> {}:
      print "start read setting"
      for key in self.cfgdict.keys():
        if key not in self.readonly:
          if type == "" or type == key:
            self.optcount += 1
            #print "readsetting: %s" %key
            self.SendMsg('{"msg_id":9,"param":"%s"}'%key)
            #time.sleep(5)
  
  def ChangeSetting(self, type, value):
    self.setok.clear()
    self.seterror.clear()
    self.SendMsg('{"msg_id":2,"type":"%s","param":"%s"}' %(type,value))
    threading.Thread(target=self.ThreadChangeSetting, name="ThreadChangeSetting").start()

  def ThreadChangeSetting(self, timeout = 30):
    self.setok.wait(timeout)
    if not self.setok.isSet():
      print "setting error"
      self.seterror.set()
    
  #size can be 0
  def StartDownload(self, file, size=0, offset=0):
    self.dlstart.clear()
    self.dlcomplete.clear()
    self.dlstop.clear()
    self.dlerror.clear()
    self.status["file"] = file
    self.status["offset"] = 0
    self.status["size"] = 0
    self.status["rem_size"] = 0
    if offset > 0:
      print "reconnect", offset
      time.sleep(5)
      #self.srv.send('{"msg_id":257,"token":0}')
    self.SendMsg('{"msg_id":1285,"param":"%s","offset":%d,"fetch_size":%d}' %(file,offset,size))
    while True:
      if self.quit.isSet():
        return
      if self.wifioff.isSet():
        return
      if self.dlstart.isSet():
        print "StartDownload", file, offset
        threading.Thread(target=self.ThreadWebDownload, args=(file,),name="ThreadWebDownload").start()
        #threading.Thread(target=self.ThreadDownload2, args=(file,self.status["size"],self.status["offset"],),name="ThreadDownload2").start()
        break
        
  def StartWebDownload(self, file, destdir):
    self.dlstart.clear()
    self.dlcomplete.clear()
    self.dlstop.clear()
    self.dlerror.clear()
    threading.Thread(target=self.ThreadWebDownload, args=(file,destdir,),name="ThreadWebDownload").start()
        
  def ThreadWebDownload(self, file, destdir):
    if not self.webportopen:
      self.SendMsg('{"msg_id":259,"param":"none_force"}')
      t1 = time.time()
      while not self.webportopen:
        t2 = time.time()
        if t2-t1 > 15.0:
          self.dlerror.set()
          return
        
    fileopen = False
    try:
      print "ThreadWebDownload", file
      ichunk = 3
      chunk_size = [512,1024,2048,4096,8192,16384,32768,65536,131072]
      self.dlstatus = {}
      info = '"file":"{0}","fetch":0,"remain":0,"total":0,"speed":0'.format(file)
      info = '{%s}'%info
      print 'blank json', info
      self.dlstatus = json.loads(info)
    
      filedir = self.status["pwd"].replace('/tmp/fuse_d/','').replace('/var/www/','')
      fileurl = 'http://%s:%s/%s/%s' %(self.ip, self.webport, filedir, file)
      print "getting %s" %fileurl
      response = urllib2.urlopen(fileurl)
  
      bytes_so_far = 0
      total_size = response.info().getheader('Content-Length').strip()
      total_size = int(total_size)
      info = '"file":"{0}","fetch":0,"remain":{1},"total":{1},"speed":0'.format(file,total_size)
      info = '{%s}'%info
      print 'start json', info
      self.dlstatus = json.loads(info)
      self.dlstart.set()
      
      tstart = time.time()
      bytes_per_sec = 0
      bytes_old_sec = 0
      #fname = __file__.replace(basename(__file__), "files/%s" %file)
      fname = destdir + "/%s" %file
      localfile = open(fname, "wb")
      fileopen = True
      i = 0
      while True:
        chunk = response.read(chunk_size[ichunk])
        this_size = len(chunk)
           
        bytes_so_far += this_size
        bytes_per_sec += this_size
        if this_size > 0:
          localfile.write(chunk)
        tstop = time.time()
        if (tstop - tstart) >= 1.1:
          print bytes_per_sec,(tstop - tstart)
          speed = int(float(bytes_per_sec)/(tstop - tstart))
          print "speed %s" %speed
          info = '"file":"{0}","fetch":{1},"remain":{2},"total":{3},"speed":{4}'.format(file, bytes_so_far, total_size - bytes_so_far, total_size, speed)
          info = '{%s}'%info
          print 'running json', info
          self.dlstatus = json.loads(info)
          tstart = tstop
          
          bytes_old_sec += bytes_per_sec
          
          i += 1
          if i >= 5:
            i = 0
            if float(bytes_per_sec) < float(bytes_old_sec)/5:
              if ichunk > 0:
                ichunk -= 1
            else:
              if ichunk < 8:
                ichunk += 1
            print "auto reset chunk size:",chunk_size[ichunk]
            bytes_old_sec = 0
          
          bytes_per_sec = 0
        if bytes_so_far >= total_size:
          break
      localfile.close()
      self.dlstop.set()
    except Exception as err:
      print "ThreadWebDownload",err
      self.dlerror.set()
      if fileopen:
        localfile.close()
      
  
  def ThreadDownload2(self, file, total_size, offset):
    #try:
    print "ThreadDownload", file, total_size
    ichunk = 3
    chunk_size = [1024,2048,4096,8192,16384,32768,65536]
    self.dlstatus = {}
    info = '"file":"{0}","fetch":{1},"remain":{2},"total":{3},"speed":0'.format(file,offset,total_size-offset,total_size)
    info = '{%s}'%info
    print 'blank json', info
    self.dlstatus = json.loads(info)
    self.dlstart.clear()
    
    tstart = time.time()
    bytes_per_sec = 0
    fname = __file__.replace(basename(__file__), "files/%s" %file)
    print "saving to", fname
    if offset == 0:
      localfile = open(fname, "wb")
    else:
      localfile = open(fname, "ab")
    bytes_so_far = 0
    while True:
      if self.quit.isSet():
        return
      if self.wifioff.isSet():
        return
      this_size = chunk_size[ichunk]
      #print bytes_so_far, this_size, total_size
      #print float(bytes_so_far)/float(total_size)*100, int(float(bytes_so_far)/float(total_size)*100)
      #self.current_screen.ids.lstSelection.text = "Download %s" %int(float(bytes_so_far)/float(total_size)*100)
      if this_size + bytes_so_far > total_size:
        this_size = total_size - bytes_so_far
      chunk = bytearray(this_size)
      view = memoryview(chunk)
      bytes_per_sec += this_size
      while this_size:
        nbytes = self.datasrv.recv_into(view, this_size)
        view = view[nbytes:]
        this_size -= nbytes
        bytes_so_far += nbytes

      localfile.write(chunk)
      
      if bytes_so_far >= total_size:
        break
        
      if self.dlcomplete.isSet():
        info = '"file":"{0}","fetch":{1},"remain":0,"total":{1},"speed":0'.format(file, total_size)
        info = '{%s}'%info
        print 'running json', info
        self.dlstatus = json.loads(info)
      else:
        tstop = time.time()
        if (tstop - tstart) > 1:
          speed = float(bytes_per_sec)/(tstop - tstart)
          info = '"file":"{0}","fetch":{1},"remain":{2},"total":{3},"speed":{4}'.format(file, bytes_so_far, total_size - bytes_so_far, total_size, speed)
          info = '{%s}'%info
          print 'running json', info
          self.dlstatus = json.loads(info)
          tstart = tstop
          bytes_per_sec = 0
    
    self.dlcomplete.wait()
    localfile.write(chunk)
    localfile.close()
    #final chunk
    print bytes_so_far, this_size, total_size, "chunk", len(chunk)
    print "closing Datasrv"
    self.dlstop.set()
     
    # except Exception as err:
      # print "ThreadDownload error", err
      # # try to reconnect
      # self.dlerror.wait(10)
      # if self.dlerror.isSet():
        # #localfile.write(chunk)
        # localfile.close()
        # gsize = getsize(fname)
        # print "fname", gsize
        # print "error wait 30 seconds"
        # print "byte_so_far",bytes_so_far
        # print "offset",self.status["offset"]
        # print "total",self.status["size"]
        # print "chunk",len("chunk")
        # time.sleep(60)
        # self.StartDownload(self.status["file"], self.status["size"], gsize)

  def StartUpload(self, filewithpath):
    self.dlstart.clear()
    self.dlcomplete.clear()
    self.dlstop.clear()
    self.dlerror.clear()
    threading.Thread(target=self.ThreadUpload, args=(filewithpath,),name="ThreadUpload").start()
    #ThisMD5 = hashlib.md5(ThisFileContent).hexdigest()
    
  def ThreadUpload(self, filewithpath):
    fileopen = False
    ichunk = 3
    chunk_size = [512,1024,2048,4096,8192,16384,32768,65536,131072]
    offset = 0
    with open(filewithpath, 'rb') as uploadfile:
      file_name = uploadfile.name.split("/")[-1:][0]
      file_name = file_name.encode('utf-8')
      file_content = uploadfile.read()
      #print len(file_content)
      #print hashlib.md5(file_content).hexdigest()
    total_size = len(file_content)
    md5_value = hashlib.md5(file_content).hexdigest()
    #print '{"msg_id":1286,"param":"%s","md5sum":"%s","offset":%d,"size":%d}' %(file_name,md5_value,offset,total_size)
    self.SendMsg('{"msg_id":1286,"param":"%s","md5sum":"%s","offset":%d,"size":%d}' %(file_name,md5_value,offset,total_size))
    while True:
      if self.dlerror.isSet():
        return
      if self.dlstop.isSet():
        return
      self.dlstart.wait(5)
      if self.dlstart.isSet():
        print "Start Upload", filewithpath, file_name
        break
    
    #Start Upload
    try:
      Datasrv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      Datasrv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      Datasrv.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
      Datasrv.connect((self.ip, self.dataport))
      tstart = time.time()
      while True:
        if self.quit.isSet():
          return
        if self.wifioff.isSet():
          return
        chunk = chunk_size[ichunk]
        if offset+chunk > total_size:
          chunk = total_size - offset
        sendchunk = buffer(file_content, offset, chunk)
        Datasrv.sendall(sendchunk)
        offset += chunk
        tstop = time.time()
        if tstop - tstart > 5.0:
          tstart = tstop
          print ("upload percent %0.2f" %(float(offset)/total_size*100)) + " %"
        if offset == total_size:
          print ("upload percent 100%")
          break
      i = 0
      while True:
        i += 1
        if self.quit.isSet():
          return
        if self.wifioff.isSet():
          return
        if self.dlerror.isSet():
          break
        self.dlcomplete.wait(5)
        if self.dlcomplete.isSet():
          print "upload complete"
          self.dlstop.set()
          break
        elif i > 6:
          self.dlerror.set()
          print "upload timeout"
          break
      Datasrv.close()
    except Exception as error:
      self.dlerror.set()
      self.dlstop.set()
      pass
# sent out: {
#   "md5sum": "38c3bc506d741fd353738136bdccabdc", 
#   "msg_id": 1286, 
#   "param": "YDXJ0087.mp4", 
#   "token": 7, 
#   "offset": 0, 
#   "size": 205747844
# }
# received: {
#   "rval": 0, 
#   "msg_id": 1286
# }
# enable_info_display.script
# "md5sum": "d41d8cd98f00b204e9800998ecf8427e"

  def ChangeDir(self, dir="/tmp/fuse_d"):
    self.lsdir.clear()
    self.status["pwd"] = ""
    #self.listing = []
    if dir == "":
      self.lsdir.set() #error
      return
    threading.Thread(target=self.ThreadChangeDir, args=(dir,), name="ThreadChangeDir").start()
    
  def ThreadChangeDir(self, dir):
    self.SendMsg('{"msg_id":1283,"param":"%s"}' %dir)
    while True:
      if self.quit.isSet():
        return
      if self.wifioff.isSet():
        return
      if self.lsdir.isSet():
        return
      if self.status["pwd"] <> "":
        print "ChangeDir to" ,self.status["pwd"]
        self.lsdir.set()
        break
        
  def RefreshFile(self, dir="/var/www/DCIM"):
    self.lsdir.clear()
    self.status["pwd"] = ""
    self.listing = []
    if dir == "":
      self.lsdir.set() #error
      return
    threading.Thread(target=self.ThreadRefreshFile, args=(dir,), name="ThreadRefreshFile").start()

  def ThreadRefreshFile(self, dir):
    if not self.webportopen:
      self.SendMsg('{"msg_id":259,"param":"none_force"}')
      t1 = time.time()
      while not self.webportopen:
        t2 = time.time()
        if t2-t1 > 15.0:
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
    else:
      self.lsdir.set() #error
     
  def CreateFileList(self, rvalfilelist):
    #print "rvalfilelist", rvalfilelist
    r = []
    if len(rvalfilelist) > 0:
      i = 0
      for item in rvalfilelist:
        i += 1
        fdesc = item[item.keys()[0]].split('|')
        fsize = fdesc[0].replace(' bytes','')
        fdict = '{"name":"%s","size":%s,"date":"%s"}' %(item.keys()[0],fsize,fdesc[1])
        #print i, fdict
        #print i, item.keys()[0], item[item.keys()[0]]
        r.append(json.loads(fdict))
    #print "create file list", r
    return r
    
  def FormatCard(self):
    self.SendMsg('{"msg_id":4}')

  def Reboot(self):
    self.SendMsg('{"msg_id":2,"type":"dev_reboot","param":"on"}')

  def RestoreFactory(self):
    self.SendMsg('{"msg_id":2,"type":"restore_factory_settings","param":"on"}')
