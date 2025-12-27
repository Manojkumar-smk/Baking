/**
 * Authentication service for user auth operations
 */
import api from './api'

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  first_name: string
  last_name: string
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  user: {
    id: string
    email: string
    first_name: string
    last_name: string
    role: 'customer' | 'admin'
  }
}

export interface RefreshTokenResponse {
  access_token: string
}

const TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

export const authService = {
  /**
   * Login user
   */
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login', data)

    // Store tokens
    if (response.data.access_token) {
      localStorage.setItem(TOKEN_KEY, response.data.access_token)
    }
    if (response.data.refresh_token) {
      localStorage.setItem(REFRESH_TOKEN_KEY, response.data.refresh_token)
    }

    return response.data
  },

  /**
   * Register new user
   */
  register: async (data: RegisterRequest): Promise<{ user: any }> => {
    const response = await api.post<{ user: any }>('/auth/register', data)
    return response.data
  },

  /**
   * Logout user
   */
  logout: () => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  },

  /**
   * Refresh access token
   */
  refreshToken: async (): Promise<string> => {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    const response = await api.post<RefreshTokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    })

    if (response.data.access_token) {
      localStorage.setItem(TOKEN_KEY, response.data.access_token)
    }

    return response.data.access_token
  },

  /**
   * Get stored access token
   */
  getAccessToken: (): string | null => {
    return localStorage.getItem(TOKEN_KEY)
  },

  /**
   * Get stored refresh token
   */
  getRefreshToken: (): string | null => {
    return localStorage.getItem(REFRESH_TOKEN_KEY)
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: (): boolean => {
    return !!localStorage.getItem(TOKEN_KEY)
  },
}

export default authService
