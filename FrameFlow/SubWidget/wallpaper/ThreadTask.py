"""后台任务线程"""
from pyside6_GUI.sub_ui.wallpaper.widgetUI.Config import *


class ThreadTask(QThread):
    """多任务后台线程"""
    # 任务枚举值
    LOADUI = 'loadui'  # UI加载任务->loadui
    LOADTHUMB = 'loadthumb'  # 略缩图加载任务
    task_enum = [LOADUI]

    # 任务信号
    start = Signal(tuple)  # 任务开始信号(任务名称,任务枚举值)
    finished = Signal(tuple)  # 任务结束信号(任务名称,任务枚举值,任务是否成功)
    done = Signal(tuple)  # 任务进行信号(任务名称,任务枚举值,一些描述任务进度的参数)

    def __init__(self, wallpaper_play: WallPaperPlay, parent, num_work=2):
        super().__init__()
        self.num_work = num_work
        self.parent = parent
        self.isRunning = False
        self.wallpaper_play = wallpaper_play
        self.task_dict = Dict()  # 任务字典{任务枚举值:[]}
        self.task_queue = Queue()  # 任务队列

    def add_task(self, task_name, task_enum, task_args):
        """提交任务(任务名称,任务枚举值,任务所需参数)"""
        try:
            with self.task_dict.get_lock:
                enum_list = self.task_dict.get_dict.get(task_enum, None)
                if enum_list is None:
                    self.task_dict.get_dict[task_enum] = List(initial_data=[task_name])
                    self.task_queue.put((task_name, task_enum, task_args))
                else:
                    if task_name not in enum_list:
                        enum_list.append(task_name)
                        self.task_queue.put((task_name, task_enum, task_args))
            if not self.isRunning:
                self.start()
        except Exception as e:
            print(f'{self.__class__.__name__}.add_task({task_name}) error: {e}')

    def task_load_thumb(self, task_name: str, image_list: list):
        """
        加载略缩图任务
        :param task_name: 任务名称
        :param image_list:[(key,path)]
        """

        def callback():
            nonlocal thumb_progress
            while self.isRunning and thumb_progress.isRunning:
                result = thumb_progress.get_result()
                if result:
                    self.finished.emit((task_name, self.LOADTHUMB, (True, result)))
            thumb_progress.stop()
            if self.task_dict.get(self.LOADTHUMB, None):
                self.task_dict[self.LOADTHUMB].remove(task_name)

        thumb_progress = ThumbProgress(image_list)
        thumb_progress.start()
        Thread(target=callback).start()

    def task_load_ui(self):
        """后台加载UI资源"""
        if file.check_exist(WallHavenAPI.key_word_path):
            for _ in range(100):
                if self.isRunning:
                    if self.wallpaper_play.get_keys():
                        self.finished_task(self.LOADUI, self.LOADUI, True)
                        break
                    time.sleep(1)
                else:
                    break
            else:
                self.finished_task(self.LOADUI, self.LOADUI, False)

    def cancel_task(self, task_name: str | list):
        """
        删除任务
        :param task_name: 任务名称
        """
        if task_name in self.task_enum:
            task_name = self.task_dict.pop(task_name, None)

    def start_task(self, task_name, task_enum):
        self.start.emit((task_name, task_enum))

    def finished_task(self, task_name, task_enum, state, data=None):
        """任务成功后发射信号"""
        if self.task_dict.get(task_enum, None):
            self.task_dict[task_enum].remove(task_name)
        self.finished.emit((task_name, task_enum, (state, data)))

    def stop(self):
        self.isRunning = False
        self.wait()

    def run(self):
        self.isRunning = True
        while self.isRunning:
            try:
                task_name, task_enum, task_args = self.task_queue.get(timeout=1)
                if task_enum == self.LOADUI:
                    Thread(target=self.task_load_ui).start()
                elif task_enum == self.LOADTHUMB:
                    self.task_load_thumb(task_name, task_args)
            except Empty:
                pass


class ThumbProgress:
    """略缩图处理类"""

    def __init__(self, image_list: list):
        """
        :param image_list:待处理的图像路径
        """
        self.isRunning = False
        self.image_list = image_list
        self.result_queue = Queue()
        self.task_count = len(image_list)  # 总任务数量
        self.finished_count = 0  # 当前完成数量
        self.process = Process(target=self.execute_thread, args=(self.image_list,))

    def execute(self, value: tuple):
        """处理图片的略缩图"""
        key, image_path = value
        if os.path.isdir(image_path):
            image_list = file.get_files_path(image_path, only_file=True, ext=file.IMAGE_EXTENSION)
            image = Image_PIL(random.choice(image_list))
            image.resize(THUMB_SIZE, stretch=Image_Enum.resize_cut)
            self.result_queue.put((key, (len(image_list), image.get_BytesIO)))
        else:
            image = Image_PIL(image_path)
            image.resize(THUMB_SIZE, stretch=Image_Enum.resize_cut)
            self.result_queue.put((key, image.get_BytesIO))

    def execute_thread(self, image_list: list):
        """多线程处理略缩图"""
        if len(image_list) <= 10:
            for image_path in image_list:
                self.execute(image_path)
        else:
            thread_pool = ThreadPoolExecutor(max_workers=4)
            for image_path in image_list:
                thread_pool.submit(self.execute, image_path)

    def get_result(self):
        try:
            result = self.result_queue.get(timeout=1)
            self.finished_count += 1
            if self.finished_count >= self.task_count:
                self.stop()
            return result
        except Empty:
            pass

    def start(self):
        if not self.isRunning:
            self.isRunning = True
            self.process.start()  # 创建多进程

    def stop(self):
        if self.isRunning:
            self.isRunning = False
            self.process.kill()
