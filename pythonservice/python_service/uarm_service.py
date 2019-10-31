import time
from threading import Thread
from django.http import HttpResponse
from rest_framework.utils import json
from pythonservice.uarm import SwiftAPI
from pythonservice.python_service.utils import logger
from pythonservice.python_service.video import Video

speed_opt = 150

cmd_g1 = "G1"
cmd_g0 = "G0"
swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'}, do_not_open=True)
try:
    swift.connect()
    logger.info("机械臂连接成功  端口: {}".format(swift.port))
except:
    logger.warning("连接机械臂失败")
swift.waiting_ready()
swift.set_mode(0)
time.sleep(1)
swift.set_position(50, 100, 40, 20, cmd="G0")
swift.flush_cmd()
# 视频线程
video = Video(video_path=None)
Thread(target=video.recording, args=()).start()


def set_position(request):
    """
    移动到指定坐标
    :param request: 请求对象
    :return: 响应信息
    """
    if request.method == 'GET':
        x = request.GET.get("x")
        y = request.GET.get("y")
        z = request.GET.get("z")
        port = request.GET.get("port")
        logger.info("参数：x=%s y=%s z=%s port=%s", x, y, z, port)
        if port is not None and swift.port != port:
            swift.connect(port)
            swift.waiting_ready()
        swift.set_position(x, y, z, cmd=cmd_g1)
        swift.flush_cmd()
        return HttpResponse("ok")
    if request.method == 'POST':
        data = json.loads(request.body)
        position = data['position']
        data.setdefault('port', None)
        port = data['port']
        logger.info("参数：x=%s y=%s z=%s port=%s", position[0], position[1], position[2], port)
        if port is not None and swift.port != port:
            swift.connect(port)
            swift.waiting_ready()
        set_position_(position[0], position[1], position[2])
        return HttpResponse("ok")


def stop(request):
    """
    机械臂收起
    :param request: 请求对象
    :return: 响应信息
    """
    if request.method == 'GET':
        port = request.GET.get("port")
        if port is not None and swift.port != port:
            swift.connect(port)
            swift.waiting_ready()
        set_position_(50, 100, 40)
        return HttpResponse("ok")
    else:
        return HttpResponse("please use get")


def slide(request):
    """
    滑动操作
    :param request: 请求对象
    :return: 响应信息
    """
    if request.method == 'GET':
        return HttpResponse("please use post")
    if request.method == 'POST':
        data = json.loads(request.body)
        data.setdefault('port', None)
        data.setdefault('speed', None)
        port = data['port']
        speed = speed_opt if data['speed'] is None else data['speed']
        trigger = int(data['trigger'])
        base_position = data['base']
        start = data['start']
        end = data['end']
        # 坐标浮点数精度过高机械臂无法处理,造成长时间无响应
        x_s = round(base_position[0] - start[0], 4)
        y_s = round(base_position[1] - start[1], 4)
        x_e = round(base_position[0] - end[0], 4)
        y_e = round(base_position[1] - end[1], 4)
        z_l = round(base_position[2], 4)
        z_h = round(z_l + 30, 4)
        if port is not None and swift.port != port:
            swift.connect(port)
            swift.waiting_ready()
        swift.set_position(x_s, y_s, z_h, speed)
        swift.flush_cmd()
        swift.set_position(z=z_l, speed=speed)
        swift.flush_cmd()
        # 此处为视频中的当前帧插入标记
        if trigger == 1:
            video.robot_start_flag = True
        swift.set_position(x_e, y_e, speed=speed, cmd=cmd_g1)
        swift.flush_cmd()
        swift.set_position(z=z_h, speed=speed)
        swift.flush_cmd()
        data.setdefault('leave', 0)
        leave = data['leave']
        if leave == 1:
            set_position_(50, 100, 40)
        return HttpResponse("ok")


def click(request):
    """
    点击操作
    :param request: 请求对象
    :return: 响应信息
    """
    if request.method == 'GET':
        return HttpResponse("please use post")
    if request.method == 'POST':
        data = json.loads(request.body)
        data.setdefault('port', None)
        data.setdefault('speed', None)
        port = data['port']
        speed = speed_opt if data['speed'] is None else data['speed']
        trigger = int(data['trigger'])
        base_position = data['base']
        position = data['position']
        times = data['time']
        pressure_duration = data['pressure_duration']
        # 坐标浮点数精度过高机械臂无法处理,造成长时间无响应
        x = round(base_position[0] - position[0], 4)
        y = round(base_position[1] - position[1], 4)
        z_l = round(base_position[2], 4)
        z_h = round(z_l + 30, 4)
        if port is not None and swift.port != port:
            swift.connect(port)
            swift.waiting_ready()
        for i in range(times):
            set_position_(x, y, z_h, speed)
            set_position_(x, y, z_l, speed)
            time.sleep(pressure_duration / 1000)
            set_position_(x, y, z_h, speed)
            # 此处为视频中的当前帧插入标记
            if trigger == 1:
                video.robot_start_flag = True
        data.setdefault('leave', 0)
        leave = data['leave']
        if leave == 1:
            set_position_(50, 100, 40)
        return HttpResponse("ok")


