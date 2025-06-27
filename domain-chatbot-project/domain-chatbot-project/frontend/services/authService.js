import { apiService } from "./api"

class AuthService {
  async login(username, password) {
    return apiService.post("/api/auth/login", { username, password })
  }

  async signup({ email, username, password, full_name }) {
    return apiService.post("/api/auth/signup", {
      email,
      username,
      password,
      full_name,
    })
  }

  async getMe(token) {
    return apiService.get("/api/auth/me", {
      headers: { Authorization: `Bearer ${token}` }
    })
  }

  async verifyToken(token) {
    // Optionally, you can use getMe for verification
    return this.getMe(token)
  }

  async updateProfile(data) {
    return apiService.put("/api/auth/profile", data)
  }
}

export const authService = new AuthService()