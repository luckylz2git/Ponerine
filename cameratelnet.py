
import threading, telnetlib, sys, platform
from os.path import dirname, basename

class CameraTelnet():
  def __init__(self, ip="192.168.42.1", port=23, username="", password = ""):
    self.ip = ip
    self.port = port
    self.username = username
    self.password = password
    self.failure = False
    self.commit = threading.Event()
  
  def Rename(self, withpathold, withpathnew, timeout = 60):
    #withpathold = withpathold.encode('utf8')
    #withpathnew = withpathnew.encode('utf8')
    threading.Thread(target=self.ThdRename, args=(withpathold,withpathnew,timeout,),name="ThdRename").start()
    
  def ThdRename(self, withpathold, withpathnew, timeout):
    #withpathold = withpathold.encode('utf8')
    #withpathnew = withpathnew.encode('utf8')
    tname = "DoRename%s" %self.ip
    t = threading.Thread(target=self.DoRename, args=(withpathold,withpathnew,),name=tname)
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
      print "telnet prompt", ret
      
      #build rename script
      sysname = platform.system()
      if sysname == "Windows":
        cmd = u'if [ -f %s ];then if [ ! -f %s ];then mkdir -p %s;mv %s %s;if [ -f %s ];then echo RenameSuccess;fi;fi;fi;' %(withpathold,withpathnew,dirname(withpathnew),withpathold,withpathnew,withpathnew)
        print "unicode",cmd
        cmd = cmd.encode('utf8')
        print "utf-8",cmd
      else: #if sysname in ("Darwin", "Linux"):
        cmd = 'if [ -f %s ];then if [ ! -f %s ];then mkdir -p %s;mv %s %s;if [ -f %s ];then echo RenameSuccess;fi;fi;fi;' %(withpathold,withpathnew,dirname(withpathnew),withpathold,withpathnew,withpathnew)
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