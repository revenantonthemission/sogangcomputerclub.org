/**
 * Memo Model - Data structure for memo entities
 */
export interface Memo {
    id: number;
    title: string;
    content: string;
    tags: string[];
    priority: number;
    category: string | null;
    is_archived: boolean;
    is_favorite: boolean;
    author: string | null;
    created_at: string;
    updated_at: string;
}

export interface MemoCreate {
    title: string;
    content: string;
    tags?: string[];
    priority?: number;
    category?: string | null;
    is_archived?: boolean;
    is_favorite?: boolean;
    author?: string | null;
}

export interface MemoUpdate {
    title?: string;
    content?: string;
    tags?: string[];
    priority?: number;
    category?: string | null;
    is_archived?: boolean;
    is_favorite?: boolean;
    author?: string | null;
}
