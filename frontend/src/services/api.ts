import axios from 'axios'
import type { TripFormData, TripPlanResponse } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json'
  }
})

apiClient.interceptors.request.use(
  (config) => {
    console.log('Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

apiClient.interceptors.response.use(
  (response) => {
    console.log('Response:', response.status, response.config.url)
    return response
  },
  (error) => {
    console.error('Response error:', error.response?.status, error.message)
    return Promise.reject(error)
  }
)

export async function generateTripPlan(formData: TripFormData): Promise<TripPlanResponse> {
  try {
    const response = await apiClient.post<TripPlanResponse>('/api/trip/plan', formData)
    return response.data
  } catch (error: any) {
    console.error('Generate trip plan failed:', error)
    throw new Error(error.response?.data?.detail || error.message || 'Generate trip plan failed')
  }
}

export async function healthCheck(): Promise<any> {
  try {
    const response = await apiClient.get('/health')
    return response.data
  } catch (error: any) {
    console.error('Health check failed:', error)
    throw new Error(error.message || 'Health check failed')
  }
}

export default apiClient