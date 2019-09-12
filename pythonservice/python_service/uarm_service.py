from django.http import HttpResponse
from rest_framework.utils import json
from uarm import SwiftAPI
import time
from python_service.utils import logger

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
