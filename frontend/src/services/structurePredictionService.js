// frontend/src/services/structurePredictionService.js
import { helixPropensity, sheetPropensity } from '@/constants/proteinData'

export function predictSecondaryStructure(sequence) {
  if (!sequence || sequence.length === 0) {
    return []
  }

  // 初始化预测结构
  const predictedStructure = new Array(sequence.length).fill('C') // 默认为无规卷曲

  // 滑动窗口预测二级结构
  const windowSize = 5

  for (let i = 0; i <= sequence.length - windowSize; i++) {
    const window = sequence.slice(i, i + windowSize)

    // 计算窗口内平均螺旋和折叠倾向性
    let helixScore = 0
    let sheetScore = 0

    for (const aa of window) {
      helixScore += helixPropensity[aa] || 0.5
      sheetScore += sheetPropensity[aa] || 0.5
    }

    helixScore /= windowSize
    sheetScore /= windowSize

    // 根据阈值判定结构
    const threshold = 1.1

    // 更新中心位置的结构
    const center = i + Math.floor(windowSize / 2)

    if (helixScore > threshold && helixScore > sheetScore) {
      predictedStructure[center] = 'H'
    } else if (sheetScore > threshold && sheetScore > helixScore) {
      predictedStructure[center] = 'E'
    }
  }

  // 平滑结构预测（合并相邻同类结构）
  return smoothStructurePrediction(predictedStructure, sequence.length)
}

function smoothStructurePrediction(predictedStructure, length) {
  const smoothed = [...predictedStructure]

  // 排除过短的结构段（少于3个残基）
  for (let i = 1; i < length - 1; i++) {
    if (smoothed[i-1] !== smoothed[i] && smoothed[i] !== smoothed[i+1]) {
      smoothed[i] = smoothed[i-1]
    }
  }

  // 合并短间隔的相同结构
  for (let i = 2; i < length - 2; i++) {
    if (smoothed[i-2] === smoothed[i+2] && smoothed[i-2] !== 'C') {
      smoothed[i-1] = smoothed[i-2]
      smoothed[i] = smoothed[i-2]
      smoothed[i+1] = smoothed[i-2]
    }
  }

  return smoothed
}