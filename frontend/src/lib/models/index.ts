/**
 * Models - Central export for all data models
 */
export * from './memo';

// Re-export generated types for convenience
// These are auto-generated from the backend OpenAPI spec
// Run: npm run generate-types
export type { components, operations, paths } from './generated/api';

// Convenience aliases for commonly used generated types
export type MemoInDB = import('./generated/api').components['schemas']['MemoInDB'];
export type MemoCreateGen = import('./generated/api').components['schemas']['MemoCreate'];
export type MemoUpdateGen = import('./generated/api').components['schemas']['MemoUpdate'];

