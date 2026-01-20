"""
name: 动态画框
func: 主要实现windows下更换壁纸功能
author:LJ
start_time: 2025/9/26
基于python3.12.9
"""
if __name__ == '__main__':
    from Fun.Norm import general

    # # 隐藏python解释器
    # general.hide_python_console()
    # try:

    from pyside6_GUI import GUI

    GUI.start_GUI()
    # except Exception as e:
    #     general.show_python_console()
    #     print(e)
    #     input('请输入任意键退出...')
    #     exit()
