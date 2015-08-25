class CameraSetting():
  def BuildSetting(self, type, options = ""):
    #=============================
    # Video Sections
    #=============================
    if type == "video_resolution":
      return self.video_resolution(options)
    elif type == "video_resolution_NTSC":
      return self.video_resolution_NTSC(options)
    elif type == "video_resolution_PAL":
      return self.video_resolution_PAL(options)
    elif type == "timelapse_video_resolution":
      return self.timelapse_video_resolution(options)
    elif type == "timelapse_video_resolution_NTSC":
      return self.timelapse_video_resolution_NTSC(options)
    elif type == "timelapse_video_resolution_PAL":
      return self.timelapse_video_resolution_PAL(options)
    elif type == "video_standard":
      return self.video_standard(options)
    elif type == "video_stamp":
      return self.video_stamp(options)
    elif type == "video_quality":
      return self.video_quality(options)
    elif type == "timelapse_video":
      return self.timelapse_video(options)
    elif type == "timelapse_video_duration":
      return self.timelapse_video_duration(options)
    elif type == "video_rotate":
      return self.video_rotate(options)
    elif type == "emergency_file_backup":
      return self.emergency_file_backup(options)
    elif type == "loop_record":
      return self.loop_record(options)
    elif type == "rec_default_mode":
      return self.rec_default_mode(options)
    elif type == "rec_mode":
      return self.rec_mode(options)
    elif type == "record_photo_time":
      return self.record_photo_time(options)
    #=============================
    # Photo Sections
    #=============================
    elif type == "capture_default_mode":
      return self.capture_default_mode(options)
    elif type == "capture_mode":
      return self.capture_mode(options)
    elif type == "photo_size":
      return self.photo_size(options)
    elif type == "photo_stamp":
      return self.photo_stamp(options)
    elif type == "photo_quality":
      return self.photo_quality(options)
    elif type == "precise_cont_time":
      return self.precise_cont_time(options)
    elif type == "precise_selftime":
      return self.precise_selftime(options)
    elif type == "precise_self_running":
      return self.precise_self_running(options)
    elif type == "burst_capture_number":
      return self.burst_capture_number(options)
    #=============================
    # System Sections
    #=============================
    elif type == "preview_status":
      return self.preview_status(options)
    elif type == "auto_low_light":
      return self.auto_low_light(options)
    elif type == "auto_power_off":
      return self.auto_power_off(options)
    elif type == "buzzer_volume":
      return self.buzzer_volume(options)
    elif type == "buzzer_ring":
      return self.buzzer_ring(options)
    elif type == "led_mode":
      return self.led_mode(options)
    elif type == "meter_mode":
      return self.meter_mode(options)
    elif type == "osd_enable":
      return self.osd_enable(options)
    elif type == "rc_button_mode":
      return self.rc_button_mode(options)
    elif type == "start_wifi_while_booted":
      return self.start_wifi_while_booted(options)
    elif type == "system_default_mode":
      return self.system_default_mode(options)
    elif type == "system_mode":
      return self.system_mode(options)
    elif type == "video_output_dev_type":
      return self.video_output_dev_type(options)
    #=============================
    # System Readonly
    #=============================
    elif type == "camera_clock":
      return self.camera_clock(options)
    elif type == "wifi_ssid":
      return self.wifi_ssid(options)
    elif type == "wifi_password":
      return self.wifi_password(options)
    elif type == "app_status":
      return self.app_status(options)
    elif type == "dev_functions":
      return self.dev_functions(options)
    elif type == "dual_stream_status":
      return self.dual_stream_status(options)
    elif type == "streaming_status":
      return self.streaming_status(options)
    elif type == "support_auto_low_light":
      return self.support_auto_low_light(options)
    elif type == "piv_enable":
      return self.piv_enable(options)
    elif type == "quick_record_time":
      return self.quick_record_time(options)
    elif type == "timelapse_photo":
      return self.timelapse_photo(options)
    elif type == "precise_cont_capturing":
      return self.precise_cont_capturing(options)
    elif type == "precise_self_remain_time":
      return self.precise_self_remain_time(options)
    elif type == "sd_card_status":
      return self.sd_card_status(options)
    elif type == "sdcard_need_format":
      return self.sdcard_need_format(options)
    elif type == "serial_number":
      return self.serial_number(options)
    elif type == "hw_version":
      return self.hw_version(options)
    elif type == "sw_version":
      return self.sw_version(options)
    else:
      return ""
      
  def video_standard(self, options):
    if options == "":
      options = '["NTSC","PAL"]'
    r = '''
        {
        "type": "options",
        "title": "Video Standard",
        "desc": "Set video standard by NTSC or PAL.",
        "section": "setting",
        "key": "video_standard",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)
    
  def video_resolution(self, options):
    if options == "":
      options = '''
          [
          "1920x1080 60P 16:9", 
          "1920x1080 30P 16:9", 
          "1920x1080 48P 16:9", 
          "1920x1080 24P 16:9", 
          "1280x960 60P 4:3", 
          "1280x960 48P 4:3", 
          "1280x720 60P 16:9", 
          "1280x720 48P 16:9", 
          "1280x720 120P 16:9", 
          "848x480 240P 16:9"
          ]
          '''
    r = '''
        {
        "type": "options",
        "title": "Video Resolution",
        "desc": "Set video resolution, with * is experimental resolution.",
        "section": "setting",
        "key": "video_resolution",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)

  def video_resolution_NTSC(self, options):
    if options == "":
      options = '''
          [
          "1920x1080 60P 16:9", 
          "1920x1080 30P 16:9", 
          "1920x1080 48P 16:9", 
          "1920x1080 24P 16:9", 
          "1280x960 60P 4:3", 
          "1280x960 48P 4:3", 
          "1280x720 60P 16:9", 
          "1280x720 48P 16:9", 
          "1280x720 120P 16:9", 
          "848x480 240P 16:9"
          ]
          '''
    r = '''
        {
        "type": "options",
        "title": "Video Resolution",
        "desc": "Set video resolution, with * is experimental resolution.",
        "section": "setting",
        "key": "video_resolution",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)

  def video_resolution_PAL(self, options):
    if options == "":
      options = '''
          [
          "1920x1080 50P 16:9", 
          "1920x1080 25P 16:9", 
          "1920x1080 48P 16:9", 
          "1920x1080 24P 16:9", 
          "1280x960 50P 4:3", 
          "1280x960 48P 4:3", 
          "1280x720 50P 16:9", 
          "1280x720 48P 16:9", 
          "1280x720 100P 16:9", 
          "848x480 200P 16:9"
          ]
          '''
    r = '''
        {
        "type": "options",
        "title": "Video Resolution",
        "desc": "Set video resolution, with * is experimental resolution.",
        "section": "setting",
        "key": "video_resolution",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)

  def timelapse_video_resolution(self, options):
    if options == "":
      options = '''
          [
          "1920x1080 60P 16:9", 
          "1920x1080 30P 16:9", 
          "1920x1080 48P 16:9", 
          "1920x1080 24P 16:9", 
          "1280x960 60P 4:3", 
          "1280x960 48P 4:3", 
          "1280x720 60P 16:9", 
          "1280x720 48P 16:9", 
          "1280x720 120P 16:9", 
          "848x480 240P 16:9"
          ]
          '''
    r = '''
        {
        "type": "options",
        "title": "Timelapse Video Resolution",
        "desc": "Set timelapse video resolution, with * is experimental resolution.",
        "section": "setting",
        "key": "timelapse_video_resolution",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)

  def timelapse_video_resolution_NTSC(self, options):
    if options == "":
      options = '''
          [
          "1920x1080 60P 16:9", 
          "1920x1080 30P 16:9", 
          "1920x1080 48P 16:9", 
          "1920x1080 24P 16:9", 
          "1280x960 60P 4:3", 
          "1280x960 48P 4:3", 
          "1280x720 60P 16:9", 
          "1280x720 48P 16:9", 
          "1280x720 120P 16:9", 
          "848x480 240P 16:9"
          ]
          '''
    r = '''
        {
        "type": "options",
        "title": "Timelapse Video Resolution",
        "desc": "Set timelapse video resolution, with * is experimental resolution.",
        "section": "setting",
        "key": "timelapse_video_resolution",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)

  def timelapse_video_resolution_PAL(self, options):
    if options == "":
      options = '''
          [
          "1920x1080 50P 16:9", 
          "1920x1080 25P 16:9", 
          "1920x1080 48P 16:9", 
          "1920x1080 24P 16:9", 
          "1280x960 50P 4:3", 
          "1280x960 48P 4:3", 
          "1280x720 50P 16:9", 
          "1280x720 48P 16:9", 
          "1280x720 100P 16:9", 
          "848x480 200P 16:9"
          ]
          '''
    r = '''
        {
        "type": "options",
        "title": "Timelapse Video Resolution",
        "desc": "Set timelapse video resolution, with * is experimental resolution.",
        "section": "setting",
        "key": "timelapse_video_resolution",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)

  def video_stamp(self, options):
    if options == "":
      options = '["off","date","time","date/time"]'
    r = '''
        {
        "type": "options",
        "title": "Video Stamp",
        "desc": "Set video stamp by date, time or datetime.",
        "section": "setting",
        "key": "video_stamp",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)

  def video_quality(self, options):
    if options == "":
      options = '["S.Fine","Fine","Normal"]'
    r = '''
        {
        "type": "options",
        "title": "Video Quality",
        "desc": "Set video quality.",
        "section": "setting",
        "key": "video_quality",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)

  def timelapse_video(self, options):
    if options == "":
      options = '["off","0.5","1","2","5","10","30","60"]'
    r = '''
        {
        "type": "options",
        "title": "Timelapse Video Interval",
        "desc": "Set timelapse video interval seconds.",
        "section": "setting",
        "key": "timelapse_video",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)
  
  def timelapse_video_duration(self, options):
    if options == "":
      options = '["off","1s","2s","5s","10s","15s","20s","25s","30s","45s","60s","90s","120s"]'
    r = '''
        {
        "type": "options",
        "title": "Timelapse Video Duration",
        "desc": "Set timelapse video duration by seconds.",
        "section": "setting",
        "key": "timelapse_video_duration",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)
  
  def video_rotate(self, options):
    if options == "":
      options = '["on","off"]'
    r = '''
        {
        "type": "bool",
        "title": "Video Rotation",
        "desc": "Set video rotation, on or off.",
        "section": "setting",
        "key": "video_rotate",
        "values": ["off","on"]
        }
        '''
    return r.replace('[options]',options)
    
  def emergency_file_backup(self, options):
    if options == "":
      options = '["on","off"]'
    r = '''
        {
        "type": "bool",
        "title": "Emergency File Backup",
        "desc": "Set video emergency file backup, on or off.",
        "section": "setting",
        "key": "emergency_file_backup",
        "values": ["off","on"]
        }
        '''
    return r.replace('[options]',options)
    
  def loop_record(self, options):
    if options == "":
      options = '["on","off"]'
    r = '''
        {
        "type": "bool",
        "title": "Loop Record",
        "desc": "Set video loop record after card is full, on or off.",
        "section": "setting",
        "key": "loop_record",
        "values": ["off","on"]
        }
        '''
    return r.replace('[options]',options)
    
  def rec_default_mode(self, options):
    if options == "":
      options = '["record","record_timelapse"]'
    r = '''
        {
        "type": "options",
        "title": "Default Record Mode",
        "desc": "Set default record mode, on camera start up.",
        "section": "setting",
        "key": "rec_default_mode",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)

  def rec_mode(self, options):
    if options == "":
      options = '["record","record_timelapse"]'
    r = '''
        {
        "type": "options",
        "title": "Current Record Mode",
        "desc": "Set current record mode.",
        "section": "setting",
        "key": "rec_mode",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)

  def record_photo_time(self, options):
    if options == "":
      options = '["5", "10", "30", "60"]'
    r = '''
        {
        "type": "options",
        "title": "Record Photo Time",
        "desc": "Set record photo time, unknown function.",
        "section": "setting",
        "key": "record_photo_time",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)
    
  def capture_default_mode(self, options):
    if options == "":
      options = '''
          [
          "precise quality",
          "precise quality cont.",
          "burst quality",
          "precise self quality"
          ]
          '''
    r = '''
        {
        "type": "options",
        "title": "Default Capture Mode",
        "desc": "Set default capture mode, on camera start up.",
        "section": "setting",
        "key": "capture_default_mode",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)

  def capture_mode(self, options):
    if options == "":
      options = '''
          [
          "precise quality",
          "precise quality cont.",
          "burst quality",
          "precise self quality"
          ]
          '''
    r = '''
        {
        "type": "options",
        "title": "Current Capture Mode",
        "desc": "Set current capture mode.",
        "section": "setting",
        "key": "capture_mode",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)

  def photo_size(self, options):
    if options == "":
      options = '''
          [
          "16M (4608x3456 4:3)",
          "13M (4128x3096 4:3)",
          "8M (3264x2448 4:3)",
          "5M (2560x1920 4:3)",
          "12M (4608x2592 16:9)"
          ]
          '''
    r = '''
        {
        "type": "options",
        "title": "Photo Size",
        "desc": "Set capture photo size.",
        "section": "setting",
        "key": "photo_size",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)

  def photo_stamp(self, options):
    if options == "":
      options = '["off","date","time","date/time"]'
    r = '''
        {
        "type": "options",
        "title": "Photo Stamp",
        "desc": "Set photo stamp by date, time or datetime.",
        "section": "setting",
        "key": "photo_stamp",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)

  def photo_quality(self, options):
    if options == "":
      options = '["S.Fine","Fine","Normal"]'
    r = '''
        {
        "type": "options",
        "title": "Photo Quality",
        "desc": "Set photo quality.",
        "section": "setting",
        "key": "photo_quality",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)

  def precise_cont_time(self, options):
    if options == "":
      options = '["0.5 sec", "1.0 sec", "2.0 sec", "5.0 sec", "10.0 sec", "30.0 sec", "60.0 sec"]'
    r = '''
        {
        "type": "options",
        "title": "Timelapse Photo Interval",
        "desc": "Set timelapse photo interval seconds.",
        "section": "setting",
        "key": "precise_cont_time",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)
    
  def precise_selftime(self, options):
    if options == "":
      options = '["3s", "5s", "10s", "15s"]'
    r = '''
        {
        "type": "options",
        "title": "Precise Selftime",
        "desc": "Set precise selftime seconds.",
        "section": "setting",
        "key": "precise_selftime",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)
    
  def precise_self_running(self, options):
    if options == "":
      options = '["on","off"]'
    r = '''
        {
        "type": "bool",
        "title": "Stop Selftime",
        "desc": "Stop precise selftime.",
        "section": "setting",
        "key": "precise_self_running",
        "values": ["off","on"]
        }
        '''
    return r.replace('[options]',options)
    
  def burst_capture_number(self, options):
    if options == "":
      options = '["3 p / s", "5 p / s", "7 p / s", "7 p / 2s"]'
    r = '''
        {
        "type": "options",
        "title": "Burst Capture Number",
        "desc": "Set burst capture number.",
        "section": "setting",
        "key": "burst_capture_number",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)
    
  def preview_status(self, options):
    if options == "":
      options = '["on","off"]'
    r = '''
        {
        "type": "bool",
        "title": "Preview Status",
        "desc": "Set preview status, on or off.",
        "section": "setting",
        "key": "preview_status",
        "values": ["off","on"]
        }
        '''
    return r.replace('[options]',options)

  def auto_low_light(self, options):
    if options == "":
      options = '["on","off"]'
    r = '''
        {
        "type": "bool",
        "title": "Auto Low Light",
        "desc": "Set auto low light, on or off.",
        "section": "setting",
        "key": "auto_low_light",
        "values": ["off","on"]
        }
        '''
    return r.replace('[options]',options)

  def auto_power_off(self, options):
    if options == "":
      options = '["off", "3 minutes", "5 minutes", "10 minutes"]'
    r = '''
        {
        "type": "options",
        "title": "Auto Power Off",
        "desc": "Set auto power off.",
        "section": "setting",
        "key": "auto_power_off",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)
    
  def buzzer_volume(self, options):
    if options == "":
      options = '["high", "low", "mute"]'
    r = '''
        {
        "type": "options",
        "title": "Buzzer Volume",
        "desc": "Set buzzer volume.",
        "section": "setting",
        "key": "buzzer_volume",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)
    
  def buzzer_ring(self, options):
    if options == "":
      options = '["on","off"]'
    r = '''
        {
        "type": "bool",
        "title": "Buzzer Ring",
        "desc": "Set buzzer ring to find your camera, on or off.",
        "section": "setting",
        "key": "buzzer_ring",
        "values": ["off","on"]
        }
        '''
    return r.replace('[options]',options)
    
  def led_mode(self, options):
    if options == "":
      options = '["all enable", "all disable", "status enable"]'
    r = '''
        {
        "type": "options",
        "title": "Led Mode",
        "desc": "Set led mode.",
        "section": "setting",
        "key": "led_mode",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)
    
  def meter_mode(self, options):
    if options == "":
      options = '["center", "average", "spot"]'
    r = '''
        {
        "type": "options",
        "title": "Meter Mode",
        "desc": "Set auto exposure meter mode.",
        "section": "setting",
        "key": "meter_mode",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)
    
  def osd_enable(self, options):
    if options == "":
      options = '["on","off"]'
    r = '''
        {
        "type": "bool",
        "title": "OSD Enable",
        "desc": "Set on screen display (OSD), on or off.",
        "section": "setting",
        "key": "osd_enable",
        "values": ["off","on"]
        }
        '''
    return r.replace('[options]',options)
    
  def rc_button_mode(self, options):
    if options == "":
      options = '["mode_shutter", "record_capture"]'
    r = '''
        {
        "type": "options",
        "title": "RC Button Mode",
        "desc": "Set remote control button mode.",
        "section": "setting",
        "key": "rc_button_mode",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)

  def start_wifi_while_booted(self, options):
    if options == "":
      options = '["on","off"]'
    r = '''
        {
        "type": "bool",
        "title": "Start WiFi",
        "desc": "Set wifi while booted.",
        "section": "setting",
        "key": "start_wifi_while_booted",
        "values": ["off","on"]
        }
        '''
    return r.replace('[options]',options)
    
  def system_default_mode(self, options):
    if options == "":
      options = '["capture", "record"]'
    r = '''
        {
        "type": "options",
        "title": "Default System Mode",
        "desc": "Set default system mode.",
        "section": "setting",
        "key": "system_default_mode",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)
    
  def system_mode(self, options):
    if options == "":
      options = '["capture", "record"]'
    r = '''
        {
        "type": "options",
        "title": "Current System Mode",
        "desc": "Set current system mode.",
        "section": "setting",
        "key": "system_mode",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)
    
  def video_output_dev_type(self, options):
    if options == "":
      options = '["hdmi", "tv", "off"]'
    r = '''
        {
        "type": "options",
        "title": "Video Output Device",
        "desc": "Set video output device type.",
        "section": "setting",
        "key": "video_output_dev_type",
        "options": [options]
        }
        '''
    return r.replace('[options]',options)
    
  def camera_clock(self, options):
    if options == "":
      options = '["on","off"]'
    r = '''
        {
        "type": "string",
        "title": "Camera Clock",
        "desc": "Readonly now, set camera clock.",
        "section": "setting",
        "key": "camera_clock"
        }
        '''
    return r.replace('[options]',options)
    
  def wifi_ssid(self, options):
    if options == "":
      options = '["on","off"]'
    r = '''
        {
        "type": "string",
        "title": "WiFi SSID",
        "desc": "Readonly now, set camera WiFi SSID.",
        "section": "setting",
        "key": "wifi_ssid"
        }
        '''
    return r.replace('[options]',options)
    
  def wifi_password(self, options):
    if options == "":
      options = '["on","off"]'
    r = '''
        {
        "type": "string",
        "title": "WiFi Password",
        "desc": "Readonly now, set camera WiFi password.",
        "section": "setting",
        "key": "wifi_password"
        }
        '''
    return r.replace('[options]',options)
  
  def app_status(self, options):
    if options == "":
      options = '["idle", "vf", "record", "recording", "capture", "precise_cont_capturing", "burst_capturing", "precise_capturing", "operation_done"]'
    r = '''
        {
        "type": "string",
        "title": "App Status",
        "desc": "Readonly, Current Camera App Status.",
        "section": "setting",
        "key": "app_status"
        }
        '''
    return r.replace('[options]',options)
    
  def dev_functions(self, options):
    if options == "":
      options = '["2615"]'
    r = '''
        {
        "type": "string",
        "title": "Dev Function",
        "desc": "Readonly, Dev Function Number.",
        "section": "setting",
        "key": "dev_functions"
        }
        '''
    return r.replace('[options]',options)
    
  def dual_stream_status(self, options):
    if options == "":
      options = '["on","off"]'
    r = '''
        {
        "type": "string",
        "title": "Dual Stream Status",
        "desc": "Readonly, dual stream status.",
        "section": "setting",
        "key": "dual_stream_status"
        }
        '''
    return r.replace('[options]',options)

  def streaming_status(self, options):
    if options == "":
      options = '["on","off"]'
    r = '''
        {
        "type": "string",
        "title": "Streaming Status",
        "desc": "Readonly, streaming status.",
        "section": "setting",
        "key": "streaming_status"
        }
        '''
    return r.replace('[options]',options)
  
  def support_auto_low_light(self, options):
    if options == "":
      options = '["on","off"]'
    r = '''
        {
        "type": "string",
        "title": "Support Auto Low Light",
        "desc": "Readonly, support auto low light.",
        "section": "setting",
        "key": "support_auto_low_light"
        }
        '''
    return r.replace('[options]',options)
    
  def piv_enable(self, options):
    if options == "":
      options = '["on","off"]'
    r = '''
        {
        "type": "string",
        "title": "PIV Enable",
        "desc": "Readonly, picture in video enable.",
        "section": "setting",
        "key": "piv_enable"
        }
        '''
    return r.replace('[options]',options)
    
  def quick_record_time(self, options):
    if options == "":
      options = '["0","1","2",???]'
    r = '''
        {
        "type": "string",
        "title": "Quick Record Time",
        "desc": "Readonly, quick record time.",
        "section": "setting",
        "key": "quick_record_time"
        }
        '''
    return r.replace('[options]',options)
    
  def timelapse_photo(self, options):
    if options == "":
      options = '["off", "2"]'
    r = '''
        {
        "type": "string",
        "title": "Timelapse Photo",
        "desc": "Readonly, timelapse photo.",
        "section": "setting",
        "key": "timelapse_photo"
        }
        '''
    return r.replace('[options]',options)
  
  def precise_cont_capturing(self, options):
    if options == "":
      options = '["on", "off"]'
    r = '''
        {
        "type": "string",
        "title": "Precise Continue Capturing",
        "desc": "Readonly, precise continue capturing.",
        "section": "setting",
        "key": "precise_cont_capturing"
        }
        '''
    return r.replace('[options]',options)

  def precise_self_remain_time(self, options):
    if options == "":
      options = '["0","1","2",???]'
    r = '''
        {
        "type": "string",
        "title": "Precise Self Remain Time",
        "desc": "Readonly, precise self remain time.",
        "section": "setting",
        "key": "precise_self_remain_time"
        }
        '''
    return r.replace('[options]',options)

  def sd_card_status(self, options):
    if options == "":
      options = '["insert",???]'
    r = '''
        {
        "type": "string",
        "title": "SD Card Status",
        "desc": "Readonly, sd card status.",
        "section": "setting",
        "key": "sd_card_status"
        }
        '''
    return r.replace('[options]',options)
    
  def sdcard_need_format(self, options):
    if options == "":
      options = '["no-need",???]'
    r = '''
        {
        "type": "string",
        "title": "SD Card Need Format",
        "desc": "Readonly, sd card need format.",
        "section": "setting",
        "key": "sdcard_need_format"
        }
        '''
    return r.replace('[options]',options)
    
  def serial_number(self, options):
    if options == "":
      options = '[""]'
    r = '''
        {
        "type": "string",
        "title": "Serial Number",
        "desc": "Readonly, serial number.",
        "section": "setting",
        "key": "serial_number"
        }
        '''
    return r.replace('[options]',options)
    
  def hw_version(self, options):
    if options == "":
      options = '[""]'
    r = '''
        {
        "type": "string",
        "title": "Hardware Version",
        "desc": "Readonly, hardware version.",
        "section": "setting",
        "key": "hw_version"
        }
        '''
    return r.replace('[options]',options)
    
  def sw_version(self, options):
    if options == "":
      options = '[""]'
    r = '''
        {
        "type": "string",
        "title": "Software Version",
        "desc": "Readonly, software version.",
        "section": "setting",
        "key": "sw_version"
        }
        '''
    return r.replace('[options]',options)
'''
==================
Start Read Setting
==================
"system_mode" "settable" ["capture", "record"]
"buzzer_volume" "settable" ["high", "low", "mute"]
"photo_size" "settable" ["16M (4608x3456 4:3)", "13M (4128x3096 4:3)", "8M (3264x2448 4:3)", "5M (2560x1920 4:3)", "12M (4608x2592 16:9)"]
"video_resolution" "settable" ["1920x1080 60P 16:9", "1920x1080 30P 16:9", "1920x1080 48P 16:9", "1920x1080 24P 16:9", "1280x960 60P 4:3", "1280x960 48P 4:3", "1280x720 60P 16:9", "1280x720 48P 16:9", "1280x720 120P 16:9", "848x480 240P 16:9"]
"emergency_file_backup" "settable" ["on", "off"]
"auto_power_off" "settable" ["off", "3 minutes", "5 minutes", "10 minutes"]
"camera_clock" "settable" ["2015-08-23 14:03:38"]
"timelapse_video_duration" "settable" []
"meter_mode" "settable" ["center", "average", "spot"]
"photo_stamp" "settable" ["off", "date", "time", "date/time"]
"buzzer_ring" "settable" ["on", "off"]
"system_default_mode" "settable" ["capture", "record"]
"auto_low_light" "settable" ["on", "off"]
"preview_status" "settable" ["on", "off"]
"osd_enable" "settable" ["on", "off"]
"wifi_ssid" "settable" []
"loop_record" "settable" ["on", "off"]
"led_mode" "settable" ["all enable", "all disable", "status enable"]
"precise_self_running" "settable" ["on", "off"]
"capture_default_mode" "settable" ["precise quality", "precise quality cont.", "burst quality", "precise self quality"]
"video_rotate" "settable" ["off", "on"]
"burst_capture_number" "settable" ["3 p / s", "5 p / s", "7 p / s", "7 p / 2s"]
"wifi_password" "settable" []
"timelapse_video" "settable" ["off", "0.5", "1", "2", "5", "10", "30", "60"]
"timelapse_video_resolution" "settable" ["1920x1080 60P 16:9", "1920x1080 30P 16:9", "1920x1080 48P 16:9", "1920x1080 24P 16:9", "1280x960 60P 4:3", "1280x960 48P 4:3", "1280x720 60P 16:9", "1280x720 48P 16:9", "1280x720 120P 16:9", "848x480 240P 16:9"]
"precise_cont_time" "settable" ["0.5 sec", "1.0 sec", "2.0 sec", "5.0 sec", "10.0 sec", "30.0 sec", "60.0 sec"]
"rec_default_mode" "settable" ["record", "record_timelapse"]
"start_wifi_while_booted" "settable" ["on", "off"]
"video_stamp" "settable" ["off", "date", "time", "date/time"]
"photo_quality" "settable" ["S.Fine", "Fine", "Normal"]
"capture_mode" "settable" ["precise quality", "precise quality cont.", "burst quality", "precise self quality"]
"video_output_dev_type" "settable" ["hdmi", "tv", "off"]
"rc_button_mode" "settable" ["mode_shutter", "record_capture"]
"record_photo_time" "settable" ["5", "10", "30", "60"]
"video_quality" "settable" ["S.Fine", "Fine", "Normal"]
"precise_selftime" "settable" ["3s", "5s", "10s", "15s"]
"rec_mode" "settable" ["record", "record_timelapse"]
"video_standard" "settable" ["NTSC", "PAL"]
"warp_enable" "settable" ["on", "off"]

