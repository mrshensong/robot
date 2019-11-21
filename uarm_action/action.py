import time
from threading import Thread
from uarm_action.uarm import SwiftAPI
from GlobalVar import Logger
from uarm_action.video import Video
from GlobalVar import GloVar, RobotArmParam, WindowStatus


class ArmAction:
    def __init__(self, camera_width, camera_height):
        self.speed_opt = 150
        self.cmd_g1 = "G1"
        self.cmd_g0 = "G0"
        self.swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'}, do_not_open=True)
        try:
            self.swift.connect()
            WindowStatus.robot_connect_status = '机械臂连接成功!'
            Logger("机械臂连接成功  端口: {}".format(self.swift.port))
        except:
            WindowStatus.robot_connect_status = '机械臂连接失败!'
            Logger("连接机械臂失败")
        self.swift.waiting_ready()
        self.swift.set_mode(0)
        time.sleep(1)
        self.swift.set_position(50, 100, 40, 20, cmd="G0")
        self.swift.flush_cmd()
        # 视频线程
        self.video = Video(video_path=None, video_width=camera_width, video_height=camera_height)

    def stop(self):
        self.set_position(50, 100, 40)

    # 机械臂解锁
    def servo_detach(self):
        self.set_position(50, 100, 40)
        self.swift.set_servo_detach()
        Logger("解锁电机")

    # 机械臂锁定
    def servo_attach(self):
        self.swift.set_servo_attach()
        Logger("锁定电机")

    # 机械臂获取当前位置
    def get_position(self):
        position = self.swift.get_position()
        RobotArmParam.base_x_point = position[0]
        RobotArmParam.base_y_point = position[1]
        RobotArmParam.base_z_point = position[2]
        Logger('机械臂当前位置为: %s' % str(position))

    # 机械臂置位
    def set_position(self, x=None, y=None, z=None, speed=150, cmd="G0"):
        self.swift.set_position(x, y, z, speed, cmd=cmd)
        self.swift.flush_cmd()

    '''以下内容为具体执行'''
    # 机械臂单击
    def play_click_action(self, info_dict):
        data = info_dict
        speed = int(data['speed'])
        trigger = int(data['trigger'])
        leave = int(data['leave'])
        base_position = data['base']
        position = data['points']
        Logger('执行-->action[click]---------坐标: %s' % str(position))
        # 坐标浮点数精度过高机械臂无法处理,造成长时间无响应
        x = round(base_position[0] - position[0], 4)
        y = round(base_position[1] - position[1], 4)
        z_l = round(base_position[2], 4)
        z_h = round(z_l + 30, 4)
        self.set_position(x, y, z_h, speed)
        self.set_position(x, y, z_l, speed)
        self.set_position(x, y, z_h, speed)
        # 此处为视频中的当前帧插入标记
        if trigger == 1:
            self.video.robot_start_flag = True
        if leave == 1:
            self.set_position(50, 100, 40)

    # 机械臂双击
    def play_double_click_action(self, info_dict):
        data = info_dict
        speed = int(data['speed'])
        # trigger = int(data['trigger'])
        leave = int(data['leave'])
        base_position = data['base']
        position = data['points']
        Logger('执行-->action[double_click]---------坐标: %s' % str(position))
        # 坐标浮点数精度过高机械臂无法处理,造成长时间无响应
        x = round(base_position[0] - position[0], 4)
        y = round(base_position[1] - position[1], 4)
        z_l = round(base_position[2], 4)
        z_h = round(z_l + 30, 4)
        for i in range(2):
            self.set_position(x, y, z_h, speed)
            self.set_position(x, y, z_l, speed)
            self.set_position(x, y, z_h, speed)
        if leave == 1:
            self.set_position(50, 100, 40)

    # 机械臂长按
    def play_long_click(self, info_dict):
        data = info_dict
        speed = int(data['speed'])
        trigger = int(data['trigger'])
        leave = int(data['leave'])
        base_position = data['base']
        position = data['points']
        pressure_duration = 1000
        Logger('执行-->action[long_click]---------坐标: %s' % str(position))
        # 坐标浮点数精度过高机械臂无法处理,造成长时间无响应
        x = round(base_position[0] - position[0], 4)
        y = round(base_position[1] - position[1], 4)
        z_l = round(base_position[2], 4)
        z_h = round(z_l + 30, 4)
        self.set_position(x, y, z_h, speed)
        self.set_position(x, y, z_l, speed)
        time.sleep(pressure_duration / 1000)
        self.set_position(x, y, z_h, speed)
        # 此处为视频中的当前帧插入标记
        if trigger == 1:
            self.video.robot_start_flag = True
        if leave == 1:
            self.set_position(50, 100, 40)

    # 机械臂滑动
    def play_slide_action(self, info_dict):
        data = info_dict
        speed = int(data['speed'])
        trigger = int(data['trigger'])
        leave = int(data['leave'])
        base_position = data['base']
        position = data['points']
        start = position[:2]
        end = position[2:]
        Logger('执行-->action[slide]---------坐标: %s' % str(position))
        # 坐标浮点数精度过高机械臂无法处理,造成长时间无响应
        x_s = round(base_position[0] - start[0], 4)
        y_s = round(base_position[1] - start[1], 4)
        x_e = round(base_position[0] - end[0], 4)
        y_e = round(base_position[1] - end[1], 4)
        z_l = round(base_position[2], 4)
        z_h = round(z_l + 30, 4)
        self.swift.set_position(x_s, y_s, z_h, speed)
        self.swift.flush_cmd()
        self.swift.set_position(z=z_l, speed=speed)
        self.swift.flush_cmd()
        # 此处为视频中的当前帧插入标记
        if trigger == 1:
            self.video.robot_start_flag = True
        self.swift.set_position(x_e, y_e, speed=speed, cmd=self.cmd_g1)
        self.swift.flush_cmd()
        self.swift.set_position(z=z_h, speed=speed)
        self.swift.flush_cmd()
        if leave == 1:
            self.set_position(50, 100, 40)

    # 摄像头录制动作
    def play_record_action(self, info_dict):
        data = info_dict
        video_path = data['video_path']
        record_status = data['record_status']
        video_type = data['video_type']
        video_name = data['video_name']
        video_file = (video_path + '/' + video_type + '/' + video_name + '.mp4')
        Logger('执行-->action[record]----status[%s]----path: %s' % (record_status, video_file))
        # 重置video对象中的video_path
        self.video.video_path = video_path
        if record_status == 'record_start':
            self.video.start_record_video(case_type=video_type, case_name=video_name)
        elif record_status == 'record_stop':
            self.video.stop_record_video()
            while self.video.restart_record_flag is False:
                time.sleep(0.02)

    # 延时动作
    def play_sleep_action(self, info_dict):
        data = info_dict
        sleep_time = float(data['sleep_time'])
        Logger('执行-->action[sleep]----status[%s]' % str(sleep_time))
        time.sleep(sleep_time)

    # 执行多条actions
    def execute_actions(self, info_list):
        data = info_list
        # 判断校验位
        if data[0].startswith('start') and data[-1] == 'stop':
            # 执行的是case&选中的actions
            if '>' in data[0]:
                # 获取描述:case/选中的actions
                description = data[0].split('>')[1]
                if description == 'actions':
                    Logger('[开始执行选中的actions]')
                else:
                    Logger('[开始执行case] : %s' % description)
            # 执行的是单个action
            else:
                description = None
            # 去掉校验信息(掐头去尾, 只保留有用内容)
            data.pop(-1)
            data.pop(0)
            # 开始执行动作
            for action in data:
                if action['execute_action'] == 'motion_action':
                    if action['action_type'] == 'click':
                        self.play_click_action(action)
                        time.sleep(0.2)
                    elif action['action_type'] == 'double_click':
                        self.play_double_click_action(action)
                        time.sleep(0.2)
                    elif action['action_type'] == 'long_click':
                        self.play_long_click(action)
                        time.sleep(0.2)
                    elif action['action_type'] == 'slide':
                        self.play_slide_action(action)
                        time.sleep(0.2)
                elif action['execute_action'] == 'record_action':
                    self.play_record_action(action)
                    time.sleep(0.2)
                elif action['execute_action'] == 'sleep_action':
                    self.play_sleep_action(action)
                    time.sleep(0.2)
            # 打印描述信息
            if description is not None:
                if description == 'actions':
                    Logger('[选中的actions执行结束]')
                else:
                    Logger('[执行结束case] : %s' % description)
        GloVar.request_status = 'ok'
        # else:
        #     return HttpResponse("data error")
    # return HttpResponse("ok")


