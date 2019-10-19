import cv2
import numpy as np

class GetStartupTime:

    def __init__(self, video_path, frame_rate):
        #
        self.image_zoom = 2
        # 帧偏差
        self.frame_deviation = 16
        # 模板匹配率
        self.match_threshold = 0.93
        # 保存图片标志
        self.image_flag = False
        # 视频帧率
        self.frame_rate = frame_rate
        # 视频路径
        self.video_path = video_path


    def get_start_and_end_match_threshold(self, end_mask, video_file):
        """
        获取起止点的匹配率列表
        :param end_mask: 稳定点模板
        :param video_file: 视频文件
        :return: 开始点匹配率列表, 稳定点匹配率列表
        """
        match_methods = [cv2.TM_SQDIFF_NORMED, cv2.TM_CCORR_NORMED, cv2.TM_CCOEFF_NORMED]
        current_match_method = match_methods[2]
        # 放置开始点和稳定点的list容器
        start_threshold_list = []
        end_threshold_list = []
        # 获取视频对象
        video_cap = cv2.VideoCapture(video_file)
        # cv2.IMREAD_COLOR: 读入一副彩色图片
        # cv2.IMREAD_GRAYSCALE: 以灰度模式读入图片
        # cv2.IMREAD_UNCHANGED: 读入一幅图片，并包括其alpha通道
        # 获取模板的灰度图
        end_mask_gray = cv2.imdecode(np.fromfile(end_mask, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        # 模板的尺寸
        end_mask_height, end_mask_width = end_mask_gray.shape
        # 视频读取
        while video_cap.isOpened():
            successfully_read, frame = video_cap.read()
            if successfully_read is True:
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame_height, frame_width = frame_gray.shape
                # 起点
                # 如果图像第一行像素为白色
                if frame[0].mean() > 235:
                    start_threshold_list.append(1.0)
                else:
                    start_threshold_list.append(0)
                # 终点
                # 根据模板图片中第一行像素值, 找到模板所在当前帧中的位置(将带查找图片选择的稍微比模板图片大一点点)
                # 行起点
                row_start = (end_mask_gray[0][0] * 10 - end_mask_height)
                if row_start < 0:
                    row_start = 0
                else:
                    row_start = row_start
                # 行终点
                row_end = (end_mask_gray[0][1] * 10 + end_mask_height)
                if row_end >= frame_height:
                    row_end = frame_height - 1
                else:
                    row_end = row_end
                # 列起点
                column_start = (end_mask_gray[0][2] * 10 - end_mask_width)
                if column_start < 0:
                    column_start = 0
                else:
                    column_start = column_start
                # 列终点
                column_end = (end_mask_gray[0][3] * 10 + end_mask_width)
                if column_end >= frame_width:
                    column_end = frame_width - 1
                else:
                    column_end = column_end
                # 目标图片(待匹配)
                target = frame_gray[row_start: row_end, column_start: column_end]
                # 模板匹配
                match_result = cv2.matchTemplate(target, end_mask_gray, current_match_method)
                # 查找匹配度和坐标位置
                min_threshold, max_threshold, min_threshold_position, max_threshold_position = cv2.minMaxLoc(match_result)
                end_threshold_list.append(max_threshold)
            else:
                print('Analysis Video End...')
                break
        video_cap.release()
        return start_threshold_list, end_threshold_list


    def detect_start_point(self, start_threshold_list):
        """
        计算起点(返回可能是起点的所有帧序号, 以及当前帧匹配率)
        :param start_threshold_list: 开始点匹配率列表
        :return: 返回是起点的帧序号以及当前帧匹配率
        """
        frame_serial_number = 0
        frame_threshold = 0
        length = len(start_threshold_list)
        for i in range(1, (length - 1)):
            if start_threshold_list[i-1] == 0 and start_threshold_list[i] == 1.0 and start_threshold_list[i+1] == 0:
                frame_serial_number = i
                frame_threshold = start_threshold_list[i]
                break
        return frame_serial_number, frame_threshold


    def detect_end_point(self, end_threshold_list):
        """
        计算终点(返回可能是终点的所有帧序号, 以及当前帧匹配率)
        :param end_threshold_list: 稳定点匹配率列表
        :return: 返回是终点的帧序号以及当前帧匹配率
        """
        # 找出所有大于match_threshold的帧匹配率
        match_threshold_expected_list = []
        for threshold in end_threshold_list:
            if threshold > self.match_threshold:
                match_threshold_expected_list.append(threshold)
            else:
                match_threshold_expected_list.append(0)

        # 更进一步筛选可能成为终点的帧
        frame_serial_number = 0
        frame_threshold = 0
        for i in range(1, len(match_threshold_expected_list)):
            # 前一帧不可能为终止点, 当前帧有可能为终止点
            if match_threshold_expected_list[i - 1] == 0 and match_threshold_expected_list[i] > 0:
                # 取连续十帧匹配率
                temp_list1 = []
                # 如果当前帧大于第十帧(取当前往前连续连续)
                if i > 10:
                    for k in range(i - 11, i - 1):
                        temp_list1.append(match_threshold_expected_list[k])
                # 可能的终点帧在前十帧(取前一帧十次)
                else:
                    for k in range(10):
                        temp_list1.append(match_threshold_expected_list[i - 1])

                temp_list2 = []
                # 如果当前帧不在最后十帧(取连续向后十帧)
                if i < len(match_threshold_expected_list) - 10:
                    for k in range(i, i + 10):
                        temp_list2.append(match_threshold_expected_list[k])
                # 如果当前帧在最后十帧(取当前帧十次)
                else:
                    for k in range(10):
                        temp_list2.append(match_threshold_expected_list[i])
                # 当前帧的往前十帧中匹配率为0的次数多余5次&往后十帧中匹配率为0的次数小于5次(判定为有更大可能为终点)
                if temp_list1.count(0) > 5 > temp_list2.count(0):
                    frame_serial_number = i
                    frame_threshold = match_threshold_expected_list[i]
                    break
        # 对目前找到的这个帧进行再判断(从此帧往后找到匹配率最大的帧停止>这一段的帧就是可能出现的所有帧)-->求出这段匹配率平均数
        average_threshold = match_threshold_expected_list[frame_serial_number]
        for frame_id in range(frame_serial_number, len(match_threshold_expected_list)-10):
            if match_threshold_expected_list[frame_id+1] > match_threshold_expected_list[frame_id]:
                before_sum = average_threshold * (frame_id - frame_serial_number + 1)
                average_threshold = (before_sum + match_threshold_expected_list[frame_id + 1]) / (frame_id - frame_serial_number + 2)
            else:
                break
        # 在此处判断(当前帧匹配率大于平均匹配率就行)
        for i in range(frame_serial_number, len(match_threshold_expected_list)):
            if match_threshold_expected_list[i] > average_threshold:
                frame_serial_number = i
                frame_threshold = match_threshold_expected_list[i]
                break
        return frame_serial_number, frame_threshold


if __name__=='__main__':
    # video_path = 'D:/Code/Robot/robot/video/2019-10-15/启动/测试1.mp4'
    # end_mask   = 'D:/Code/Robot/robot/picture/2019-10-15/启动/测试1.jpg'
    video_path = 'D:/Code/Robot/robot/video/2019-10-15/启动/测试2.mp4'
    end_mask = 'D:/Code/Robot/robot/picture/2019-10-15/启动/测试2.jpg'
    test = GetStartupTime(video_path=video_path, frame_rate=240)
    start_threshold_list, end_threshold_list = test.get_start_and_end_match_threshold(end_mask=end_mask, video_file=video_path)
    print('起始', test.detect_start_point(start_threshold_list))
    print('终点', test.detect_end_point(end_threshold_list))