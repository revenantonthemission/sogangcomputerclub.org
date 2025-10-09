import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/svelte';
import Page from './+page.svelte';

describe('About Us - Welcome Page', () => {
	it('should render the welcome page', () => {
		const { container } = render(Page);

		expect(container).toBeTruthy();
	});

	it('should have content rendered', () => {
		const { container } = render(Page);

		// Page should have some content
		expect(container.firstChild).toBeTruthy();
	});
});
