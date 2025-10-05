<script>
    let { children } = $props();
    import "../app.css";
    import { page } from '$app/state'; 

    import Header from "../lib/components/Header.svelte"
    import Footer from "../lib/components/Footer.svelte"
  
    import { isMobileMenuOpen } from '$lib/Header.js';
 
 </script>

<style>
@font-face {
	font-family: 'Pretendard Variable';
	font-weight: 45 920;
	font-style: normal;
	font-display: swap;
	src: url('/fonts/PretendardVariable.woff2') format('woff2-variations');
}

@font-face {
	font-family: 'SogangUniversity';
	src: url('/fonts/SOGANG_UNIVERSITY_for_windows.ttf') format('truetype');
}
</style>

<div class="font-[Pretendard_Variable]">
<Header />
{@render children()}
{#if page.url.pathname !== '/login' && page.url.pathname !== '/' && page.url.pathname !== '/sign-up'}
  <footer><Footer /></footer>
{/if}
</div>