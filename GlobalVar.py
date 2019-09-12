# 文件之间参数传递
class gloVar():
    # 配置文件路径
    config_file_path = 'config/config.ini'
    # 框选屏幕大小标志
    box_screen_flag = False
    # 保存图片标志(是否需要保存图片,用来实时监测目标位置)
    save_pic_flag = False

# 需要获取机械臂点击起点(录像case时起点标志位)
class robot_other():
    # 机械臂起点标志
    robot_start_flag = False


# Icon路径
class icon_path():
    # 应用窗口图标
    Icon_file       = 'config/Icon/other_icon/Icon.jpg'
    # 视频栏背景图标
    background_file = 'config/Icon/other_icon/background.jpg'
    # 视频栏播放器图标
    Icon_player_play       = 'config/Icon/video_icon/play.png'
    Icon_player_replay     = 'config/Icon/video_icon/replay.png'
    Icon_player_pause      = 'config/Icon/video_icon/pause.png'
    Icon_player_last_video = 'config/Icon/video_icon/last_video.png'
    Icon_player_next_video = 'config/Icon/video_icon/next_video.png'
    Icon_player_last_frame = 'config/Icon/video_icon/last_frame.png'
    Icon_player_next_frame = 'config/Icon/video_icon/next_frame.png'
    # ui相关action图标
    Icon_ui_setting      = 'config/Icon/other_icon/setting.png'
    Icon_ui_open_camera  = 'config/Icon/other_icon/open_camera.png'
    Icon_ui_close_camera = 'config/Icon/other_icon/close_camera.png'
    Icon_ui_capture      = 'config/Icon/other_icon/capture.png'
    Icon_ui_box_screen   = 'config/Icon/other_icon/box_screen.png'
    Icon_ui_folder_go    = 'config/Icon/other_icon/folder_go.png'
    # robot相关action图标
    Icon_restart_server     = 'config/Icon/robot_icon/restart_server.png'
    Icon_robot_click        = 'config/Icon/robot_icon/click.png'
    Icon_robot_double_click = 'config/Icon/robot_icon/double_click.png'
    Icon_robot_long_click   = 'config/Icon/robot_icon/long_click.png'
    Icon_robot_slide        = 'config/Icon/robot_icon/slide.png'
    Icon_robot_lock         = 'config/Icon/robot_icon/lock.png'
    Icon_robot_unlock       = 'config/Icon/robot_icon/unlock.png'
    Icon_robot_get_position = 'config/Icon/robot_icon/get_position.png'

class uArm_action():
    # 机械臂动作类型(点击/双击/长按/滑动)
    uArm_action_type = None
    uArm_click = 'click'
    uArm_double_click = 'double_click'
    uArm_long_click = 'long_click'
    uArm_slide = 'slide'
    uArm_get_position = 'get_position'
    uArm_unlock = 'servo_detach'
    uArm_lock = 'servo_attach'

# 机械臂操作参数
class uArm_param():
    base_x_point = 0.0
    base_y_point = 0.0
    base_z_point = 0.0
    actual_screen_width  = 226
    actual_screen_height = 127
    port_address = 'http://localhost:8000/uArm/'


# 自定义log对象
import time
class logger():
    def __init__(self, string):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ' >> -- ' + str(string))