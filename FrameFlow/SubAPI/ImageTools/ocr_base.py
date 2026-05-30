# r\FrameFlow(PROJECT_ROOT)\FrameFlow\SubAPI\ImageTools\ocr_base.py


# 方案二：参数化任务执行器（推荐，适合生产环境）
# 思路：把每次调用封装成一个轻量级任务，使用线程池/协程池并发执行，并加入重试、日志、结果收集。

# 示例（Python + concurrent.futures）：

# python
# from concurrent.futures import ThreadPoolExecutor, as_completed

# def call_api_with_id(item_id):
#     payload = {"base": "fixed", "changing_attr": item_id}
#     # 实际请求逻辑（含超时、重试）
#     return requests.post(url, json=payload).json()

# ids = [1, 2, 3, 4, 5]
# with ThreadPoolExecutor(max_workers=5) as executor:
#     future_to_id = {executor.submit(call_api_with_id, id): id for id in ids}
#     for future in as_completed(future_to_id):
#         try:
#             result = future.result()
#             # 收集结果或写入队列
#         except Exception as e:
#             log_error(e)


    



            