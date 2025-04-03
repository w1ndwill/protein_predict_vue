// frontend/src/constants/proteinData.js
export const aminoAcidGroups = {
  hydrophobic: ['A', 'I', 'L', 'M', 'F', 'W', 'V'],
  hydrophilic: ['S', 'T', 'N', 'Q'],
  positive: ['R', 'H', 'K'],
  negative: ['D', 'E'],
  special: ['C', 'G', 'P', 'Y']
}

export const groupColors = {
  hydrophobic: '#ff7f7f',
  hydrophilic: '#7fbfff',
  positive: '#7fff7f',
  negative: '#ff7fff',
  special: '#ffff7f'
}

export const groupTranslations = {
  hydrophobic: '疏水性',
  hydrophilic: '亲水性',
  positive: '正电荷',
  negative: '负电荷',
  special: '特殊'
}

export const helixPropensity = {
  'A': 1.4, 'L': 1.2, 'M': 1.2, 'E': 1.5, 'Q': 1.3, 'K': 1.2,
  'R': 1.1, 'H': 1.0, 'I': 0.9, 'W': 0.8, 'V': 0.9, 'F': 0.9,
  'Y': 0.7, 'D': 0.8, 'N': 0.7, 'T': 0.7, 'S': 0.7, 'G': 0.4,
  'P': 0.3, 'C': 0.9
}

export const sheetPropensity = {
  'V': 1.9, 'I': 1.8, 'Y': 1.6, 'F': 1.5, 'W': 1.4, 'T': 1.2,
  'C': 1.2, 'L': 1.1, 'M': 1.0, 'A': 0.7, 'R': 0.8, 'G': 0.6,
  'D': 0.5, 'K': 0.7, 'S': 0.8, 'H': 0.9, 'N': 0.7, 'Q': 0.8,
  'P': 0.3, 'E': 0.5
}