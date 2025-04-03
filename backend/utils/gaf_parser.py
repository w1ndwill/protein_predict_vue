import pandas as pd
import numpy as np
from Bio import SeqIO
from collections import defaultdict
from pathlib import Path


def parse_goa_gaf(file_path): # 解析GAF文件
    """
    解析从GO官网下载的GAF 2.2格式文件
    https://current.geneontology.org/products/pages/downloads.html
    """
    # GAF 2.2官方列定义
    columns = [
        'DB', 'DB_Object_ID', 'DB_Object_Symbol', 'Qualifier',
        'GO_ID', 'DB_Reference', 'Evidence_Code', 'With_From',
        'Aspect', 'DB_Object_Name', 'DB_Object_Synonym', 'DB_Object_Type',
        'Taxon', 'Date', 'Assigned_By', 'Annotation_Extension', 'Gene_Product_Form_ID'
    ]

    # 类型优化
    dtype_spec = {
        'DB': 'category',
        'DB_Object_ID': 'string',
        'GO_ID': 'string',
        'Evidence_Code': 'category',
        'Aspect': 'category',
        'Taxon': 'string'
    }

    # 只读取必要列
    return pd.read_csv(
        file_path,
        sep='\t',
        comment='!',
        header=None,
        names=columns,
        dtype=dtype_spec,
        usecols=['DB_Object_ID', 'GO_ID', 'Evidence_Code', 'Aspect', 'Taxon'],
        low_memory=False
    )


def build_go_labels(gaf_df, aspect='F', min_samples=10, max_samples=1000, max_terms=1000):
    """
    构建多标签分类的标签矩阵
    Args:
        gaf_df: GAF数据框
        aspect: GO方面 ('F'=分子功能, 'P'=生物过程, 'C'=细胞组分)
        min_samples: 每个GO术语的最小样本数
        max_samples: 每个GO术语的最大样本数 (防止某些术语过度主导)
        max_terms: 最大GO术语数量
    Returns:
        protein_labels: dict, 蛋白质ID到标签向量的映射
        go_to_idx: dict, GO ID到索引的映射
    """
    # 1. 数据过滤
    # 仅保留人类蛋白质
    human_filter = gaf_df['Taxon'].str.contains('taxon:9606')

    # 排除不可靠的证据代码
    unreliable_codes = ['IEA', 'NAS', 'ND', 'NR']
    evidence_filter = ~gaf_df['Evidence_Code'].isin(unreliable_codes)

    # 选择特定GO方面
    aspect_filter = (gaf_df['Aspect'] == aspect)

    # 应用过滤器
    filtered = gaf_df[human_filter & evidence_filter & aspect_filter].copy()
    filtered.loc[:, 'UniProt_ID'] = filtered['DB_Object_ID'].str.split(':').str[-1]

    # 2. 构建初始标签映射
    label_map = defaultdict(set)
    for _, row in filtered.iterrows():
        label_map[row['UniProt_ID']].add(row['GO_ID'])

    # 3. 统计GO术语频率
    go_counts = defaultdict(int)
    for terms in label_map.values():
        for go in terms:
            go_counts[go] += 1

    # 4. 选择合适的GO术语
    valid_go_terms = set()
    balanced_go_terms = []

    # 按频率排序GO术语
    sorted_go_terms = sorted(
        [(go, count) for go, count in go_counts.items()],
        key=lambda x: x[1],
        reverse=True
    )

    # 筛选符合条件的GO术语
    for go, count in sorted_go_terms:
        if min_samples <= count <= max_samples:
            valid_go_terms.add(go)
            balanced_go_terms.append((go, count))
            if len(valid_go_terms) >= max_terms:
                break

    # 5. 过滤并均衡标签数据
    filtered_label_map = {}
    for prot, terms in label_map.items():
        valid_terms = terms & valid_go_terms
        if valid_terms:  # 只保留至少有一个有效GO术语的蛋白质
            filtered_label_map[prot] = valid_terms

    # 6. 生成GO术语到索引的映射
    all_go_terms = sorted(valid_go_terms)
    go_to_idx = {go: i for i, go in enumerate(all_go_terms)}

    # 7. 生成标签向量
    protein_labels = {}
    for prot, terms in filtered_label_map.items():
        label_vector = np.zeros(len(all_go_terms), dtype=np.float32)
        for go in terms:
            if go in go_to_idx:
                label_vector[go_to_idx[go]] = 1.0
        protein_labels[prot] = label_vector

    # 8. 打印统计信息
    print(f"\nSelected {len(valid_go_terms)} GO terms with {min_samples}-{max_samples} annotations")
    print("\nTop 10 most common GO terms:")
    for go, count in balanced_go_terms[:10]:
        print(f"GO:{go}: {count} annotations")

    # 9. 打印分布统计
    term_counts = np.array([count for _, count in balanced_go_terms])
    print(f"\nGO术语分布统计:")
    print(f"最小注释数: {term_counts.min()}")
    print(f"最大注释数: {term_counts.max()}")
    print(f"平均注释数: {term_counts.mean():.2f}")
    print(f"中位数注释数: {np.median(term_counts):.2f}")

    return protein_labels, go_to_idx


def load_sequences(fasta_path):
    """加载FASTA文件并验证路径"""
    fasta_path = Path(fasta_path)
    if not fasta_path.exists():
        raise FileNotFoundError(f"FASTA文件不存在于：{fasta_path.resolve()}")

    return {rec.id.split('|')[1]: str(rec.seq)
            for rec in SeqIO.parse(fasta_path, "fasta")
            if '|' in rec.id}  # 确保是UniProt格式