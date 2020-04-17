import os
import re
import cv2
import time
import subprocess
import numpy as np
from uarm_action.uarm import SwiftAPI
from GlobalVar import Logger
from uarm_action.video_of_external_camera import ExternalCameraVideo
from uarm_action.video_of_system_camera import SystemCameraVideo
from GlobalVar import *


class ArmAction:
    def __init__(self, use_external_camera_flag, camera_width, camera_height):
        # 连接机械臂
        self.connect_robot()
        # 如果为True则使用外接相机, False使用电脑内置相机
        # 视频线程
        if use_external_camera_flag is True:
            self.video = ExternalCameraVideo(video_path=None, video_width=camera_width, video_height=camera_height)
        else:
            self.video = SystemCameraVideo(video_path=None, video_width=camera_width, video_height=camera_height)

    # 重新连接机械臂
    def connect_robot(self):
        self.speed_opt = 150
        self.cmd_g1 = "G1"
        self.cmd_g0 = "G0"
        self.swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'}, do_not_open=True)
        try:
            self.swift.connect()
            WindowStatus.robot_connect_status = '机械臂连接成功'
            Logger("机械臂连接成功  端口: {}".format(self.swift.port))
        except:
            WindowStatus.robot_connect_status = '机械臂连接失败'
            Logger("连接机械臂失败")
        self.swift.waiting_ready()
        self.swift.set_mode(0)
        time.sleep(1)
        self.swift.set_position(50, 100, 40, 20, cmd="G0")
        self.swift.flush_cmd()
        # 锁定机械臂
        self.swift.set_servo_attach()

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
        # 将基准坐标写入配置文件
        Profile(type='write', file=GloVar.config_file_path, section='param', option='base_point', value=str(position))
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
        self.set_position(x, y, z_l+1.3, speed)
        if trigger == 1:
            self.video.allow_start_flag = True
        self.set_position(x, y, z_h, speed)
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
        # 此处为视频中的当前帧插入标记(抬起前还是抬起后插入标记)
        if trigger == 1:
            self.video.allow_start_flag = True
        # self.set_position(x, y, z_h, speed)
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
            self.video.allow_start_flag = True
        self.swift.set_position(x_e, y_e, speed=speed, cmd=self.cmd_g1)
        self.swift.flush_cmd()
        self.swift.set_position(z=z_h, speed=speed)
        self.swift.flush_cmd()
        if leave == 1:
            self.set_position(50, 100, 40)

    # 执行机械臂动作
    def play_motion_action(self, action):
        if action['action_type'] == 'click':
            self.play_click_action(action)
        elif action['action_type'] == 'double_click':
            self.play_double_click_action(action)
        elif action['action_type'] == 'long_click':
            self.play_long_click(action)
        elif action['action_type'] == 'slide':
            self.play_slide_action(action)

    # 摄像头录制动作
    def play_record_action(self, info_dict):
        data = info_dict
        # 视频路径为参数中的获取到的路径+当前case开始执行的时间
        video_path = MergePath([data['video_path'], GloVar.current_time]).merged_path
        record_status = data['record_status']
        video_type = data['video_type']
        video_name = data['video_name']
        Logger('执行-->action[record]----status[%s]' % record_status)
        # 重置video对象中的video_path
        self.video.video_path = video_path
        if record_status == 'record_start':
            self.video.start_record_video(case_type=video_type, case_name=video_name)
        elif record_status == 'record_stop':
            self.video.stop_record_video()
            while self.video.restart_record_flag is False:
                time.sleep(0.02)

    # 断言动作
    def play_assert_action(self, info_dict):
        data = info_dict
        template_image = data[AssertAction.assert_template_name]
        Logger('执行-->action[assert]---------模板: %s' % str(template_image))
        if os.path.exists(template_image) is False:
            Logger('预期模板不存在: ' + template_image)
            return False
        target_image = GloVar.camera_image.copy()
        # 获取模板的灰度图
        template_image = cv2.imdecode(np.fromfile(template_image, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        target_image = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)
        # 模板匹配
        threshold = self.match_template(target_image, template_image)
        if threshold > 0.95:
            Logger('预期界面-->匹配正确')
            return True
        else:
            Logger('预期界面-->匹配错误')
            return False

    # 恢复动作
    def play_restore_action(self, info_dict):
        # 恢复app到桌面
        screen_type = info_dict[RestoreAction.restore_screen]
        package = self.get_current_package_name(screen_type)
        Logger('执行-->action[restore_screen]---------包名: %s' % str(package))
        if package is not None:
            self.restore_app(package)
            Logger('退出当前app[%s]' % package)
        else:
            Logger('没有获取到app包名')
        time.sleep(1)

    # 延时动作
    @staticmethod
    def play_sleep_action(info_dict):
        data = info_dict
        sleep_time = float(data['sleep_time'])
        Logger('执行-->action[sleep]----status[%s]' % str(sleep_time))
        time.sleep(sleep_time)

    # 执行调用的函数
    def play_call_function_action(self, info_dict):
        function_name = info_dict[CallFunctionAction.function_name]
        function_name = MergePath([GloVar.project_path, 'function', function_name]).merged_path
        function_info_dict_list = Common.read_script_tag(function_name)
        info_dict_list = []
        for info_dict in function_info_dict_list:
            info_dict = Common.add_action_mark(info_dict)
            info_dict_list.append(info_dict)
        info_dict_list = self.arrange_actions(info_dict_list)
        Logger('执行-->action[call_function]----函数名[%s]' % str(function_name))
        self.deal_action_list(info_dict_list)
        Logger('结束-->action[call_function]----函数名[%s]' % str(function_name))

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
            # 重新整理action_list并执行
            action_list = self.arrange_actions(data)
            self.deal_action_list(action_list)
            # 打印描述信息
            if description is not None:
                if description == 'actions':
                    Logger('[选中的actions执行结束]')
                else:
                    Logger('[执行结束case] : %s' % description)
                WindowStatus.operating_status = '空闲状态/动作执行结束'
        GloVar.request_status = 'ok'
        # else:
        #     return HttpResponse("data error")
    # return HttpResponse("ok")

    # 先整理动作(遇到if-else将他们整理成逻辑语句)
    @staticmethod
    def arrange_actions(action_list):
        # 存放新整理的动作列表
        new_arrange_actions = []
        # 存放嵌套的逻辑dict(按顺序, 目的为了获取每一级嵌套结束后, 获取当前的逻辑词典)
        action_dict_list = []
        # 判断是否逻辑语句标志(出现1个if时候=1, 2个if=2...)
        logic_flag = 0
        # 判断是否循环语句标志(出现1个loop_start时候=1, 2个loop_start=2...)
        loop_flag = 0
        # 判断需要将当前action放入逻辑语句动作中的哪个键值中(if/then/else)
        logic_or_loop_type = None
        # 保存上一次嵌套的类型, 以保证可以存放入正确的类型里面
        old_logic_or_loop_type = None
        for i in range(len(action_list)):
            action = action_list[i]
            # 判断逻辑起点(logic_action = if 为起点)
            if action['execute_action'] == 'logic_action':
                if action[LogicAction.logic_action] == LogicAction.logic_if:
                    # 每进入一个新的嵌套(需要保证之前的类型, 一面当前嵌套结束后, 后面动作不知道归为哪一类)
                    old_logic_or_loop_type = logic_or_loop_type
                    logic_flag += 1
                    # 存放逻辑语句动作
                    logic_action_dict = {'execute_action': 'logic_action',
                                         LogicAction.logic_if: [],
                                         LogicAction.logic_then: [],
                                         LogicAction.logic_else: [],
                                         LogicAction.logic_end_if: []}
                    # 将逻辑语句追加到action_list后面
                    if logic_flag == 1:
                        if loop_flag > 0:
                            current_action_dict[logic_or_loop_type].append(logic_action_dict)
                        else:
                            # 只有最外层才可以追加进new_arrange_actions里面
                            new_arrange_actions.append(logic_action_dict)
                    # 其余情况追加到前一个逻辑里面
                    else:
                        current_action_dict[logic_or_loop_type].append(logic_action_dict)
                    current_action_dict = logic_action_dict
                    action_dict_list.append(current_action_dict)
                elif action[LogicAction.logic_action] == LogicAction.logic_end_if:
                    logic_flag -= 1
                    action_dict_list.pop(-1)
                    if len(action_dict_list) > 0:
                        current_action_dict = action_dict_list[-1]
                    else:
                        current_action_dict = {}
            # 判断逻辑起点(loop_action = loop_start 为起点)
            elif action['execute_action'] == 'loop_action':
                if action[LoopAction.loop_action] == LoopAction.loop_start:
                    # 每进入一个新的嵌套(需要保证之前的类型, 一面当前嵌套结束后, 后面动作不知道归为哪一类)
                    old_logic_or_loop_type = logic_or_loop_type
                    loop_flag += 1
                    # 存放循环语句动作
                    loop_action_dict = {'execute_action': 'loop_action',
                                        LoopAction.loop_num: int(action[LoopAction.loop_num]),
                                        LoopAction.loop_start: [],
                                        LoopAction.loop_end: []}
                    # 将循环语句追加到action_list后面
                    if loop_flag == 1:
                        if logic_flag > 0:
                            current_action_dict[logic_or_loop_type].append(loop_action_dict)
                        else:
                            # 只有最外层才可以追加进new_arrange_actions里面
                            new_arrange_actions.append(loop_action_dict)
                    # 其余情况追加到前一个循环中
                    else:
                        current_action_dict[logic_or_loop_type].append(loop_action_dict)
                    current_action_dict = loop_action_dict
                    action_dict_list.append(current_action_dict)
                elif action[LoopAction.loop_action] == LoopAction.loop_end:
                    loop_flag -= 1
                    action_dict_list.pop(-1)
                    if len(action_dict_list) > 0:
                        current_action_dict = action_dict_list[-1]
                    else:
                        current_action_dict = {}
            # 通过logic_flag将动作装入新动作列表
            if logic_flag > 0 or loop_flag > 0:
                # 通过逻辑改变当前逻辑语句动作键值
                if action['execute_action'] == 'logic_action':
                    if action[LogicAction.logic_action] == LogicAction.logic_if:
                        logic_or_loop_type = LogicAction.logic_if
                    elif action[LogicAction.logic_action] == LogicAction.logic_then:
                        logic_or_loop_type = LogicAction.logic_then
                    elif action[LogicAction.logic_action] == LogicAction.logic_else:
                        logic_or_loop_type = LogicAction.logic_else
                    elif action[LogicAction.logic_action] == LogicAction.logic_end_if:
                        logic_or_loop_type = LogicAction.logic_end_if
                        # 当嵌套结束时候恢复嵌套之前的类型(接着在此类型上添加action)
                        logic_or_loop_type = old_logic_or_loop_type
                # 通过循环改变当前循环语句动作键值
                elif action['execute_action'] == 'loop_action':
                    if action[LoopAction.loop_action] == LoopAction.loop_start:
                        logic_or_loop_type = LoopAction.loop_start
                    elif action[LoopAction.loop_action] == LoopAction.loop_end:
                        logic_or_loop_type = LoopAction.loop_end
                        # 当嵌套结束时候恢复嵌套之前的类型(接着在此类型上添加action)
                        logic_or_loop_type = old_logic_or_loop_type
                # 在当前action_dict中的键值中追加action
                else:
                    # ?当前action属于loop还是logic???
                    current_action_dict[logic_or_loop_type].append(action)
            else:
                if action['execute_action'] != 'logic_action' and action['execute_action'] != 'loop_action':
                    new_arrange_actions.append(action)
        return new_arrange_actions

    # 处理action_list动作并执行(其中包含逻辑语句)
    def deal_action_list(self, action_list):
        # 开始执行动作
        for i in range(len(action_list)):
            action = action_list[i]
            if action['execute_action'] == 'motion_action':
                self.play_motion_action(action)
                time.sleep(0.2)
            elif action['execute_action'] == 'record_action':
                self.play_record_action(action)
                time.sleep(0.2)
            elif action['execute_action'] == 'logic_action':
                time.sleep(1)
                self.execute_logic_action(action)
            elif action['execute_action'] == 'loop_action':
                self.execute_loop_action(action)
            elif action['execute_action'] == 'restore_action':
                self.play_restore_action(action)
            elif action['execute_action'] == 'sleep_action':
                self.play_sleep_action(action)
                time.sleep(0.2)
            elif action['execute_action'] == 'call_function_action':
                self.play_call_function_action(action)
            elif action['execute_action'] == 'adb_action':
                adb_command = action[ADBAction.adb_command]
                adb_desc = action[ADBAction.adb_desc]
                Logger('执行-->action[adb]----描述[%s]' % str(adb_desc))
                self.execute_adb_command(adb_command)
                time.sleep(0.2)

    # 执行逻辑动作
    def execute_logic_action(self, logic_dict):
        logic_if_action = None
        logic_then_action_list = []
        logic_else_action_list = []
        if len(logic_dict[LogicAction.logic_if]) > 0:
            logic_if_action = logic_dict[LogicAction.logic_if][0]
        if len(logic_dict[LogicAction.logic_then]) > 0:
            logic_then_action_list = logic_dict[LogicAction.logic_then]
        if len(logic_dict[LogicAction.logic_else]) > 0:
            logic_else_action_list = logic_dict[LogicAction.logic_else]
        # 开始去执行
        if logic_if_action is not None:
            if logic_if_action['execute_action'] == 'assert_action':
                flag = self.play_assert_action(logic_if_action)
            # 可以添加其他类型的判断语句
            else:
                return
            # if
            if flag is True:
                # then
                break_flag = self.split_and_execute_action(logic_then_action_list)
            # else
            else:
                break_flag = self.split_and_execute_action(logic_else_action_list)
            return break_flag

    # 执行循环动作
    def execute_loop_action(self, loop_dict):
        loop_num = int(loop_dict[LoopAction.loop_num])
        loop_action_list = loop_dict[LoopAction.loop_start]
        for i in range(loop_num):
            break_flag = self.split_and_execute_action(loop_action_list)
            if break_flag is True:
                Logger('跳出当前loop循环')
                break

    # 拆解action动作并执行(要使用break, 可以在此处返回值用来标记(break_flag,判断是否需要执行跳出循环))
    def split_and_execute_action(self, action_list):
        break_flag = False
        # 开始执行动作
        for i in range(len(action_list)):
            action = action_list[i]
            if action['execute_action'] == 'motion_action':
                self.play_motion_action(action)
                time.sleep(0.2)
            elif action['execute_action'] == 'record_action':
                self.play_record_action(action)
                time.sleep(0.2)
            elif action['execute_action'] == 'restore_action':
                self.play_restore_action(action)
            elif action['execute_action'] == 'sleep_action':
                self.play_sleep_action(action)
                time.sleep(0.2)
            elif action['execute_action'] == 'logic_action':
                break_flag = self.execute_logic_action(action)
                if break_flag is True:
                    break
            elif action['execute_action'] == 'loop_action':
                self.execute_loop_action(action)
            elif action['execute_action'] == 'break_action':
                break_flag = True
                break
            elif action['execute_action'] == 'call_function_action':
                self.play_call_function_action(action)
            elif action['execute_action'] == 'adb_action':
                adb_command = action[ADBAction.adb_command]
                adb_desc = action[ADBAction.adb_desc]
                Logger('执行-->action[adb]----描述[%s]' % str(adb_desc))
                self.execute_adb_command(adb_command)
                time.sleep(0.2)
        return break_flag

    # 断言操作需要用到的模板匹配
    @staticmethod
    def match_template(source_img, target_img):
        """
        :param source_img: 源图像(大图)
        :param target_img: 靶子图像(小图)
        :return:
        """
        if type(source_img) is str:
            source_img = cv2.imdecode(np.fromfile(source_img, dtype=np.uint8), -1)
        if type(target_img) is str:
            target_img = cv2.imdecode(np.fromfile(target_img, dtype=np.uint8), -1)
        # 匹配方法
        match_method = cv2.TM_CCOEFF_NORMED
        # 模板匹配
        match_result = cv2.matchTemplate(source_img, target_img, match_method)
        # 查找匹配度和坐标位置
        min_threshold, max_threshold, min_threshold_position, max_threshold_position = cv2.minMaxLoc(match_result)
        # 返回最大匹配率
        return max_threshold

    # 执行adb命令
    @staticmethod
    def execute_adb_command(command):
        pi = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pi.wait()
        stdout = pi.stdout.read()
        stdout = stdout.decode('gbk', 'ignore')
        return stdout

    # 获取当前包名
    def get_current_package_name(self, screen_type):
        command = GloVar.adb_command + ' shell dumpsys window | findstr mCurrentFocus'
        result = self.execute_adb_command(command)
        current_package = None
        # 匹配包名
        # 中控屏
        if screen_type == GloVar.screen_type[0]:
            pattern = re.compile(r'mCurrentFocus=Window\{[\da-zA-Z]+\s+[\da-zA-Z]+\s+\S+/')
        # 副驾屏
        elif screen_type == GloVar.screen_type[1]:
            pattern = re.compile(r'mCurrentFocusSecondDisplay=Window\{[\da-zA-Z]+\s+[\da-zA-Z]+\s+\S+/')
        # 其他
        else:
            pattern = re.compile(r'Window\{[\da-zA-Z]+\s+[\da-zA-Z]+\s+\S+/')
        package_list = pattern.findall(str(result))
        if len(package_list) > 0:
            current_package = package_list[0].split(' ')[-1].split('/')[0]
        Logger('获取到当前package: ' + str(current_package))
        return current_package

    # 恢复当前app到初始状态
    def restore_app(self, package):
        if package.startswith('com.chehejia'):
            if 'launcher' in package:
                return
            command = GloVar.adb_command + ' shell pm clear ' + package
        else:
            command = GloVar.adb_command + ' shell am force-stop ' + package
        self.execute_adb_command(command)
        time.sleep(1)

'''传入的样例'''
# start / start>actions /start>D:/Code/robot/case/测试/滑动测试.xml(三种形式分别:单个action/选中的多个actions/一条case)
# {'des_text': '单击', 'action_type': 'click', 'points': [-53.046, 100.332], 'speed': '200', 'leave': '1', 'trigger': '0', 'execute_action': 'motion_action', 'base': [0.0, 0.0, 0.0]}
# {'des_text': '双击', 'action_type': 'double_click', 'points': [-64.662, 120.263], 'speed': '150', 'leave': '1', 'trigger': '0', 'execute_action': 'motion_action', 'base': [0.0, 0.0, 0.0]}
# {'des_text': '长按', 'action_type': 'long_click', 'points': [-47.819, 93.744], 'speed': '150', 'leave': '1', 'trigger': '0', 'execute_action': 'motion_action', 'base': [0.0, 0.0, 0.0]}
# {'des_text': '滑动', 'action_type': 'slide', 'points': [-63.5, 87.833, -63.5, 138.843], 'speed': '150', 'leave': '1', 'trigger': '0', 'execute_action': 'motion_action', 'base': [0.0, 0.0, 0.0]}
# {'camera_video': 'record', 'record_status': 'record_start', 'video_type': 'test', 'video_name': 'test', 'execute_action': 'record_action'}
# {'assert_template': 'picture', 'assert_template_name': 'D:/Code/robot/picture/assert/123.bmp', 'execute_action': 'assert_action'}
# {'sleep': 'time/s', 'sleep_time': '5.0', 'execute_action': 'sleep_action'}
# {'camera_video': 'record', 'record_status': 'record_stop', 'video_type': 'test', 'video_name': 'test', 'execute_action': 'record_action'}
# stop