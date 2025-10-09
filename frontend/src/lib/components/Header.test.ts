import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import Header from './Header.svelte';

describe('Header', () => {
	beforeEach(() => {
		// Mock window.innerWidth
		Object.defineProperty(window, 'innerWidth', {
			writable: true,
			configurable: true,
			value: 1024
		});
	});

	it('should render the header with logo and title', () => {
		render(Header);

		// Check if SGCC title is rendered
		expect(screen.getByText('SGCC')).toBeInTheDocument();
		expect(screen.getByText('Sogang computer club')).toBeInTheDocument();

		// Check if logo link exists
		const logoLink = screen.getByRole('link', { name: /main menu/i });
		expect(logoLink).toBeInTheDocument();
		expect(logoLink).toHaveAttribute('href', '/');
	});

	it('should have correct navigation structure', () => {
		render(Header);

		// Check header element exists
		const header = document.querySelector('header');
		expect(header).toBeInTheDocument();

		// Check nav element exists
		const nav = document.querySelector('nav');
		expect(nav).toBeInTheDocument();
	});

	it('should toggle mobile menu when button is clicked', async () => {
		// Set mobile viewport
		Object.defineProperty(window, 'innerWidth', {
			writable: true,
			configurable: true,
			value: 768
		});

		render(Header);

		// Find the open menu button
		const openMenuButton = screen.getByRole('button', { name: /open menu/i });
		expect(openMenuButton).toBeInTheDocument();

		// Click to open menu
		await fireEvent.click(openMenuButton);

		// Check if close button appears (should have multiple, checking for any)
		const closeMenuButtons = screen.getAllByRole('button', { name: /close menu/i });
		expect(closeMenuButtons.length).toBeGreaterThan(0);
	});

	it('should render mobile menu icon on small screens', () => {
		// Set mobile viewport before render
		Object.defineProperty(window, 'innerWidth', {
			writable: true,
			configurable: true,
			value: 768
		});

		// Trigger resize event
		window.dispatchEvent(new Event('resize'));

		render(Header);

		// Mobile menu button should be visible - check if it exists in DOM
		// In jsdom, desktop:hidden class should make it visible on mobile
		const buttons = document.querySelectorAll('button[aria-label]');
		const hasMenuButton = Array.from(buttons).some(
			(btn) =>
				btn.getAttribute('aria-label')?.toLowerCase().includes('menu') ||
				btn.getAttribute('aria-label')?.toLowerCase().includes('open')
		);
		expect(hasMenuButton).toBe(true);
	});

	it('should have accessible labels for buttons', () => {
		Object.defineProperty(window, 'innerWidth', {
			writable: true,
			configurable: true,
			value: 768
		});

		window.dispatchEvent(new Event('resize'));

		render(Header);

		// Check aria-label attributes exist on buttons
		const buttons = document.querySelectorAll('button[aria-label]');
		const hasAccessibleButton = Array.from(buttons).some((btn) =>
			btn.hasAttribute('aria-label')
		);
		expect(hasAccessibleButton).toBe(true);
	});
});
