from setuptools import setup, find_packages

setup(
    name="Fun",
    version="1.4",
    author='LJ',
    author_email='3028405217@qq.com',
    packages=find_packages(),
    description="基础功能函数",
    python_requires=">=3.9",
    # 指定依赖库，安装时会自动下载
    install_requires=[
        "psutil>=7.1.0",  # 可以指定版本号，>=表示最低版本要求
        "ntplib>=0.4.0",
        "pythonnet>=3.0.5",
        "matplotlib>=3.9.4",
        "opencv-python>=4.12.0.88",
    ],
    # 包内的依赖文件(相对路径)
    package_data={
        "Fun": [
            "libs/*.dll",  # 匹配DLL文件
        ]
    },
    include_package_data=True,  # 启用MANIFEST.in和package_data配置
)
