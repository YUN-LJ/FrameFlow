"""
name: 动态画框
func: 主要实现windows下更换壁纸功能
author:LJ
start_time: 2025/9/26
基于python3.12.9
"""
if __name__ == '__main__':
    import model,time
    start = time.time()
    data = model.Data.get_new_data()
    print(data.head())
    print(data.loc[0],'测试分支test')
    print('执行时间',time.time()-start)