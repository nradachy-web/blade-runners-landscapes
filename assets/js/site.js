// Blade Runners — site interactions
(function () {
  const header = document.getElementById('header');
  const stickyCta = document.getElementById('stickyCta');
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobileMenu');

  // Header shadow on scroll + reveal sticky CTA after first viewport
  let lastY = 0;
  function onScroll() {
    const y = window.scrollY;
    if (header) header.classList.toggle('header--scrolled', y > 8);
    if (stickyCta) stickyCta.classList.toggle('sticky-cta--visible', y > window.innerHeight * 0.6);
    lastY = y;
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Mobile menu toggle
  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', () => {
      const open = mobileMenu.classList.toggle('is-open');
      hamburger.classList.toggle('is-active', open);
      document.body.classList.toggle('menu-open', open);
    });
    mobileMenu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
      mobileMenu.classList.remove('is-open');
      hamburger.classList.remove('is-active');
      document.body.classList.remove('menu-open');
    }));
  }

  // Smooth scroll for hash links
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const id = a.getAttribute('href');
      if (id.length > 1) {
        const el = document.querySelector(id);
        if (el) {
          e.preventDefault();
          const offset = (header ? header.offsetHeight : 0) + 8;
          window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - offset, behavior: 'smooth' });
        }
      }
    });
  });

  // Reveal-on-scroll with safety fallback
  const revealEls = document.querySelectorAll('[data-animate], .svc-card, .review-card');
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('is-visible'); io.unobserve(e.target); } });
  }, { threshold: 0.05, rootMargin: '0px 0px -10% 0px' });
  revealEls.forEach(el => io.observe(el));
  // Fallback: any element still hidden after 1.8s gets revealed unconditionally
  // (covers headless screenshots, prefers-reduced-motion, broken JS environments)
  setTimeout(() => revealEls.forEach(el => el.classList.add('is-visible')), 1800);
})();
