import re
import configparser


'''修改ini配置文件保留注释行'''


class ConfigWithComment:

    def __init__(self, file):
        self.file = file

    # 查找ini文件中所有section和对应的text
    def read_sections(self):
        # 读取文本
        with open(self.file, encoding='utf-8') as f:
            text = f.read()
        section_pattern = re.compile(r'\[\w+\]')
        section_name_list = section_pattern.findall(text)
        section_text_list = []
        for num in range(len(section_name_list)):
            if num == len(section_name_list) - 1:
                section_text = text
                section_text_list.append(section_text)
            else:
                section_text = text.split(section_name_list[num+1])[0]
                text = text.split(section_text)[1]
                section_text_list.append(section_text)
        # 将[param]变为param
        section_name_list = [name.split('[')[1].split(']')[0] for name in section_name_list]
        return section_name_list, section_text_list

    # 查找ini文件中section下的所有options和options所在行
    @staticmethod
    def read_options(section_text):
        # 先获取所有有=的行
        option_pattern = re.compile(r'.+=.+\n')
        option_result = option_pattern.findall(section_text)
        # 去掉注释行
        valid_option_row = []
        valid_option = {}
        for option in option_result:
            if option.startswith(';') is False:
                valid_option_row.append(option)
                key, value = option.split('=')[0].strip(), option.split('=')[1].strip()
                valid_option[key] = value
        return valid_option, valid_option_row

    # 读出参数值
    def read_config_value(self, section, option):
        config_read = configparser.ConfigParser()
        config_read.read(self.file, encoding='utf-8')
        value = config_read.get(section, option)
        return value

    # 写入参数
    def write_config_value(self, section, option, value):
        # 获取sections名 & 每个section的文本
        section_name_list, section_text_list = self.read_sections()
        # 判断section是否存在(不在的话新建section)
        if section not in section_name_list:
            new_section_text = '[' + section + ']\n'
            new_section_text = new_section_text + option + ' = ' + value + '\n'
            file_text = ''.join(section_text_list) + new_section_text
        # 在的话直接在section中重写即可
        else:
            index = section_name_list.index(section)
            valid_option, valid_option_row = self.read_options(section_text_list[index])
            if option in valid_option.keys():
                for row in valid_option_row:
                    if row.startswith(option) is True:
                        new_row = option + ' = ' + value + '\n'
                        section_text_list[index] = section_text_list[index].replace(row, new_row)
            else:
                # 新建
                new_row = valid_option_row[-1] + option + ' = ' + value + '\n'
                section_text_list[index] = section_text_list[index].replace(valid_option_row[-1], new_row)
            file_text = ''.join(section_text_list)
        with open(self.file, 'w+', encoding='utf-8') as f:
            f.write(file_text)


if __name__ == '__main__':
    file_name = 'D:/Code/robot/config/config.ini'
    config = ConfigWithComment(file=file_name)
    config.write_config_value(section='test', option='启动/高德地图', value='2000')
    # config.write_config_value(section='back', option='laugh', value='2')
    # config.write_config_value(section='param', option='use_external_camera', value='False')
