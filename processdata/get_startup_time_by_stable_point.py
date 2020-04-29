import re
from processdata.get_data_graph import GenerateDataGraph
from processdata.get_report import GenerateReport
from processdata.get_excel import GenerateExcel
from GlobalVar import *
from datetime import datetime


class GetStartupTimeByStablePoint:

    def __init__(self, video_path):
        # 视频路径
        self.video_path = video_path
        # 获取路径中的时间
        pattern = re.compile(r'\d+-\d+-\d+')
        time_list = pattern.findall(self.video_path)
        # 开始时间
        test_time = '/'.join(time_list)
        # 更改report路径
        self.report_path = MergePath([GloVar.project_path, 'report', test_time]).merged_path
        if os.path.exists(self.report_path) is False:
            os.makedirs(self.report_path)
        # 模板匹配率(匹配率大于此, 说明可以开始检测稳定帧)
        self.template_start_frame_match_threshold = 0.80
        # 稳定帧匹配率(匹配率连续大于此匹配率, 才说明帧稳定)
        self.template_stability_frame_match_threshold = 0.99
        # 基准图片和视频帧匹配率连续超过某一匹配率的次数(可以说明帧稳定)
        self.frame_stability_times = 10
        # 待处理的视频列表
        self.videos_list = []

    # 获取roi模板的位置信息(roi图片/column行数,0-3)
    @staticmethod
    def get_position_info_from_roi(roi, column):
        thousands = roi[0][column] * 1000
        hundred = roi[1][column] * 100
        ten = roi[2][column] * 10
        single = roi[3][column] * 1
        num = thousands + hundred + ten + single
        return num

    # 计算开始和结束位置(通过稳定点)
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
        # 处理逐鹿需要的信息
        if GloVar.compete_platform_flag is True:
            # 视频起始(第一帧)时间
            first_frame_time = float(os.path.split(video_file)[1].split('.')[0].split('-')[1])
            # 视频中起点时间
            start_flag_time = float(os.path.split(video_file)[1].split('.')[0].split('-')[0])
            # 最小时间差值(给一个尽可能大的值)
            min_time_diff = 1000000000
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
        start_point_result = (1, 1.0)
        end_point_result = (1, 0.0)
        # 计算待检测模板在整帧中的位置(需要截取出来)
        # 获取视频的尺寸
        frame_height = video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        frame_width = video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        # 获取模板的灰度图
        end_mask_gray = cv2.imdecode(np.fromfile(end_mask, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        # 根据模板图片中第一行像素值, 找到模板所在当前帧中的位置(将带查找图片选择的稍微比模板图片大一点点每个边大20像素)
        # 行起点
        row_start = self.get_position_info_from_roi(end_mask_gray, 0) - GloVar.template_border
        row_start = 0 if row_start < 0 else row_start
        # 行终点
        row_end = self.get_position_info_from_roi(end_mask_gray, 1) + GloVar.template_border
        row_end = frame_height - 1 if row_end >= frame_height else row_end
        # 列起点
        column_start = self.get_position_info_from_roi(end_mask_gray, 2) - GloVar.template_border
        column_start = 0 if column_start < 0 else column_start
        # 列终点
        column_end = self.get_position_info_from_roi(end_mask_gray, 3) + GloVar.template_border
        column_end = frame_width - 1 if column_end >= frame_width else column_end
        # 视频读取
        while video_cap.isOpened():
            # 帧从1开始
            frame_id += 1
            successfully_read, frame = video_cap.read()
            # 获取帧所在时间
            current_time = video_cap.get(cv2.CAP_PROP_POS_MSEC)
            if successfully_read is True:
                # 灰度化
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # 目标图片(待匹配)
                target = frame_gray[row_start: row_end, column_start: column_end]
                # 起点
                if start_point_exist_flag is False:
                    # 系统本身通过视频第一行颜色判断
                    if GloVar.compete_platform_flag is False:
                        # 如果图像第一行像素为白色(排除前十帧可能出现的乱帧)
                        if frame[0].mean() > 245 and frame_id > 10:
                            start_point_result = (frame_id, 1.0)
                            start_point_exist_flag = True
                    # 逐鹿平台通过时间判断起点
                    else:
                        current_time_diff = abs(first_frame_time + current_time - start_flag_time)
                        if current_time_diff <= min_time_diff:
                            min_time_diff = current_time_diff
                        elif current_time_diff > min_time_diff:
                            start_point_result = (frame_id, 1.0)
                            start_point_exist_flag = True
                    # 先寻找起点(没有找到起点进行下一循环)
                    continue
                # 起点之后寻找模板出现的帧
                elif template_appear_flag is False:
                    threshold = Common.match_template(target, end_mask_gray)
                    if threshold >= self.template_start_frame_match_threshold:
                        template_appear_flag = True
                        last_picture = target
                    else:
                        continue
                # 终点(稳定点)
                if template_appear_flag is True:
                    match_rate = Common.match_template(target, last_picture)
                    if cycle_flag is True:
                        if match_rate > self.template_stability_frame_match_threshold:
                            cycle_flag = True
                            stability_num += 1
                            if stability_num == self.frame_stability_times:
                                end_point_result = (frame_id - self.frame_stability_times,
                                                    self.template_stability_frame_match_threshold)
                                break
                        else:
                            cycle_flag = False
                            stability_num = 0
                    else:
                        if match_rate > self.template_stability_frame_match_threshold:
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

    # 处理视频, 从视频中获取处理信息
    def process_video(self, video_id, file, end_mask):
        Logger('正在计算<%s>起止点...' % file)
        # 计算起始帧和停止帧
        (start_frame, start_threshold), (end_frame, end_threshold) = \
            self.get_start_and_end_match_threshold(end_mask=end_mask, video_file=file)
        start_frame = start_frame
        end_frame = end_frame
        frame_gap = end_frame - start_frame
        # 不同平台不同方法(系统和逐鹿)
        if GloVar.compete_platform_flag is False:
            frame_rate = 120
            # 获取拍摄视频的时间
            file_name = os.path.split(file)[1]
            pattern = re.compile(r'\d+_\d+_\d+_\d+_\d+_\d+')
            current_time = pattern.findall(file_name)[0]
        else:
            frame_rate = 30
            # 需要将时间戳转为时间
            time_stamp = int(os.path.split(file)[1].split('-')[0])
            current_time = datetime.fromtimestamp(time_stamp / 1000.0).strftime('%Y_%m_%d_%H_%M_%S')
        time_gap = int(frame_gap * (1000 / frame_rate))
        # 将拍摄时间格式更改为2020-04-23 14:20:54
        current_time_list = current_time.split('_')
        current_time = '-'.join(current_time_list[:3]) + ' ' + ':'.join(current_time_list[3:])
        Logger('%s-->起始点: 帧> %d, 匹配率> %.4f' % (file, start_frame, start_threshold))
        Logger('%s-->终止点: 帧> %d, 匹配率> %.4f' % (file, end_frame, end_threshold))
        return {'次序': video_id, '开始帧': start_frame, '开始帧匹配率': start_threshold, '结束帧': end_frame,
                '结束帧匹配率': end_threshold, '差帧': frame_gap, '耗时': time_gap, '时间': current_time}

    # 处理一条case(可能含有多次执行产生的多个视频, 传入的参数为产生的这些视频的当前目录路径)
    def process_case(self, video_name_path):
        video_count = 0
        video_valid_count = 0
        video_info_list = []
        video_files = os.listdir(video_name_path)
        case_name = video_name_path.split('/')[-1]
        video_name_path_cut_list = video_name_path.split('/')
        new_video_name_path_cut_list = video_name_path_cut_list[:-4] + ['template'] + video_name_path_cut_list[-2:]
        end_mask = '/'.join(new_video_name_path_cut_list).replace('/video/', '/picture/') + '.bmp'
        # 选择不同平台(此处处理不同(分为系统和逐鹿))
        if GloVar.compete_platform_flag is False:
            # 通过读取配置文件获取标准耗时(单位/ms)
            option = '/'.join(video_name_path_cut_list[-2:])
            # standard_time_gap = 800
            standard_time_gap = int(Profile(type='read', file=GloVar.config_file_path, section='standard', option=option).value)
            frame_rate = 120
        else:
            standard_time_gap = int(os.listdir(video_name_path)[0].split('.')[0].split('-')[-1])
            frame_rate = 30
        # 标准差帧
        standard_frame_gap = int(standard_time_gap / (1000 / frame_rate))
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
                if video_info['开始帧'] != 1 and video_info['结束帧'] != 1 and video_info['开始帧'] != video_info['结束帧']:
                    video_valid_count += 1
                    sum_frame_gap += int(video_info['差帧'])
        # 避免分母为0的情况
        if sum_frame_gap == 0:
            video_valid_count = 1
        average_frame_gap = int(sum_frame_gap / video_valid_count)
        average_time_gap = int((sum_frame_gap * (1000 / frame_rate)) / video_valid_count)
        # 获取状态
        if average_frame_gap == 0 or video_valid_count < video_count:
            status = 'error'
        else:
            if average_time_gap > int(standard_time_gap * 1.1):
                status = 'failed'
            else:
                status = 'pass'
        # 当前case中有某次计算出异常的问题, 判断是否需要重新测试
        retest_flag = 'YES' if status == 'error' else 'NO'
        # 返回的信息跟excel模型相似(列表第一个参数代表case类型, 也就是sheet名字)
        return [case_name, video_count, video_info_list, standard_frame_gap, standard_time_gap, average_frame_gap,
                average_time_gap, status, retest_flag]

    # 获取起止点以及对应匹配率等等
    def get_all_video_start_and_end_points(self):
        """
        此处传入视频路径(算出路径下所有case视频的起止点)
        :return:
        """
        # 获取视频名文件夹(如:D:/Code/robot/video/2019-11-27/15-10-55/测试/点击设置, 里面装有1/2/3/4/5.MP4这样的记录次数的文件)
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
        # 返回(如:{'滑动':[[桌面滑动], [设置滑动]], '点击':[[点击设置], [点击地图]]})
        return case_type_dict

    # 生成excel
    @staticmethod
    def get_excel(excel_path, case_data_dict):
        generate_excel = GenerateExcel(excel_path=excel_path, data_dict=case_data_dict)
        generate_excel.write_data_to_excel()

    # 通过excel获取柱形图
    @staticmethod
    def get_graph_data(graph_path, case_date_dict):
        generate_graph = GenerateDataGraph(graph_path=graph_path, data_dict=case_date_dict)
        generate_graph.get_graphs()

    # 生成html并保存
    @staticmethod
    def get_report(report_path, case_data_dict):
        generate_report = GenerateReport(report_path=report_path, data_dict=case_data_dict)
        generate_report.save_html()

    # 结合(1.生成excel, 2.通过excel获取柱形图, 3.生成html并保存)
    def data_processing(self):
        # 获取数据(dict类型)
        case_data_dict = self.get_all_video_start_and_end_points()
        # 保存excel
        self.get_excel(excel_path=self.report_path, case_data_dict=case_data_dict)
        # # 通过excel获取柱形图
        self.get_graph_data(graph_path=self.report_path, case_date_dict=case_data_dict)
        # # 生成html并保存
        self.get_report(report_path=self.report_path, case_data_dict=case_data_dict)
        # 将数据处理完成标志位置位
        GloVar.data_process_finished_flag = True
        Logger('data process finished!')
        WindowStatus.operating_status = '空闲状态/测试结束'

    # 实时数据处理
    def data_processing_by_real_time(self):
        # 获取数据(dict类型)
        video_data_dict = self.get_all_video_start_and_end_points()
        if GloVar.video_process_data:
            video_type_list = video_data_dict.keys()
            for video_type in video_type_list:
                if video_type in GloVar.video_process_data.keys():
                    for video_data in video_data_dict[video_type]:
                        GloVar.video_process_data[video_type].append(video_data)
                else:
                    GloVar.video_process_data.update(video_data_dict)
        else:
            GloVar.video_process_data = video_data_dict
        # 保存excel
        self.get_excel(excel_path=self.report_path, case_data_dict=GloVar.video_process_data)
        # 获取柱形图
        self.get_graph_data(graph_path=self.report_path, case_date_dict=GloVar.video_process_data)
        # 生成html并保存
        self.get_report(report_path=self.report_path, case_data_dict=GloVar.video_process_data)
        Logger('[当前case产生的数据更新完毕]')


if __name__ == '__main__':
    # video_path = 'D:/Code/robot/video/2019-10-15'
    # video_path = 'D:/Code/robot/video/2019-12-03/点击/点击设置'
    video_path = 'D:/Code/robot_exe/video/2020-03-23/15-13-51/启动/启动音乐'
    test = GetStartupTimeByStablePoint(video_path=video_path)
    # test.data_processing()
    video = 'D:/Test/Python/TestVideo/video/tc_Fun_xingneng_0108.mp4'
    picture = 'D:/Test/Python/TestVideo/image/tc_Fun_xingneng_0108.bmp'
    aaa = test.get_start_and_end_match_threshold(picture, video)
    print(aaa)