def servo_detach(request):
    set_position_(50, 100, 40)
    swift.set_servo_detach()
    return HttpResponse("解锁电机")


def servo_attach(request):
    swift.set_servo_attach()
    return HttpResponse("锁定电机")


def get_position(request):
    """
    获取机械臂当前坐标
    :param request: 请求对象
    :return: 坐标: x,y,z
    """
    p = swift.get_position()
    return HttpResponse("{0[0]},{0[1]},{0[2]}".format(p))


def set_position_(x=None, y=None, z=None, speed=speed_opt, cmd="G0"):
    logger.info("set position: {},{},{} speed={} cmd={}".format(x, y, z, speed, cmd))
    swift.set_position(x, y, z, speed, cmd=cmd)
    swift.flush_cmd()


# 执行视频录制相关动作
def execute_record_action(request):
    if request.method == 'GET':
        return HttpResponse("please use post")
    if request.method == 'POST':
        data = json.loads(request.body)
        # data.setdefault('port', None)
        # data.setdefault('speed', None)
        video_path    = data['video_path']
        record_status = data['record_status']
        video_type    = data['video_type']
        video_name    = data['video_name']
        # 重置video对象中的video_path
        video.video_path = video_path
        if record_status == 'record_start':
            video.start_record_video(case_type=video_type, case_name=video_name)
        elif record_status == 'record_stop':
            video.stop_record_video()
            while video.re_start_record_flag is False:
                time.sleep(0.02)
        # print(record_status)
        return HttpResponse("ok")


# 执行延时相关动作
def execute_sleep_action(request):
    if request.method == 'GET':
        return HttpResponse("please use post")
    if request.method == 'POST':
        data = json.loads(request.body)
        # data.setdefault('port', None)
        # data.setdefault('speed', None)
        sleep_time = float(data['sleep_time'])
        time.sleep(sleep_time)
        return HttpResponse("ok")


# 执行多条actions
def execute_actions(request):
    if request.method == 'GET':
        return HttpResponse("please use post")
    if request.method == 'POST':
        data = json.loads(request.body)
        # 判断校验位
        if data[0] == 'start' and data[-1] == 'stop':
            # 去掉校验信息(只保留有用内容)
            data.pop(-1)
            data.pop(0)
            for action in data:
                if action['execute_action'] == 'motion_action':
                    if action['action_type'] == 'click':
                        play_click_action(action)
                    elif action['action_type'] == 'double_click':
                        play_double_click_action(action)
                    elif action['action_type'] == 'long_click':
                        play_long_click(action)
                    elif action['action_type'] == 'slide':
                        play_slide_action(action)
                elif action['execute_action'] == 'record_action':
                    play_record_action(action)
                elif action['execute_action'] == 'sleep_action':
                    play_sleep_action(action)
        else:
            return HttpResponse("data error")
    return HttpResponse("ok")


# 以下内容为具体执行
def play_click_action(info_dict):
    data = info_dict
    speed = int(data['speed'])
    trigger = int(data['trigger'])
    leave = int(data['leave'])
    base_position = data['base']
    position = data['points']
    # 坐标浮点数精度过高机械臂无法处理,造成长时间无响应
    x = round(base_position[0] - position[0], 4)
    y = round(base_position[1] - position[1], 4)
    z_l = round(base_position[2], 4)
    z_h = round(z_l + 30, 4)
    set_position_(x, y, z_h, speed)
    set_position_(x, y, z_l, speed)
    set_position_(x, y, z_h, speed)
    # 此处为视频中的当前帧插入标记
    if trigger == 1:
        video.robot_start_flag = True
    if leave == 1:
        set_position_(50, 100, 40)
    return HttpResponse("ok")


