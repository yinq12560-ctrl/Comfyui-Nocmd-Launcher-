"""
ComfyUI 端口监视器

"""

import sys
import os
import time
import threading
import subprocess
import webbrowser
from pathlib import Path

# 获取当前脚本所在目录
BASE_PATH = Path(__file__).parent.absolute()
sys.path.insert(0, str(BASE_PATH))

# 配置
CHECK_INTERVAL = 5  # 检查间隔(秒)
SERVER_URL = "http://127.0.0.1:8188"
LOG_FILE = BASE_PATH / "comfyui_monitor.log"

class PortMonitor:
    def __init__(self):
        self.running = True
        self.current_status = "unknown"
        self.last_check_time = 0
        
        # 检查依赖
        if not self.check_dependencies():
            self.show_error("缺少必要依赖")
            sys.exit(1)
        
        # 导入图形库
        import pystray
        from PIL import Image, ImageDraw
        self.pystray = pystray
        self.Image = Image
        self.ImageDraw = ImageDraw
        
        # 创建托盘
        self.icon = self.create_icon("red")
        self.tray_icon = None
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        # 运行托盘
        self.run_tray()
    
    def log(self, message):
        """记录日志"""
        try:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\n")
        except:
            pass
    
    def check_dependencies(self):
        """检查依赖"""
        try:
            import pystray
            from PIL import Image
            return True
        except ImportError as e:
            self.log(f"缺少依赖: {e}")
            return False
    
    def check_port_8188(self):
        """检查端口8188是否被占用"""
        try:
            # 使用netstat检查端口
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # 查找端口8188
            for line in result.stdout.split('\n'):
                if ':8188' in line and 'LISTENING' in line:
                    return True
            
            return False
            
        except Exception as e:
            self.log(f"检查端口失败: {e}")
            return False
    
    def get_status(self):
        """获取当前状态 - 只有运行/停止"""
        port_occupied = self.check_port_8188()
        return "running" if port_occupied else "stopped"
    
    def create_icon(self, color):
        """创建托盘图标"""
        # 颜色映射
        colors = {
            "red": (255, 100, 100),      # 红色：停止
            "green": (100, 255, 100),    # 绿色：运行中
        }
        
        rgb = colors.get(color, colors["red"])
        
        image = self.Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = self.ImageDraw.Draw(image)
        
        # 外圆
        draw.ellipse([5, 5, 59, 59], fill=(*rgb, 200))
        
        # 内圆
        draw.ellipse([15, 15, 49, 49], fill=(*rgb, 255))
        
        # C字形状 (ComfyUI的C)
        draw.arc([20, 20, 44, 44], 45, 315, fill=(255, 255, 255, 255), width=4)
        
        # 根据状态添加不同标记
        if color == "green":
            # 运行中：中心加一个点
            draw.ellipse([30, 30, 34, 34], fill=(255, 255, 255, 255))
        
        return image
    
    def update_icon(self, status):
        """根据状态更新图标"""
        color_map = {
            "running": "green",
            "stopped": "red",
        }
        
        color = color_map.get(status, "red")
        new_icon = self.create_icon(color)
        
        if self.tray_icon:
            self.tray_icon.icon = new_icon
            
            # 更新提示文本
            status_text = {
                "running": "🟢 运行中",
                "stopped": "🔴 已停止",
            }
            
            self.tray_icon.title = f"ComfyUI\n{status_text.get(status, '未知')}\n端口: 8188"
    
    def monitor_loop(self):
        """监控主循环"""
        self.log("监控线程启动 - 简化版")
        
        while self.running:
            try:
                # 获取状态
                status = self.get_status()
                
                # 如果状态变化，更新图标
                if status != self.current_status:
                    self.log(f"状态变化: {self.current_status} -> {status}")
                    self.current_status = status
                    self.update_icon(status)
                
                # 记录检查时间
                self.last_check_time = time.time()
                
                # 等待
                for _ in range(CHECK_INTERVAL):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.log(f"监控循环错误: {e}")
                time.sleep(60)
        
        self.log("监控线程退出")
    
    def safe_start_comfyui(self):
        """安全启动ComfyUI"""
        try:
            self.log("执行安全启动")
            
            # 使用启动脚本 - 显示窗口以便调试
            start_bat = BASE_PATH / "启动器.bat"
            if start_bat.exists():
                self.log(f"使用启动脚本: {start_bat}")
                
                # 使用start命令打开新窗口，这样可以看到进度
                cmd = f'start "" cmd /c "{start_bat}"'  
                self.log(f"执行命令: {cmd}")
                
                subprocess.Popen(
                    cmd,
                    shell=True,
                    cwd=str(BASE_PATH)
                )
                return True
            else:
                self.log(f"启动脚本不存在: {start_bat}")
                return False
                
        except Exception as e:
            self.log(f"启动失败: {e}")
            import traceback
            self.log(f"详细错误: {traceback.format_exc()}")
            return False
    
    def safe_stop_comfyui(self):
        """安全停止ComfyUI"""
        try:
            self.log("执行安全停止")
            
            # 使用关闭脚本 - 显示窗口以便调试
            stop_bat = BASE_PATH / "关闭器.bat"
            if stop_bat.exists():
                self.log(f"使用关闭脚本: {stop_bat}")
                
                # 使用start命令打开新窗口，这样可以看到进度
                cmd = f'start "" cmd /k "{stop_bat}"'  # 使用/k保持窗口打开以便查看结果
                self.log(f"执行命令: {cmd}")
                
                subprocess.Popen(
                    cmd,
                    shell=True,
                    cwd=str(BASE_PATH)
                )
            else:
                self.log(f"关闭脚本不存在: {stop_bat}")
                # 直接终止端口
                self.log("直接清理端口")
                # 使用subprocess直接执行命令
                subprocess.run(
                    ["cmd", "/c", "netstat -ano | findstr :8188"],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                # 清理端口进程
                subprocess.run(
                    ["cmd", "/c", "for /f \"tokens=5\" %i in ('netstat -ano ^| findstr :8188') do taskkill /f /pid %i"],
                    shell=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
        except Exception as e:
            self.log(f"停止失败: {e}")
            import traceback
            self.log(f"详细错误: {traceback.format_exc()}")
    
    def show_error(self, message):
        """显示错误"""
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("ComfyUI监视器", message)
            root.destroy()
        except:
            pass
    
    def run_tray(self):
        """运行托盘图标"""
        # 创建菜单 - 使用 None 作为分隔线
        menu_items = [
            self.pystray.MenuItem("▶ 启动 ComfyUI", self.on_start),
            self.pystray.MenuItem("⏹ 停止 ComfyUI", self.on_stop),
            self.pystray.MenuItem("🌐 打开 Web 界面", self.on_open_web),
            self.pystray.MenuItem("📊 刷新状态", self.on_refresh),
            self.pystray.MenuItem("---", None),  # 分隔线
            self.pystray.MenuItem("📂 打开目录", self.on_open_dir),
            self.pystray.MenuItem("📝 查看日志", self.on_view_log),
            self.pystray.MenuItem("---", None),  # 分隔线
            self.pystray.MenuItem("⚙️ 检查依赖", self.on_check_deps),
            self.pystray.MenuItem("❌ 退出监视器", self.on_quit)
        ]
        
        menu = self.pystray.Menu(*menu_items)
        
        # 创建托盘图标
        self.tray_icon = self.pystray.Icon(
            "comfyui_port_monitor",
            self.icon,
            "ComfyUI监视器\n正在启动...",
            menu
        )
        
        # 初始状态检查
        initial_status = self.get_status()
        self.current_status = initial_status
        self.update_icon(initial_status)
        
        # 启动托盘
        self.log("启动托盘图标")
        self.tray_icon.run()
    
    # 菜单事件处理
    def on_start(self, icon, item):
        self.safe_start_comfyui()
    
    def on_stop(self, icon, item):
        self.safe_stop_comfyui()
    
    def on_open_web(self, icon, item):
        webbrowser.open(SERVER_URL)
    
    def on_refresh(self, icon, item):
        status = self.get_status()
        status_text = {
            "running": "🟢 运行中",
            "stopped": "🔴 已停止",
        }
        
        # 更新图标
        self.update_icon(status)
        
        # 显示通知
        try:
            import win10toast
            toaster = win10toast.ToastNotifier()
            toaster.show_toast(
                "ComfyUI 状态",
                status_text.get(status, "未知状态"),
                duration=2,
                threaded=True
            )
        except:
            pass
    
    def on_open_dir(self, icon, item):
        os.startfile(str(BASE_PATH))
    
    def on_view_log(self, icon, item):
        if LOG_FILE.exists():
            os.startfile(str(LOG_FILE))
    
    def on_check_deps(self, icon, item):
        try:
            import subprocess
            # 使用便携版Python安装依赖
            python_path = BASE_PATH / "python_embeded" / "python.exe"
            
            if python_path.exists():
                subprocess.run([
                    str(python_path), "-m", "pip", "install", 
                    "pystray", "Pillow", "requests", "win10toast"
                ], cwd=str(BASE_PATH), capture_output=True)
                
                # 提示
                try:
                    import win10toast
                    toaster = win10toast.ToastNotifier()
                    toaster.show_toast("ComfyUI监视器", "依赖检查完成", duration=3)
                except:
                    pass
        except Exception as e:
            self.log(f"检查依赖失败: {e}")
    
    def on_quit(self, icon, item):
        self.log("用户退出")
        self.running = False
        if self.tray_icon:
            self.tray_icon.stop()

def main():
    """主函数"""
    # 创建监视器
    monitor = PortMonitor()

if __name__ == "__main__":
    main()