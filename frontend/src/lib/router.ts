import { writable } from 'svelte/store';

export interface Route {
  path: string;
  component: any;
}

function createRouter() {
  const { subscribe, set } = writable(window.location.pathname);

  function navigate(path: string) {
    window.history.pushState({}, '', path);
    set(path);
  }

  // Listen to browser back/forward buttons
  window.addEventListener('popstate', () => {
    set(window.location.pathname);
  });

  // Intercept all clicks on links to prevent page reload
  // Only intercept <a> tags with href, not buttons or other elements
  document.addEventListener('click', (e) => {
    const target = e.target as HTMLElement;
    const link = target.closest('a[href]') as HTMLAnchorElement;
    
    // Only handle actual links (not buttons or other elements)
    // And only if they're internal links
    if (link && 
        link.tagName === 'A' && 
        link.href && 
        link.href.startsWith(window.location.origin) &&
        !link.hasAttribute('target') &&
        !link.hasAttribute('download')) {
      e.preventDefault();
      const path = link.href.replace(window.location.origin, '');
      navigate(path);
    }
  });

  return {
    subscribe,
    navigate,
  };
}

export const router = createRouter();
export const navigate = router.navigate;
