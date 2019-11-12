import pandas as pd
from GlobalVar import Logger


# 操作excel
class OperateExcel:
    def __init__(self, file, data_list):
        # 传入的list由多个词典组成
        # {'name': video, 'start_frame': start_frame, 'start_threshold': start_threshold, 'end_frame': end_frame, 'end_threshold': end_threshold}
        self.file = file
        self.data_list = data_list

    # 将传进来的数据转换为可以直接在excel中保存的DataFrame
    def generate_data(self):
        data_list = []
        sheet_name_list = []
        for data in self.data_list:
            data_dict = {}
            # 通过文件名的倒数第二个获取到case类型(也就是sheet名)
            case_type = data['name'].split('/')[-2]
            data_dict['case_type'] = case_type
            # 将所有的case_type放入列表, 然后去重(即可知道需要新建几个sheet)
            sheet_name_list.append(case_type)
            # case文件名
            file_name =  data['name'].split('/')[-1]
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
        excel_writer = pd.ExcelWriter(self.file)
        # 直接在data_list_by_case_type取出数据即可
        for data in data_list_by_sheet:
            file_name_list = []
            start_frame_list = []
            start_threshold_list = []
            end_frame_list = []
            end_threshold_list = []
            for i in range(1, len(data)):
                file_name_list.append(data[i]['file_name'].split('.')[0])
                start_frame_list.append(data[i]['start_frame'])
                start_threshold_list.append(data[i]['start_threshold'])
                end_frame_list.append(data[i]['end_frame'])
                end_threshold_list.append(data[i]['end_threshold'])
            sheet_name = data[0]
            data = {'用例' : file_name_list,
                    '开始帧' : start_frame_list,
                    '开始帧匹配率' : start_threshold_list,
                    '结束帧' : end_frame_list,
                    '结束帧匹配率' : end_threshold_list}
            Logger('保存sheet: ' + sheet_name)
            df = pd.DataFrame(data=data)
            df.to_excel(excel_writer=excel_writer, sheet_name=sheet_name, index=False)
        excel_writer.save()
        excel_writer.close()
