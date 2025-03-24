import os
import subprocess
import sys

REQUIREMENTS_FILE = 'requirements.txt'

def install_dependencies():
    """自动安装项目依赖"""
    if not os.path.isfile(REQUIREMENTS_FILE):
        print(f"错误：依赖文件 {REQUIREMENTS_FILE} 未找到！")
        sys.exit(1)
    try:
        print("正在检查并安装依赖...")
        subprocess.check_call([
            sys.executable,  # 使用当前 Python 解释器
            '-m', 'pip', 'install',
            '-r', REQUIREMENTS_FILE
        ])
        print("依赖安装完成。")
    except subprocess.CalledProcessError as e:
        print(f"安装依赖失败，错误码：{e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"发生未知错误：{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    install_dependencies()
    # 此处导入项目主模块
    # from your_project import main_app
    # main_app.run()