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
		const openMenuButton = screen.getByLabelText(/open menu/i);
		expect(openMenuButton).toBeInTheDocument();

		// Click to open menu
		await fireEvent.click(openMenuButton);

		// Check if close button appears
		const closeMenuButton = screen.getByLabelText(/close menu/i);
		expect(closeMenuButton).toBeInTheDocument();
	});

	it('should render mobile menu icon on small screens', () => {
		// Set mobile viewport
		Object.defineProperty(window, 'innerWidth', {
			writable: true,
			configurable: true,
			value: 768
		});

		render(Header);

		// Mobile menu button should be visible
		const menuButton = screen.getByLabelText(/open menu/i);
		expect(menuButton).toBeInTheDocument();
	});

	it('should have accessible labels for buttons', () => {
		Object.defineProperty(window, 'innerWidth', {
			writable: true,
			configurable: true,
			value: 768
		});

		render(Header);

		// Check aria-label attributes
		const menuButton = screen.getByLabelText(/open menu/i);
		expect(menuButton).toHaveAttribute('aria-label');
	});
});
