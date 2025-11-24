from flask import Flask, render_template, request, jsonify, session
import threading
import time
import json

# 导入现有的ServerController类
from ServerController import ServerController

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于会话管理

# 全局服务器控制器实例
server_controller = ServerController()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/connect', methods=['POST'])
def connect():
    data = request.json
    ip = data.get('ip')
    port = data.get('port')
    password = data.get('password')
    
    try:
        port = int(port)
    except ValueError:
        return jsonify({'status': 'error', 'message': '端口必须是数字'})
    
    if not ip or not port or not password:
        return jsonify({'status': 'error', 'message': '请填写完整的连接信息'})
    
    # 连接到服务器
    result = server_controller.connect_to_server(ip, port, password)
    
    if result:
        session['connected'] = True
        return jsonify({'status': 'success', 'message': '连接成功'})
    else:
        return jsonify({'status': 'error', 'message': '连接失败，请检查服务器信息和密码'})

@app.route('/disconnect')
def disconnect():
    server_controller.disconnect()
    session.pop('connected', None)
    return jsonify({'status': 'success', 'message': '已断开连接'})

@app.route('/status')
def status():
    return jsonify({'connected': server_controller.connected})

@app.route('/command', methods=['POST'])
def execute_command():
    if not server_controller.connected:
        return jsonify({'status': 'error', 'message': '未连接到服务器'})
    
    data = request.json
    command_type = data.get('type')
    params = data.get('params', {})
    
    try:
        if command_type == 'get_player_list':
            result = server_controller.get_player_list()
        elif command_type == 'get_server_stats':
            result = server_controller.get_server_stats()
        elif command_type == 'get_save_games':
            result = server_controller.get_save_games()
        elif command_type == 'save_game':
            save_name = params.get('name')
            result = server_controller.save_game(save_name)
        elif command_type == 'broadcast_message':
            message = params.get('message')
            result = server_controller.broadcast_message(message)
        elif command_type == 'kick_player':
            player_guid = params.get('guid')
            result = server_controller.kick_player(player_guid)
        elif command_type == 'ban_player':
            player_name = params.get('name')
            result = server_controller.ban_player(player_name)
        elif command_type == 'whitelist_player':
            player_name = params.get('name')
            result = server_controller.whitelist_player(player_name)
        elif command_type == 'set_admin':
            player_name = params.get('name')
            result = server_controller.set_admin(player_name)
        elif command_type == 'load_save':
            save_name = params.get('name')
            result = server_controller.load_save(save_name)
        elif command_type == 'create_new_game':
            result = server_controller.create_new_game()
        elif command_type == 'shutdown_server':
            delay = params.get('delay', 0)
            message = params.get('message', '')
            result = server_controller.shutdown_server(delay, message)
        else:
            return jsonify({'status': 'error', 'message': '未知命令类型'})
        
        # 确保结果是JSON可序列化的
        if isinstance(result, (dict, list)):
            return jsonify({'status': 'success', 'data': result})
        else:
            return jsonify({'status': 'success', 'data': str(result)})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'命令执行失败: {e}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)