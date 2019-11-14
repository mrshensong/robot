import os
from GlobalVar import Logger


# 生成测试报告
class GenerateReport:
    def __init__(self, report_path):
        self.report_path = report_path
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
        text = '\n<h3 style="text-align:center">【'+ case_type +'】类测试结果如下: </h3>' +\
               '\n<p style="text-align:center"><img src="'+ graph +'"/></p>'
        return text

    # 保存生成的html代码
    def save_html(self):
        html_head = '<!DOCTYPE HTML>\n' +\
               '<html>\n' +\
               '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n' +\
               '<body>\n' +\
               '<h1 style="text-align:center">北京车和家</h1>'
        html_tail = '\n</body>' +\
                    '\n</html>'
        html_body = ''
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