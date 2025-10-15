import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Transaction APIs
export const uploadTransactions = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await axios.post(`${API_BASE_URL}/transactions/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const getTransactions = async (limit = 100) => {
  const response = await api.get(`/transactions/list?limit=${limit}`)
  return response.data
}

export const updateTransactionCategory = async (transactionId, category) => {
  const response = await api.put(
    `/transactions/${transactionId}/category?category=${category}`
  )
  return response.data
}

export const splitTransaction = async (transactionId, splits) => {
  const response = await api.post(`/transactions/${transactionId}/split`, {
    transaction_id: transactionId,
    splits: splits,
  })
  return response.data
}

export const deleteTransaction = async (transactionId) => {
  const response = await api.delete(`/transactions/${transactionId}`)
  return response.data
}

export const getCategories = async () => {
  const response = await api.get('/transactions/categories')
  return response.data
}

// Report APIs
export const getSpendingSummary = async (startDate, endDate) => {
  const params = new URLSearchParams()
  if (startDate) params.append('start_date', startDate)
  if (endDate) params.append('end_date', endDate)
  
  const response = await api.get(`/reports/summary?${params.toString()}`)
  return response.data
}

export const getCategoryPieChart = async (startDate, endDate) => {
  const params = new URLSearchParams()
  if (startDate) params.append('start_date', startDate)
  if (endDate) params.append('end_date', endDate)
  
  const response = await api.get(`/reports/chart/category-pie?${params.toString()}`)
  return response.data
}

export const getSpendingTrendChart = async (startDate, endDate) => {
  const params = new URLSearchParams()
  if (startDate) params.append('start_date', startDate)
  if (endDate) params.append('end_date', endDate)
  
  const response = await api.get(`/reports/chart/spending-trend?${params.toString()}`)
  return response.data
}

export const getCategoryBarChart = async (startDate, endDate) => {
  const params = new URLSearchParams()
  if (startDate) params.append('start_date', startDate)
  if (endDate) params.append('end_date', endDate)
  
  const response = await api.get(`/reports/chart/category-bar?${params.toString()}`)
  return response.data
}

// Tag APIs
export const getAllTags = async () => {
  const response = await api.get('/tags/list')
  return response.data
}

export const addTagToTransaction = async (transactionId, tagName) => {
  const response = await api.post(`/tags/${transactionId}/add`, {
    tag_name: tagName
  })
  return response.data
}

export const removeTagFromTransaction = async (transactionId, tagName) => {
  const response = await api.delete(`/tags/${transactionId}/remove?tag_name=${tagName}`)
  return response.data
}

export const getTransactionTags = async (transactionId) => {
  const response = await api.get(`/tags/${transactionId}/list`)
  return response.data
}

export const getTransactionsByTag = async (tagName) => {
  const response = await api.get(`/tags/filter/${encodeURIComponent(tagName)}`)
  return response.data
}

export const getAllSources = async () => {
  const response = await api.get('/tags/sources')
  return response.data
}

export const getAllMerchants = async () => {
  const response = await api.get('/tags/merchants')
  return response.data
}

export default api

