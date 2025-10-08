import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { resolve } from 'path';

export default defineConfig({
	plugins: [svelte({ hot: !process.env.VITEST })],
	test: {
		environment: 'happy-dom',
		globals: true,
		setupFiles: ['./vitest-setup.ts']
	},
	resolve: {
		alias: {
			$lib: resolve('./src/lib')
		}
	}
});