"streaming_status" "readonly" []
"piv_enable" "readonly" []
"app_status" "readonly" ["idle", "vf", "record", "recording", "capture", "precise_cont_capturing", "burst_capturing", "precise_capturing", "operation_done"]
"sdcard_need_format" "readonly" []
"precise_cont_capturing" "readonly" []
"timelapse_photo" "readonly" ["off", "2"]
"quick_record_time" "readonly" []
"serial_number" "readonly" []
"sd_card_status" "readonly" []
"precise_self_remain_time" "readonly" []
"dual_stream_status" "readonly" []
"sw_version" "readonly" []
"hw_version" "readonly" []
"support_auto_low_light" "readonly" []
"dev_functions" "readonly" []
================
Read All Options
================
'''

'''
259 >>> 258 >>> 257
[{"camera_clock": "2015-08-20 20:33:40"}, 
{"video_standard": "NTSC"}, 
{"app_status": "idle"}, 
{"video_resolution": "2304x1296 30P 16:9"}, 
{"video_stamp": "off"}, 
{"video_quality": "S.Fine"}, 
{"timelapse_video": "0.5"}, 
{"capture_mode": "precise quality"}, 
{"photo_size": "16M (4608x3456 4:3)"}, 
{"photo_stamp": "off"}, 
{"photo_quality": "S.Fine"}, 
{"timelapse_photo": "off"}, 
{"preview_status": "on"}, 
{"buzzer_volume": "mute"}, 
{"buzzer_ring": "off"}, 
{"capture_default_mode": "precise quality"}, 
{"precise_cont_time": "0.5 sec"}, 
{"burst_capture_number": "7 p / s"}, 
{"wifi_ssid": "XiaoYiCamera"}, 
{"wifi_password": "1234567890"}, 
{"led_mode": "all enable"}, 
{"meter_mode": "center"}, 
{"sd_card_status": "insert"}, 
{"video_output_dev_type": "hdmi"}, 
{"sw_version": "YDXJv22_1.2.10_build-20150810145216_b1049_i841_s1081"}, 
{"hw_version": "YDXJ_v22"}, 
{"dual_stream_status": "on"}, 
{"streaming_status": "on"}, 
{"precise_cont_capturing": "off"}, 
{"piv_enable": "on"}, 
{"auto_low_light": "off"}, 
{"loop_record": "off"}, 
{"warp_enable": "off"}, 
{"support_auto_low_light": "on"}, 
{"precise_selftime": "5s"}, 
{"precise_self_running": "off"}, 
{"auto_power_off": "off"}, 
{"serial_number": "Z221509S2884591"}, 
{"system_mode": "record"}, 
{"system_default_mode": "record"}, 
{"start_wifi_while_booted": "on"}, 
{"quick_record_time": "0"}, 
{"precise_self_remain_time": "0"}, 
{"sdcard_need_format": "no-need"}, 
{"video_rotate": "off"}, 
{"emergency_file_backup": "off"}, 
{"osd_enable": "off"}, 
{"rec_default_mode": "record"}, 
{"rec_mode": "record"}, 
{"record_photo_time": "5"}, 
{"dev_functions": "2615"}, 
{"rc_button_mode": "mode_shutter"}, 
{"timelapse_video_duration": "10s"}, 
{"timelapse_video_resolution": "2304x1296 30P 16:9"}]
'''
