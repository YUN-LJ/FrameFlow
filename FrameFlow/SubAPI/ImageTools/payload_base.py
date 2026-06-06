from typing import Type,Any
import base64

class PayloadBase():
    """请求调用时提供的请求体参数"""
    def __init__(self):
        self.image = 'image='

    def set_image(self, image_base64: str):
        self.image = 'image=' + image_base64

    @property
    def get_payload(self) -> str:
        """获取参数"""
        if self.image == 'image=':
            raise ValueError('请设置图片参数')
        return '&'.join(self.__dict__.values())
    


class PayloadBuilder:
    def __init__(self):
        self._payload_class = None
        self._image_path = None
        self._options = {}

    def set_type(self, payload_class: Type[BasePayload]):
        self._payload_class = payload_class
        return self

    def set_image(self, path: str):
        self._image_path = path
        return self

    def set_option(self, key: str, value: Any):
        self._options[key] = value
        return self

    def build(self) -> BasePayload:
        if not self._payload_class or not self._image_path:
            raise ValueError("需要指定 Payload 类型和图片路径")
        with open(self._image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode()
        return self._payload_class(image_base64, **self._options)