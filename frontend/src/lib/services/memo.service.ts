/**
 * MemoService - Controller layer for memo operations
 * Handles API calls and business logic
 */
import type { Memo, MemoCreate, MemoUpdate } from '$lib/models';

// API configuration - Use full URL for SSR, relative URL for client
const API_BASE_URL = import.meta.env.PUBLIC_API_BASE_URL || (typeof window === 'undefined'
    ? 'http://backend:8000'
    : '/api');

/**
 * API 요청 래퍼 함수 - 공통 에러 처리 및 JSON 파싱
 */
async function apiRequest<T>(url: string, options?: RequestInit): Promise<T> {
    const response = await fetch(url, options);
    if (!response.ok) {
        const errorText = await response.text().catch(() => response.statusText);
        throw new Error(`API Error (${response.status}): ${errorText}`);
    }
    return response.json();
}

/**
 * Fetch all memos with pagination
 */
export async function getMemos(skip: number = 0, limit: number = 100): Promise<Memo[]> {
    return apiRequest<Memo[]>(`${API_BASE_URL}/memos/?skip=${skip}&limit=${limit}`);
}

/**
 * Fetch a single memo by ID
 */
export async function getMemo(id: number): Promise<Memo> {
    return apiRequest<Memo>(`${API_BASE_URL}/memos/${id}`);
}

/**
 * Create a new memo
 */
export async function createMemo(memo: MemoCreate): Promise<Memo> {
    return apiRequest<Memo>(`${API_BASE_URL}/memos/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(memo),
    });
}

/**
 * Update an existing memo
 */
export async function updateMemo(id: number, memo: MemoUpdate): Promise<Memo> {
    return apiRequest<Memo>(`${API_BASE_URL}/memos/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(memo),
    });
}

/**
 * Delete a memo
 */
export async function deleteMemo(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/memos/${id}`, {
        method: 'DELETE',
    });
    if (!response.ok) {
        const errorText = await response.text().catch(() => response.statusText);
        throw new Error(`API Error (${response.status}): ${errorText}`);
    }
}

/**
 * Search memos by query
 */
export async function searchMemos(query: string): Promise<Memo[]> {
    return apiRequest<Memo[]>(`${API_BASE_URL}/memos/search/?q=${encodeURIComponent(query)}`);
}
