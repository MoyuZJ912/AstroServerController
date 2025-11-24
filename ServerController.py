import socket
import json
import time
import threading
from contextlib import contextmanager

class ServerController:
    """完整的服务器控制器 - 基于AstroLauncher的RCON实现"""
    
    def __init__(self):
        self.rcon = None
        self.connected = False
        self.server_ip = ""
        self.server_port = 0
        self.password = ""
        self.lock = False
        
    @contextmanager
    def lock_rcon(self):
        """RCON命令锁 - 防止并发冲突"""
        try:
            while self.lock:
                time.sleep(0.01)
            self.lock = True
            yield self
        finally:
            self.lock = False
    
    def connect_to_server(self, ip, port, password):
        """连接到服务器RCON"""
        try:
            self.server_ip = ip
            self.server_port = port
            self.password = password
            
            # 创建socket连接
            self.rcon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.rcon.settimeout(10)  # 10秒超时
            
            print(f"正在连接到 {ip}:{port}...")
            self.rcon.connect((ip, port))
            
            # 发送认证密码
            with self.lock_rcon():
                self.rcon.sendall(f"{password}\n".encode())
                time.sleep(0.5)  # 等待认证
            
            # 测试连接
            test_result = self.send_command("Help")
            if test_result and "error" not in str(test_result).lower():
                self.connected = True
                print("✅ 连接成功！")
                return True
            else:
                print("❌ 认证失败，请检查密码")
                self.rcon.close()
                return False
                
        except socket.timeout:
            print("❌ 连接超时，请检查服务器地址和端口")
            return False
        except ConnectionRefusedError:
            print("❌ 连接被拒绝，请检查服务器是否运行且RCON已启用")
            return False
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    def send_command(self, command, timeout=5):
        """发送RCON命令到服务器"""
        if not self.connected or not self.rcon:
            return "未连接到服务器"
        
        try:
            with self.lock_rcon():
                # 发送命令
                full_command = f"{command}\n"
                self.rcon.sendall(full_command.encode())
                
                # 接收响应
                raw_data = self.recv_all(timeout)
                parsed_data = self.parse_response(raw_data)
                
                return parsed_data
                
        except Exception as e:
            return f"命令发送失败: {e}"
    
    def recv_all(self, timeout=5):
        """接收所有响应数据 - 基于AstroRCON的实现"""
        try:
            self.rcon.settimeout(timeout)
            BUFF_SIZE = 4096
            data = b''
            
            while True:
                part = self.rcon.recv(BUFF_SIZE)
                data += part
                if len(part) < BUFF_SIZE:
                    break
                    
            return data
        except socket.timeout:
            return "超时".encode('utf-8')
        except Exception:
            return "接收错误".encode('utf-8')
    
    def parse_response(self, raw_data):
        """解析响应数据 - 基于AstroRCON的实现"""
        try:
            if raw_data and raw_data != b"":
                raw_data = raw_data.rstrip()
                # 尝试解析JSON
                return json.loads(raw_data.decode())
        except:
            # 如果不是JSON，返回原始文本
            return raw_data.decode('utf-8', errors='ignore') if raw_data else "无响应"
        return "无响应"
    
    def disconnect(self):
        """断开连接"""
        if self.rcon:
            self.rcon.close()
        self.connected = False
        self.rcon = None
        print("🔌 已断开连接")
    
    # 预定义命令方法 - 基于AstroLauncher的实现
    def get_player_list(self):
        """获取玩家列表"""
        return self.send_command("DSListPlayers")
    
    def get_server_stats(self):
        """获取服务器统计信息"""
        return self.send_command("DSServerStatistics")
    
    def get_save_games(self):
        """获取存档列表"""
        return self.send_command("DSListGames")
    
    def save_game(self, save_name=None):
        """保存游戏"""
        if save_name:
            return self.send_command(f"DSSaveGame {save_name}")
        else:
            return self.send_command("DSSaveGame")
    
    def broadcast_message(self, message):
        """广播消息"""
        return self.send_command(f"Broadcast {message}")
    
    def shutdown_server(self, delay=0, message=""):
        """关闭服务器"""
        if message:
            return self.send_command(f"Shutdown {delay} {message}")
        else:
            return self.send_command("Shutdown")
    
    def kick_player(self, player_guid):
        """踢出玩家"""
        return self.send_command(f"DSKickPlayerGuid {player_guid}")
    
    def create_new_game(self):
        """创建新游戏"""
        return self.send_command("DSNewGame")
    
    def set_player_category(self, player_name, category):
        """设置玩家权限类别"""
        return self.send_command(f"SetPlayerCategoryForPlayerName {player_name} {category}")
    
    def ban_player(self, player_name):
        """封禁玩家"""
        return self.set_player_category(player_name, "Blacklisted")
    
    def whitelist_player(self, player_name):
        """将玩家加入白名单"""
        return self.set_player_category(player_name, "Whitelisted")
    
    def set_admin(self, player_name):
        """给予玩家管理员权限"""
        return self.set_player_category(player_name, "Admin")
    
    def load_save(self, save_name):
        """加载指定存档"""
        return self.send_command(f"LoadGame {save_name}")
    
    def rename_save(self, old_name, new_name):
        """重命名存档"""
        return self.send_command(f"DSRenameGame {old_name} {new_name}")
    
    def delete_save(self, save_name):
        """删除存档"""
        return self.send_command(f"DSDeleteGame {save_name}")
    
    def set_save_interval(self, milliseconds):
        """设置自动保存间隔"""
        return self.send_command(f"DSSetAutoSaveInterval {milliseconds}")
    
    def enable_whitelist(self, enable):
        """启用或禁用白名单"""
        return self.send_command(f"DSSetWhitelistEnabled {1 if enable else 0}")

