class PayloadBase():
    """请求调用时提供的请求体参数"""
    def __init__(self):
        self.image = 'image='

    def set_image(self, image_base64: str):
        self.image = 'image=' + image_base64

    @property
    def payload(self) -> str:
        """获取参数"""
        if self.image == 'image=':
            raise ValueError('请设置图片参数')
        return '&'.join(self.__dict__.values())
    