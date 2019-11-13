from openpyxl import load_workbook
import matplotlib
import matplotlib.pyplot as plt
# 设置中文字体和负号正常显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False


class DataGraph:
    def __init__(self, file):
        self.file = file

    # 获取某个单元格的值
    def get_cell_value(self, sheet, row, column):
        cell_value = sheet.cell(row=row, column=column).value
        return cell_value

    # 获取某行所有值
    def get_row_values(self, sheet, row):
        columns = sheet.max_column
        row_data = []
        for i in range(1, columns + 1):
            cell_value = sheet.cell(row=row, column=i).value
            row_data.append(cell_value)
        # 去掉行头(在这里就代表case名)
        row_data.pop(0)
        return row_data

    # 获取某列的所有值
    def get_column_values(self, sheet, column):
        rows = sheet.max_row
        column_data = []
        for i in range(1, rows + 1):
            cell_value = sheet.cell(row=i, column=column).value
            column_data.append(cell_value)
        # 去掉列头(在这里就代表差帧)
        column_data.pop(0)
        return column_data

    # 从excel表中获取数据(每一个sheet表对应一个数据图)
    def get_data(self):
        # 载入excel
        work_book = load_workbook(self.file)
        # 获取所有sheet
        sheet_list = work_book.sheetnames
        # 设置data_list存放获取到的数据([[cases, frame_gap], [cases, frame_gap]])
        data_list = []
        for sheet in sheet_list:
            print('sheet表: ', sheet)
            work_sheet = work_book[sheet]
            cases = self.get_column_values(sheet=work_sheet, column=1)
            frame_gap = self.get_column_values(sheet=work_sheet, column=6)
            data_list.append([cases, frame_gap])
        work_book.close()
        return data_list


    def drawing(self, file_name, case_list, frame_gap_list):
        # 水平条形图
        """
        绘制水平条形图方法barh
        参数一：y轴
        参数二：x轴
        """
        plt.figure()
        plt.barh(y=range(len(case_list)), width=frame_gap_list, height=0.4, color='steelblue', alpha=0.8)  # 从下往上画
        plt.yticks(range(len(case_list)), case_list)
        # plt.xlim(30, 47)
        plt.xlabel("差帧")
        plt.title("间隔帧数")
        for x, y in enumerate(frame_gap_list):
            plt.text(y + 0.2, x - 0.1, '%s' % y)
        plt.savefig(file_name)
        # plt.show()

    # 获取图片
    def get_graphs(self):
        data_list = self.get_data()
        for data in data_list:
            file_name = self.file.split('.')[0] + '-' + str(data_list.index(data) + 1) + '.png'
            self.drawing(file_name=file_name, case_list=data[0], frame_gap_list=data[1])



if __name__=='__main__':
    file = 'D:/Code/robot/report/2019-10-15/report.xlsx'
    # DataGraph(file=None).drawing()
    data_graph = DataGraph(file=file)
    data_graph.get_graphs()