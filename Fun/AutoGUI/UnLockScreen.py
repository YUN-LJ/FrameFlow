import sys
import os
import json
import threading
import time
from cryptography.fernet import Fernet
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QGroupBox, QTextEdit, QMessageBox, QSystemTrayIcon, 
                               QMenu, QCheckBox, QSpinBox, QStyle)
from PySide6.QtCore import QThread, Signal, Qt, QTimer
from PySide6.QtGui import QIcon, QAction, QPalette, QColor, QPainter
import pyautogui
import psutil
import ctypes
from ctypes import wintypes

class AutoLoginThread(QThread):
    """自动登录线程"""
    status_signal = Signal(str)
    login_attempt_signal = Signal(str)
    
    def __init__(self, password_manager, delay_seconds=10):
        super().__init__()
        self.password_manager = password_manager
        self.delay_seconds = delay_seconds
        self.running = True
        self.last_lock_state = False
        
    def run(self):
        self.status_signal.emit("自动登录监控已启动")
        
        while self.running:
            try:
                is_locked = self.is_workstation_locked()
                
                # 检测到从解锁变为锁定状态
                if is_locked and not self.last_lock_state:
                    self.status_signal.emit(f"检测到系统锁定，将在{self.delay_seconds}秒后自动登录")
                    self.perform_auto_login_after_delay()
                
                self.last_lock_state = is_locked
                time.sleep(2)  # 每2秒检查一次
                
            except Exception as e:
                self.status_signal.emit(f"监控错误: {str(e)}")
                time.sleep(5)
    
    def is_workstation_locked(self):
        """检查工作站是否锁定"""
        try:
            # 方法1: 检查logonui进程
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and 'logonui.exe' in proc.info['name'].lower():
                    return True
            
            # 方法2: 使用Windows API
            try:
                hwnd = ctypes.windll.user32.GetForegroundWindow()
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
                    window_title = buff.value
                    if "windows default lock screen" in window_title.lower():
                        return True
            except Exception:
                pass
                    
            return False
        except Exception:
            return False
    
    def perform_auto_login_after_delay(self):
        """延迟后执行自动登录"""
        time.sleep(self.delay_seconds)
        
        if not self.running:
            return
            
        current_password = self.password_manager.get_current_password()
        if current_password:
            self.status_signal.emit("正在执行自动登录...")
            self.login_attempt_signal.emit("自动登录尝试中")
            self.simulate_login(current_password)
        else:
            self.status_signal.emit("未找到存储的密码，无法自动登录")
    
    def simulate_login(self, password):
        """模拟登录输入"""
        try:
            # 输入密码
            pyautogui.write(password)
            time.sleep(0.5)
            pyautogui.press('enter')
            
            self.login_attempt_signal.emit("自动登录完成")
            self.status_signal.emit("自动登录执行完成")
            
        except Exception as e:
            error_msg = f"自动登录失败: {str(e)}"
            self.login_attempt_signal.emit(error_msg)
            self.status_signal.emit(error_msg)
    
    def stop(self):
        """停止线程"""
        self.running = False

class PasswordManager:
    """密码管理器"""
    def __init__(self, config_file="auto_login_config.json"):
        self.config_file = config_file
        self.key_file = "encryption.key"
        self.load_or_create_key()
        self.load_config()
    
    def load_or_create_key(self):
        """加载或创建加密密钥"""
        try:
            if os.path.exists(self.key_file):
                with open(self.key_file, 'rb') as f:
                    self.key = f.read()
            else:
                self.key = Fernet.generate_key()
                with open(self.key_file, 'wb') as f:
                    f.write(self.key)
            
            self.fernet = Fernet(self.key)
        except Exception as e:
            print(f"密钥处理错误: {e}")
            # 使用固定密钥作为备用方案（不推荐用于生产环境）
            self.key = b'default_key_32_bytes_long_123456789012'
            self.fernet = Fernet(Fernet.generate_key())
    
    def encrypt_password(self, password):
        """加密密码"""
        return self.fernet.encrypt(password.encode()).decode()
    
    def decrypt_password(self, encrypted_password):
        """解密密码"""
        try:
            return self.fernet.decrypt(encrypted_password.encode()).decode()
        except Exception:
            return None
    
    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {"password": None, "auto_start": False, "delay": 10}
        except Exception:
            self.config = {"password": None, "auto_start": False, "delay": 10}
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def set_password(self, password):
        """设置密码"""
        if password:
            encrypted = self.encrypt_password(password)
            self.config["password"] = encrypted
            return self.save_config()
        return False
    
    def get_current_password(self):
        """获取当前密码"""
        encrypted = self.config.get("password")
        if encrypted:
            return self.decrypt_password(encrypted)
        return None
    
    def clear_password(self):
        """清除密码"""
        self.config["password"] = None
        return self.save_config()

class AutoLoginWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.password_manager = PasswordManager()
        self.auto_login_thread = None
        self.init_ui()
        self.init_tray_icon()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("Windows自动登录工具")
        self.setGeometry(300, 300, 500, 600)
        
        # 设置深色主题
        self.set_dark_theme()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 密码设置组
        password_group = QGroupBox("密码设置")
        password_layout = QVBoxLayout()
        
        # 当前密码状态
        self.password_status_label = QLabel("状态: 未设置密码")
        password_layout.addWidget(self.password_status_label)
        
        # 密码输入
        password_input_layout = QHBoxLayout()
        password_input_layout.addWidget(QLabel("新密码:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_input_layout.addWidget(self.password_input)
        password_layout.addLayout(password_input_layout)
        
        # 确认密码
        confirm_layout = QHBoxLayout()
        confirm_layout.addWidget(QLabel("确认密码:"))
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        confirm_layout.addWidget(self.confirm_input)
        password_layout.addLayout(confirm_layout)
        
        # 密码操作按钮
        button_layout = QHBoxLayout()
        self.set_password_btn = QPushButton("设置密码")
        self.clear_password_btn = QPushButton("清除密码")
        self.test_login_btn = QPushButton("测试登录")
        
        self.set_password_btn.clicked.connect(self.set_password)
        self.clear_password_btn.clicked.connect(self.clear_password)
        self.test_login_btn.clicked.connect(self.test_login)
        
        button_layout.addWidget(self.set_password_btn)
        button_layout.addWidget(self.clear_password_btn)
        button_layout.addWidget(self.test_login_btn)
        password_layout.addLayout(button_layout)
        
        password_group.setLayout(password_layout)
        layout.addWidget(password_group)
        
        # 自动登录设置组
        auto_login_group = QGroupBox("自动登录设置")
        auto_login_layout = QVBoxLayout()
        
        # 延迟设置
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("锁定后延迟(秒):"))
        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setRange(5, 60)
        self.delay_spinbox.setValue(self.password_manager.config.get("delay", 10))
        self.delay_spinbox.valueChanged.connect(self.update_delay)
        delay_layout.addWidget(self.delay_spinbox)
        auto_login_layout.addLayout(delay_layout)
        
        # 自动启动控制
        control_layout = QHBoxLayout()
        self.start_monitor_btn = QPushButton("启动监控")
        self.stop_monitor_btn = QPushButton("停止监控")
        
        self.start_monitor_btn.clicked.connect(self.start_auto_login)
        self.stop_monitor_btn.clicked.connect(self.stop_auto_login)
        
        control_layout.addWidget(self.start_monitor_btn)
        control_layout.addWidget(self.stop_monitor_btn)
        auto_login_layout.addLayout(control_layout)
        
        auto_login_group.setLayout(auto_login_layout)
        layout.addWidget(auto_login_group)
        
        # 状态显示
        status_group = QGroupBox("状态信息")
        status_layout = QVBoxLayout()
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        self.status_display.setMaximumHeight(150)
        status_layout.addWidget(self.status_display)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # 登录尝试记录
        login_group = QGroupBox("登录尝试记录")
        login_layout = QVBoxLayout()
        self.login_display = QTextEdit()
        self.login_display.setReadOnly(True)
        self.login_display.setMaximumHeight(100)
        login_layout.addWidget(self.login_display)
        login_group.setLayout(login_layout)
        layout.addWidget(login_group)
        
        # 更新初始状态
        self.update_password_status()
        
    def set_dark_theme(self):
        """设置深色主题"""
        app.setStyle('Fusion')
        
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        app.setPalette(dark_palette)
        
    def create_tray_icon(self):
        """创建自定义托盘图标"""
        from PySide6.QtGui import QPixmap
        
        # 创建一个简单的图标
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(42, 130, 218))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 16, 16)
        
        painter.setBrush(Qt.white)
        painter.drawEllipse(4, 6, 2, 2)
        painter.drawEllipse(10, 6, 2, 2)
        painter.drawArc(4, 8, 8, 4, 0, 180 * 16)
        painter.end()
        
        return QIcon(pixmap)
        
    def init_tray_icon(self):
        """初始化系统托盘图标"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # 使用自定义图标而不是QStyle
        self.tray_icon.setIcon(self.create_tray_icon())
        
        tray_menu = QMenu()
        
        show_action = QAction("显示", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
        
    def tray_icon_activated(self, reason):
        """托盘图标激活处理"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.activateWindow()
            
    def update_password_status(self):
        """更新密码状态显示"""
        if self.password_manager.get_current_password():
            self.password_status_label.setText("状态: 密码已设置")
            self.start_monitor_btn.setEnabled(True)
            self.test_login_btn.setEnabled(True)
        else:
            self.password_status_label.setText("状态: 未设置密码")
            self.start_monitor_btn.setEnabled(False)
            self.test_login_btn.setEnabled(False)
            
    def set_password(self):
        """设置密码"""
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        if not password:
            QMessageBox.warning(self, "警告", "请输入密码")
            return
            
        if password != confirm:
            QMessageBox.warning(self, "警告", "两次输入的密码不一致")
            return
            
        if self.password_manager.set_password(password):
            QMessageBox.information(self, "成功", "密码设置成功")
            self.password_input.clear()
            self.confirm_input.clear()
            self.update_password_status()
            self.add_status_message("密码已更新")
        else:
            QMessageBox.critical(self, "错误", "密码设置失败")
            
    def clear_password(self):
        """清除密码"""
        reply = QMessageBox.question(self, "确认", "确定要清除密码吗？",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.password_manager.clear_password():
                self.update_password_status()
                self.add_status_message("密码已清除")
            else:
                QMessageBox.critical(self, "错误", "清除密码失败")
                
    def test_login(self):
        """测试登录功能"""
        if not self.password_manager.get_current_password():
            QMessageBox.warning(self, "警告", "请先设置密码")
            return
            
        reply = QMessageBox.question(self, "测试登录", 
                                   "这将模拟登录输入过程。请确保当前不在敏感界面。\n是否继续？",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.add_status_message("开始测试登录...")
            QTimer.singleShot(3000, self.simulate_test_login)  # 3秒后执行
            
    def simulate_test_login(self):
        """模拟测试登录"""
        try:
            password = self.password_manager.get_current_password()
            if password:
                # 模拟输入
                pyautogui.write("test_input")
                time.sleep(0.5)
                pyautogui.press('backspace', presses=10)  # 清除测试输入
                time.sleep(0.5)
                pyautogui.write(password)
                self.add_status_message("测试登录完成 - 密码已输入")
                self.add_login_message("测试登录执行完成")
            else:
                self.add_status_message("测试登录失败 - 未找到密码")
        except Exception as e:
            self.add_status_message(f"测试登录错误: {str(e)}")
            
    def update_delay(self, delay):
        """更新延迟时间"""
        self.password_manager.config["delay"] = delay
        self.password_manager.save_config()
        
    def start_auto_login(self):
        """启动自动登录监控"""
        if not self.password_manager.get_current_password():
            QMessageBox.warning(self, "警告", "请先设置密码")
            return
            
        if self.auto_login_thread and self.auto_login_thread.isRunning():
            QMessageBox.information(self, "信息", "监控已在运行中")
            return
            
        self.auto_login_thread = AutoLoginThread(
            self.password_manager, 
            self.delay_spinbox.value()
        )
        self.auto_login_thread.status_signal.connect(self.add_status_message)
        self.auto_login_thread.login_attempt_signal.connect(self.add_login_message)
        self.auto_login_thread.start()
        
        self.start_monitor_btn.setEnabled(False)
        self.stop_monitor_btn.setEnabled(True)
        
    def stop_auto_login(self):
        """停止自动登录监控"""
        if self.auto_login_thread:
            self.auto_login_thread.stop()
            self.auto_login_thread.wait(2000)  # 等待2秒
            self.auto_login_thread = None
            
        self.add_status_message("自动登录监控已停止")
        self.start_monitor_btn.setEnabled(True)
        self.stop_monitor_btn.setEnabled(False)
        
    def add_status_message(self, message):
        """添加状态消息"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_display.append(f"[{timestamp}] {message}")
        
    def add_login_message(self, message):
        """添加登录尝试消息"""
        timestamp = time.strftime("%H:%M:%S")
        self.login_display.append(f"[{timestamp}] {message}")
        
    def closeEvent(self, event):
        """关闭事件处理"""
        if self.auto_login_thread and self.auto_login_thread.isRunning():
            reply = QMessageBox.question(self, "确认退出", 
                                       "自动登录监控正在运行，确定要退出吗？",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.stop_auto_login()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
            
    def quit_application(self):
        """退出应用程序"""
        self.stop_auto_login()
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    window = AutoLoginWindow()
    window.show()
    
    sys.exit(app.exec())