class ControllerInterface:
    """控制器用户界面"""
    
    def __init__(self):
        self.controller = ServerController()
        self.running = True
    
    def clear_screen(self):
        """清屏"""
        print("\n" * 50)
    
    def show_banner(self):
        """显示横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    ASTRONEER 服务器控制器                      ║
║                 十分感谢 AstroLauncher RCON                   ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def get_connection_info(self):
        """获取连接信息"""
        self.clear_screen()
        self.show_banner()
        
        print("请输入服务器连接信息：")
        print("-" * 50)
        
        # 获取服务器IP
        while True:
            ip = input("服务器IP地址 (默认: 127.0.0.1): ").strip()
            if not ip:
                ip = "127.0.0.1"
            if self.is_valid_ip(ip):
                break
            print("❌ 无效的IP地址，请重新输入")
        
        # 获取端口
        while True:
            port_str = input("RCON端口 (默认: 25575): ").strip()
            if not port_str:
                port = 25575
            else:
                try:
                    port = int(port_str)
                    if 1 <= port <= 65535:
                        break
                    else:
                        print("❌ 端口号必须在1-65535之间")
                except ValueError:
                    print("❌ 请输入有效的端口号")
        
        # 获取密码
        password = input("RCON密码: ").strip()
        if not password:
            print("❌ 密码不能为空")
            return False
        
        return ip, port, password
    
    def is_valid_ip(self, ip):
        """验证IP地址格式"""
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False
    
    def show_control_panel(self):
        """显示控制面板"""
        self.clear_screen()
        self.show_banner()
        
        print(f"📍 已连接到: {self.controller.server_ip}:{self.controller.server_port}")
        print("=" * 60)
        
        menu_items = [
            ("1", "📊 服务器状态", self.show_server_status),
            ("2", "👥 玩家列表", self.show_player_list),
            ("3", "💾 存档列表", self.show_save_games),
            ("4", "💾 保存游戏", self.save_current_game),
            ("5", "📢 广播消息", self.broadcast_message),
            ("6", "🆕 创建新游戏", self.create_new_game),
            ("7", "👢 踢出玩家", self.kick_player),
            ("8", "� 封禁玩家", self.ban_player),
            ("9", "✅ 白名单玩家", self.whitelist_player),
            ("10", "👑 设置管理员", self.set_admin),
            ("11", "�🔄 切换存档", self.switch_save),
            ("12", "🔄 重启服务器", self.restart_server),
            ("13", "⏹️  关闭服务器", self.shutdown_server),
            ("0", "🔌 断开连接", self.disconnect),
            ("help", "❓ 显示帮助", self.show_help),
            ("clear", "🧹 清屏", self.clear_screen)
        ]
        
        print("可用命令:")
        print("-" * 40)
        for key, description, _ in menu_items:
            print(f"  {key:6} - {description}")
        print("-" * 40)
    
    def show_server_status(self):
        """显示服务器状态"""
        print("\n🔄 获取服务器状态中...")
        stats = self.controller.get_server_stats()
        
        print("\n📊 服务器状态:")
        print("-" * 30)
        if isinstance(stats, dict):
            for key, value in stats.items():
                print(f"  {key}: {value}")
        else:
            print(f"  {stats}")
    
    def show_player_list(self):
        """显示玩家列表"""
        print("\n🔄 获取玩家列表中...")
        players = self.controller.get_player_list()
        
        print("\n👥 在线玩家:")
        print("-" * 40)
        if isinstance(players, dict) and 'playerInfo' in players:
            online_players = [p for p in players['playerInfo'] if p.get('inGame', False)]
            if online_players:
                for i, player in enumerate(online_players, 1):
                    name = player.get('playerName', '未知')
                    guid = player.get('playerGuid', '未知')[:8] + "..."
                    print(f"  {i}. {name} (GUID: {guid})")
            else:
                print("  🎯 没有在线玩家")
        else:
            print(f"  ❌ 获取玩家列表失败: {players}")
    
    def show_save_games(self):
        """显示存档列表"""
        print("\n🔄 获取存档列表中...")
        saves = self.controller.get_save_games()
        
        print("\n💾 存档列表:")
        print("-" * 50)
        if isinstance(saves, dict) and 'gameList' in saves:
            for i, save in enumerate(saves['gameList'], 1):
                name = save.get('name', '未知')
                date = save.get('date', '未知日期')
                active = " ✅ 当前存档" if save.get('name') == saves.get('activeSaveName') else ""
                print(f"  {i}. {name} - {date}{active}")
        else:
            print(f"  ❌ 获取存档列表失败: {saves}")
    
    def save_current_game(self):
        """保存当前游戏"""
        save_name = input("输入存档名称 (直接回车使用默认名称): ").strip()
        print("\n💾 保存游戏中...")
        
        if save_name:
            result = self.controller.save_game(save_name)
        else:
            result = self.controller.save_game()
        
        if result and "error" not in str(result).lower():
            print("✅ 游戏保存成功！")
        else:
            print(f"❌ 保存失败: {result}")
    
    def broadcast_message(self):
        """广播消息"""
        message = input("请输入要广播的消息: ").strip()
        if not message:
            print("❌ 消息不能为空")
            return
        
        print(f"\n📢 发送广播: {message}")
        result = self.controller.broadcast_message(message)
        
        if result and "error" not in str(result).lower():
            print("✅ 广播发送成功！")
        else:
            print(f"❌ 广播发送失败: {result}")
    
    def create_new_game(self):
        """创建新游戏"""
        confirm = input("⚠️  确定要创建新游戏吗？当前进度将丢失！(y/N): ").strip().lower()
        if confirm == 'y':
            print("\n🆕 创建新游戏中...")
            result = self.controller.create_new_game()
            if result and "error" not in str(result).lower():
                print("✅ 新游戏创建成功！")
            else:
                print(f"❌ 创建失败: {result}")
        else:
            print("❌ 操作已取消")
    
    def kick_player(self):
        """踢出玩家"""
        self.show_player_list()
        player_guid = input("\n请输入要踢出玩家的GUID: ").strip()
        if not player_guid:
            print("❌ GUID不能为空")
            return
        
        print(f"\n👢 踢出玩家 {player_guid}...")
        result = self.controller.kick_player(player_guid)
        
        if result and "error" not in str(result).lower():
            print("✅ 玩家已被踢出！")
        else:
            print(f"❌ 踢出失败: {result}")
    
    def restart_server(self):
        """重启服务器"""
        delay = input("重启延迟时间(秒，默认10): ").strip()
        message = input("重启消息 (直接回车跳过): ").strip()
        
        try:
            delay = int(delay) if delay else 10
        except:
            delay = 10
        
        print(f"\n🔄 准备重启服务器...")
        result = self.controller.shutdown_server(delay, message)
        
        if result and "error" not in str(result).lower():
            print("✅ 重启命令已发送！")
        else:
            print(f"❌ 重启命令发送失败: {result}")
    
    def shutdown_server(self):
        """关闭服务器"""
        confirm = input("⚠️  确定要关闭服务器吗？(y/N): ").strip().lower()
        if confirm == 'y':
            delay = input("关闭延迟时间(秒，默认10): ").strip()
            message = input("关闭消息 (直接回车跳过): ").strip()
            
            try:
                delay = int(delay) if delay else 10
            except:
                delay = 10
            
            print(f"\n⏹️  准备关闭服务器...")
            result = self.controller.shutdown_server(delay, message)
            
            if result and "error" not in str(result).lower():
                print("✅ 服务器关闭命令已发送！")
                # 给服务器关闭留出时间
                time.sleep(delay + 2)
                self.disconnect()
            else:
                print(f"❌ 关闭失败: {result}")
        else:
            print("❌ 操作已取消")
    
    def ban_player(self):
        """封禁玩家"""
        self.show_player_list()
        player_name = input("\n请输入要封禁的玩家名称: ").strip()
        if not player_name:
            print("❌ 玩家名称不能为空")
            return
        
        print(f"\n🚫 封禁玩家 {player_name}...")
        result = self.controller.ban_player(player_name)
        
        if result and "error" not in str(result).lower():
            print("✅ 玩家已被封禁！")
        else:
            print(f"❌ 封禁失败: {result}")
    
    def whitelist_player(self):
        """将玩家加入白名单"""
        player_name = input("请输入要加入白名单的玩家名称: ").strip()
        if not player_name:
            print("❌ 玩家名称不能为空")
            return
        
        print(f"\n✅ 将玩家 {player_name} 加入白名单...")
        result = self.controller.whitelist_player(player_name)
        
        if result and "error" not in str(result).lower():
            print("✅ 玩家已被加入白名单！")
        else:
            print(f"❌ 操作失败: {result}")
    
    def set_admin(self):
        """给予玩家管理员权限"""
        self.show_player_list()
        player_name = input("\n请输入要给予管理员权限的玩家名称: ").strip()
        if not player_name:
            print("❌ 玩家名称不能为空")
            return
        
        print(f"\n👑 给予玩家 {player_name} 管理员权限...")
        result = self.controller.set_admin(player_name)
        
        if result and "error" not in str(result).lower():
            print("✅ 玩家已获得管理员权限！")
        else:
            print(f"❌ 操作失败: {result}")
    
    def switch_save(self):
        """切换存档"""
        self.show_save_games()
        save_name = input("\n请输入要切换的存档名称: ").strip()
        if not save_name:
            print("❌ 存档名称不能为空")
            return
        
        confirm = input(f"⚠️  确定要切换到存档 '{save_name}' 吗？当前未保存的进度将丢失！(y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ 操作已取消")
            return
        
        print(f"\n🔄 切换到存档 {save_name}...")
        result = self.controller.load_save(save_name)
        
        if result and "error" not in str(result).lower():
            print("✅ 存档切换成功！")
        else:
            print(f"❌ 切换失败: {result}")
    
    def disconnect(self):
        """断开连接"""
        self.controller.disconnect()
        self.running = False
    
    def show_help(self):
        """显示帮助"""
        print("""
