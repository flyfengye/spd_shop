import time
import os
import traceback
import xlrd
import xlwt
from xlutils.copy import copy


class FileAccess:
    def __init__(self):
        pass

    @staticmethod
    def save_text(file_path, content):
        """content: bytes 对象"""
        dir_path = os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content.decode('utf-8'))
        except Exception as e:
            print(e)
            try:
                with open(file_path, 'w', encoding='gbk') as f:
                    f.write(content.decode('gbk'))
            except Exception as e:
                print(e)
                with open(file_path, 'wb') as f:
                    f.write(content)

    @staticmethod
    def read_text(file_path):
        with open(file_path, 'rb') as f:
            return f.read()


class ExcelAccess:
    def __init__(self):
        pass

    @staticmethod
    def write_to_excel(dict_data, excel_path):

        data_all = xlrd.open_workbook(excel_path, formatting_info=True)
        sheet_0 = data_all.sheets()[0]
        rows = sheet_0.nrows
        cols = sheet_0.ncols
        wb = copy(data_all)
        wb_sheet_0 = wb.get_sheet(0)

        alignment = xlwt.Alignment()
        alignment.horz = 0x02  # 设置水平居中
        alignment.vert = 0x01  # 设置垂直居中
        style = xlwt.XFStyle()  # 创建样式
        style.alignment = alignment  # 给样式添加文字居中属性

        for i in range(0, cols):
            key = sheet_0.cell(0, i).value.strip()
            if not key:
                continue
            if key not in dict_data:
                continue
            wb_sheet_0.write(rows, i, dict_data[key], style)

        while True:
            try:
                wb.save(excel_path)
            except IOError:
                print("数据记录失败,请关闭excel!")
                time.sleep(10)
                continue
            except Exception as e:
                print("数据记录失败,其他错误!")
                print(traceback.format_exc())
                del e
            break
