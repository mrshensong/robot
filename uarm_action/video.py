import os
import cv2
import time
import gxipy as gx
import numpy as np
from threading import Thread
from GlobalVar import GloVar, MergePath, Logger


class Video:

    def __init__(self, video_path, video_width, video_height):
        # 保存视频需要用到的参数
        self.video_path = video_path
        # 视频需要保存的高和宽
        self.video_width = video_width
        self.video_height = video_height
        # 相机对象
        self.cam = None
        # 帧率
        self.frame_rate = 120.0
        # 保存的视频名
        self.video_file_name = None
        # 帧id
        self.frame_id = 0
        # 保存视频帧列表
        self.video_frames_list = []
        # 开始和停止录像标志
        self.record_flag = False
        # 在录制的视频中给某一帧做标记(当做动作的起点, True:标记, False不做标记)
        self.robot_start_flag = False
        # 线程结束标志位
        self.record_thread_flag = True
        # 是否可以重新开始录制视频
        self.restart_record_flag = True
        # 视频类型(app冷/app热/滑动流畅度等等)
        self.case_type = None
        # 视频名称(桌面滑动)
        self.case_name = None
        # 畸变矫正相关参数
        npz_file = np.load('uarm_action/calibrate.npz')
        # npz_file = np.load('calibrate.npz')
        self.mtx = npz_file['mtx']
        self.dist = npz_file['dist']
        self.map_x = None
        self.map_y = None
        # 开启视频流
        Thread(target=self.video_stream, args=()).start()


    # 消除畸变函数
    def un_distortion(self, img):
        try:
            # 耗时操作
            # dst = cv2.undistort(img, mtx, dist, None, new_camera_mtx)
            # 替代方案(节省时间)/map_x, map_y使用全局变量更加节省时间
            if self.map_x is None and self.map_y is None:
                # 计算一个从畸变图像到非畸变图像的映射(只需要执行一次, 找出映射关系即可)
                h, w = img.shape[:2]
                new_camera_mtx, roi = cv2.getOptimalNewCameraMatrix(self.mtx, self.dist, (w, h), 1, (w, h))
                self.map_x, self.map_y = cv2.initUndistortRectifyMap(self.mtx, self.dist, None, new_camera_mtx, (w, h), 5)
            # 使用映射关系对图像进行去畸变
            dst = cv2.remap(img, self.map_x, self.map_y, cv2.INTER_LINEAR)
        except TypeError:
            # 如果发生异常则获取(传入容器是故意传入一个元祖, 使其产生TypeError异常, 好捕捉到开始帧)
            image = img[1]
            dst = cv2.remap(image, self.map_x, self.map_y, cv2.INTER_LINEAR)
            dst[0].fill(255)
        # 裁剪图片
        # x, y, w, h = roi
        # if roi != (0, 0, 0, 0):
        #     dst = dst[y:y + h, x:x + w]
        return dst


    # 调用笔记本摄像头模拟工业摄像头
    def video_stream_1(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_height)
        while self.record_thread_flag is True:
            _, GloVar.camera_image = cap.read()
            if self.record_flag is True:
                # 标记这一帧
                if self.robot_start_flag is False:
                    self.video_frames_list.append(GloVar.camera_image.copy())
                else:
                    self.video_frames_list.append(GloVar.camera_image.copy()[0].fill(255))
        cap.release()
        Logger('退出视频录像线程')


    # 视频流线程
    def video_stream(self):
        # create a device manager
        device_manager = gx.DeviceManager()
        dev_num, dev_info_list = device_manager.update_device_list()
        if dev_num is 0:
            Logger('Number of enumerated devices is 0')
            return
        # open device by serial number(通过sn码获取相机对象)
        self.cam = device_manager.open_device_by_sn(dev_info_list[0].get("sn"))
        # if camera is mono(如果相机是单通道, 则关闭相机)
        if self.cam.PixelColorFilter.is_implemented() is False:
            Logger('This sample does not support mono camera.')
            self.cam.close_device()
            return
        # set continuous acquisition(连续触发模式)
        self.cam.TriggerMode.set(gx.GxSwitchEntry.OFF)
        # 白平衡设置(连续白平衡)
        self.cam.BalanceWhiteAuto.set(gx.GxAutoEntry.CONTINUOUS)
        '''120帧'''
        # 相机采集帧率(相机采集帧率设置为120)
        self.cam.AcquisitionFrameRate.set(self.frame_rate)
        # set exposure(曝光设置为8250, 通过相机帧率计算公司得到, 120帧对应曝光时间为120fps)
        self.cam.ExposureTime.set(8250.0)
        # set gain(设置增益, 调节相机亮度)
        self.cam.Gain.set(8.0)
        '''100帧'''
        # # 相机采集帧率(相机采集帧率设置为60)
        # self.cam.AcquisitionFrameRate.set(self.frame_rate)
        # # set exposure(曝光设置为9930, 通过相机帧率计算公司得到, 100帧对应曝光时间为100fps)
        # self.cam.ExposureTime.set(9930.0)
        # # set gain(设置增益, 调节相机亮度)
        # self.cam.Gain.set(1.0)
        '''60帧'''
        # # 相机采集帧率(相机采集帧率设置为60)
        # self.cam.AcquisitionFrameRate.set(self.frame_rate)
        # # set exposure(曝光设置为16580, 通过相机帧率计算公司得到, 60帧对应曝光时间为60fps)
        # self.cam.ExposureTime.set(16580.0)
        # # set gain(设置增益, 调节相机亮度)
        # self.cam.Gain.set(1.0)
        # set roi(设置相机ROI, 裁剪尺寸)
        self.cam.Width.set(self.video_width)  # 宽度
        self.cam.Height.set(self.video_height)  # 高度
        self.cam.OffsetX.set(int((1920 - self.video_width) / 2))  # 宽度偏移量
        self.cam.OffsetY.set(int((1200 - self.video_height) / 2))  # 高度偏移量
        # start data acquisition(开始相机流采集)
        self.cam.stream_on()
        # acquisition image: num is the image number
        while self.record_thread_flag is True:  # 只要标志为True, 摄像头一直工作
            raw_image = self.cam.data_stream[0].get_image()
            if raw_image is None:
                Logger('Getting image failed.')
                continue
            if self.record_flag is True:
                robot_start_flag = self.robot_start_flag
                Thread(target=self.get_frame, args=(raw_image, robot_start_flag,)).start()
                self.frame_id += 1
                self.robot_start_flag = False
            else:
                numpy_image = raw_image.get_numpy_array()
                image = cv2.cvtColor(np.asarray(numpy_image), cv2.COLOR_BayerBG2BGR)
                GloVar.camera_image = self.un_distortion(image)
                time.sleep(0.003)
        # stop data acquisition
        self.cam.stream_off()
        # close device
        self.cam.close_device()


    # 获取帧(raw_image: 原生帧, start_flag:动作起点标志)
    def get_frame(self, raw_image, start_flag=False):
        # 使用大恒相机方法: 将raw原生图转为RGB(RGB格式open-cv不支持)
        # # (通过原生图生成RGB图)
        # rgb_image = raw_image.convert("RGB")
        # # (从RGB图像数据创建numpy数组)
        # numpy_image = rgb_image.get_numpy_array()

        # 这里直接使用open-cv将raw原生图转为open-cv支持的BGR(替换掉大恒将raw转为RGB的过程)
        numpy_image = raw_image.get_numpy_array()
        GloVar.camera_image = cv2.cvtColor(np.asarray(numpy_image), cv2.COLOR_BayerBG2BGR)

        # 验证图片顺序是否正确
        # cv2.putText(image, str(raw_image.get_frame_id()), (200, 100), cv2.FONT_HERSHEY_COMPLEX, 2.0, (100, 200, 200), 5)
        # 畸变校正(加在这儿最好, 有点问题, 未验证)
        # image = self.un_distortion(image, self.mtx, self.dist)

        # 将摄像头产生的frame放到容器中
        if start_flag is False:
            self.video_frames_list.append(GloVar.camera_image.copy())
        else:
            # 添加起点标志(故意传入一个数组(使其发生TypeError异常), 这样畸变校正时, 通过捕捉才能识别到此帧)
            self.video_frames_list.append(('start_flag', GloVar.camera_image.copy()))

        # # print height, width, and frame ID of the acquisition image(打印帧信息)
        # # print("Frame ID: %d   Height: %d   Width: %d" % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width()))


    # 保存视频
    def save_video(self):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.video_file_name, fourcc, self.frame_rate, (self.video_width, self.video_height))
        while True:
            if len(self.video_frames_list) > 0:
                frame = self.un_distortion(self.video_frames_list[0])
                out.write(frame)
                self.video_frames_list.pop(0)
            elif self.record_flag is False:
                while True:
                    if len(self.video_frames_list) > 0:
                        frame = self.un_distortion(self.video_frames_list[0])
                        out.write(frame)
                        self.video_frames_list.pop(0)
                    else:
                        break
                break
            else:
                time.sleep(0.001)
        out.release()
        self.restart_record_flag = True
        Logger('视频保存结束: %s' %self.video_file_name)


    def start_record_video(self, case_type='test', case_name='test'):
        # 判断视频是否保存完成(保存完毕才允许再次开始录像)
        if self.restart_record_flag is False:
            Logger('当前还有未保存完的视频, 请稍等...')
            while self.restart_record_flag is False:
                time.sleep(0.002)
        # 传入视频类型和视频名
        self.case_type = case_type
        self.case_name = case_name
        # 创建文件夹(没有就创建)
        video_path = self.video_path + '/' + self.case_type
        if os.path.exists(video_path) is False:
            os.makedirs(video_path)
        self.video_file_name = self.video_path + '/' + self.case_type + '/' + self.case_name + '.mp4'
        # 重新录制视频标志重新置位
        self.restart_record_flag = False
        '''开始录像(通过标志位)'''
        self.record_flag = True
        Thread(target=self.save_video, args=()).start()
        Logger('开始录制视频: %s' %self.video_file_name)


    def stop_record_video(self):
        self.record_flag = False
        Logger('当前视频总帧数为: %d' %self.frame_id)
        Logger('正在保存缓存区的视频...')
        self.frame_id = 0


    def stop_record_thread(self):
        # 判断视频是否保存完成(保存完才能停止线程)
        if self.restart_record_flag is False:
            Logger('当前还有未保存完的视频, 请稍等一会再退出线程...')
            while self.restart_record_flag is False:
                time.sleep(0.002)
        time.sleep(0.5)
        self.record_thread_flag = False


if __name__=='__main__':
    video = Video(video_path='D:/Code/robot/video', video_width=1600, video_height=800)
    # time.sleep(2)
    time.sleep(5)
    # 第一个视频
    video.start_record_video(case_type='test', case_name='123')
    time.sleep(5)
    # 模拟机械臂产生一个起始信号
    video.robot_start_flag = True
    time.sleep(5)
    video.stop_record_video()

    # # 第二个视频
    # video.start_record_video(case_type='test', case_name='456')
    # time.sleep(10)
    # video.stop_record_video()
    video.stop_record_thread()