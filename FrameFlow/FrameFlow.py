"""
name: 动态画框
func: 主要实现windows下更换壁纸功能
author:LJ
start_time: 2025/9/26
基于python3.12.9
"""
if __name__ == '__main__':
    import os, time, sys
    from Fun.Norm.file import del_file
    from pyside6_GUI import GUI
    from GlobalModule import data_manage, GlobalValue

    try:
        GUI.start_GUI()
    except Exception as e:
        print(e)
    finally:
        del_file(GlobalValue.image_cache_dir)
        data_manage.stop()
        sys.exit(0)
        time.sleep(5)
        os._exit(0)
