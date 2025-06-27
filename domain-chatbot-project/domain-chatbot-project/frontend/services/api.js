const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

class ApiService {
  getAuthHeaders() {
    const token = localStorage.getItem("token")
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    }
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`
    const config = {
      headers: this.getAuthHeaders(),
      ...options,
    }

    const response = await fetch(url, config)

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: "Network error" }))
      throw new Error(error.message || `HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  async get(endpoint) {
    return this.request(endpoint, { method: "GET" })
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async put(endpoint, data) {
    return this.request(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: "DELETE" })
  }
}

export const apiService = new ApiService()
