import cv2
import gxipy as gx
import numpy as np

class Video:

    def __init__(self):
        # 保存视频需要用到的参数
        # 保存视频帧列表
        self.video_frames_list = []
        # 线程结束标志位
        self.record_thread_flag = True
        # 开始和停止录像标志
        self.record_flag = False

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
        while self.record_thread_flag:  # 只要标志为True, 摄像头一直工作
            # 关闭摄像头
            # if self.close_camera_flag is True:
            #     break
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
            # 当录像标志打开时, 将frame存起来
            if self.record_flag is True:
                # 将摄像头产生的frame放到容器中
                self.video_frames_list.append(numpy_image.copy())
                # print height, width, and frame ID of the acquisition image
                print("Frame ID: %d   Height: %d   Width: %d" % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width()))

        # stop data acquisition
        cam.stream_off()
        # close device
        cam.close_device()