from datetime import datetime

import torch
from pathlib import Path
from esm import pretrained
from models.multi_label_gnn import MultiLabelGNN
from torch_geometric.data import Data
from torch_geometric.utils import to_undirected
import json


class ProteinPredictor:
    def __init__(self, model_path, device=None):
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)

        print(f"正在使用设备: {self.device}")

        # 初始化ESM模型
        self.esm_model, self.alphabet = pretrained.load_model_and_alphabet("esm2_t6_8M_UR50D")
        self.esm_model = self.esm_model.to(self.device)
        self.esm_model.eval()
        self.batch_converter = self.alphabet.get_batch_converter()

        # 加载GNN模型
        self.model = MultiLabelGNN(
            input_dim=320,
            hidden_dim=128,
            output_dim=8  # GO slim类别数
        ).to(self.device)

        # 加载模型权重
        state_dict = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(state_dict)
        self.model.eval()

        # GO slim映射（与预测结果对应）
        self.go_categories = [
            'protein_binding',
            'dna_binding',
            'catalytic',
            'structural',
            'transcription',
            'signal',
            'transport',
            'enzyme_regulation'
        ]

    def _create_sequence_edges(self, seq_len):
        src = torch.arange(0, seq_len - 1, dtype=torch.long)
        dst = torch.arange(1, seq_len, dtype=torch.long)
        return to_undirected(torch.stack([src, dst]))

    def process_sequence(self, sequence, max_length=1000):
        # 验证和清理序列
        sequence = sequence.strip().upper()
        if len(sequence) > max_length:
            sequence = sequence[:max_length]

        # 生成ESM特征
        with torch.no_grad():
            batch_labels, batch_strs, batch_tokens = self.batch_converter([("protein", sequence)])
            batch_tokens = batch_tokens.to(self.device)
            results = self.esm_model(batch_tokens, repr_layers=[6])
            embeddings = results["representations"][6]
            emb = embeddings[0, 1:len(sequence) + 1].cpu()

        # 创建图数据
        edge_index = self._create_sequence_edges(len(sequence))
        data = Data(
            x=emb,
            edge_index=edge_index,
            seq=sequence
        )
        return data

    def predict(self, sequence, threshold=0.5):
        """预测蛋白质功能并返回前端需要的格式"""
        try:
            # 生成预测ID: SEQ_时间戳_前6位序列
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            prediction_id = f"SEQ_{timestamp}"

            # 处理序列并预测
            data = self.process_sequence(sequence)
            data = data.to(self.device)

            self.model.eval()
            with torch.no_grad():
                out = self.model(data)
                probs = torch.sigmoid(out)

            # 生成预测结果
            results = []
            for i, category in enumerate(self.go_categories):
                if probs[0][i] > threshold:
                    results.append({
                        'timestamp': timestamp,
                        'protein_id': prediction_id,  # 使用新生成的ID
                        'sequence': sequence,
                        'function': category,
                        'confidence': float(probs[0][i])
                    })

            # 按置信度排序
            results.sort(key=lambda x: x['confidence'], reverse=True)
            return results

        except Exception as e:
            raise e

def main():
    # 测试代码
    model_path = 'models/best_model.pt'
    test_sequence = "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHF"

    predictor = ProteinPredictor(model_path)
    results = predictor.predict(test_sequence)

    print("\n预测结果:")
    for result in results:
        print(f"功能: {result['function']}")
        print(f"置信度: {result['confidence']:.3f}")
        print("-" * 30)


if __name__ == "__main__":
    main()