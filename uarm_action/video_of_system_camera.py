import os
import cv2
import time
from threading import Thread
from GlobalVar import GloVar, Logger


class SystemCameraVideo:

    def __init__(self, video_path, video_width, video_height):
        # 保存视频需要用到的参数
        self.video_path = video_path
        # 视频需要保存的高和宽
        self.video_width = video_width
        self.video_height = video_height
        # 相机对象
        self.cam = None
        # 帧率
        self.frame_rate = 30.0
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
        # 开启视频流
        Thread(target=self.video_stream, args=()).start()


    # 调用笔记本摄像头模拟工业摄像头
    def video_stream(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_height)
        while self.record_thread_flag is True:
            _, GloVar.camera_image = cap.read()
            if self.record_flag is True:
                image = GloVar.camera_image
                # 标记这一帧
                if self.robot_start_flag is False:
                    self.video_frames_list.append(image.copy())
                else:
                    image[0].fill(255)
                    self.video_frames_list.append(image.copy())
                    self.robot_start_flag = False
                self.frame_id += 1
        cap.release()
        Logger('退出视频录像线程')


    # 保存视频
    def save_video(self):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.video_file_name, fourcc, self.frame_rate, (self.video_width, self.video_height))
        while True:
            if len(self.video_frames_list) > 0:
                out.write(self.video_frames_list[0])
                self.video_frames_list.pop(0)
            elif self.record_flag is False:
                while True:
                    if len(self.video_frames_list) > 0:
                        out.write(self.video_frames_list[0])
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
        # 创建文件夹(没有就创建)/(D:/Code/robot/video/2019-11-27/测试/点击设置/1.2.3.4.5)--多次测试会产生这样的视频
        video_path = self.video_path + '/' + self.case_type + '/' + self.case_name
        if os.path.exists(video_path) is False:
            os.makedirs(video_path)
        # 以当前目录的文件产生顺序命名
        video_count = len(os.listdir(video_path))
        self.video_file_name = video_path + '/' + str(video_count + 1) + '.mp4'
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
    video = SystemCameraVideo(video_path='D:/Code/robot/video', video_width=1600, video_height=800)
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