import os
from GlobalVar import Logger


# 生成测试报告
class GenerateReport:
    def __init__(self, report_path, data_dict):
        self.report_path = report_path
        self.data_dict = data_dict
        self.report_name = '/'.join([report_path, 'report.html'])
        self.body_background_color = '#F0F0F0'
        self.chart_background_color = '#D8F0D8'
        self.chart_border_color = '#A8A8A8'
        self.chart_skip_line_color = '#FFF0D8'
        self.chart_hover_line_color = '#99CC99'

    # 获取report路径下的所有report图片(.png)
    def get_report_graph(self):
        graph_list = []
        files = os.listdir(self.report_path)
        for file in files:
            if file.endswith('.png'):
                graph_list.append(file)
        return graph_list

    # 通过柱形图表来生成html中的一部分
    def generate_html_by_graph(self, graph):
        # 居左必须加此句
        # '<p style="text-align:left"><img src="'+ graph +'"/></p>\n'
        case_type = graph.split('.')[0]
        text = '<h3 style="text-align:left">【'+ case_type +'】类测试结果如下: </h3>\n' \
               '<hr/>\n' \
               '<p align="center"><img src="'+ graph +'"/></p>\n'
        return text


    # 获取表图报告
    def get_table_chart_report(self):
        html_chat = '<p style="font-family:arial;font-size:20px;font-weight:bold">测试用例执行详细情况如下: </p>\n' \
                    '<hr/>\n' \
                    '<table width="100%" border= "1px solid '+ self.chart_border_color +'" cellspacing="0">\n' \
                    '<tr height="50" align="center" style="font-weight: bold">\n' \
                    '<td width="10%"><font color="#606060">类型</font></td>\n' \
                    '<td width="30%"><font color="#606060">用例</font></td>\n' \
                    '<td width="10%"><font color="#606060">次数</font></td>\n' \
                    '<td width="10%"><font color="#606060">标准(ms)</font></td>\n' \
                    '<td width="10%"><font color="#606060">平均值(ms)</font></td>\n' \
                    '<td width="10%"><font color="#606060">最大值(ms)</font></td>\n' \
                    '<td width="10%"><font color="#606060">最小值(ms)</font></td>\n' \
                    '<td width="10%"><font color="#606060">状态</font></td>\n' \
                    '</tr>\n'
        for key, data in self.data_dict.items():
            data_length = len(data)
            for i in range(data_length):
                # 计算耗时最大值和最小值
                time_consume_list = [execute_info['耗时'] for execute_info in data[i][2]]
                time_consume_max_value = max(time_consume_list)
                time_consume_min_value = min(time_consume_list)
                if data[i][7] == 'failed':
                    result_color = '#FF3030'
                else:
                    result_color = '#18C0A8'
                # 第一个需要合并单元格(展示测试类型)
                if i == 0:
                    html_chat += '<tr height="30" align="center">\n' \
                                 '<td rowspan="' + str(data_length) + '" bgcolor="99CC99"><font color="#60A8D8">' + str(key) + '</font></td>\n' \
                                 '<td><font color="#30D878">' + str(data[i][0]) +'</font></td>\n' \
                                 '<td><font color="#1890C0">' + str(data[i][1]) +'</font></td>\n' \
                                 '<td><font color="#30D8D8">' + str(data[i][4]) +'</font></td>\n' \
                                 '<td><font color="#FFA860">' + str(data[i][6]) +'</font></td>\n' \
                                 '<td><font color="#0078C0">' + str(time_consume_max_value) +'</font></td>\n' \
                                 '<td><font color="#996699">' + str(time_consume_min_value) +'</font></td>\n' \
                                 '<td style="font-weight: bold; font-size: 14pt"><font color="' + result_color + '">' + str(data[i][7]) + '</font></td>\n' \
                                 '</tr>\n'
                else:
                    html_chat += '<tr height="30" align="center">\n' \
                                 '<td><font color="#30D878">' + str(data[i][0]) + '</font></td>\n' \
                                 '<td><font color="#1890C0">' + str(data[i][1]) + '</font></td>\n' \
                                 '<td><font color="#30D8D8">' + str(data[i][4]) + '</font></td>\n' \
                                 '<td><font color="#FFA860">' + str(data[i][6]) + '</font></td>\n' \
                                 '<td><font color="#0078C0">' + str(time_consume_max_value) + '</font></td>\n' \
                                 '<td><font color="#996699">' + str(time_consume_min_value) + '</font></td>\n' \
                                 '<td style="font-weight: bold; font-size: 14pt"><font color="' + result_color + '">' + str(data[i][7]) + '</font></td>\n' \
                                 '</tr>\n'
        html_chat += '</table>\n'
        return html_chat


    # 获取报告描述
    def get_description_chart(self):
        # 报告路径
        report_path = self.report_name
        # 开始时间
        start_time = '-'.join(os.path.split(self.report_name)[0].split('/')[-2:])
        # case总数
        case_totle_num = 0
        # 成功case个数
        case_success_num = 0
        # 失败case个数
        case_fail_num = 0
        # 成功率
        case_success_rate = 0.0
        for key, data in self.data_dict.items():
            data_length = len(data)
            for i in range(data_length):
                case_totle_num += 1
                if data[i][7] == 'pass':
                    case_success_num += 1
        case_fail_num = case_totle_num - case_success_num
        case_success_rate = '%.0f%%' % ((case_success_num / case_totle_num) * 100)
        report_status = 'pass' if case_fail_num == 0 else 'failed'
        result_status_color = '#18C0A8' if report_status == 'pass' else '#FF3030'
        html_description = '<p style="font-family:arial;font-size:20px;font-weight:bold"><i>'+ str(start_time) +'</i>/测试报告详情如下: </p>\n' \
                        '<hr/>\n' \
                        '<table width="100%" border= "1px solid '+ self.chart_border_color +'" cellspacing="0">\n' \
                        '<tr height="50" align="center" style="font-weight: bold">\n' \
                        '<td width="30%"><font color="#606060">报告路径</font></td>\n' \
                        '<td width="20%"><font color="#606060">开始时间</font></td>\n' \
                        '<td width="10%"><font color="#606060">成功</font></td>\n' \
                        '<td width="10%"><font color="#606060">失败</font></td>\n' \
                        '<td width="10%"><font color="#606060">总计</font></td>\n' \
                        '<td width="10%"><font color="#606060">成功率</font></td>\n' \
                        '<td width="10%"><font color="#606060">状态</font></td>\n' \
                        '</tr>\n' \
                        '<tr height="30" align="center">\n' \
                        '<td><font color="#60A8D8">'+ str(report_path) +'</font></td>\n' \
                        '<td><font color="#30D878">'+ str(start_time) +'</font></td>\n' \
                        '<td><font color="#1890C0">'+ str(case_success_num) +'</font></td>\n' \
                        '<td><font color="#30D8D8">'+ str(case_fail_num) +'</font></td>\n' \
                        '<td><font color="#0078C0">'+ str(case_totle_num) +'</font></td>\n' \
                        '<td><font color="#996699">'+ str(case_success_rate) +'</font></td>\n' \
                        '<td style="font-weight: bold; font-size: 16pt"><font color="'+ str(result_status_color) +'">'+ str(report_status) +'</font></td>\n' \
                        '</tr>\n' \
                        '</table>\n'
        return html_description


    # 保存生成的html代码
    def save_html(self):
        html_head = '<!DOCTYPE HTML>\n' \
                '<html>\n' \
                '<head>\n' \
                '<meta charset="utf-8">\n' \
                '<style type="text/css">\n' \
                'table{ border-collapse:collapse; border-spacing:0; border:1 px solid '+ self.body_background_color +'}\n' \
                'table{width: 100%; background-color: '+ self.chart_background_color +';}\n' \
                'table tr:nth-child(2n){background-color: '+ self.chart_skip_line_color +'}\n' \
                'table tr:hover{background-color: '+ self.chart_hover_line_color +'}\n' \
                '</style>\n' \
                '</head>\n' \
                '<body bgcolor='+ self.body_background_color +'>\n'
        html_tail = '</body>\n</html>'
        # 获取报告开头描述
        html_description = self.get_description_chart()
        # 获取图表
        html_body = self.get_table_chart_report()
        # 获取html_body内容
        graph_list = self.get_report_graph()
        for graph in graph_list:
            text = self.generate_html_by_graph(graph=graph)
            html_body += text
        html = html_head + html_description + html_body + html_tail
        with open(self.report_name, 'w', encoding='utf-8') as f:
            f.write(html)
        Logger('生成报告: ' + self.report_name)


if __name__=='__main__':
    generate_report = GenerateReport(report_path='D:/Code/robot/report/2019-10-15')
    generate_report.save_html()