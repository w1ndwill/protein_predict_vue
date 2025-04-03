import os
import torch
from .multi_label_gnn import MultiLabelGNN

# 获取当前目录路径
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, 'best_model.pt')


def load_model():
    """
    加载预训练的GNN模型
    """
    # 检查模型文件是否存在
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"找不到预训练模型文件: {MODEL_PATH}")

    try:
        # 初始化模型（参数需要与训练时一致）
        model = MultiLabelGNN(
            input_dim=512,  # 输入特征维度
            hidden_dim=256,  # 隐藏层维度
            output_dim=128  # 输出维度（GO术语数量）
        )

        # 加载预训练权重
        model.load_state_dict(torch.load(MODEL_PATH))
        model.eval()  # 设置为评估模式

        return model

    except Exception as e:
        raise RuntimeError(f"加载模型失败: {str(e)}")


# 导出模型加载函数
__all__ = ['load_model']