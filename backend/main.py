from flask import Flask, request, jsonify, send_from_directory
import os
import pandas as pd
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
import re
from pathlib import Path
import json

# 导入用户认证相关功能
from auth import register_user, login_user, verify_token
from database import init_db

# 导入预测模块
from predict_seq import ProteinPredictor

# 初始化Flask应用
app = Flask(__name__)

# 配置文件上传和结果保存
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['RESULTS_FOLDER'] = './results'
app.config['ALLOWED_EXTENSIONS'] = {'fasta', 'txt'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传大小为16MB

# 确保上传和结果目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# 初始化数据库
init_db()

# 加载预测模型
MODEL_PATH = 'models/best_model.pt'
predictor = ProteinPredictor(MODEL_PATH)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    return jsonify({"message": "蛋白质功能预测系统API"})


# 身份验证相关路由
@app.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ('username', 'email', 'password')):
            return jsonify({"message": "请提供完整的注册信息"}), 400

        result = register_user(data['username'], data['email'], data['password'])

        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({"message": f"注册过程中发生错误: {str(e)}"}), 500


@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ('username', 'password')):
            return jsonify({"message": "请提供用户名和密码"}), 400

        result = login_user(data['username'], data['password'])

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401

    except Exception as e:
        return jsonify({"message": f"登录过程中发生错误: {str(e)}"}), 500


# 中间件：验证令牌
def verify_auth_token():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None, jsonify({"message": "未提供授权令牌"}), 401

    token_parts = auth_header.split()
    if len(token_parts) != 2 or token_parts[0] != 'Bearer':
        return None, jsonify({"message": "无效的授权格式"}), 401

    token = token_parts[1]
    result = verify_token(token)
    if not result['success']:
        return None, jsonify({"message": result['message']}), 401

    return result, None, None


