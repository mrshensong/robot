import os
from GlobalVar import Logger


# 生成测试报告
class GenerateReport:
    def __init__(self, report_path, data_dict):
        self.report_path = report_path
        self.data_dict = data_dict
        self.report_name = '/'.join([report_path, 'report.html'])

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
        case_type = graph.split('.')[0]
        text = '\n<h3 style="text-align:left">【'+ case_type +'】类测试结果如下: </h3>' +\
               '\n<p style="text-align:left"><img src="'+ graph +'"/></p>'
        return text


    # 获取表图报告
    def get_table_chart_report(self, data_dict):
        html_chat = '<table border="1" cellspacing="0">\n' +\
                    '<tr bgcolor="gray" height="50" align="center">\n' +\
                    '<td width="250">类型</td>\n' +\
                    '<td width="500">用例</td>\n' +\
                    '<td width="100">次数</td>\n' +\
                    '<td width="100">标准(ms)</td>\n' +\
                    '<td width="100">平均值(ms)</td>\n' +\
                    '<td width="100">状态</td>\n' +\
                    '</tr>\n'
        for key, data in data_dict.items():
            data_length = len(data)
            for i in range(data_length):
                if data[i][7] == 'failed':
                    background_color = 'red'
                else:
                    background_color = 'green'
                # 第一个需要合并单元格(展示测试类型)
                if i == 0:
                    html_chat += '<tr bgcolor="'+ background_color +'" height="30" align="center">\n' +\
                                 '<td bgcolor="blue" rowspan="'+ str(data_length) +'">'+ str(key) +'</td>\n' +\
                                 '<td align="left">'+ str(data[i][0]) +'</td>\n' +\
                                 '<td>'+ str(data[i][1]) +'</td>\n' +\
                                 '<td>'+ str(data[i][4]) +'</td>\n' +\
                                 '<td>'+ str(data[i][6]) +'</td>\n' +\
                                 '<td>'+ str(data[i][7]) +'</td>\n' +\
                                 '</tr>\n'
                else:
                    html_chat += '<tr bgcolor="'+ background_color +'" height="30" align="center">\n' + \
                                 '<td align="left">' + str(data[i][0]) + '</td>\n' + \
                                 '<td>' + str(data[i][1]) + '</td>\n' + \
                                 '<td>' + str(data[i][4]) + '</td>\n' + \
                                 '<td>' + str(data[i][6]) + '</td>\n' + \
                                 '<td>' + str(data[i][7]) + '</td>\n' + \
                                 '</tr>\n'
        html_chat += '</table>\n'
        return html_chat


    # 保存生成的html代码
    def save_html(self):
        html_head = '<!DOCTYPE HTML>\n' +\
               '<html>\n' +\
               '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n' +\
               '<body>\n' +\
               '<h2 style="text-align:left">' + self.report_name + '</h1>\n' +\
               '<br/>\n'
        html_tail = '\n</body>' +\
                    '\n</html>'
        # html_body = ''
        html_body = self.get_table_chart_report(self.data_dict)
        # 获取html_body内容
        graph_list = self.get_report_graph()
        for graph in graph_list:
            text = self.generate_html_by_graph(graph=graph)
            html_body += text
        html = html_head + html_body + html_tail
        with open(self.report_name, 'w', encoding='utf-8') as f:
            f.write(html)
        Logger('生成报告: ' + self.report_name)


if __name__=='__main__':
    generate_report = GenerateReport(report_path='D:/Code/robot/report/2019-10-15')
    generate_report.save_html()