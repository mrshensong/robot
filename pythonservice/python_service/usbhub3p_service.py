from pythonservice import brainstem
from pythonservice.brainstem.result import Result
from django.http import HttpResponse
from pythonservice.python_service.utils import logger

try:
    stem = brainstem.stem.USBHub3p()
    result = stem.discoverAndConnect(brainstem.link.Spec.USB)
except:
    logger.info("UsbHub连接失败")


# 打开端口
def setPortEnable(request):
    stem = brainstem.stem.USBHub3p()
    result = stem.discoverAndConnect(brainstem.link.Spec.USB)
    if request.method == 'GET':
        port = request.GET.get("port")
        if result == (Result.NO_ERROR):
            stem.usb.setPortEnable(int(port))
            stem.disconnect()
            return HttpResponse('打开端口 ' + port + ' 成功')
        else:
            return HttpResponse('不能找到设备')
    else:
        return HttpResponse('只支持Get方法')


# 打开全部端口
def setPortAllEnable(request):
    stem = brainstem.stem.USBHub3p()
    result = stem.discoverAndConnect(brainstem.link.Spec.USB)
    if request.method == 'GET':
        if result == (Result.NO_ERROR):
            for port in range(0, 8):
                stem.usb.setPortEnable(port)
            stem.disconnect()
            return HttpResponse('打开全部端口')
        else:
            return HttpResponse('不能找到设备')
    else:
        return HttpResponse('只支持Get方法')


# 关闭端口
def setPortDisable(request):
    stem = brainstem.stem.USBHub3p()
    result = stem.discoverAndConnect(brainstem.link.Spec.USB)
    if request.method == 'GET':
        port = request.GET.get("port")
        if result == (Result.NO_ERROR):
            stem.usb.setPortDisable(int(port))
            stem.disconnect()
            return HttpResponse('关闭端口 ' + port + ' 成功')
        else:
            return HttpResponse('不能找到设备')
    else:
        return HttpResponse('只支持Get方法')


# 关闭全部端口
def setPortAllDisable(request):
    stem = brainstem.stem.USBHub3p()
    result = stem.discoverAndConnect(brainstem.link.Spec.USB)
    if request.method == 'GET':
        if result == (Result.NO_ERROR):
            for port in range(0, 8):
                stem.usb.setPortDisable(port)
            stem.disconnect()
            return HttpResponse('关闭全部端口')
        else:
            return HttpResponse('不能找到设备')
    else:
        return HttpResponse('只支持Get方法')


# 打开端口电源
def setPowerEnable(port):
    if result == (Result.NO_ERROR):
        stem.usb.setPowerEnable(port)
        return HttpResponse('打开端口 %d 电源 成功' % port)
    else:
        return HttpResponse('不能找到设备')


# 打开所有端口电源
def setAllPowerEnable():
    if result == (Result.NO_ERROR):
        for port in range(0, 8):
            stem.usb.setPowerEnable(port)
            return HttpResponse('打开端口 %d 电源 成功' % port)
    else:
        return HttpResponse('不能找到设备')


# 关闭端口电源
def setPowerDisable(port):
    if result == (Result.NO_ERROR):
        stem.usb.setPowerDisable(port)
        return HttpResponse('关闭端口 %d 电源成功' % port)
    else:
        return HttpResponse('不能找到设备')


# 关闭所有端口电源
def setPowerAllDisable():
    if result == (Result.NO_ERROR):
        for port in range(0, 8):
            stem.usb.setPowerDisable(port)
            return HttpResponse('关闭端口 %d 电源成功' % port)
    else:
        return HttpResponse('不能找到设备')


# 端口数据传输可用
def setDataEnable(port):
    if result == (Result.NO_ERROR):
        stem.usb.setDataEnable(port)
        return HttpResponse('设置端口 %d 据传输可用 成功' % port)
    else:
        return HttpResponse('不能找到设备')


# 所有端口数据传输可用
def setDataAllEnable():
    if result == (Result.NO_ERROR):
        for port in range(0, 8):
            stem.usb.setDataEnable(port)
            return HttpResponse('设置端口 %d 据传输可用 成功' % port)
    else:
        return HttpResponse('不能找到设备')


# 端口数据传输不可用
def setDataDisable(port):
    if result == (Result.NO_ERROR):
        stem.usb.setDataDisable(port)
        return HttpResponse('设置端口 %d 据传输不可用 成功' % port)
    else:
        return HttpResponse('不能找到设备')


# 所有端口数据传输不可用
def setDataAllDisable():
    if result == (Result.NO_ERROR):
        for port in range(0, 8):
            stem.usb.setDataDisable(port)
            return HttpResponse('设置端口 %d 据传输不可用 成功' % port)
    else:
        return HttpResponse('不能找到设备')


def switch_to_method(var):
    switcher = {
        0: setPortEnable(1),
        1: setPortDisable(1),
        2: setPowerEnable(1),
        3: setPowerDisable(1),
        4: setDataEnable(1),
        5: setDataDisable(1)
    }
    switcher.get(var, "无有效function")
