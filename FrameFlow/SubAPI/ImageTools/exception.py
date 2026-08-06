class BaiduAPIException(Exception):
    """所有百度API相关的异常的基类"""
    pass


class NetworkError(BaiduAPIException):
    """网络请求失败(HTTP状态码非2xx)"""
    pass


class APIError(BaiduAPIException):
    """百度API返回错误码"""
    def __init__(self, error_code:str,error_msg:str):
        self.error_code = error_code
        self.error_msg = error_msg
        super().__init__(f"API error {error_code}: {error_msg}")