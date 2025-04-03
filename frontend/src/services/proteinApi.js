// src/services/proteinApi.js
import axios from 'axios'

export async function predictFromSequence(sequence) {
  return await axios.post('/api/predict/sequence', { sequence })
}

export async function getHistoryRecords() {
  return await axios.get('/api/history')
}

export async function getHistoryResult(filename) {
  return await axios.get(`/api/results/${filename}`)
}

export async function getProteinData(proteinId, filename) {
  return await axios.get(`/api/protein/${proteinId}`, {
    params: { filename }
  })
}