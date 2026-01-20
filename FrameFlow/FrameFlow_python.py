from Fun.Norm import general

# 隐藏python解释器
general.hide_python_console()

import os, sys
from FrameFlow.pyside6_GUI import GUI  # 导入FrameFlow.py的依赖


def run_FrameFlow():
    # 1. 定位 FrameFlow.py 的路径（打包后仍能找到）
    current_dir = os.path.dirname(sys.argv[0])
    target_file = os.path.join(current_dir, "FrameFlow.py")

    # 2. 验证文件是否存在（避免打包后路径问题）
    if not os.path.exists(target_file):
        print(f"错误：未找到 {target_file}")
        return False

    # 3. 关键：读取 FrameFlow.py 的源码，在主进程中执行
    # 相当于把 FrameFlow.py 的代码“嵌入”主进程运行，共享同一个解释器
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            # 执行源码（__file__ 会自动指向 be_called.py，保持原脚本逻辑）
            exec(compile(f.read(), target_file, "exec"), globals(), locals())
        return True
    except Exception as e:
        print(f"执行 be_called.py 失败：{e}")
        return False


if __name__ == "__main__":
    print("主脚本启动（使用内置解释器）...")
    success = run_FrameFlow()
    if success:
        print("FrameFlow.py 执行成功!")
    else:
        print("执行失败")
        input("按回车退出...")
