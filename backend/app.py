from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
from pathlib import Path
import os
import pandas as pd
from werkzeug.utils import secure_filename
from predict_seq import ProteinPredictor

app = Flask(__name__)
CORS(app)

# 配置
UPLOAD_FOLDER = 'static/uploads'
RESULTS_FOLDER = 'static/results'
SEQUENCE_RESULTS_FILE = 'static/results/sequence_predictions.csv'
ALLOWED_EXTENSIONS = {'fasta'}
MODEL_PATH = 'models/best_model.pt'

app.config.update(
    UPLOAD_FOLDER=UPLOAD_FOLDER,
    RESULTS_FOLDER=RESULTS_FOLDER
)

# 确保目录存在
for folder in [UPLOAD_FOLDER, RESULTS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# 初始化序列预测器
predictor = ProteinPredictor(MODEL_PATH, device='cuda')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/predict/sequence', methods=['POST'])
def predict_sequence():
    try:
        data = request.get_json()
        if not data or 'sequence' not in data:
            return jsonify({'error': '未提供蛋白质序列'}), 400

        sequence = data['sequence']
        if not sequence or len(sequence) < 4:
            return jsonify({'error': '序列长度过短'}), 400

        # 预测
        predictions = predictor.predict(sequence)

        # 准备保存的数据
        df = pd.DataFrame(predictions)

        # 确保列的顺序正确
        df = df[['timestamp', 'protein_id', 'sequence', 'function', 'confidence']]

        # 保存到CSV
        if os.path.exists(SEQUENCE_RESULTS_FILE):
            df.to_csv(SEQUENCE_RESULTS_FILE, mode='a', header=False, index=False)
        else:
            df.to_csv(SEQUENCE_RESULTS_FILE, index=False)

        return jsonify({
            'results': predictions,
            'filename': 'sequence_predictions.csv'
        })

    except Exception as e:
        print(f"序列预测错误：{str(e)}")
        return jsonify({'error': f'预测过程错误：{str(e)}'}), 500


@app.route('/predict', methods=['POST'])
def predict_fasta():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400

    file = request.files['file']
    if file.filename == '' or not file:
        return jsonify({'error': '没有选择文件'}), 400

    if allowed_file(file.filename):
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            orig_filename = secure_filename(file.filename)
            result_filename = f"{timestamp}_{orig_filename}.csv"

            # 保存并预测
            input_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'test.fasta')
            result_filepath = os.path.join(app.config['RESULTS_FOLDER'], result_filename)

            file.save(input_filepath)

            import sys
            from predict_fasta import main
            sys.argv = [
                'predict_fasta.py',
                '--fasta', input_filepath,
                '--model', MODEL_PATH,
                '--output', result_filepath
            ]
            main()

            # 读取结果
            if os.path.exists(result_filepath):
                results_df = pd.read_csv(result_filepath)

                # 按蛋白质ID和置信度排序
                results_df = results_df.sort_values(
                    ['protein_id', 'confidence'],
                    ascending=[True, False]
                )

                # 添加一个新的API端点，获取单个蛋白质的序列
                return jsonify({
                    'results': results_df.to_dict(orient='records'),
                    'filename': result_filename
                })

            return jsonify({'error': '无法读取预测结果'}), 500

        except Exception as e:
            print(f"FASTA预测错误：{str(e)}")
            return jsonify({'error': f'预测过程错误：{str(e)}'}), 500

    return jsonify({'error': '不支持的文件类型'}), 400


# 添加一个新路由，用于获取指定蛋白质ID的序列
@app.route('/protein/<protein_id>', methods=['GET'])
def get_protein_sequence(protein_id):
    try:
        # 从请求参数中获取文件名
        filename = request.args.get('filename')
        if not filename:
            return jsonify({'error': '未提供文件名'}), 400

        file_path = os.path.join(app.config['RESULTS_FOLDER'], filename)
        if not os.path.exists(file_path):
            return jsonify({'error': '找不到结果文件'}), 404

        df = pd.read_csv(file_path)
        protein_data = df[df['protein_id'] == protein_id]

        if protein_data.empty:
            return jsonify({'error': '找不到指定的蛋白质'}), 404

        # 获取该蛋白质的序列信息（应该对于同一蛋白质ID，所有行的序列都相同）
        sequence = protein_data['sequence'].iloc[0]

        return jsonify({
            'protein_id': protein_id,
            'sequence': sequence,
            'predictions': protein_data.to_dict(orient='records')
        })

    except Exception as e:
        return jsonify({'error': f'获取蛋白质序列失败：{str(e)}'}), 500

@app.route('/')
def index():
    return jsonify({'message': '蛋白质功能预测系统 API'})


@app.route('/history', methods=['GET'])
def get_history():
    try:
        # 获取所有预测结果文件
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

if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=5000)