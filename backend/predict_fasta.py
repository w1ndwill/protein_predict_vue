import torch
import argparse
from pathlib import Path
from Bio import SeqIO
import pandas as pd
from models.multi_label_gnn import MultiLabelGNN
from data.protein_dataset import ProteinGraphDataset
from torch_geometric.loader import DataLoader

def parse_args():
    parser = argparse.ArgumentParser(description='预测蛋白质序列的功能')
    parser.add_argument('--fasta', type=str, default='test.fasta', help='输入的FASTA文件路径')
    parser.add_argument('--model', type=str, default='models/best_model.pt', help='模型文件路径')
    parser.add_argument('--output', type=str, default='predictions.csv', help='输出预测结果的文件路径')
    parser.add_argument('--batch_size', type=int, default=32, help='批处理大小')
    parser.add_argument('--threshold', type=float, default=0.5, help='预测阈值')
    return parser.parse_args()


def load_fasta(fasta_file):
    """从FASTA文件加载序列"""
    sequences = {}
    for record in SeqIO.parse(fasta_file, "fasta"):
        sequences[record.id] = str(record.seq)
    return sequences


def predict_proteins(model, loader, device, threshold, sequences):
    """预测蛋白质功能"""
    model.eval()
    predictions = {}
    prediction_details = []

    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    with torch.no_grad(): #  关闭梯度
        for batch in loader:
            batch = batch.to(device)
            out = model(batch)
            probs = torch.sigmoid(out)

            for i in range(len(batch.protein_id)):
                pid = batch.protein_id[i]
                pred_indices = torch.where(probs[i] > threshold)[0]
                pred_functions = []

                for idx in pred_indices:
                    slim_category = list(loader.dataset.go_slim_mapping.keys())[idx.item()]
                    confidence = probs[i][idx].item()
                    pred_functions.append((slim_category, confidence))

                    prediction_details.append({
                        'timestamp': timestamp,
                        'protein_id': pid,
                        'sequence': sequences[pid],  # 添加完整序列
                        'function': slim_category,
                        'confidence': confidence
                    })

                predictions[pid] = pred_functions

    return predictions, prediction_details


def main():
    args = parse_args()

    print("正在初始化...")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # 创建缓存目录
    cache_dir = Path('data/predict_cache')
    cache_dir.mkdir(parents=True, exist_ok=True)

    print(f"加载FASTA文件: {args.fasta}")
    sequences = load_fasta(args.fasta)
    protein_ids = list(sequences.keys())
    print(f"发现 {len(protein_ids)} 个蛋白质序列")

    # 预定义GO slim类别
    go_slim_categories = [
        'protein_binding',
        'dna_binding',
        'catalytic',
        'structural',
        'transcription',
        'signal',
        'transport',
        'enzyme_regulation'
    ]

    print("创建数据集...")
    dataset = ProteinGraphDataset(
        root=str(cache_dir),
        protein_ids=protein_ids,
        labels={pid: [0] * len(go_slim_categories) for pid in protein_ids},
        sequences=sequences,
        go_dict={cat: i for i, cat in enumerate(go_slim_categories)},
        force_reprocess=True
    )

    print("处理蛋白质序列...")
    dataset.process()

    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=False)

    # 加载模型
    model = MultiLabelGNN(
        input_dim=320,
        hidden_dim=128,
        output_dim=len(go_slim_categories)
    ).to(device)
    model.load_state_dict(torch.load(args.model, map_location=device))

    print("开始预测...")
    predictions, prediction_details = predict_proteins(model, loader, device, args.threshold, sequences)

    # 保存预测结果
    df = pd.DataFrame(prediction_details)
    # 确保列的顺序正确
    df = df[['timestamp', 'protein_id', 'sequence', 'function', 'confidence']]
    df.to_csv(args.output, index=False)
    print(f"预测结果已保存到: {args.output}")

    # 打印示例预测结果
    print("\n预测结果示例:")
    for pid in list(predictions.keys())[:5]:
        print(f"\n蛋白质: {pid}")
        print("预测的功能:")
        for func, conf in predictions[pid]:
            print(f"- {func} (置信度: {conf:.3f})")


if __name__ == "__main__":
    main()