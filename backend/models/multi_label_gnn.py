import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import (
    GATConv,
    global_mean_pool,
    global_max_pool,
    global_add_pool,
    GraphNorm,
    TopKPooling
)

class MultiLabelGNN(torch.nn.Module):
    def __init__(self, input_dim=320, hidden_dim=128, output_dim=8):
        super().__init__()

        self.dropout = nn.Dropout(0.6)  # 提高dropout率

        # 第一层GAT：使用3个注意力头
        self.conv1 = GATConv(
            in_channels=input_dim,
            out_channels=hidden_dim,
            heads=2,
            dropout=0.5
        )

        # 第二层GAT：使用3个注意力头，添加残差连接
        self.conv2 = GATConv(
            in_channels=hidden_dim * 2,
            out_channels=hidden_dim,
            heads=2,
            dropout=0.5,
            residual=True
        )

        # 第三层GAT：使用1个注意力头
        self.conv3 = GATConv(
            in_channels=hidden_dim * 2,
            out_channels=hidden_dim,
            heads=1,
            dropout=0.5,
            residual=True
        )

        # 批量归一化层
        self.bn1 = torch.nn.BatchNorm1d(hidden_dim * 2)
        self.bn2 = torch.nn.BatchNorm1d(hidden_dim * 2)
        self.bn3 = torch.nn.BatchNorm1d(hidden_dim)

        # 层归一化
        self.layer_norm1 = torch.nn.LayerNorm(hidden_dim * 2)
        self.layer_norm2 = torch.nn.LayerNorm(hidden_dim * 2)
        self.layer_norm3 = torch.nn.LayerNorm(hidden_dim)

        # 输出MLP
        self.mlp = torch.nn.Sequential(
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.BatchNorm1d(hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.4),
            torch.nn.Linear(hidden_dim, output_dim)
        )


    def forward(self, batch):
        x, edge_index = batch.x, batch.edge_index

        # 第一层GAT
        x = self.conv1(x, edge_index)
        x = F.elu(x)
        x = self.bn1(x)
        x = self.layer_norm1(x)
        x = F.dropout(x, p=0.4, training=self.training)

        # 第二层GAT
        x = self.conv2(x, edge_index)
        x = F.elu(x)
        x = self.bn2(x)
        x = self.layer_norm2(x)
        x = F.dropout(x, p=0.4, training=self.training)

        # 第三层GAT
        x = self.conv3(x, edge_index)
        x = F.elu(x)
        x = self.bn3(x)
        x = self.layer_norm3(x)
        x = F.dropout(x, p=0.4, training=self.training)

        # 全局池化
        x = global_mean_pool(x, batch.batch)

        # 输出层
        x = self.mlp(x)

        # 确保输出维度正确
        batch_size = x.size(0)
        num_classes = x.size(1)
        x = x.view(batch_size, num_classes)

        return x



