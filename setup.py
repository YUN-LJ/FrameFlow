from setuptools import setup, find_packages

setup(
    name="Fun",
    version="1.5",
    author='LJ',
    author_email='3028405217@qq.com',
    packages=find_packages(),
    description="基础功能函数库 - 包含文件处理、图像处理、Qt组件等常用工具",
    long_description=open('README.md', encoding='utf-8').read() if __import__('os').path.exists('README.md') else "",
    long_description_content_type="text/markdown",
    python_requires=">=3.9",

    # 核心依赖（必须安装）
    install_requires=[
        # 图像处理
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",

        # Windows系统API
        "pywin32>=306",

        # Qt框架
        "PySide6>=6.5.0",
        "PySide6-Fluent-Widgets>=1.9.0",

        # 多屏幕支持
        "screeninfo>=0.8.0",

        # 系统监控
        "psutil>=5.9.0",

        # NTP时间同步
        "ntplib>=0.4.0",

        # 终端模拟
        "pywinpty>=3.0.3",

        # ANSI转HTML
        "ansi2html>=1.9.0",
    ],

    # 可选依赖（按需安装）
    extras_require={
        # 硬件监控功能（需要pythonnet和.NET运行时）
        "hardware": [
            "pythonnet>=3.0.0",
        ],
        # 完整功能（包含所有可选依赖）
        "full": [
            "pythonnet>=3.0.0",
        ],
    },

    # 包内的非Python文件
    package_data={
        "Fun": [
            "libs/*.dll",  # OpenHardwareMonitor相关DLL
            "libs/*.sys",  # 系统驱动文件
        ]
    },

    # 启用MANIFEST.in配置
    include_package_data=True,

    # 项目分类标签
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License",
    ],

    # 关键词
    keywords="utility tools image-processing qt-widgets windows",

    # 项目URL
    project_urls={
        "Bug Reports": "https://github.com/yourusername/AutoWallpaper/issues",
        "Source": "https://github.com/yourusername/AutoWallpaper",
    },
)
