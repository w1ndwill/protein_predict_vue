import os
import torch
import numpy as np
from torch_geometric.data import Dataset, Data
from torch_geometric.utils import to_undirected
from esm import pretrained
from tqdm import tqdm

class ProteinGraphDataset(Dataset):
    def __init__(self, root, protein_ids, labels, sequences,go_dict,
                 feature_model="esm2_t6_8M_UR50D",
                 max_length=1000, force_reprocess=False):
        self.protein_ids = protein_ids
        self.labels = labels
        self.sequences = sequences
        self.go_dict = go_dict
        self.feature_model = feature_model
        self.max_length = max_length
        self.force_reprocess = force_reprocess
        self.training = False
        self._num_classes = len(go_dict)  # 使用下划线前缀的私有变量

        # 初始化ESM模型
        self.model, self.alphabet = pretrained.load_model_and_alphabet(feature_model)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.model.to(self.device)
        self.batch_converter = self.alphabet.get_batch_converter()
        self.model.eval()
        super().__init__(root)

    @property
    def num_classes(self):
        return self._num_classes

    @num_classes.setter
    def num_classes(self, value):
        self._num_classes = value

    def _map_to_slim_categories(self):
        """将GO terms映射到功能大类"""
        self.go_slim_mapping = {
            'protein_binding': [  # 蛋白质结合相关
                'GO:0042803',  # protein homodimerization activity
                'GO:0019901',  # protein kinase binding
                'GO:0019899',  # enzyme binding
                'GO:0005102',  # signaling receptor binding
                'GO:0031625',  # ubiquitin protein ligase binding
                'GO:0045296',  # cadherin binding
                'GO:0044877',  # protein-containing complex binding
                'GO:0005178',  # integrin binding
                'GO:0051117',  # ATPase binding
                'GO:0008022',  # protein C-terminus binding
                'GO:0042802',  # identical protein binding
                'GO:0051400',  # BH3 domain binding
                'GO:0017018',  # myosin binding
                'GO:0030674',  # protein binding, bridging
                'GO:0051425',  # PTB domain binding
                'GO:1903231'   # microRNA binding
            ],
            'dna_binding': [  # DNA结合相关
                'GO:1990837',  # sequence-specific dsDNA binding
                'GO:0003677',  # DNA binding
                'GO:0003700',  # DNA-binding TF activity
                'GO:0003682',  # chromatin binding
                'GO:0000977',  # RNA pol II TF activity
                'GO:0003690',  # double-stranded DNA binding
                'GO:0003691',  # telomeric DNA binding
                'GO:0043565',  # sequence-specific DNA binding
                'GO:0003681',  # bent DNA binding
                'GO:0000978'  # RNA polymerase II cis-binding
            ],
            'catalytic': [  # 催化活性相关
                'GO:0004674',  # protein kinase activity
                'GO:0061630',  # ubiquitin ligase activity
                'GO:0003924',  # GTPase activity
                'GO:0004842',  # ubiquitin-protein transferase activity
                'GO:0016887',  # ATPase activity
                'GO:0004715',  # non-membrane spanning protein tyrosine kinase activity
                'GO:0004713',  # protein tyrosine kinase activity
                'GO:0016491',  # oxidoreductase activity
                'GO:0004252',  # serine-type endopeptidase activity
                'GO:0008233',  # peptidase activity
                'GO:0016301',  # kinase activity
                'GO:0016787',  # hydrolase activity
                'GO:0004553'  # hydrolase activity, O-glycosyl bonds
            ],
            'structural': [  # 结构相关
                'GO:0005509',  # calcium ion binding
                'GO:0008270',  # zinc ion binding
                'GO:0005524',  # ATP binding
                'GO:0051015',  # actin filament binding
                'GO:0003779',  # actin binding
                'GO:0008307',  # structural constituent of muscle
                'GO:0005200',  # structural constituent of cytoskeleton
                'GO:0051015',  # actin filament binding
                'GO:0008092',  # cytoskeletal protein binding
                'GO:0005198'  # structural molecule activity
            ],
            'transcription': [  # 转录相关
                'GO:0001228',  # transcriptional activator activity
                'GO:0003713',  # transcription coactivator activity
                'GO:0140297',  # DNA-binding transcription factor binding
                'GO:0003714',  # transcription corepressor activity
                'GO:0001227',  # transcriptional repressor activity
                'GO:0003712',  # transcription coregulator activity
                'GO:0016251',  # RNA polymerase II general transcription activity
                'GO:0003702'  # RNA polymerase II distal enhancer activity
            ],
            'signal': [  # 信号相关
                'GO:0004984',  # olfactory receptor activity
                'GO:0004930',  # G protein-coupled receptor activity
                'GO:0038023',  # signaling receptor activity
                'GO:0004871',  # signal transducer activity
                'GO:0035326',  # enhancer binding
                'GO:0048018',  # receptor ligand activity
                'GO:0005125',  # cytokine activity
                'GO:0005102'  # signaling receptor binding
            ],
            'transport': [  # 运输相关
                'GO:0022857',  # transmembrane transporter activity
                'GO:0015267',  # channel activity
                'GO:0005216',  # ion channel activity
                'GO:0005215',  # transporter activity
                'GO:0022891',  # substrate-specific transmembrane transporter activity
                'GO:0015075',  # ion transmembrane transporter activity
                'GO:0022804',  # active transmembrane transporter activity
                'GO:0015238'  # drug transmembrane transporter activity
            ],
            'enzyme_regulation': [  # 酶调控相关
                'GO:0004857',  # enzyme inhibitor activity
                'GO:0004860',  # protein kinase inhibitor activity
                'GO:0004866',  # endopeptidase inhibitor activity
                'GO:0030234',  # enzyme regulator activity
                'GO:0019207',  # kinase regulator activity
                'GO:0019887',  # protein kinase regulator activity
                'GO:0008047',  # enzyme activator activity
                'GO:0019210'  # kinase inhibitor activity
            ]
        }

        # 创建反向映射
        self.go_to_slim = {}
        for slim_cat, go_terms in self.go_slim_mapping.items():
            for term in go_terms:
                self.go_to_slim[term] = slim_cat

    def _filter_by_go_slim(self, min_terms=1):
        self._map_to_slim_categories()

        # 如果是预测场景(没有真实标签)，则保留所有蛋白质
        if all(sum(self.labels[pid]) == 0 for pid in self.protein_ids):
            print("预测模式: 保留所有蛋白质")
            new_labels = {pid: [0] * len(self.go_slim_mapping) for pid in self.protein_ids}
            self.labels = new_labels
            self.num_classes = len(self.go_slim_mapping)
            return

        new_labels = {}
        filtered_protein_ids = []

        print("开始GO slim过滤")
        print(f"过滤前蛋白质数量: {len(self.protein_ids)}")

        for pid in self.protein_ids:
            if pid in self.labels:
                orig_label = self.labels[pid]
                slim_label = [0] * len(self.go_slim_mapping)

                # 放宽过滤条件
                converted = False
                for term, idx in self.go_dict.items():
                    if term in self.go_to_slim and idx < len(orig_label):
                        if orig_label[idx] == 1:
                            slim_cat = self.go_to_slim[term]
                            slim_idx = list(self.go_slim_mapping.keys()).index(slim_cat)
                            slim_label[slim_idx] = 1
                            converted = True

                # 只要有转换成功就保留
                if converted:  # 移除 min_terms 条件
                    new_labels[pid] = slim_label
                    filtered_protein_ids.append(pid)

        print(f"过滤后蛋白质数量: {len(filtered_protein_ids)}")
        self.labels = new_labels
        self.protein_ids = filtered_protein_ids
        self.num_classes = len(self.go_slim_mapping)

    @property
    def raw_file_names(self):
        return []

    @property
    def processed_file_names(self):
        return [f'{pid.replace("|", "_").replace(":", "_")}.pt' for pid in self.protein_ids]

    def processed_file_exists(self):
        # 检查所有蛋白质文件是否存在
        return all(
            os.path.exists(os.path.join(self.processed_dir, f))
            for f in self.processed_file_names
        )

    def apply_go_slim(self):
        """应用GO slim过滤并更新标签"""
        self._filter_by_go_slim()
        return self  # 允许链式调用

    def _process(self):
        if not self.force_reprocess and self.processed_file_exists():
            # 只在第一次检查时输出信息
            if not hasattr(ProteinGraphDataset, '_processed_shown'):
                print(f"已找到处理好的数据在 {self.processed_dir}")
                ProteinGraphDataset._processed_shown = True
            return

    def process(self):
        self._filter_by_go_slim(min_terms=1)

        os.makedirs(self.processed_dir, exist_ok=True)

        # 检查哪些蛋白质需要处理
        to_process = []
        for pid in self.protein_ids:
            file_path = os.path.join(self.processed_dir, f'{pid}.pt')
            if self.force_reprocess or not os.path.exists(file_path):
                to_process.append(pid)

        if not to_process:
            print("所有数据已处理完成")
            return

        # 计算总批次数
        batch_size = 32
        total_batches = len(self.protein_ids) // batch_size + (1 if len(self.protein_ids) % batch_size != 0 else 0)

        print(f"需要处理 {len(self.protein_ids)} 个蛋白质，共 {total_batches} 个批次")

        batches = [self.protein_ids[i:i + batch_size]
                  for i in range(0, len(self.protein_ids), batch_size)]

        with torch.no_grad():
            for batch_ids in tqdm(batches, desc="正在按批次处理蛋白质", total=total_batches):
                valid_ids = []
                batch_seqs = []
                for pid in batch_ids:
                    seq = self.sequences[pid][:self.max_length]
                    if len(seq) < 4:
                        continue
                    valid_ids.append(pid)
                    batch_seqs.append((pid, seq))

                if not valid_ids:
                    continue

                _, _, batch_tokens = self.batch_converter(batch_seqs)
                batch_tokens = batch_tokens.to(self.device)
                results = self.model(batch_tokens, repr_layers=[6])
                embeddings = results["representations"][6]

                for idx, pid in enumerate(valid_ids):
                    # 处理文件名,替换非法字符
                    safe_pid = pid.replace("|", "_").replace(":", "_")
                    file_path = os.path.join(self.processed_dir, f'{safe_pid}.pt')

                    seq = batch_seqs[idx][1]
                    emb = embeddings[idx, 1:len(seq) + 1].cpu()

                    edge_index = self._create_sequence_edges(len(seq))

                    data = Data(
                        x=emb,
                        edge_index=edge_index,
                        y=torch.tensor(self.labels[pid], dtype=torch.float),  # 这里需要使用转换后的标签
                        seq=seq,
                        protein_id=pid
                    )

                    torch.save(data, file_path)
                    # torch.save(data, os.path.join(self.processed_dir, f'{pid}.pt'))

    def _create_sequence_edges(self, seq_len):
        src = torch.arange(0, seq_len - 1, dtype=torch.long)
        dst = torch.arange(1, seq_len, dtype=torch.long)
        return to_undirected(torch.stack([src, dst]))

    def len(self):
        return len(self.protein_ids)

    def get(self, idx):
        pid = self.protein_ids[idx]
        safe_pid = pid.replace("|", "_").replace(":", "_")
        file_path = os.path.join(self.processed_dir, f'{safe_pid}.pt')

        # 移除 weights_only 参数
        data = torch.load(file_path, map_location='cpu')

        # 确保标签维度正确
        if isinstance(self.labels[pid], np.ndarray):
            data.y = torch.from_numpy(self.labels[pid]).float()
        else:
            data.y = torch.tensor(self.labels[pid], dtype=torch.float)

        return data

    def _download(self):
        pass

    def __getitem__(self, idx):
        data = super().__getitem__(idx)
        if self.training:
            # 随机删除更多边
            edge_mask = torch.rand(data.edge_index.size(1)) > 0.15
            data.edge_index = data.edge_index[:, edge_mask]

            # 添加高斯噪声
            noise = torch.randn_like(data.x) * 0.1
            data.x = data.x + noise
        return data

    def train(self, mode=True):
        """
        设置数据集的训练模式
        Args:
            mode (bool): True表示训练模式，False表示评估模式
        Returns:
            self: 返回数据集实例本身
        """
        self.training = mode
        return self