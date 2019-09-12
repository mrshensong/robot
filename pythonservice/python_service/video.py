# coding=utf-8
import os
import cv2
import time
import numpy as np
from mindvision import mvsdk
import threading
from ctypes import *

class VideoProcess(object):
    def __init__(self, video_path):
        self.video_path = video_path
        # 相机对象
        self.hCamera = None
        # 相机特征描述
        self.cap = None
        # 相机黑白or彩色(True:黑白, False:彩色)
        self.monoCamera = None
        # 备注：从相机传输到PC端的是RAW数据，在PC端通过软件ISP转为RGB数据（如果是黑白相机就不需要转换格式，但是ISP还有其它处理，所以也需要分配这个buffer）
        self.pFrameBuffer = None
        '''保存视频需要用到的参数'''
        # 保存视频帧列表
        self.video_frames_list = []
        # 线程结束标志位
        self.record_thread_flag = True
        # 开始和停止录像标志
        self.record_flag = False
        # 是否需要停止视频保存
        self.stop_save_flag = False
        # 录像打开时, 停止录像后关闭(接着改变stop_save_flag标志, 保存视频线程由此可以知道需要停止保存视频)
        self.flag = False
        # 是否可以重新开始录制视频
        self.re_start_record_flag = True
        # 视频类型(app冷/app热/滑动流畅度等等)
        self.case_type = None
        # 视频名称(桌面滑动)
        self.case_name = None
        # 视频需要保存的高和宽
        self.video_width  = 1280
        self.video_height = 720
        # 开始和停止时间戳
        self.start_time = None
        self.end_time = None

    # 初始化相机
    def camera_init(self):
        # 枚举相机
        DevList = mvsdk.CameraEnumerateDevice()
        nDev = len(DevList)
        if nDev < 1:
            print("No camera was found!")
            return

        for i, DevInfo in enumerate(DevList):
            print("{}: {} {}".format(i, DevInfo.GetFriendlyName(), DevInfo.GetPortType()))
        i = 0 if nDev == 1 else int(input("Select camera: "))
        DevInfo = DevList[i]
        print(DevInfo)
        return DevInfo

    # 打开相机
    def camera_open(self):
        # 打开相机
        hCamera = 0
        DevInfo = self.camera_init()
        try:
            hCamera = mvsdk.CameraInit(DevInfo, -1, -1)
            self.hCamera = hCamera
        except mvsdk.CameraException as e:
            print("CameraInit Failed({}): {}".format(e.error_code, e.message))
            return

    # 设置相机并开始启动相机
    def camera_setting(self):
        # 获取相机特性描述
        self.cap = mvsdk.CameraGetCapability(self.hCamera)
        # 判断是黑白相机还是彩色相机
        self.monoCamera = (self.cap.sIspCapacity.bMonoSensor != 0)
        # 黑白相机让ISP直接输出MONO数据，而不是扩展成R=G=B的24位灰度
        if self.monoCamera:
            mvsdk.CameraSetIspOutFormat(self.hCamera, mvsdk.CAMERA_MEDIA_TYPE_MONO8)
        else:
            mvsdk.CameraSetIspOutFormat(self.hCamera, mvsdk.CAMERA_MEDIA_TYPE_BGR8)
        # 设置分辨率
        mvsdk.CameraSetImageResolutionEx(self.hCamera, iIndex=0XFF, Mode=0, ModeSize=0, x=0, y=0, width=1280, height=720, ZoomWidth=0, ZoomHeight=0)
        # 相机模式切换成连续采集
        mvsdk.CameraSetTriggerMode(self.hCamera, 0)
        # 手动曝光，曝光时间30ms
        # 曝光时间4.1995, 增益为3.175
        mvsdk.CameraSetAeState(self.hCamera, 0)
        # mvsdk.CameraSetExposureTime(self.hCamera, 30 * 1000)
        mvsdk.CameraSetExposureTime(self.hCamera, 4.1529 * 1000) # 4.1529/240fps
        # mvsdk.CameraSetExposureTime(self.hCamera, 5.5242 * 1000) # 5.5242/180fps
        # mvsdk.CameraSetExposureTime(self.hCamera, 6.6150 * 1000) # 6.6150/150fps
        # mvsdk.CameraSetExposureTime(self.hCamera, 8.2668 * 1000) # 8.2668/120fps
        # 设置模拟增益值(4.094/传入的参数为:增益值/0.125)
        mvsdk.CameraSetAnalogGain(self.hCamera, c_int(32))
        # 让SDK内部取图线程开始工作
        mvsdk.CameraPlay(self.hCamera)
        # 计算RGB buffer所需的大小，这里直接按照相机的最大分辨率来分配
        FrameBufferSize = self.cap.sResolutionRange.iWidthMax * self.cap.sResolutionRange.iHeightMax * (1 if self.monoCamera else 3)
        # 分配RGB buffer，用来存放ISP输出的图像
        # 备注：从相机传输到PC端的是RAW数据，在PC端通过软件ISP转为RGB数据（如果是黑白相机就不需要转换格式，但是ISP还有其它处理，所以也需要分配这个buffer）
        self.pFrameBuffer = mvsdk.CameraAlignMalloc(FrameBufferSize, 16)

    # 输出frame
    def get_frame(self):
        pRawData, FrameHead = mvsdk.CameraGetImageBuffer(self.hCamera, 200)
        mvsdk.CameraImageProcess(self.hCamera, pRawData, self.pFrameBuffer, FrameHead)
        mvsdk.CameraReleaseImageBuffer(self.hCamera, pRawData)
        # 此时图片已经存储在pFrameBuffer中，对于彩色相机pFrameBuffer=RGB数据，黑白相机pFrameBuffer=8位灰度数据
        # 把pFrameBuffer转换成opencv的图像格式以进行后续算法处理
        frame_data = (mvsdk.c_ubyte * FrameHead.uBytes).from_address(self.pFrameBuffer)
        frame = np.frombuffer(frame_data, dtype=np.uint8)
        frame = frame.reshape((FrameHead.iHeight, FrameHead.iWidth, 1 if FrameHead.uiMediaType == mvsdk.CAMERA_MEDIA_TYPE_MONO8 else 3))
        return frame


    # 此处获取视频流
    def camera_running(self):
        while (cv2.waitKey(1) & 0xFF) != ord('q'):
            # 从相机取一帧图片
            try:
                frame = self.get_frame()
                # frame = cv2.resize(frame, (1280, 1024), interpolation=cv2.INTER_LINEAR)
                cv2.imshow("Press q to end", frame)
            except mvsdk.CameraException as e:
                if e.error_code != mvsdk.CAMERA_STATUS_TIME_OUT:
                    print("CameraGetImageBuffer failed({}): {}".format(e.error_code, e.message))

    # 相机停止工作
    def camera_stop(self):
        # 关闭相机
        mvsdk.CameraUnInit(self.hCamera)
        # 释放帧缓存
        mvsdk.CameraAlignFree(self.pFrameBuffer)

    # 视频流(cv_展示)
    def video_stream_cv(self):
        try:
            # 相机初始化
            self.camera_init()
            # 打开相机
            self.camera_open()
            # 设置相机并开始启动相机
            self.camera_setting()
            # 读取视频帧并展示
            self.camera_running()
            # 相继停止工作并关闭相机
            self.camera_stop()
        finally:
            cv2.destroyAllWindows()

    # 视频流(帧入栈)
    def video_stream_enqueue(self):
        frames = 0
        # try:
        #     # 相机初始化
        #     self.camera_init()
        #     # 打开相机
        #     self.camera_open()
        #     # 设置相机并开始启动相机
        #     self.camera_setting()
        # except Exception as e:
        #     print('[camera open error]:', e)
        FFF = True
        # 获取视频帧
        while self.record_thread_flag:
            if self.flag:
                self.stop_save_flag = False
                self.flag = False
            while self.record_flag:
                while FFF:
                    self.start_time = time.time()
                    FFF = False
                # self.stop_save_flag = True
                # self.flag = True
                try:
                    frame = self.get_frame()
                    self.enqueue_frame(frame.copy())
                    frames += 1
                except Exception as e:
                    print('[collecting frame error]', e)
                    break
            time.sleep(0.2)
        # 视频线程结束(关闭相机)
        self.camera_stop()
        print('[总帧数为]', frames)

    '''保存视频相关'''
    # 帧入栈
    def enqueue_frame(self, frame):
        self.video_frames_list.append(frame)

    # 帧出栈
    def dequeue_frame(self):
        return self.video_frames_list.pop(0)

    # 判断video_frame_list是否为空
    def empty(self):
        return len(self.video_frames_list) == 0

    # 保存视频线程
    def save_out_video(self):
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = None
            # 开始保存视频
            while self.record_thread_flag:
                count = 0
                flag_out = False
                while self.record_flag or self.stop_save_flag or not self.empty():
                    # 此时不能录制视频(需要先保存完上一视频)
                    self.re_start_record_flag = False
                    if count == 0:
                        print('[开始保存视频]')
                        flag_out = True
                        video_file_path = os.path.join(self.video_path, self.case_type, self.case_name + '.mp4')
                        out = cv2.VideoWriter(video_file_path, fourcc, 240.0, (self.video_width, self.video_height), True)
                    if not self.empty():
                        out.write(self.video_frames_list[0])
                        self.dequeue_frame()
                    count += 1
                if flag_out:
                    print('[视频保存完毕]')
                    out.release()
                    time.sleep(3)
                    # 恢复标志位
                    self.stop_save_flag = False
                    # 此时可以录制视频
                    self.re_start_record_flag = True
                time.sleep(0.2)
        except Exception as e:
            raise Exception('save video thread error!', e)

    # 录像+保存视频
    def recording(self):
        try:
            # 相机初始化
            self.camera_init()
            # 打开相机
            self.camera_open()
            # 设置相机并开始启动相机
            self.camera_setting()
        except Exception as e:
            print('[camera open error]:', e)
        # 开启视频流采集和视频保存线程
        record_video_thread = threading.Thread(target=self.video_stream_enqueue, args=())
        save_video_thread = threading.Thread(target=self.save_out_video, args=())
        thread_pool = [record_video_thread, save_video_thread]
        for thread in thread_pool:
            thread.start()
        for thread in thread_pool:
            thread.join()


    # 开始录制视频
    def start_record_video(self, case_type='test', case_name='test'):
        self.case_type = case_type
        self.case_name = case_name
        video_path = os.path.join(self.video_path, self.case_type)
        if os.path.exists(video_path) is False:
            os.makedirs(video_path)
        if self.re_start_record_flag is False:
            print('[上一个视频还未保存完成, 请稍等...]')
        while self.re_start_record_flag is False:
            time.sleep(0.5)
        self.record_flag = True
        self.stop_save_flag = True
        self.flag = True
        print('[开始录像]')


    # 停止录制视频
    def stop_record_video(self):
        self.record_flag = False
        self.end_time = time.time()
        print('[停止录像]')

    # 结束录像线程
    def stop_record_thread(self):
        while self.re_start_record_flag is False:
            time.sleep(1)
        self.record_thread_flag = False
        print('[停止录像线程]')


if __name__=='__main__':
    path = 'D:\\Work\\MindVision\\DemoPy\\'
    video = VideoProcess(path)


    def case_run():
        # video.case_type = 'video'
        # video.case_name = 'test3'
        # video_path = os.path.join(path, video.case_type)
        # if os.path.exists(video_path) is False:
        #     os.makedirs(video_path)
        # if video.re_start_record_flag is False:
        #     print('[上一个视频还未保存完成, 请稍等...]')
        # while video.re_start_record_flag is False:
        #     time.sleep(0.5)
        # 开始录制视频
        video.start_record_video()
        # print('[开始录像]')

        time.sleep(10)

        # 停止录制视频
        video.stop_record_video()
        # print('[停止录像]')

        video.stop_record_thread()
        # while video.re_start_record_flag is False:
        #     time.sleep(1)
        # video.record_thread_flag = False
        # print('[录像线程结束]')


    def recording():
        video.recording()


    def running():
        run_case = threading.Thread(target=case_run, args=())
        record = threading.Thread(target=recording, args=())
        thread_pool = [run_case, record]
        for thread in thread_pool:
            thread.start()
        for thread in thread_pool:
            thread.join()


    running()
    time_e = video.end_time - video.start_time
    print('time_e: ', time_e)