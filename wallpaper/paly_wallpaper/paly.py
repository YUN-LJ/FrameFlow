"""壁纸播放模块"""
if __name__ == '__main__':
    import model, time

    start = time.time()
    data = model.Data.get_new_data()
    print(data.head())
    print(data.loc[0])
    print('执行时间', time.time() - start)
