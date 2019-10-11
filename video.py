# coding=utf-8
import os
import cv2
import time
import numpy as np
import gxipy as gx
import threading

class VideoProcess(object):
    def __init__(self, video_path):
        # 视频路径
        self.video_path = video_path
        # 收集摄像头产生的frame
        self.frame_collection = []
        # 关闭摄像头标志位(为True时关闭摄像头)
        self.close_camera_flag = False
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


    def daheng(self):
        # print the demo information
        print("")
        print("-------------------------------------------------------------")
        print("Sample to show how to acquire color image continuously and show acquired image.")
        print("-------------------------------------------------------------")
        print("")
        print("Initializing......")
        print("")

        # create a device manager
        device_manager = gx.DeviceManager()
        dev_num, dev_info_list = device_manager.update_device_list()
        if dev_num is 0:
            print("Number of enumerated devices is 0")
            return

        # open device by serial number
        cam = device_manager.open_device_by_sn(dev_info_list[0].get("sn"))

        # if camera is mono
        if cam.PixelColorFilter.is_implemented() is False:
            print("This sample does not support mono camera.")
            cam.close_device()
            return

        # set continuous acquisition
        cam.TriggerMode.set(gx.GxSwitchEntry.OFF)

        # set exposure(曝光)
        cam.ExposureTime.set(10000.0)

        # set gain(增益)
        cam.Gain.set(10.0)

        # set roi(ROI)
        cam.Width.set(1600)
        cam.Height.set(1000)
        cam.OffsetX.set(100)
        cam.OffsetY.set(160)

        #
        cam.BalanceWhiteAuto.set(True)

        # set param of improving image quality
        if cam.GammaParam.is_readable():
            gamma_value = cam.GammaParam.get()
            gamma_lut = gx.Utility.get_gamma_lut(gamma_value)
        else:
            gamma_lut = None
        if cam.ContrastParam.is_readable():
            contrast_value = cam.ContrastParam.get()
            contrast_lut = gx.Utility.get_contrast_lut(contrast_value)
        else:
            contrast_lut = None
        color_correction_param = cam.ColorCorrectionParam.get()

        # start data acquisition
        cam.stream_on()

        # acquisition image: num is the image number
        while True:
            # 关闭摄像头
            if self.close_camera_flag is True:
                break
            # get raw image
            raw_image = cam.data_stream[0].get_image()
            if raw_image is None:
                print("Getting image failed.")
                continue
            # get RGB image from raw image
            rgb_image = raw_image.convert("RGB")
            if rgb_image is None:
                continue
            # improve image quality
            rgb_image.image_improvement(color_correction_param, contrast_lut, gamma_lut)
            # create numpy array with data from raw image
            numpy_image = rgb_image.get_numpy_array()
            if numpy_image is None:
                continue
            # 将图片格式转换为cv模式
            numpy_image = cv2.cvtColor(np.asarray(numpy_image), cv2.COLOR_RGB2BGR)
            # 将摄像头产生的frame放到容器中
            self.frame_collection.append(numpy_image.copy())

            # print height, width, and frame ID of the acquisition image
            print("Frame ID: %d   Height: %d   Width: %d" % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width()))

        # stop data acquisition
        cam.stream_off()
        # close device
        cam.close_device()


    def get_frame(self):
        if len(self.frame_collection) > 0:
            frame = self.frame_collection[0]
            self.frame_collection.pop(0)
        else:
            pass
        # return frame


    # 此处获取视频流
    def camera_running(self):
        while (cv2.waitKey(1) & 0xFF) != ord('q'):
            # 从相机取一帧图片
            try:
                frame = self.get_frame()
                # frame = cv2.resize(frame, (1280, 1024), interpolation=cv2.INTER_LINEAR)
                cv2.imshow("Press q to end", frame)
            except Exception as e:
                print('[读取视频错误] : %s' % e)

    # 视频流(cv_展示)
    def video_stream_cv(self):
        try:
            # 读取视频帧并展示
            self.camera_running()
        finally:
            cv2.destroyAllWindows()

    # 视频流(帧入栈)
    def video_stream_enqueue(self):
        frames = 0
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