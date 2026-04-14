import base64
import urllib
import requests


class IDCardOCR:
    """身份证识别"""
    API_KEY = "q422CYyVE2l8KlRA2BGsEmoU"  # 百度智能云API密钥
    SECRET_KEY = "hByljmVq2KO3SNxL0nXJD9gI8DNPvtz6"  # 百度智能云API密钥
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    class Payload:
        """请求参数"""

        def __init__(self):
            self.id_card_side = 'id_card_side=front'
            self.image = 'image='
            self.detect_ps = 'detect_ps=false'
            self.detect_risk = 'detect_risk=false'
            self.detect_quality = 'detect_quality=false'
            self.detect_photo = 'detect_photo=false'
            self.detect_card = 'detect_card=false'
            self.detect_direction = 'detect_direction=false'
            self.detect_screenshot = 'detect_screenshot=false'

        def set_image(self, image_base64: str):
            self.image = 'image=' + image_base64

        @property
        def get_payload(self) -> str:
            return '&'.join(self.__dict__.values())

    def __init__(self):
        # 请求地址
        self.url = "https://aip.baidubce.com/rest/2.0/ocr/v1/idcard?access_token=" + self.get_access_token()
        self.payload = self.Payload()

    def get_result(self, image_path: str):
        """获取图像识别结果"""
        self.payload.set_image(self.get_file_content_as_base64(image_path))
        payload = self.payload.get_payload
        response = requests.request("POST", self.url, headers=self.headers, data=payload.encode("utf-8"))

        response.encoding = "utf-8"
        return self.transformation_result(response.text)

    def transformation_result(self, result) -> dict | None:
        content = result.get("words_result", None)
        if content is not None:
            transformation_result = {
                '姓名': content['姓名']['words'],
                '性别': content['性别']['words'],
                '出生': content['出生']['words'],
                '民族': content['民族']['words'],
                '住址': content['住址']['words'],
                '公民身份号码': content['公民身份号码']['words'],
            }
            return transformation_result

    def get_file_content_as_base64(self, path, urlencoded=True):
        """
        获取文件base64编码
        :param path: 文件路径
        :param urlencoded: 是否对结果进行urlencoded
        :return: base64编码信息
        """
        with open(path, "rb") as f:
            content = base64.b64encode(f.read()).decode("utf8")
            if urlencoded:
                content = urllib.parse.quote_plus(content)
        return content

    def get_access_token(self):
        """
        使用 AK，SK 生成鉴权签名（Access Token）
        :return: access_token，或是None(如果错误)
        """
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": self.API_KEY, "client_secret": self.SECRET_KEY}
        return str(requests.post(url, params=params).json().get("access_token"))


if __name__ == '__main__':
    ocr = IDCardOCR()
    print(ocr.get_result(r"E:\user_file\download\IMG_20260326_151150.jpg"))
