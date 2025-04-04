// src/services/functionalSitesService.js
export function predictFunctionalSites(sequence) {
  // 简单预测算法 (实际项目中可替换为API调用)
  const sites = [];

  // 示例：基于模式匹配预测活性位点
  const activePatterns = ['RGD', 'CXXC', 'SH'];
  const bindingPatterns = ['WXXW', 'PXXP', 'YXN'];
  const ptmPatterns = ['KR', 'ST', 'YT'];

  // 查找活性位点
  activePatterns.forEach(pattern => {
    findPatternPositions(sequence, pattern).forEach(pos => {
      sites.push({
        position: pos,
        length: pattern.replace(/X/gi, '').length,
        type: 'active-site',
        description: `${pattern} 活性位点模式 (${pos+1}-${pos+pattern.length})`
      });
    });
  });

  // 查找结合位点
  bindingPatterns.forEach(pattern => {
    findPatternPositions(sequence, pattern).forEach(pos => {
      sites.push({
        position: pos,
        length: pattern.replace(/X/gi, '').length,
        type: 'binding-site',
        description: `${pattern} 结合位点模式 (${pos+1}-${pos+pattern.length})`
      });
    });
  });

  // 查找修饰位点
  ptmPatterns.forEach(pattern => {
    findPatternPositions(sequence, pattern).forEach(pos => {
      sites.push({
        position: pos,
        length: pattern.replace(/X/gi, '').length,
        type: 'ptm-site',
        description: `${pattern} 修饰位点模式 (${pos+1}-${pos+pattern.length})`
      });
    });
  });

  return sites;
}

export async function fetchFunctionalSites(sequence, proteinId) {
  try {
    const response = await fetch('http://localhost:5000/predict/sites', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        sequence,
        protein_id: proteinId
      })
    });

    if (!response.ok) {
      throw new Error('位点预测请求失败');
    }

    return await response.json();
  } catch (error) {
    console.error('获取功能位点失败:', error);
    // 失败时返回本地预测结果作为备选
    return predictFunctionalSites(sequence);
  }
}

function findPatternPositions(sequence, pattern) {
  const positions = [];

  // 处理通配符模式 (如 'CxxC')
  const regexPattern = pattern.replace(/X/gi, '.');
  const regex = new RegExp(regexPattern, 'gi');

  let match;
  while ((match = regex.exec(sequence)) !== null) {
    positions.push(match.index);
  }

  return positions;
}