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

class CameraSetting():
  def BuildSetting(self, type, options = ""):
    r = ''
    if type == "video_resolution":
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
    elif type == "timelapse_video_resolution":
      if options == "":
        options = '["1920x1080 60P 16:9"]'
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
    elif type == "video_standard":
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
    elif type == "video_stamp":
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
    elif type == "video_quality":
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
    elif type == "timelapse_video":
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
    elif type == "capture_mode":
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
        "title": "Photo Capture Mode",
        "desc": "Set photo capture mode.",
        "section": "setting",
        "key": "capture_mode",
        "options": [options]
        }
        '''
    elif type == "capture_default_mode":
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
        "title": "Capture Default Mode",
        "desc": "Set photo capture mode on camera start up.",
        "section": "setting",
        "key": "capture_default_mode",
        "options": [options]
        }
        '''
    elif type == "photo_size":
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
        "desc": "Set photo size.",
        "section": "setting",
        "key": "photo_size",
        "options": [options]
        }
        '''
    elif type == "photo_stamp":
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
    elif type == "photo_quality":
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
    elif type == "preview_status":
      if options == "":
        options = '["on","off"]'
      r = '''
        {
        "type": "bool",
        "title": "Preview Status",
        "desc": "Set preview status, on or off.",
        "section": "setting",
        "key": "preview_status"
        }
        '''
    elif type == "buzzer_volume":
      if options == "":
        options = '["high","low","mute"]'
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
    elif type == "buzzer_ring":
      if options == "":
        options = '["on","off"]'
      r = '''
        {
        "type": "bool",
        "title": "Buzzer Ring",
        "desc": "Set buzzer ring, on or off.",
        "section": "setting",
        "key": "buzzer_ring"
        }
        '''
    elif type == "precise_cont_time":
      if options == "":
        options = '["0.5 sec", "1.0 sec", "2.0 sec", "5.0 sec", "10.0 sec", "30.0 sec", "60.0 sec"]'
      r = '''
        {
        "type": "options",
        "title": "Precise Continue Time",
        "desc": "Set Precise Continue Time.",
        "section": "setting",
        "key": "precise_cont_time",
        "options": [options]
        }
        '''
    #return json format string
    r = r.replace('[options]',options)
    return r

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
