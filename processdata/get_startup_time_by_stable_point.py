import os
import cv2
import numpy as np
from openpyxl import Workbook
from processdata.get_data_graph import GenerateDataGraph
from processdata.get_report import GenerateReport
from GlobalVar import MergePath, Logger, GloVar


'''
此类通过稳定点来寻找终点
1.在起始点之后开始检测
2.对比相邻的两张图片
3.连续10张图片相似度大于99%(大概可以判定稳定点)
'''


class GetStartupTime:

    def __init__(self, video_path):
        # 视频路径
        self.video_path = video_path
        # 报告路径
        self.report_path = video_path.replace('/video/', '/report/')
        if os.path.exists(self.report_path) is False:
            os.makedirs(self.report_path)
        # excel存储数据
        self.report_excel = self.report_path + '/' + 'report.xlsx'
        # 模板匹配率
        self.match_threshold = 0.93
        self.template_edge = 10
        # 待处理的视频列表
        self.videos_list = []


    def match_template(self, source_img, target_img):
        '''
        :param source_img: 源图像(大图)
        :param target_img: 靶子图像(小图)
        :param match_rate: 匹配率
        :return:
        '''
        if type(source_img) is str:
            source_img = cv2.imdecode(np.fromfile(source_img, dtype=np.uint8), -1)
        if type(target_img) is str:
            target_img = cv2.imdecode(np.fromfile(target_img, dtype=np.uint8), -1)
        # 匹配方法
        match_method = cv2.TM_CCOEFF_NORMED
        # 模板匹配
        match_result = cv2.matchTemplate(source_img, target_img, match_method)
        # 查找匹配度和坐标位置
        min_threshold, max_threshold, min_threshold_position, max_threshold_position = cv2.minMaxLoc(match_result)
        # 返回最大匹配率
        return max_threshold



    def get_start_and_end_match_threshold(self, end_mask, video_file):
        """
        获取起止点的匹配率列表
        :param end_mask: 稳定点模板
        :param video_file: 视频文件
        :return: 开始点匹配率列表, 稳定点匹配率列表
        """
        # 获取视频对象
        video_cap = cv2.VideoCapture(video_file)
        # 帧编号
        frame_id = 0
        # 起点结果是否找到标志位
        start_point_exist_flag = False
        # 模板出现标志
        template_appear_flag = False
        # 上一帧图片(前后两帧需要对比)
        last_picture = None
        # 匹配率连续大于0.99的次数(只要中断就从零计算)/原理:连续十帧匹配率大于0.99就可以认为此帧为稳定帧
        stability_num = 0
        # 上一循环是否匹配率大于0.99的标志
        cycle_flag = False
        # 起始帧和结束帧结果(frame_id, match_rate), (frame_id, match_rate)
        start_point_result = ()
        end_point_result = ()
        # 计算待检测模板在整帧中的位置(需要截取出来)
        # 获取视频的尺寸
        frame_height = video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        frame_width = video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        # 获取模板的灰度图
        end_mask_gray = cv2.imdecode(np.fromfile(end_mask, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        # 模板的尺寸
        end_mask_height, end_mask_width = end_mask_gray.shape
        # 根据模板图片中第一行像素值, 找到模板所在当前帧中的位置(将带查找图片选择的稍微比模板图片大一点点每个边大20像素)
        # 行起点
        # row_start = (end_mask_gray[0][0] * 10 - end_mask_height)
        row_start = (end_mask_gray[0][0] * 10 - self.template_edge)
        row_start = 0 if row_start < 0 else row_start
        # 行终点
        # row_end = (end_mask_gray[0][1] * 10 + end_mask_height)
        row_end = (end_mask_gray[0][1] * 10 + self.template_edge)
        row_end = frame_height - 1 if row_end >= frame_height else row_end
        # 列起点
        # column_start = (end_mask_gray[0][2] * 10 - end_mask_width)
        column_start = (end_mask_gray[0][2] * 10 - self.template_edge)
        column_start = 0 if column_start < 0 else column_start
        # 列终点
        # column_end = (end_mask_gray[0][3] * 10 + end_mask_width)
        column_end = (end_mask_gray[0][3] * 10 + self.template_edge)
        column_end = frame_width - 1 if column_end >= frame_width else column_end
        # 视频读取
        while video_cap.isOpened():
            # 帧从1开始
            frame_id += 1
            successfully_read, frame = video_cap.read()
            if successfully_read is True:
                # 灰度化
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # 目标图片(待匹配)
                target = frame_gray[row_start: row_end, column_start: column_end]
                # 起点
                if start_point_exist_flag is False:
                    # 如果图像第一行像素为白色
                    if frame[0].mean() > 245:
                        start_point_result = (frame_id, 1.0)
                        start_point_exist_flag = True
                    # 先寻找起点(没有找到起点进行下一循环)
                    continue
                # 起点之后寻找模板出现的帧
                elif template_appear_flag is False:
                    threshold = self.match_template(target, end_mask_gray)
                    if threshold >= self.match_threshold:
                        template_appear_flag = True
                        last_picture = target
                    else:
                        continue
                # 终点(稳定点)
                if template_appear_flag is True:
                    match_rate = self.match_template(target, last_picture)
                    print(match_rate)
                    if cycle_flag is True:
                        if match_rate > 0.99:
                            cycle_flag = True
                            stability_num += 1
                            if stability_num == 15:
                                end_point_result = (frame_id - 15, 0.99)
                                break
                        else:
                            cycle_flag = False
                            stability_num = 0
                            last_picture = target
                    else:
                        if match_rate > 0.99:
                            cycle_flag = True
                            stability_num = 1
                        else:
                            cycle_flag = False
                            stability_num = 0
                            last_picture = target
            else:
                break
        video_cap.release()
        return start_point_result, end_point_result


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
        return frame_serial_number, round(frame_threshold, 4)

    # 获取起止点以及对应匹配率等等
    def get_all_video_start_and_end_points(self):
        """
        此处传入视频路径(算出路径下所有case视频的起止点)
        :return:
        """
        # 找出目录下需要处理的视频
        for home, dirs, files in os.walk(self.video_path):
            for file in files:
                # 判断视频文件(通过后缀名)
                (file_text, extension) = os.path.splitext(file)
                if extension in ['.mp4', '.MP4', '.avi', '.AVI']:
                    # 文件名列表, 包含完整路径
                    file = MergePath([home, file]).merged_path
                    self.videos_list.append(file)
        # 用list保存起始和终止点参数(需要写入excel)
        data_list = []
        # 需要试用视频文件路径作为参数
        for video in self.videos_list:
            Logger('正在计算<%s>起止点...' % video)
            end_mask = video.replace('/video/', '/picture/').split('.')[0] + '.jpg'
            start_threshold_list, end_threshold_list = self.get_start_and_end_match_threshold(end_mask=end_mask, video_file=video)
            # 起始帧和停止帧(因这里帧数从零开始, 故而帧数增加一个)
            start_frame, start_threshold = self.detect_start_point(start_threshold_list)
            end_frame, end_threshold = self.detect_end_point(end_threshold_list)
            start_frame = start_frame + 1
            end_frame = end_frame + 1
            frame_gap = end_frame - start_frame
            Logger('%s-->起始点: 帧> %d, 匹配率> %.4f' % (video, start_frame, start_threshold))
            Logger('%s-->终点点: 帧> %d, 匹配率> %.4f' % (video, end_frame, end_threshold))
            data_list.append({'name':video, 'start_frame':start_frame, 'start_threshold':start_threshold, 'end_frame':end_frame, 'end_threshold':end_threshold, 'frame_gap':frame_gap})
        GloVar.data_process_finished_flag = True
        return data_list

    # 将得到的数据写入excel
    def write_data_to_excel(self, file, original_data_list):
        data_list = []
        sheet_name_list = []
        for data in original_data_list:
            data_dict = {}
            # 通过文件名的倒数第二个获取到case类型(也就是sheet名)
            case_type = data['name'].split('/')[-2]
            data_dict['case_type'] = case_type
            # 将所有的case_type放入列表, 然后去重(即可知道需要新建几个sheet)
            sheet_name_list.append(case_type)
            # case文件名
            file_name = data['name'].split('/')[-1].split('.')[0]
            data_dict['file_name'] = file_name
            # 开始帧
            start_frame = data['start_frame']
            data_dict['start_frame'] = start_frame
            # 开始帧的匹配率
            start_threshold = data['start_threshold']
            data_dict['start_threshold'] = start_threshold
            # 结束帧
            end_frame = data['end_frame']
            data_dict['end_frame'] = end_frame
            # 结束帧的匹配率
            end_threshold = data['end_threshold']
            data_dict['end_threshold'] = end_threshold
            # 帧差
            frame_gap = data['frame_gap']
            data_dict['frame_gap'] = frame_gap
            # 将一行内容存入list
            data_list.append(data_dict)
        # sheet_name去重
        sheet_name_list = list(set(sheet_name_list))
        # 创建新list(每一个子list放同样类型的case的dict元素)
        data_list_by_sheet = [[sheet_name] for sheet_name in sheet_name_list]
        for data in data_list:
            sheet_name = data['case_type']
            data.pop('case_type')
            index = sheet_name_list.index(sheet_name)
            data_list_by_sheet[index].append(data)
        # 开始在excel中写入数据
        work_book = Workbook()
        # 直接在data_list_by_case_type取出数据即可
        for data in data_list_by_sheet:
            # 创建sheet表
            work_sheet = work_book.create_sheet(data[0])
            # 创建表头
            work_sheet.append(['用例', '开始帧', '开始帧匹配率', '结束帧', '结束帧匹配率', '差帧'])
            for i in range(1, len(data)):
                # 写入每一行内容
                work_sheet.append(list(data[i].values()))
        # 删除掉第一个空白sheet
        work_book.remove(work_book['Sheet'])
        Logger('生成数据表: ' + file)
        work_book.save(file)
        work_book.close()

    # 通过excel获取柱形图
    def get_graph_data(self):
        generate_graph = GenerateDataGraph(file=self.report_excel)
        generate_graph.get_graphs()

    # 生成html并保存
    def get_report(self):
        generate_report = GenerateReport(report_path=self.report_path)
        generate_report.save_html()

    # 结合(1.生成excel, 2.通过excel获取柱形图, 3.生成html并保存)
    def data_processing(self):
        # 保存excel
        data_list = self.get_all_video_start_and_end_points()
        self.write_data_to_excel(file=self.report_excel, original_data_list=data_list)
        # 通过excel获取柱形图
        self.get_graph_data()
        # 生成html并保存
        self.get_report()
        Logger('data process finished!')


if __name__ == '__main__':
    video_path = 'D:/Code/robot/video/2019-10-15'
    test = GetStartupTime(video_path=video_path)
    # test.data_processing()
    # print(test.get_start_and_end_match_threshold('D:/Test/Python/TestVideo/video/test_.mp4'))
    # print(test.get_start_and_end_match_threshold('D:/Code/robot/picture/template/启动/音乐.jpg', 'D:/Code/robot/video/2019-12-31/17-04-00/启动/音乐/1.mp4'))
    print(test.get_start_and_end_match_threshold('D:/Code/robot/picture/template/启动/音乐.jpg', 'D:/Code/robot/video/2019-12-31/16-50-53/启动/音乐/1.mp4'))