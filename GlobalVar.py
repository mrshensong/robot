# 文件之间参数传递
class gloVar():
    # 配置文件路径
    config_file_path = 'config/config.ini'
    # 框选屏幕大小标志
    box_screen_flag = False
    # 保存图片标志(是否需要保存图片,用来实时监测目标位置)
    save_pic_flag = False
    # 添加动作按钮是否可以点击(需要先框选车机屏幕大小, 之后才能点击)
    add_action_button_flag = False
    # request请求状态(在可接收信息的时候才可以允许发送请求: ok可以发送请求/其余情况不可以发送请求)
    request_status = 'ok'


class robot_other():
    # 机械臂起点标志
    robot_start_flag = False
    # 需要进行框选动作时, 打开此标志
    select_template_flag = False
    # 全局传递图像
    image = None
    # 全局传递模板图片路径
    mask_path = None
    # 数据处理标志
    data_process_flag = False
    # 判断当前action是否已经保存成为case标志
    actions_saved_to_case = True


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
    # ui工具栏相关action图标
    Icon_ui_setting      = 'config/Icon/other_icon/setting.png'
    Icon_ui_open_camera  = 'config/Icon/other_icon/open_camera.png'
    Icon_ui_close_camera = 'config/Icon/other_icon/close_camera.png'
    Icon_ui_capture      = 'config/Icon/other_icon/capture.png'
    Icon_ui_box_screen   = 'config/Icon/other_icon/box_screen.png'
    Icon_ui_folder_go    = 'config/Icon/other_icon/folder_go.png'
    # robot工具栏相关action图标
    Icon_restart_server       = 'config/Icon/robot_icon/restart_server.png'
    Icon_robot_click          = 'config/Icon/robot_icon/click.png'
    Icon_robot_double_click   = 'config/Icon/robot_icon/double_click.png'
    Icon_robot_long_click     = 'config/Icon/robot_icon/long_click.png'
    Icon_robot_slide          = 'config/Icon/robot_icon/slide.png'
    Icon_robot_lock           = 'config/Icon/robot_icon/lock.png'
    Icon_robot_unlock         = 'config/Icon/robot_icon/unlock.png'
    Icon_robot_get_position   = 'config/Icon/robot_icon/get_position.png'
    Icon_robot_with_record    = 'config/Icon/robot_icon/with_record.png'
    Icon_robot_without_record = 'config/Icon/robot_icon/without_record.png'
    # 视频播放工具栏相关图标
    Icon_video_play         = 'config/Icon/other_icon/video_play.png'
    # 自定义控件相关图标
    Icon_custom_delete            = 'config/Icon/custom_widget_icon/delete.png'
    Icon_custom_play              = 'config/Icon/custom_widget_icon/play.png'
    Icon_tab_widget_add           = 'config/Icon/tab_widget_icon/add.png'
    Icon_tab_widget_delete        = 'config/Icon/tab_widget_icon/delete.png'
    Icon_tab_widget_all_select    = 'config/Icon/tab_widget_icon/all_select.png'
    Icon_tab_widget_all_un_select = 'config/Icon/tab_widget_icon/all_un_select.png'
    Icon_tab_widget_execute       = 'config/Icon/tab_widget_icon/execute.png'
    Icon_tab_widget_import        = 'config/Icon/tab_widget_icon/import.png'
    Icon_tab_widget_save          = 'config/Icon/tab_widget_icon/save.png'


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
    # 机械臂是否操作同时脚本录制(False不录制脚本/True录制脚本)
    uArm_with_record = False


# 机械臂操作参数
class uArm_param():
    base_x_point = 0.0
    base_y_point = 0.0
    base_z_point = 0.0
    actual_screen_width  = 226
    actual_screen_height = 127
    port_address = 'http://localhost:8000/uArm/'


# 添加动作子窗口
class add_action_window():
    # 是否有添加动作
    add_action_flag = False
    # 添加动作子窗口的信息选项名称
    des_text    = 'des_text'
    action_type = 'action_type'
    points      = 'points'
    take_back   = 'take_back'


class window_status():
    # 机械臂('机械臂连接成功!' / '机械臂连接失败!')
    robot_connect_status = '机械臂未连接!'
    # 视频帧率
    video_frame_rate = '120fps'
    # action_tab页面
    action_tab_status = '没有action'
    # case_tab页面
    case_tab_status = '没有打开case目录'


# 配置文件的读取和写入
import configparser
class profile():
    def __init__(self, type='read', file=None, section=None, option=None, value=None):
        if type == 'read':
            self.path = self.get_config_value(file=file, section=section, option=option)
        if type == 'write':
            self.set_config_value(file=file, section=section, option=option, value=value)


    # 获取config的参数
    def get_config_value(self, file, section, option):
        config = configparser.ConfigParser()
        config.read(file, encoding='utf-8')
        return config.get(section, option)


    # 设置config的参数
    def set_config_value(self, file, section, option, value):
        config = configparser.ConfigParser()
        config.read(file, encoding='utf-8')
        if section not in config.sections():
            config.add_section(section)
        config.set(section, option, str(value))
        with open(file, 'w+', encoding='utf-8') as cf:
            config.write(cf)


# 自定义log对象
import time
class logger():
    def __init__(self, string):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ' >> -- ' + str(string))


# 合并路径(传入要合并的几个部分)
class merge_path():
    merged_path = None
    def __init__(self, section_path):
        path_list = []
        for section in section_path:
            if '\\\\' in section:
                section = section.replace('\\\\', '/')
            elif '\\' in section:
                section = section.replace('\\', '/')
            else:
                section = section
            path_list.append(section)
        merged_path = '/'.join(path_list)
        if '//' in merged_path:
            self.merged_path = merged_path.replace('//', '/')
        else:
            self.merged_path = merged_path