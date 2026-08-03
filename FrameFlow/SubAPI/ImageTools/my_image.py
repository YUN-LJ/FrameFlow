from io import BytesIO
from openpyxl.drawing.image import Image

try:
    from PIL import Image as PILImage
except ImportError:
    PILImage = False


def _import_image(img):
    if not PILImage:
        raise ImportError('You must install Pillow to fetch image objects')

    if not isinstance(img, PILImage.Image):
        img = PILImage.open(img)

    return img

class MyImage(Image):
    """Image in a spreadsheet"""

    _id = 1
    _path = "/xl/media/image{0}.{1}"
    anchor = "A1"

    def __init__(self, img):

        self.ref = img
        mark_to_close = isinstance(img, str)
        image = _import_image(img)
        self.width, self.height = image.size

        try:
            self.format = image.format.lower()
        except AttributeError:
            self.format = "png"
        self._cached_data = self._extract_image_data(image)
        
        if mark_to_close:
            # PIL instances created for metadata should be closed.
            image.close()

    def _extract_image_data(self,image):
        if self.format in ['gif', 'jpeg', 'png']:
            try:
                fp = image.fp
                # 记录当前指针位置
                pos = fp.tell() if hasattr(fp, 'tell') else 0
                fp.seek(0)
                data = fp.read()
                # 恢复指针位置，避免干扰后续可能的操作（例如 _data() 中的 seek(0)）
                fp.seek(pos)
                return data
            except (AttributeError, OSError, ValueError):
                # 如果 fp 不可用或不支持 seek，回退为 PNG 编码
                pass

        # 其他格式或回退方案：将图像保存为 PNG 到内存
        with BytesIO() as buf:
            image.save(buf, format="png")
            return buf.getvalue()
    def mygetdata(self):
        """外部调用的数据获取接口，不会触发任何 close()"""
        if not hasattr(self, '_cached_data'):
            # 惰性加载（例如未在 __init__ 中成功缓存时）
            image = _import_image(self.ref)
            try:
                self._cached_data = self._extract_image_data(image)
            finally:
                if isinstance(self.ref, str):
                    image.close()
        return self._cached_data

    def _data(self):
        """
        Return image data, convert to supported types if necessary
        """
        img = _import_image(self.ref)
        # don't convert these file formats
        if self.format in ['gif', 'jpeg', 'png']:
            img.fp.seek(0)
            fp = img.fp
        else:
            fp = BytesIO()
            img.save(fp, format="png")
            fp.seek(0)

        data = fp.read()
        fp.close()
        return data


    @property
    def path(self):
        return self._path.format(self._id, self.format)