'''传入的样例'''
# start / start>actions /start>D:/Code/robot/case/测试/滑动测试.xml(三种形式分别:单个action/选中的多个actions/一条case)
# {'des_text': '单击', 'action_type': 'click', 'points': [-53.046, 100.332], 'speed': '200', 'leave': '1', 'trigger': '0', 'execute_action': 'motion_action', 'base': [0.0, 0.0, 0.0]}
# {'des_text': '双击', 'action_type': 'double_click', 'points': [-64.662, 120.263], 'speed': '150', 'leave': '1', 'trigger': '0', 'execute_action': 'motion_action', 'base': [0.0, 0.0, 0.0]}
# {'des_text': '长按', 'action_type': 'long_click', 'points': [-47.819, 93.744], 'speed': '150', 'leave': '1', 'trigger': '0', 'execute_action': 'motion_action', 'base': [0.0, 0.0, 0.0]}
# {'des_text': '滑动', 'action_type': 'slide', 'points': [-63.5, 87.833, -63.5, 138.843], 'speed': '150', 'leave': '1', 'trigger': '0', 'execute_action': 'motion_action', 'base': [0.0, 0.0, 0.0]}
# {'camera_video': 'record', 'record_status': 'record_start', 'video_type': 'test', 'video_name': 'test', 'execute_action': 'record_action'}
# {'sleep': 'time/s', 'sleep_time': '5.0', 'execute_action': 'sleep_action'}
# {'camera_video': 'record', 'record_status': 'record_stop', 'video_type': 'test', 'video_name': 'test', 'execute_action': 'record_action'}
# stop