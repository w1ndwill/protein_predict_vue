// frontend/src/utils/proteinUtils.js
import { aminoAcidGroups, groupColors, groupTranslations } from '../constants/proteinData'

export function getAminoAcidClass(aa) {
  for (const [group, aminoAcids] of Object.entries(aminoAcidGroups)) {
    if (aminoAcids.includes(aa)) return group
  }
  return ''
}

export function translateType(type) {
  return groupTranslations[type] || type
}

export function getNodeColor(group) {
  return groupColors[group] || '#ccc'
}

export function getStructureClass(struct) {
  switch (struct) {
    case 'H': return 'helix'
    case 'E': return 'sheet'
    case 'C': return 'coil'
    default: return ''
  }
}

export function getStructureTitle(struct) {
  switch (struct) {
    case 'H': return 'α螺旋 (Alpha Helix)'
    case 'E': return 'β折叠 (Beta Sheet)'
    case 'C': return '无规卷曲 (Random Coil)'
    default: return '未知结构'
  }
}

// src/utils/proteinUtils.js
export function isMultiProteinResult(results) {
  if (!results || results.length === 0) return false
  // 检测是否有多个不同的蛋白质ID
  const uniqueIds = new Set(results.map(r => r.protein_id))
  return uniqueIds.size > 1
}

export function getProteinOptions(results) {
  if (!results.length) return []
  // 从结果中提取唯一的蛋白质ID
  const proteinIds = [...new Set(results.map(r => r.protein_id))]
  return proteinIds.map(id => ({
    value: id,
    label: id
  }))
}

export function getProteinLength(sequence) {
  return sequence ? sequence.length : 0
}