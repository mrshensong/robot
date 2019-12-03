import os
import cv2
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Alignment, PatternFill, colors
from processdata.get_data_graph import GenerateDataGraph
from processdata.get_report import GenerateReport
from GlobalVar import MergePath, Logger, RobotOther


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
        # 待处理的视频列表
        self.videos_list = []


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
        # 获取视频帧率
        self.frame_rate = int(video_cap.get(cv2.CAP_PROP_FPS))
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
            if start_threshold_list[i-1] == 0 and start_threshold_list[i] == 1.0:
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

    # 处理视频, 从视频中获取处理信息
    def process_video(self, video_id, file, end_mask):
        Logger('正在计算<%s>起止点...' % file)
        start_threshold_list, end_threshold_list = self.get_start_and_end_match_threshold(end_mask=end_mask, video_file=file)
        # 起始帧和停止帧(因这里帧数从零开始, 故而帧数增加一个)
        start_frame, start_threshold = self.detect_start_point(start_threshold_list)
        end_frame, end_threshold = self.detect_end_point(end_threshold_list)
        start_frame = start_frame + 1
        end_frame = end_frame + 1
        frame_gap = end_frame - start_frame
        Logger('%s-->起始点: 帧> %d, 匹配率> %.4f' % (file, start_frame, start_threshold))
        Logger('%s-->终止点: 帧> %d, 匹配率> %.4f' % (file, end_frame, end_threshold))
        return {'次序':video_id, '开始帧':start_frame, '开始帧匹配率':start_threshold, '结束帧':end_frame, '结束帧匹配率':end_threshold, '差帧':frame_gap}

    # 处理一条case(可能含有多次执行产生的多个视频, 传入的参数为产生的这些视频的当前目录路径)
    def process_case(self, video_name_path):
        video_count = 0
        video_info_list = []
        video_files = os.listdir(video_name_path)
        case_name = video_name_path.split('/')[-1]
        end_mask = video_name_path.replace('/video/', '/picture/') + '.jpg'
        # 差帧标准
        standard_frame_gap = 100
        # 差帧总和 & 平均差帧
        sum_frame_gap, average_frame_gap = 0, 0
        # 处理一个case中的多次执行产生的视频
        for video_file in video_files:
            (file_text, extension) = os.path.splitext(video_file)
            if extension in ['.mp4', '.MP4', '.avi', '.AVI']:
                video_count += 1
                file = MergePath([video_name_path, video_file]).merged_path
                # 获取到视频处理后的信息
                video_info = self.process_video(video_id=video_count, file=file, end_mask=end_mask)
                video_info_list.append(video_info)
                sum_frame_gap += int(video_info['差帧'])
        average_frame_gap = int(sum_frame_gap / video_count)
        status = 'failed' if average_frame_gap > standard_frame_gap else 'pass'
        # 返回的信息跟excel模型相似(列表第一个参数代表case类型, 也就是sheet名字)
        return [case_name, video_count, video_info_list, standard_frame_gap, average_frame_gap, status]

    # 获取起止点以及对应匹配率等等
    def get_all_video_start_and_end_points(self):
        """
        此处传入视频路径(算出路径下所有case视频的起止点)
        :return:
        """
        # 获取视频名文件夹(如:D:/Code/robot/video/2019-11-27/测试/点击设置, 里面装有1/2/3/4/5.MP4这样的记录次数的文件)
        video_name_path_list = []
        for home, dirs, files in os.walk(self.video_path):
            if len(files) > 0:
                # 修正路径
                home = MergePath([home]).merged_path
                video_name_path_list.append(home)
        # 用dict保存每一个case类型(相当于excel的sheet名)
        case_type_dict = {}
        # 遍历每一个case视频(这样的路径: D:/Code/robot/video/2019-11-27/测试/点击设置)
        for video_name_path in video_name_path_list:
            case_type = video_name_path.split('/')[-2:-1][0]
            case_data = self.process_case(video_name_path=video_name_path)
            if case_type not in list(case_type_dict.keys()):
                case_type_dict[case_type] = []
            case_type_dict[case_type].append(case_data)
        # 将数据处理完成标志位置位
        RobotOther.data_process_finished_flag = True
        # 返回(如:{'滑动':[[桌面滑动], [设置滑动]], '点击':[[点击设置], [点击地图]]})
        return case_type_dict

    # 将得到的数据写入excel
    def write_data_to_excel(self, file, original_data_dict):
        # 开始在excel中写入数据
        work_book = Workbook()
        # 样式/居中
        align = Alignment(horizontal='center', vertical='center')
        # 单元格填充颜色
        yellow_background = PatternFill("solid", fgColor="FFFF66")
        green_background = PatternFill("solid", fgColor="0099CC")
        gray_background = PatternFill("solid", fgColor="999999")
        # 直接在original_data_dict取出数据即可
        for key, data in original_data_dict.items():
            # 创建sheet表
            work_sheet = work_book.create_sheet(key)
            # 创建表头
            work_sheet.append(['用例', '次数', '次序', '开始帧', '开始帧匹配率', '结束帧', '结束帧匹配率', '差帧', '标准差帧', '平均差帧', '状态'])
            # 表头背景颜色
            for i in range(1, 12):
                work_sheet.cell(1, i).alignment = align
                work_sheet.cell(1, i).fill = gray_background
            # 当前可用行号
            current_row = 2
            # 背景颜色根据此数来确定(奇数为yellow, 偶数为green)
            background_color_select_num = 1
            for i in range(len(data)):
                background_color = green_background if background_color_select_num % 2 else yellow_background
                # 写一条case的数据(返回可用的行号)
                current_row = self.write_case_to_excel(work_sheet, current_row, data[i], align, background_color)
                background_color_select_num += 1
        # 删除掉第一个空白sheet
        work_book.remove(work_book['Sheet'])
        Logger('生成数据表: ' + file)
        work_book.save(file)
        work_book.close()

    # 将case写入sheet表中
    def write_case_to_excel(self, sheet, current_row, case_data, align, background_color):
        # 占用行直接获取次数即可(list第二个数为次数, 直接拿来用)
        occupied_row = int(case_data[1])
        # 下一个case当前行(也就是写完这个case后的下一行)
        next_current_row = current_row + occupied_row
        # 如果执行了多次
        if occupied_row > 1:
            # 合并用例
            sheet.merge_cells('A'+str(current_row) +':' +'A'+str(next_current_row -1))
            # case名
            sheet.cell(current_row, 1).value = case_data[0]
            sheet.cell(current_row, 1).alignment = align
            sheet.cell(current_row, 1).fill = background_color
            # 合并次数
            sheet.merge_cells('B' + str(current_row) + ':' + 'B' + str(next_current_row - 1))
            # 次数
            sheet.cell(current_row, 2).value = case_data[1]
            sheet.cell(current_row, 2).alignment = align
            sheet.cell(current_row, 2).fill = background_color
            # 装入每一次测试数据(从一个case产生多个视频)
            for id, data in enumerate(case_data[2]):
                sheet.cell(current_row + id, 3).value = data['次序']
                sheet.cell(current_row + id, 3).alignment = align
                sheet.cell(current_row + id, 3).fill = background_color
                sheet.cell(current_row + id, 4).value = data['开始帧']
                sheet.cell(current_row + id, 4).alignment = align
                sheet.cell(current_row + id, 4).fill = background_color
                sheet.cell(current_row + id, 5).value = data['开始帧匹配率']
                sheet.cell(current_row + id, 5).alignment = align
                sheet.cell(current_row + id, 5).fill = background_color
                sheet.cell(current_row + id, 6).value = data['结束帧']
                sheet.cell(current_row + id, 6).alignment = align
                sheet.cell(current_row + id, 6).fill = background_color
                sheet.cell(current_row + id, 7).value = data['结束帧匹配率']
                sheet.cell(current_row + id, 7).alignment = align
                sheet.cell(current_row + id, 7).fill = background_color
                sheet.cell(current_row + id, 8).value = data['差帧']
                sheet.cell(current_row + id, 8).alignment = align
                sheet.cell(current_row + id, 8).fill = background_color
            # 合并标准差帧
            sheet.merge_cells('I' + str(current_row) + ':' + 'I' + str(next_current_row - 1))
            # 标准差帧
            sheet.cell(current_row, 9).value = case_data[3]
            sheet.cell(current_row, 9).alignment = align
            sheet.cell(current_row, 9).fill = background_color
            # 合并平均差帧
            sheet.merge_cells('J' + str(current_row) + ':' + 'J' + str(next_current_row - 1))
            # 平均差帧
            sheet.cell(current_row, 10).value = case_data[4]
            sheet.cell(current_row, 10).alignment = align
            sheet.cell(current_row, 10).fill = background_color
            # 合并状态
            sheet.merge_cells('K' + str(current_row) + ':' + 'K' + str(next_current_row - 1))
            # 状态
            sheet.cell(current_row, 11).value = case_data[5]
            sheet.cell(current_row, 11).alignment = align
            if case_data[5] == 'failed':
                background_color = PatternFill("solid", fgColor=colors.RED)
            else:
                background_color = PatternFill("solid", fgColor=colors.GREEN)
            sheet.cell(current_row, 11).fill = background_color
        # 只有执行了一次的数据
        else:
            sheet.cell(current_row, 1).value = case_data[0]
            sheet.cell(current_row, 1).alignment = align
            sheet.cell(current_row, 1).fill = background_color
            sheet.cell(current_row, 2).value = case_data[1]
            sheet.cell(current_row, 2).alignment = align
            sheet.cell(current_row, 2).fill = background_color
            sheet.cell(current_row, 3).value = case_data[2][0]['次序']
            sheet.cell(current_row, 3).alignment = align
            sheet.cell(current_row, 3).fill = background_color
            sheet.cell(current_row, 4).value = case_data[2][0]['开始帧']
            sheet.cell(current_row, 4).alignment = align
            sheet.cell(current_row, 4).fill = background_color
            sheet.cell(current_row, 5).value = case_data[2][0]['开始帧匹配率']
            sheet.cell(current_row, 5).alignment = align
            sheet.cell(current_row, 5).fill = background_color
            sheet.cell(current_row, 6).value = case_data[2][0]['结束帧']
            sheet.cell(current_row, 6).alignment = align
            sheet.cell(current_row, 6).fill = background_color
            sheet.cell(current_row, 7).value = case_data[2][0]['结束帧匹配率']
            sheet.cell(current_row, 7).alignment = align
            sheet.cell(current_row, 7).fill = background_color
            sheet.cell(current_row, 8).value = case_data[2][0]['差帧']
            sheet.cell(current_row, 8).alignment = align
            sheet.cell(current_row, 8).fill = background_color
            sheet.cell(current_row, 9).value = case_data[3]
            sheet.cell(current_row, 9).alignment = align
            sheet.cell(current_row, 9).fill = background_color
            sheet.cell(current_row, 10).value = case_data[4]
            sheet.cell(current_row, 10).alignment = align
            sheet.cell(current_row, 10).fill = background_color
            sheet.cell(current_row, 11).value = case_data[5]
            sheet.cell(current_row, 11).alignment = align
            if case_data[5] == 'failed':
                background_color = PatternFill("solid", fgColor=colors.RED)
            else:
                background_color = PatternFill("solid", fgColor=colors.GREEN)
            sheet.cell(current_row, 11).fill = background_color
        return next_current_row

    # 通过excel获取柱形图
    def get_graph_data(self, graph_path, case_date_dict):
        generate_graph = GenerateDataGraph(graph_path=graph_path, data_dict=case_date_dict)
        generate_graph.get_graphs()

    # 生成html并保存
    def get_report(self, report_path, case_data_dict):
        generate_report = GenerateReport(report_path=report_path, data_dict=case_data_dict)
        generate_report.save_html()

    # 结合(1.生成excel, 2.通过excel获取柱形图, 3.生成html并保存)
    def data_processing(self):
        # 获取数据(dict类型)
        case_data_dict = self.get_all_video_start_and_end_points()
        # 保存excel
        self.write_data_to_excel(file=self.report_excel, original_data_dict=case_data_dict)
        # # 通过excel获取柱形图
        self.get_graph_data(graph_path=self.report_path, case_date_dict=case_data_dict)
        # # 生成html并保存
        self.get_report(report_path=self.report_path, case_data_dict=case_data_dict)
        Logger('data process finished!')


if __name__=='__main__':
    # video_path = 'D:/Code/robot/video/2019-10-15'
    video_path = 'D:/Code/robot/video/2019-12-03/点击/点击设置'
    test = GetStartupTime(video_path=video_path)
    test.data_processing()