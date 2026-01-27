/**
 * API Module - Re-exports for backward compatibility
 * 
 * @deprecated Import from '$lib/models' and '$lib/services' instead
 * 
 * Example:
 *   import type { Memo } from '$lib/models';
 *   import { getMemos, createMemo } from '$lib/services';
 */

// Re-export models
export type { Memo, MemoCreate, MemoUpdate } from '$lib/models';

// Re-export services
export {
    getMemos,
    getMemo,
    createMemo,
    updateMemo,
    deleteMemo,
    searchMemos
} from '$lib/services';
