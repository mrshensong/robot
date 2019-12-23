import matplotlib
import matplotlib.pyplot as plt
from GlobalVar import Logger, MergePath
# 设置中文字体和负号正常显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False


class GenerateDataGraph:
    def __init__(self, graph_path, data_dict):
        self.graph_path = graph_path
        self.data_dict = data_dict
        # self.standard_value = int(Profile(type='read', file=GloVar.config_file_path, section='standard', option='critical_value').value)
        self.standard_value = 100


    def drawing(self, file_name, case_list, actual_value_list, standard_list, status_list):
        # 水平条形图
        """
        绘制水平条形图方法barh
        参数一：y轴
        参数二：x轴
        """
        # 将传入的数据倒序排列(因为图表画图是从下往上画图, 正好与正常人们理解的从上往下相反)
        case_list.reverse()
        actual_value_list.reverse()
        standard_list.reverse()
        status_list.reverse()
        # 根据数据量设置画布大小, 以及刻度范围
        case_num = len(case_list)
        # 画布大小根据case数量来
        plt.figure(figsize=(12, case_num + 2))
        # plt.set_facecolor('blueviolet')
        # 根据在标准值和测试值中取最大值再加上20, 作为表的宽度
        chat_width = max(actual_value_list + standard_list) + 100
        # 设置x & y 轴范围
        plt.axis([10, chat_width, -1, case_num + 1])
        # 画条形(真实数据, 横向展示)
        y_list = [num + 0.2 for num in range(case_num)]
        plt.barh(y=y_list, width=actual_value_list, label='测试时间', height=0.4, color='#18C0A8', alpha=1.0)
        # plt.barh(y=y_list, width=actual_value_list, label='测试时间', height=0.4, color='#00C0C0', alpha=0.6)
        # 画条形(标准数据, 紧挨着真实数据)
        y_list = [num - 0.2 for num in range(case_num)]
        plt.barh(y=y_list, width=standard_list, label='标准时间', height=0.4, color='#FFA860', alpha=1.0)
        # 显示case名
        plt.yticks(range(case_num), case_list)
        # 柱形图标注
        # 标注真实测量数据
        for x, y in enumerate(actual_value_list):
            plt.text(y + 10, x + 0.1, '%s' % y, ha='center', va='bottom')
        # 标注标准数据
        for x, y in enumerate(standard_list):
            plt.text(y + 10, x - 0.3, '%s' % y, ha='center', va='bottom')
        # 标注pass/failed
        for num, status in enumerate(status_list):
            if status == 'failed':
                plt.text(chat_width - 40, num - 0.1, 'failed', size=16, color='#FF3030', ha='center', va='bottom')
            else:
                plt.text(chat_width - 40, num - 0.1, 'pass', size=16, color='#18C0A8', ha='center', va='bottom')
        # 获取图片title
        title = file_name.split('/')[-1].split('.')[0]
        plt.title('[' + title + ']' + '-->流畅度测试')
        plt.xlabel('-*- 时间/ms -*-')
        # 显示图例
        plt.legend(loc='upper left')
        # 避免出现title或者纵坐标显示不完整的问题
        plt.tight_layout()
        plt.savefig(file_name)
        Logger('生成数据图: ' + file_name)


    def get_graphs(self):
        for key, data in self.data_dict.items():
            file_name = MergePath([self.graph_path, key+'.png']).merged_path
            case_list, time_gap_list, standard_list, status_list = [], [], [], []
            for case in data:
                case_list.append(case[0])
                standard_list.append(case[4])
                time_gap_list.append(case[6])
                status_list.append(case[7])
            self.drawing(file_name, case_list, time_gap_list, standard_list, status_list)



if __name__=='__main__':
    graph_path = 'D:/Code/robot/report/2019-11-27'
    data_dict = {}
    data_graph = GenerateDataGraph(graph_path=graph_path, data_dict=data_dict)
    data_graph.get_graphs()