def play_double_click_action(info_dict):
    data = info_dict
    speed = int(data['speed'])
    trigger = int(data['trigger'])
    leave = int(data['leave'])
    base_position = data['base']
    position = data['points']
    # 坐标浮点数精度过高机械臂无法处理,造成长时间无响应
    x = round(base_position[0] - position[0], 4)
    y = round(base_position[1] - position[1], 4)
    z_l = round(base_position[2], 4)
    z_h = round(z_l + 30, 4)
    for i in range(2):
        set_position_(x, y, z_h, speed)
        set_position_(x, y, z_l, speed)
        set_position_(x, y, z_h, speed)
    if leave == 1:
        set_position_(50, 100, 40)
    return HttpResponse("ok")


def play_long_click(info_dict):
    data = info_dict
    speed = int(data['speed'])
    trigger = int(data['trigger'])
    leave = int(data['leave'])
    base_position = data['base']
    position = data['points']
    pressure_duration = 1000
    # 坐标浮点数精度过高机械臂无法处理,造成长时间无响应
    x = round(base_position[0] - position[0], 4)
    y = round(base_position[1] - position[1], 4)
    z_l = round(base_position[2], 4)
    z_h = round(z_l + 30, 4)
    set_position_(x, y, z_h, speed)
    set_position_(x, y, z_l, speed)
    time.sleep(pressure_duration / 1000)
    set_position_(x, y, z_h, speed)
    # 此处为视频中的当前帧插入标记
    if trigger == 1:
        video.robot_start_flag = True
    if leave == 1:
        set_position_(50, 100, 40)
    return HttpResponse("ok")


def play_slide_action(info_dict):
    data = info_dict
    speed = int(data['speed'])
    trigger = int(data['trigger'])
    leave = int(data['leave'])
    base_position = data['base']
    start = data['points'][:2]
    end = data['points'][2:]
    # 坐标浮点数精度过高机械臂无法处理,造成长时间无响应
    x_s = round(base_position[0] - start[0], 4)
    y_s = round(base_position[1] - start[1], 4)
    x_e = round(base_position[0] - end[0], 4)
    y_e = round(base_position[1] - end[1], 4)
    z_l = round(base_position[2], 4)
    z_h = round(z_l + 30, 4)
    swift.set_position(x_s, y_s, z_h, speed)
    swift.flush_cmd()
    swift.set_position(z=z_l, speed=speed)
    swift.flush_cmd()
    # 此处为视频中的当前帧插入标记
    if trigger == 1:
        video.robot_start_flag = True
    swift.set_position(x_e, y_e, speed=speed, cmd=cmd_g1)
    swift.flush_cmd()
    swift.set_position(z=z_h, speed=speed)
    swift.flush_cmd()
    if leave == 1:
        set_position_(50, 100, 40)
    return HttpResponse("ok")


def play_record_action(info_dict):
    data = info_dict
    video_path = data['video_path']
    record_status = data['record_status']
    video_type = data['video_type']
    video_name = data['video_name']
    # 重置video对象中的video_path
    video.video_path = video_path
    if record_status == 'record_start':
        video.start_record_video(case_type=video_type, case_name=video_name)
    elif record_status == 'record_stop':
        video.stop_record_video()
        while video.re_start_record_flag is False:
            time.sleep(0.02)
    # print(record_status)
    return HttpResponse("ok")


def play_sleep_action(info_dict):
    data = info_dict
    sleep_time = float(data['sleep_time'])
    time.sleep(sleep_time)
    return HttpResponse("ok")


# start
# {'des_text': '单击', 'action_type': 'click', 'points': [-53.046, 100.332], 'speed': '200', 'leave': '1', 'trigger': '0', 'execute_action': 'motion_action', 'base': [0.0, 0.0, 0.0]}
# {'des_text': '双击', 'action_type': 'double_click', 'points': [-64.662, 120.263], 'speed': '150', 'leave': '1', 'trigger': '0', 'execute_action': 'motion_action', 'base': [0.0, 0.0, 0.0]}
# {'des_text': '长按', 'action_type': 'long_click', 'points': [-47.819, 93.744], 'speed': '150', 'leave': '1', 'trigger': '0', 'execute_action': 'motion_action', 'base': [0.0, 0.0, 0.0]}
# {'des_text': '滑动', 'action_type': 'slide', 'points': [-63.5, 87.833, -63.5, 138.843], 'speed': '150', 'leave': '1', 'trigger': '0', 'execute_action': 'motion_action', 'base': [0.0, 0.0, 0.0]}
# {'camera_video': 'record', 'record_status': 'record_start', 'video_type': 'test', 'video_name': 'test', 'execute_action': 'record_action'}
# {'sleep': 'time/s', 'sleep_time': '5.0', 'execute_action': 'sleep_action'}
# {'camera_video': 'record', 'record_status': 'record_stop', 'video_type': 'test', 'video_name': 'test', 'execute_action': 'record_action'}
# stop