# 预测相关路由
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # 验证令牌
        user_info, error_response, error_code = verify_auth_token()
        if error_response:
            return error_response, error_code

        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({'error': '没有文件被上传'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400

        if file and allowed_file(file.filename):
            # 生成安全的文件名
            original_filename = secure_filename(file.filename)
            filename = f"{uuid.uuid4().hex}_{original_filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # 解析FASTA文件并预测
            results = []
            try:
                with open(file_path, 'r') as f:
                    current_id = None
                    current_seq = ""

                    for line in f:
                        line = line.strip()
                        if not line:
                            continue

                        if line.startswith('>'):
                            # 处理上一个序列(如果存在)
                            if current_id and current_seq:
                                sequence_results = predictor.predict(current_seq)
                                results.extend(sequence_results)

                            # 提取新的蛋白质ID
                            header_match = re.match(r'>(\S+)', line)
                            current_id = header_match.group(1) if header_match else f"SEQ_{len(results) + 1}"
                            current_seq = ""
                        else:
                            current_seq += line

                    # 处理最后一个序列
                    if current_id and current_seq:
                        sequence_results = predictor.predict(current_seq)
                        results.extend(sequence_results)

            except Exception as e:
                return jsonify({'error': f'FASTA文件解析错误: {str(e)}'}), 400

            # 保存结果到CSV
            if results:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                result_filename = f"prediction_{timestamp}.csv"
                result_path = os.path.join(app.config['RESULTS_FOLDER'], result_filename)

                # 将结果转换为DataFrame并保存
                df = pd.DataFrame(results)
                df.to_csv(result_path, index=False)

                return jsonify({
                    'message': '预测成功',
                    'filename': result_filename,
                    'results': results
                })
            else:
                return jsonify({'error': '无法从文件中提取有效序列'}), 400
        else:
            return jsonify({'error': '不支持的文件类型'}), 400

    except Exception as e:
        return jsonify({'error': f'预测过程错误：{str(e)}'}), 500


@app.route('/predict/sequence', methods=['POST'])
def predict_sequence():
    try:
        # 验证令牌
        user_info, error_response, error_code = verify_auth_token()
        if error_response:
            return error_response, error_code

        data = request.get_json()
        if not data or 'sequence' not in data:
            return jsonify({'error': '未提供蛋白质序列'}), 400

        sequence = data['sequence']

        # 简单验证序列格式
        if not re.match(r'^[A-Za-z]+$', sequence):
            return jsonify({'error': '序列包含无效字符'}), 400

        # 调用预测函数
        results = predictor.predict(sequence)

        # 保存结果到CSV
        if results:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            result_filename = f"prediction_{timestamp}.csv"
            result_path = os.path.join(app.config['RESULTS_FOLDER'], result_filename)

            # 将结果转换为DataFrame并保存
            df = pd.DataFrame(results)
            df.to_csv(result_path, index=False)

            return jsonify({
                'message': '预测成功',
                'filename': result_filename,
                'results': results
            })
        else:
            return jsonify({'error': '预测未返回结果'}), 400

    except Exception as e:
        return jsonify({'error': f'预测过程错误：{str(e)}'}), 500


@app.route('/results')
def list_results():
    try:
        # 验证令牌
        user_info, error_response, error_code = verify_auth_token()
        if error_response:
            return error_response, error_code

        results = []
        for filename in os.listdir(app.config['RESULTS_FOLDER']):
            if filename.endswith('.csv'):
                file_path = os.path.join(app.config['RESULTS_FOLDER'], filename)
                file_stat = os.stat(file_path)
                results.append({
                    'filename': filename,
                    'created_time': datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'size': f'{file_stat.st_size / 1024:.1f}KB'
                })

        # 按时间倒序排序
        results.sort(key=lambda x: x['created_time'], reverse=True)
        return jsonify(results)

    except Exception as e:
        return jsonify({'error': f'获取历史记录失败：{str(e)}'}), 500


@app.route('/results/<filename>')
def get_result(filename):
    try:
        # 验证令牌
        user_info, error_response, error_code = verify_auth_token()
        if error_response:
            return error_response, error_code

        file_path = os.path.join(app.config['RESULTS_FOLDER'], filename)
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            return jsonify(df.to_dict(orient='records'))
        return jsonify({'error': '找不到结果文件'}), 404

    except Exception as e:
        return jsonify({'error': f'读取结果失败：{str(e)}'}), 500


@app.route('/results/<filename>', methods=['DELETE'])
def delete_result(filename):
    try:
        # 验证令牌
        user_info, error_response, error_code = verify_auth_token()
        if error_response:
            return error_response, error_code

        file_path = os.path.join(app.config['RESULTS_FOLDER'], filename)
        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404

        # 检查是否为预测结果文件
        if not filename.endswith('.csv'):
            return jsonify({'error': '只能删除预测结果文件'}), 400

        # 删除文件
        os.remove(file_path)
        return jsonify({'message': '文件已成功删除'}), 200
    except Exception as e:
        return jsonify({'error': f'删除失败：{str(e)}'}), 500


@app.route('/predict/sites', methods=['POST'])
def predict_protein_sites():
    try:
        # 验证令牌
        user_info, error_response, error_code = verify_auth_token()
        if error_response:
            return error_response, error_code

        data = request.get_json()
        if not data or 'sequence' not in data:
            return jsonify({'error': '未提供蛋白质序列'}), 400

        sequence = data['sequence']
        protein_id = data.get('protein_id', 'unknown')

        # 这里可以实现更复杂的功能位点预测算法
        # 以下是简单示例
        sites = []

        # 活性位点模式匹配
        active_patterns = {
            'RGD': '细胞粘附活性位点',
            'CXXC': '氧化还原活性位点',
            'SH': '丝氨酸水解酶活性位点'
        }

        # 结合位点模式匹配
        binding_patterns = {
            'WXXW': 'SH3结构域结合位点',
            'PXXP': 'SH2结构域结合位点',
            'YXN': '酪氨酸激酶底物结合位点'
        }

        # 修饰位点模式匹配
        ptm_patterns = {
            'KR': '甲基化位点',
            'ST': '磷酸化位点',
            'YT': '酪氨酸磷酸化位点'
        }

        # 简单模式匹配(实际应用中应使用更复杂算法)
        import re

        # 处理活性位点
        for pattern, desc in active_patterns.items():
            regex = pattern.replace('X', '.')
            for match in re.finditer(regex, sequence):
                sites.append({
                    'position': match.start(),
                    'length': len(pattern),
                    'type': 'active-site',
                    'description': f'{desc} ({pattern})'
                })

        # 处理结合位点
        for pattern, desc in binding_patterns.items():
            regex = pattern.replace('X', '.')
            for match in re.finditer(regex, sequence):
                sites.append({
                    'position': match.start(),
                    'length': len(pattern),
                    'type': 'binding-site',
                    'description': f'{desc} ({pattern})'
                })

        # 处理修饰位点
        for pattern, desc in ptm_patterns.items():
            regex = pattern.replace('X', '.')
            for match in re.finditer(regex, sequence):
                sites.append({
                    'position': match.start(),
                    'length': len(pattern),
                    'type': 'ptm-site',
                    'description': f'{desc} ({pattern})'
                })

        return jsonify({
            'protein_id': protein_id,
            'sequence': sequence,
            'sites': sites
        })

    except Exception as e:
        print(f"功能位点预测错误：{str(e)}")
        return jsonify({'error': f'预测过程错误：{str(e)}'}), 500


@app.route('/protein/<protein_id>', methods=['GET'])
def get_protein(protein_id):
    try:
        # 验证令牌
        user_info, error_response, error_code = verify_auth_token()
        if error_response:
            return error_response, error_code

        filename = request.args.get('filename')
        if not filename:
            return jsonify({'error': '未提供文件名参数'}), 400

        file_path = os.path.join(app.config['RESULTS_FOLDER'], filename)
        if not os.path.exists(file_path):
            return jsonify({'error': '找不到结果文件'}), 404

        # 读取CSV查找特定蛋白质序列
        df = pd.read_csv(file_path)
        protein_data = df[df['protein_id'] == protein_id]

        if protein_data.empty:
            return jsonify({'error': '找不到指定蛋白质'}), 404

        # 提取序列数据
        sequence = protein_data['sequence'].iloc[0] if 'sequence' in protein_data.columns else None

        return jsonify({
            'protein_id': protein_id,
            'sequence': sequence
        })

    except Exception as e:
        return jsonify({'error': f'获取蛋白质数据失败：{str(e)}'}), 500


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=5000)