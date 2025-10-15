/**
 * API Client for CreatorPulse Backend
 * Communicates with FastAPI backend at localhost:8000
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Token management
let authToken: string | null = localStorage.getItem('authToken');

export const setAuthToken = (token: string | null) => {
  authToken = token;
  if (token) {
    localStorage.setItem('authToken', token);
  } else {
    localStorage.removeItem('authToken');
  }
};

export const getAuthToken = () => authToken;

// Generic API request handler
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }

  // Handle empty responses (like 204 No Content for DELETE)
  const contentType = response.headers.get('content-type');
  if (response.status === 204 || !contentType || !contentType.includes('application/json')) {
    return undefined as T;
  }

  return response.json();
}

// Authentication API
export const authApi = {
  signup: async (email: string, password: string, fullName?: string, timezone?: string) => {
    const data = await apiRequest<{ access_token: string; user: any }>('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({
        email,
        password,
        full_name: fullName,
        timezone: timezone || 'UTC',
      }),
    });
    setAuthToken(data.access_token);
    return data;
  },

  login: async (email: string, password: string) => {
    const data = await apiRequest<{ access_token: string; user: any }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    setAuthToken(data.access_token);
    return data;
  },

  logout: () => {
    setAuthToken(null);
  },

  getCurrentUser: async () => {
    return apiRequest<any>('/auth/me');
  },
};

// Sources API
export const sourcesApi = {
  getAll: async (sourceType?: string, isActive?: boolean) => {
    const params = new URLSearchParams();
    if (sourceType) params.append('source_type', sourceType);
    if (isActive !== undefined) params.append('is_active', String(isActive));

    return apiRequest<{ sources: any[] }>(`/sources/?${params.toString()}`);
  },

  getStats: async () => {
    return apiRequest<{
      total: number;
      twitter: number;
      youtube: number;
      rss: number;
      newsletter: number;
    }>('/sources/stats');
  },

  create: async (sourceData: any) => {
    return apiRequest<any>('/sources/', {
      method: 'POST',
      body: JSON.stringify(sourceData),
    });
  },

  update: async (sourceId: string, updateData: any) => {
    return apiRequest<any>(`/sources/${sourceId}`, {
      method: 'PATCH',
      body: JSON.stringify(updateData),
    });
  },

  delete: async (sourceId: string) => {
    return apiRequest<void>(`/sources/${sourceId}`, {
      method: 'DELETE',
    });
  },
};

// Content API
export const contentApi = {
  fetch: async () => {
    return apiRequest<{ message: string; results: any }>('/content/fetch', {
      method: 'POST',
    });
  },

  getAll: async (contentType?: string, page = 1, pageSize = 20) => {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (contentType) params.append('content_type', contentType);

    return apiRequest<{ items: any[]; total: number; pages: number }>(`/content/?${params.toString()}`);
  },

  getStats: async () => {
    return apiRequest<{
      total: number;
      by_type: Record<string, number>;
    }>('/content/stats');
  },

  delete: async (contentId: string) => {
    return apiRequest<void>(`/content/${contentId}`, {
      method: 'DELETE',
    });
  },
};

// Trends API
export const trendsApi = {
  detect: async () => {
    return apiRequest<{ message: string; trends_detected: number }>('/trends/detect', {
      method: 'POST',
    });
  },

  getTop: async (limit = 3) => {
    return apiRequest<{ trends: any[] }>(`/trends/top?limit=${limit}`);
  },

  getAll: async (page = 1, pageSize = 20) => {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    return apiRequest<{ items: any[]; total: number; pages: number }>(`/trends/?${params.toString()}`);
  },

  getStats: async () => {
    return apiRequest<{
      total_trends: number;
      active_trends: number;
      avg_score: number;
      top_keywords: string[];
    }>('/trends/stats');
  },

  delete: async (trendId: string) => {
    return apiRequest<void>(`/trends/${trendId}`, {
      method: 'DELETE',
    });
  },
};

// Style Profiles API
export const styleProfilesApi = {
  create: async (newsletterText: string, newsletterTitle?: string) => {
    return apiRequest<any>('/style-profiles/', {
      method: 'POST',
      body: JSON.stringify({
        newsletter_text: newsletterText,
        newsletter_title: newsletterTitle,
      }),
    });
  },

  getAll: async (page = 1, pageSize = 10) => {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    return apiRequest<{ profiles: any[]; total: number; total_pages: number }>(`/style-profiles/?${params.toString()}`);
  },

  getAggregated: async () => {
    return apiRequest<any>('/style-profiles/aggregated');
  },

  getStats: async () => {
    return apiRequest<{
      total_profiles: number;
      analyzed_profiles: number;
      has_primary: boolean;
    }>('/style-profiles/stats');
  },

  setPrimary: async (profileId: string) => {
    return apiRequest<any>(`/style-profiles/${profileId}/primary`, {
      method: 'PATCH',
    });
  },

  delete: async (profileId: string) => {
    return apiRequest<void>(`/style-profiles/${profileId}`, {
      method: 'DELETE',
    });
  },
};

// Drafts API
export const draftsApi = {
  generate: async (forceRegenerate = false, includeTrends = true, maxTrends = 3) => {
    return apiRequest<any>('/drafts/generate', {
      method: 'POST',
      body: JSON.stringify({
        force_regenerate: forceRegenerate,
        include_trends: includeTrends,
        max_trends: maxTrends,
      }),
    });
  },

  getAll: async (page = 1, pageSize = 10, status?: string) => {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (status) params.append('status', status);

    return apiRequest<{ drafts: any[]; total: number }>(`/drafts/?${params.toString()}`);
  },

  getById: async (draftId: string) => {
    return apiRequest<any>(`/drafts/${draftId}`);
  },

  update: async (draftId: string, updateData: any) => {
    return apiRequest<any>(`/drafts/${draftId}`, {
      method: 'PATCH',
      body: JSON.stringify(updateData),
    });
  },

  delete: async (draftId: string) => {
    return apiRequest<void>(`/drafts/${draftId}`, {
      method: 'DELETE',
    });
  },

  getStats: async () => {
    return apiRequest<{
      total_drafts: number;
      pending_drafts: number;
      reviewed_drafts: number;
      sent_drafts: number;
      archived_drafts: number;
      avg_generation_time?: number;
    }>('/drafts/stats');
  },
};

// Newsletter Sends API
export const newsletterSendsApi = {
  send: async (
    draftId: string,
    recipientEmail: string,
    isTest = false,
    fromEmail?: string,
    fromName?: string
  ) => {
    return apiRequest<{ message: string; message_id: string }>('/newsletter-sends/send', {
      method: 'POST',
      body: JSON.stringify({
        draft_id: draftId,
        recipient_email: recipientEmail,
        is_test: isTest,
        from_email: fromEmail,
        from_name: fromName,
      }),
    });
  },

  getAll: async (page = 1, pageSize = 10, status?: string, draftId?: string) => {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (status) params.append('status', status);
    if (draftId) params.append('draft_id', draftId);

    return apiRequest<{ sends: any[]; total: number }>(`/newsletter-sends/?${params.toString()}`);
  },

  getStats: async () => {
    return apiRequest<{
      total_sends: number;
      successful_sends: number;
      failed_sends: number;
      open_rate: number;
      click_rate: number;
    }>('/newsletter-sends/stats');
  },
};