///
        """)
        input("\n按回车键继续...")
    
    def process_command(self, command):
        """处理用户命令"""
        command_map = {
            '1': self.show_server_status,
            '2': self.show_player_list,
            '3': self.show_save_games,
            '4': self.save_current_game,
            '5': self.broadcast_message,
            '6': self.create_new_game,
            '7': self.kick_player,
            '8': self.ban_player,
            '9': self.whitelist_player,
            '10': self.set_admin,
            '11': self.switch_save,
            '12': self.restart_server,
            '13': self.shutdown_server,
            '0': self.disconnect,
            'help': self.show_help,
            'clear': self.clear_screen,
            'disconnect': self.disconnect
        }
        
        if command in command_map:
            try:
                command_map[command]()
            except Exception as e:
                print(f"❌ 执行命令时出错: {e}")
        else:
            print("❌ 未知命令，输入 'help' 查看帮助")
    
    def run(self):
        """运行控制器"""
        try:
            # 获取连接信息
            connection_info = self.get_connection_info()
            if not connection_info:
                return
            
            ip, port, password = connection_info
            
            # 尝试连接
            if not self.controller.connect_to_server(ip, port, password):
                input("\n按回车键退出...")
                return
            
            # 主循环
            while self.running and self.controller.connected:
                try:
                    self.show_control_panel()
                    command = input("\n请输入命令编号: ").strip().lower()
                    
                    if command in ['quit', 'exit', '0', 'disconnect']:
                        self.disconnect()
                        break
                    
                    self.process_command(command)
                    
                    if self.running and self.controller.connected:
                        input("\n按回车键继续...")
                        
                except KeyboardInterrupt:
                    print("\n\n⚠️  检测到中断信号...")
                    confirm = input("确定要退出吗？(y/N): ").strip().lower()
                    if confirm == 'y':
                        self.disconnect()
                        break
                except Exception as e:
                    print(f"❌ 发生错误: {e}")
                    input("\n按回车键继续...")
            
        except Exception as e:
            print(f"❌ 程序运行出错: {e}")
        
        finally:
            if self.controller.connected:
                self.controller.disconnect()
            print("\n👋 感谢使用ASTRONEER服务器控制器！")

def main():
    """主函数"""
    controller = ControllerInterface()
    controller.run()

if __name__ == "__main__":
    main()