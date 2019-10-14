import os
import cv2
import time
import gxipy as gx
import numpy as np
from threading import Thread
from pythonservice.python_service.utils import logger

class Video:

    def __init__(self, video_path):
        # 保存视频需要用到的参数
        self.video_path = video_path
        # 保存视频帧列表
        self.video_frames_list = []
        # 线程结束标志位
        self.record_thread_flag = True
        # 开始和停止录像标志
        self.record_flag = False
        # 是否可以重新开始录制视频
        self.re_start_record_flag = True
        # 视频类型(app冷/app热/滑动流畅度等等)
        self.case_type = None
        # 视频名称(桌面滑动)
        self.case_name = None
        # 视频需要保存的高和宽
        self.video_width = None
        self.video_height = None


    # 视频流线程
    def video_stream_1(self):
        # create a device manager
        device_manager = gx.DeviceManager()
        dev_num, dev_info_list = device_manager.update_device_list()
        if dev_num is 0:
            logger.warning('Number of enumerated devices is 0')
            return

        # open device by serial number
        cam = device_manager.open_device_by_sn(dev_info_list[0].get("sn"))

        # if camera is mono
        if cam.PixelColorFilter.is_implemented() is False:
            logger.warning('This sample does not support mono camera.')
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
        while self.record_thread_flag is True:  # 只要标志为True, 摄像头一直工作
            # 关闭摄像头
            # if self.close_camera_flag is True:
            #     break
            # get raw image
            raw_image = cam.data_stream[0].get_image()
            if raw_image is None:
                logger.error('Getting image failed.')
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
            # 当录像标志打开时, 将frame存起来
            if self.record_flag is True:
                # 在这儿是否需要判断Frame ID有重复的情况(如果有的话就需要进行处理--考虑要不要加进去)
                # 将摄像头产生的frame放到容器中
                self.video_frames_list.append(numpy_image.copy())
                # print height, width, and frame ID of the acquisition image
                print("Frame ID: %d   Height: %d   Width: %d" % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width()))

        # stop data acquisition
        cam.stream_off()
        # close device
        cam.close_device()


    # 调用笔记本摄像头模拟工业摄像头
    def video_stream(self):
        cap = cv2.VideoCapture(0)
        self.video_width = int(cap.get(3))
        self.video_height = int(cap.get(4))
        while self.record_thread_flag is True:
            _, frame = cap.read()
            cv2.waitKey(10)
            if self.record_flag is True:
                self.video_frames_list.append(frame.copy())
            #     cv2.imshow('frame', frame.copy())
            # else:
            #     cv2.destroyAllWindows()
        cap.release()


    # 保存视频线程
    def save_out_video(self):
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = None
            # 开始保存视频
            while self.record_thread_flag:
                count = 0
                flag_out = False
                while self.record_flag or len(self.video_frames_list) > 0:
                    # 此时不能录制视频(需要先保存完上一视频)
                    self.re_start_record_flag = False
                    if count == 0:
                        logger.info('开始保存视频')
                        flag_out = True
                        video_file_path = self.video_path + '/' + self.case_type + '/' + self.case_name + '.mp4'
                        # out = cv2.VideoWriter(video_file_path, fourcc, 240.0, (self.video_width, self.video_height), True)
                        while True:
                            if self.video_height is not None and self.video_width is not None:
                                out = cv2.VideoWriter(video_file_path, fourcc, 30.0, (self.video_width, self.video_height), True)
                                break
                    if len(self.video_frames_list) > 0:
                        out.write(self.video_frames_list[0])
                        self.video_frames_list.pop(0)
                    count = 1
                if flag_out:
                    logger.info('视频保存完毕')
                    out.release()
                    time.sleep(3)
                    # 此时可以录制视频
                    self.re_start_record_flag = True
                time.sleep(0.2)
        except Exception as e:
            logger.error('save video thread error!')
            raise Exception('save video thread error!', e)


    # 录像+保存视频
    def recording(self):
        # 开启视频流采集和视频保存线程
        Thread(target=self.video_stream, args=()).start()
        Thread(target=self.save_out_video, args=()).start()


    # 开始录制视频
    def start_record_video(self, case_type='test', case_name='test'):
        self.case_type = case_type
        self.case_name = case_name
        video_path = self.video_path + '/' + self.case_type
        if os.path.exists(video_path) is False:
            os.makedirs(video_path)
        if self.re_start_record_flag is False:
            logger.warning('上一个视频还未保存完成, 请稍等...')
        while self.re_start_record_flag is False:
            time.sleep(0.02)
        self.record_flag = True
        logger.info('开始录像')


    # 停止录制视频
    def stop_record_video(self):
        self.record_flag = False
        logger.info('停止录像')

    # 结束录像线程
    def stop_record_thread(self):
        while self.re_start_record_flag is False:
            time.sleep(0.02)
        self.record_thread_flag = False
        logger.info('停止录像线程')


if __name__=='__main__':
    path = 'D:/Work/MindVision/DemoPy/'
    video = Video(path)


    def case_run():
        # 开始录制视频
        video.start_record_video(case_type='test', case_name='123')
        time.sleep(10)
        # 停止录制视频
        video.stop_record_video()
        video.start_record_video(case_type='test', case_name='234')
        time.sleep(6)
        # 停止录制视频
        video.stop_record_video()
        video.stop_record_thread()


    def recording():
        video.recording()


    def running():
        Thread(target=case_run, args=()).start()
        Thread(target=recording, args=()).start()

    running()