
import threading, telnetlib, sys, platform
from os.path import dirname, basename

class CameraTelnet():
  def __init__(self, ip="192.168.42.1", port=23, username="", password = ""):
    self.ip = ip
    self.port = port
    self.username = username
    self.password = password
    self.failure = False
    self.retvalue = ''
    self.commit = threading.Event()
  
  def RunCommand(self, cmdlist, msglist, timeout=60):
     threading.Thread(target=self.ThdCommand, args=(cmdlist, msglist, timeout,) ,name="ThdCommand").start()
  
  def ThdCommand(self, cmdlist, msglist, timeout):
    tname = "DoCommand%s" %self.ip
    t = threading.Thread(target=self.DoCommand, args=(cmdlist, msglist,), name=tname)
    t.start()
    print "start %s" %tname
    t.join(timeout)
    print "join %s" %tname
    if not self.commit.isSet():
      for thread in threading.enumerate():
        if thread.isAlive() and thread.name == tname:
          print "CameraTelnet: kill %s" %thread.name
          try:
            thread._Thread__stop()
          except:
            pass
      self.failure = True
  
  def DoCommand(self, cmdlist, msglist):
    print "DoCommand start %s" %self.ip
    self.failure = False
    self.retvalue = ''
    self.commit.clear()
    try:
      ret = ""
      tn = telnetlib.Telnet(self.ip, self.port, 10)
      #needs user name
      if self.username <> "":
        ret = tn.read_until('login: ')
        tn.write(self.username +'\n')
        print "login", ret
      #nees password
      if self.password <> "":
        ret = tn.read_until('password: ')
        tn.write(self.password +'\n')
        print "password", ret
      #command lines prompt
      if self.username <> "":
        prompt = '~ # '
      else:
        prompt = '/ # '
      ret = tn.read_until(prompt)
      
      i = 0
      sysname = platform.system()
      #build command
      for cmd in cmdlist:
        if sysname == "Windows":
          cmd = u'' + cmd
        #else: #if sysname in ("Darwin", "Linux"):
        cmd = cmd.encode('utf8')
        tn.write(cmd + '\n')
        ret = tn.read_until(prompt)
        print ret, msglist[i]
        a = ret.split(msglist[i])
        print a
        if len(a) == 1:
          self.failure = True
          print "DoCommand %d err:" %i
          break
        else:
          self.retvalue = a[1]
          print "DoCommand %d ok:" %i, a[1]
        i += 1
      if self.failure == False:
        self.commit.set()
      tn.write('exit\n')
      tn.close()
    except Exception as err:
      print "CameraTelnet: error", err
      self.failure = True
      pass
  
  def Meter(self, timeout = 60):
    threading.Thread(target=self.ThdMeter, args=(timeout,) ,name="ThdMeter").start()
  
  def ThdMeter(self, timeout):
    tname = "DoMeter%s" %self.ip
    t = threading.Thread(target=self.DoMeter, name=tname)
    t.start()
    print "start t"
    t.join(timeout)
    print "join t"
    if not self.commit.isSet():
      for thread in threading.enumerate():
        if thread.isAlive() and thread.name == tname:
          print "CameraTelnet: kill %s" %thread.name
          try:
            thread._Thread__stop()
          except:
            pass
      self.failure = True
      
  def DoMeter(self):
    print "meter start %s" %self.ip
    self.failure = False
    self.commit.clear()
    try:
      ret = ""
      tn = telnetlib.Telnet(self.ip, self.port, 10)
      #needs user name
      if self.username <> "":
        ret = tn.read_until('login: ')
        tn.write(self.username +'\n')
        print "login", ret
      #nees password
      if self.password <> "":
        ret = tn.read_until('password: ')
        tn.write(self.password +'\n')
        print "password", ret
      #command lines prompt
      if self.username <> "":
        prompt = '~ # '
        
      else:
        prompt = '/ # '
      ret = tn.read_until(prompt)
      #print "telnet prompt", ret
      
      sysname = platform.system()
      
      #build rename script old->new
      if sysname == "Windows":
        cmd = u'cp -f /tmp/fuse_a/custom/meter.ash /tmp/fuse_a/custom/action.ash && ls -l /tmp/fuse_a/custom/action.ash'
      else: #if sysname in ("Darwin", "Linux"):
        cmd = 'cp -f /tmp/fuse_a/custom/meter.ash /tmp/fuse_a/custom/action.ash && ls -l /tmp/fuse_a/custom/action.ash'
      cmd = cmd.encode('utf8')
      tn.write(cmd + '\n')
      ret = tn.read_until(prompt)
      print "meter %s ok:" %self.ip, len(ret.split('root'))
      self.commit.set()
      tn.write('exit\n')
      tn.close()
    except Exception as err:
      print "CameraTelnet: error", err
      self.failure = True
      pass
  
  def SetExposure(self, aevalue='', timeout = 60):
    threading.Thread(target=self.ThdMeter, args=(aevalue,timeout,) ,name="ThdExposure").start()
    
  def ThdExposure(self, aevalue, timeout):
    tname = "DoExposure%s" %self.ip
    t = threading.Thread(target=self.DoExposure, name=tname)
    t.start()
    print "start t"
    t.join(timeout)
    print "join t"
    if not self.commit.isSet():
      for thread in threading.enumerate():
        if thread.isAlive() and thread.name == tname:
          print "CameraTelnet: kill %s" %thread.name
          try:
            thread._Thread__stop()
          except:
            pass
      self.failure = True
    
  def DoExposure(self, aevalue):
    pass
    
  def Rename(self, withpathold, withpathnew, timeout = 60):
    #withpathold = withpathold.encode('utf8')
    #withpathnew = withpathnew.encode('utf8')
    threading.Thread(target=self.ThdRename, args=(withpathold,withpathnew,timeout,) ,name="ThdRename").start()
    
  def ThdRename(self, withpathold, withpathnew, timeout):
    #withpathold = withpathold.encode('utf8')
    #withpathnew = withpathnew.encode('utf8')
    tname = "DoRename%s" %self.ip
    t = threading.Thread(target=self.DoRename, args=(withpathold,withpathnew,) ,name=tname)
    t.start()
    print "start t"
    t.join(timeout)
    print "join t"
    if not self.commit.isSet():
      for thread in threading.enumerate():
        if thread.isAlive() and thread.name == tname:
          print "CameraTelnet: kill %s" %thread.name
          try:
            thread._Thread__stop()
          except:
            pass
      self.failure = True
    
  def DoRename(self, withpathold, withpathnew):
    #withpathold = withpathold.encode('utf8')
    #withpathnew = withpathnew.encode('utf8')
    print withpathold
    print withpathnew
    self.failure = False
    self.commit.clear()
    try:
      ret = ""
      tn = telnetlib.Telnet(self.ip, self.port, 10)
      #needs user name
      if self.username <> "":
        ret = tn.read_until('login: ')
        tn.write(self.username +'\n')
        print "login", ret
      #nees password
      if self.password <> "":
        ret = tn.read_until('password: ')
        tn.write(self.password +'\n')
        print "password", ret
      #command lines prompt
      if self.username <> "":
        prompt = '~ # '
        
      else:
        prompt = '/ # '
      ret = tn.read_until(prompt)
      #print "telnet prompt", ret
      
      sysname = platform.system()
      
      #build rename script old->new
      if sysname == "Windows":
        cmd = u'if [ -f %s ];then if [ ! -f %s ];then mkdir -p %s;mv %s %s;fi;fi;' %(withpathold,withpathnew,dirname(withpathnew),withpathold,withpathnew)
      else: #if sysname in ("Darwin", "Linux"):
        cmd = 'if [ -f %s ];then if [ ! -f %s ];then mkdir -p %s;mv %s %s;fi;fi;' %(withpathold,withpathnew,dirname(withpathnew),withpathold,withpathnew)
      cmd = cmd.encode('utf8')
      tn.write(cmd + '\n')
      ret = tn.read_until(prompt)
      print ret
      tn.write('sleep 1\n')
      ret = tn.read_until(prompt)
      #check rename status
      if sysname == "Windows":
        cmd = u'if [ -f %s ];then echo RenameSuccess;fi' %withpathnew
      else: #if sysname in ("Darwin", "Linux"):
        cmd = 'if [ -f %s ];then echo RenameSuccess;fi' %withpathnew
      cmd = cmd.encode('utf8')
      tn.write(cmd + '\n')
      ret = tn.read_until(prompt)
      a = ret.split("RenameSuccess")
      print a
      if len(a) > 1:
        self.commit.set()
        print "CameraTelnet: rename success"
      else:
        self.failure = True
        print "CameraTelnet: rename failure"
      tn.write('exit\n')
      tn.close()
    except Exception as err:
      print "CameraTelnet: error", err
      self.failure = True
      pass