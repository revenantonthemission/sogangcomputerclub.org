/**
 * MemoStore - Reactive state management for memos
 * Uses Svelte 5 runes for reactivity
 */
import type { Memo } from '$lib/models';
import * as MemoService from '$lib/services/memo.service';

// State using Svelte 5 runes pattern (for use in .svelte files)
// For .ts files, we export functions that work with the service layer

/**
 * Create a memo store instance
 * Can be used in components with $state
 */
export function createMemoStore() {
    let memos = $state<Memo[]>([]);
    let loading = $state(false);
    let error = $state<string | null>(null);

    return {
        get memos() { return memos; },
        get loading() { return loading; },
        get error() { return error; },

        async loadMemos(skip: number = 0, limit: number = 100) {
            loading = true;
            error = null;
            try {
                memos = await MemoService.getMemos(skip, limit);
            } catch (e) {
                error = e instanceof Error ? e.message : 'Failed to load memos';
            } finally {
                loading = false;
            }
        },

        async createMemo(data: Parameters<typeof MemoService.createMemo>[0]) {
            loading = true;
            error = null;
            try {
                const newMemo = await MemoService.createMemo(data);
                memos = [...memos, newMemo];
                return newMemo;
            } catch (e) {
                error = e instanceof Error ? e.message : 'Failed to create memo';
                throw e;
            } finally {
                loading = false;
            }
        },

        async updateMemo(id: number, data: Parameters<typeof MemoService.updateMemo>[1]) {
            loading = true;
            error = null;
            try {
                const updatedMemo = await MemoService.updateMemo(id, data);
                memos = memos.map(m => m.id === id ? updatedMemo : m);
                return updatedMemo;
            } catch (e) {
                error = e instanceof Error ? e.message : 'Failed to update memo';
                throw e;
            } finally {
                loading = false;
            }
        },

        async deleteMemo(id: number) {
            loading = true;
            error = null;
            try {
                await MemoService.deleteMemo(id);
                memos = memos.filter(m => m.id !== id);
            } catch (e) {
                error = e instanceof Error ? e.message : 'Failed to delete memo';
                throw e;
            } finally {
                loading = false;
            }
        },

        async searchMemos(query: string) {
            loading = true;
            error = null;
            try {
                memos = await MemoService.searchMemos(query);
            } catch (e) {
                error = e instanceof Error ? e.message : 'Failed to search memos';
            } finally {
                loading = false;
            }
        }
    };
}
