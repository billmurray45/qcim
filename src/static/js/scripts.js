// ========================================
// Mobile Detection Utility
// ========================================
const isMobileDevice = (() => {
  const userAgent = navigator.userAgent || navigator.vendor || window.opera;
  const isMobileUA = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent.toLowerCase());
  const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  const isSmallScreen = window.innerWidth <= 768;
  const result = isMobileUA || (isTouchDevice && isSmallScreen);
  return () => result;
})();

// ========================================
// Mobile Menu Toggle
// ========================================
const initMobileMenu = () => {
  const toggle = document.querySelector('.nav__toggle');
  const list = document.querySelector('.nav__list');
  const links = document.querySelectorAll('[data-link]');

  if (!toggle || !list) return;

  // Toggle menu
  toggle.addEventListener('click', (e) => {
    e.stopPropagation();
    const isOpen = list.classList.toggle('is-open');
    toggle.setAttribute('aria-expanded', String(isOpen));
  });

  // Close on link click
  links.forEach(link => {
    link.addEventListener('click', () => {
      list.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');

      // Update active state
      links.forEach(l => l.classList.remove('is-active'));
      link.classList.add('is-active');
    });
  });

  // Close on outside click
  document.addEventListener('click', (e) => {
    const inNav = e.target.closest('.nav');
    if (!inNav && list.classList.contains('is-open')) {
      list.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });
};

// ========================================
// Smooth Scroll for Anchor Links
// ========================================
const initSmoothScroll = () => {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href');

      // Skip empty anchors
      if (href === '#' || href === '#login') {
        e.preventDefault();
        return;
      }

      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();

        const headerOffset = 100;
        const elementPosition = target.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });
      }
    });
  });
};

// ========================================
// Counter Animation on Scroll
// ========================================
const initCounterAnimation = () => {
  const counterElements = document.querySelectorAll('.counter__value');

  if (counterElements.length === 0) return;

  const animateCounter = (element) => {
    const target = Number(element.dataset.target || 0);
    const suffix = element.dataset.suffix || '';
    const duration = 800;
    const fps = 60;
    const totalFrames = (duration / 1000) * fps;
    const increment = target / totalFrames;

    let currentValue = 0;
    let frame = 0;

    const updateCounter = () => {
      frame++;
      currentValue += increment;

      if (frame < totalFrames) {
        element.textContent = `${Math.floor(currentValue)}${suffix}`;
        requestAnimationFrame(updateCounter);
      } else {
        element.textContent = `${target}${suffix}`;
      }
    };

    updateCounter();
  };

  // Use Intersection Observer for triggering animation
  // Use more aggressive settings for mobile to ensure counters load earlier
  const isMobile = isMobileDevice();
  const observerOptions = {
    threshold: isMobile ? 0.01 : 0.2,
    rootMargin: isMobile ? '300px' : '100px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !entry.target.dataset.animated) {
        animateCounter(entry.target);
        entry.target.dataset.animated = 'true';
      }
    });
  }, observerOptions);

  counterElements.forEach(el => observer.observe(el));
};

// ========================================
// Newsletter Form Handler
// ========================================
const initNewsletterForm = () => {
  const form = document.getElementById('footerSubscribe');

  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const input = form.querySelector('input[type="email"]');
    const button = form.querySelector('button[type="submit"]');
    const email = input.value;

    // Simple validation
    if (!email || !email.includes('@')) {
      showToast('error', 'Ошибка', 'Введите корректный email адрес');
      return;
    }

    // Simulate submission
    button.textContent = 'Subscribing...';
    button.disabled = true;

    setTimeout(() => {
      button.textContent = 'Subscribed!';
      input.value = '';

      setTimeout(() => {
        button.textContent = 'Subscribe';
        button.disabled = false;
      }, 2000);
    }, 1000);
  });
};

// ========================================
// Scroll Animations with Animate.css
// ========================================
const initScrollAnimations = () => {
  const animatedElements = document.querySelectorAll('.animate-on-scroll');

  if (animatedElements.length === 0) return;

  const isMobile = isMobileDevice();

  // More aggressive settings for mobile devices
  const observerOptions = {
    threshold: isMobile ? 0.01 : 0.1,
    rootMargin: isMobile ? '300px 0px 300px 0px' : '0px 0px -100px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting && !entry.target.dataset.animated) {
        const animationType = entry.target.dataset.animation || 'fadeInUp';
        const delay = entry.target.dataset.delay || '0';

        // Добавляем задержку
        setTimeout(() => {
          entry.target.classList.add('animate__animated', `animate__${animationType}`);
          entry.target.dataset.animated = 'true';
          // Ensure visibility after animation
          entry.target.style.opacity = '1';
        }, parseInt(delay));
      }
    });
  }, observerOptions);

  animatedElements.forEach(el => {
    // Игнорируем элементы с GSAP классами (они анимируются через GSAP)
    if (el.classList.contains('gsap-scale') || el.classList.contains('gsap-text-reveal')) {
      return;
    }

    // CRITICAL FIX: Don't hide content on mobile devices
    // On mobile, content should be visible immediately to avoid blank screens
    if (!isMobile) {
      el.style.opacity = '0';
    } else {
      // On mobile, keep content visible but still observe for animation
      el.style.opacity = '1';
    }

    observer.observe(el);

    // После анимации делаем видимым
    el.addEventListener('animationstart', () => {
      el.style.opacity = '1';
    });
  });

  // Fallback: ensure all elements are visible after 3 seconds on mobile
  if (isMobile) {
    setTimeout(() => {
      animatedElements.forEach(el => {
        if (!el.dataset.animated) {
          el.style.opacity = '1';
          el.classList.add('animate__animated', 'animate__fadeIn');
          el.dataset.animated = 'true';
        }
      });
    }, 3000);
  }
};

// ========================================
// GSAP Animations
// ========================================
const initGSAPAnimations = () => {
  if (typeof gsap === 'undefined') {
    // GSAP not loaded - ensure all elements are visible
    console.warn('GSAP not loaded, ensuring content visibility');
    const gsapElements = document.querySelectorAll('[class*="gsap-"]');
    gsapElements.forEach(el => {
      el.style.opacity = '1';
      el.style.transform = 'none';
    });
    return;
  }

  gsap.registerPlugin(ScrollTrigger);

  const isMobile = isMobileDevice();

  // On mobile, use simpler, more reliable animations
  const mobileAnimationSettings = {
    duration: 0.6,
    ease: 'power2.out',
    scrollTrigger: {
      start: 'top 90%',
      toggleActions: 'play none none none'
    }
  };

  const desktopAnimationSettings = {
    duration: 1,
    ease: 'power2.out',
    scrollTrigger: {
      start: 'top 80%',
      toggleActions: 'play none none none'
    }
  };

  // Анимация секций с масштабированием
  gsap.utils.toArray('.gsap-scale').forEach((element) => {
    // Ensure element is visible first on mobile
    if (isMobile) {
      element.style.opacity = '1';
    }

    gsap.from(element, {
      scale: isMobile ? 0.95 : 0.9,
      opacity: isMobile ? 1 : 0,
      ...(isMobile ? mobileAnimationSettings : desktopAnimationSettings)
    });
  });

  // Анимация заголовков с разделением на буквы
  gsap.utils.toArray('.gsap-text-reveal').forEach((element) => {
    // Skip complex text animation on mobile
    if (isMobile) {
      element.style.opacity = '1';
      gsap.from(element, {
        y: 20,
        opacity: 0.5,
        ...mobileAnimationSettings
      });
      return;
    }

    const text = element.textContent;
    element.innerHTML = text.split('').map(char =>
      char === ' ' ? ' ' : `<span style="display:inline-block">${char}</span>`
    ).join('');

    gsap.from(element.querySelectorAll('span'), {
      y: 50,
      opacity: 0,
      rotationX: -90,
      stagger: 0.02,
      duration: 0.8,
      ease: 'back.out(1.7)',
      scrollTrigger: {
        trigger: element,
        start: 'top 80%',
        toggleActions: 'play none none none'
      }
    });
  });

  // Анимация появления слева/справа
  gsap.utils.toArray('.gsap-slide-left').forEach((element) => {
    if (isMobile) element.style.opacity = '1';

    gsap.from(element, {
      x: isMobile ? -30 : -100,
      opacity: isMobile ? 1 : 0,
      ...(isMobile ? mobileAnimationSettings : desktopAnimationSettings)
    });
  });

  gsap.utils.toArray('.gsap-slide-right').forEach((element) => {
    if (isMobile) element.style.opacity = '1';

    gsap.from(element, {
      x: isMobile ? 30 : 100,
      opacity: isMobile ? 1 : 0,
      ...(isMobile ? mobileAnimationSettings : desktopAnimationSettings)
    });
  });

  // 3D эффект для карточек (упрощенный на мобильных)
  gsap.utils.toArray('.gsap-3d-card').forEach((element) => {
    if (isMobile) {
      element.style.opacity = '1';
      gsap.from(element, {
        y: 20,
        opacity: 0.5,
        ...mobileAnimationSettings
      });
    } else {
      gsap.from(element, {
        rotationY: -45,
        opacity: 0,
        duration: 1.2,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: element,
          start: 'top 85%',
          toggleActions: 'play none none none'
        }
      });
    }
  });

  // Fallback: ensure all GSAP elements are visible after delay on mobile
  if (isMobile) {
    setTimeout(() => {
      const gsapElements = document.querySelectorAll('[class*="gsap-"]');
      gsapElements.forEach(el => {
        el.style.opacity = '1';
      });
    }, 2000);
  }
};

// ========================================
// Active Navigation Link on Scroll
// ========================================
const initActiveNavOnScroll = () => {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav__link[data-link]');

  if (sections.length === 0 || navLinks.length === 0) return;

  const updateActiveLink = () => {
    const scrollPosition = window.scrollY + 150;

    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.offsetHeight;
      const sectionId = section.getAttribute('id');

      if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
        navLinks.forEach(link => {
          link.classList.remove('is-active');
          if (link.getAttribute('href') === `#${sectionId}`) {
            link.classList.add('is-active');
          }
        });
      }
    });

    // Handle home section at the top
    if (window.scrollY < 100) {
      navLinks.forEach(link => link.classList.remove('is-active'));
      const homeLink = document.querySelector('.nav__link[href="#home"]');
      if (homeLink) homeLink.classList.add('is-active');
    }
  };

  // Throttle scroll event for performance
  let ticking = false;
  window.addEventListener('scroll', () => {
    if (!ticking) {
      window.requestAnimationFrame(() => {
        updateActiveLink();
        ticking = false;
      });
      ticking = true;
    }
  });
};

// ========================================
// Header Scroll Effect
// ========================================
const initHeaderScroll = () => {
  const header = document.querySelector('.header');

  if (!header) return;

  let lastScroll = 0;

  window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;

    if (currentScroll > 50) {
      header.style.background = 'rgba(0, 125, 68, 0.98)';
      header.style.backdropFilter = 'blur(10px)';
      header.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.5)';
    } else {
      header.style.background = 'transparent';
      header.style.backdropFilter = 'none';
      header.style.boxShadow = 'none';
    }

    lastScroll = currentScroll;
  });
};

// ========================================
// Parallax Effect for Hero Shapes
// ========================================
const initParallaxEffect = () => {
  const shapes = document.querySelectorAll('.shape');

  if (shapes.length === 0) return;

  let rafPending = false;
  window.addEventListener('scroll', () => {
    if (rafPending) return;
    rafPending = true;
    requestAnimationFrame(() => {
      const scrolled = window.pageYOffset;
      shapes.forEach((shape, index) => {
        const speed = 0.1 + (index * 0.05);
        const yPos = -(scrolled * speed);
        shape.style.transform = `translateY(${yPos}px) rotate(${shape.classList.contains('shape--slash') ? '32deg' : shape.classList.contains('shape--curve') ? '-18deg' : '0deg'})`;
      });
      rafPending = false;
    });
  });
};

// ========================================
// Modal Functionality
// ========================================
const initModals = () => {
  const loginModal = document.getElementById('loginModal');
  const profileModal = document.getElementById('profileModal');
  const loginBtn = document.getElementById('loginBtn');
  const profileBtn = document.getElementById('profileBtn');
  const closeButtons = document.querySelectorAll('.modal__close');
  const overlays = document.querySelectorAll('.modal__overlay');

  // Open login modal
  if (loginBtn) {
    loginBtn.addEventListener('click', function (e) {
      e.preventDefault();
      openModal(loginModal);
    });
  }

  // Open profile modal
  if (profileBtn) {
    profileBtn.addEventListener('click', function (e) {
      e.preventDefault();
      openModal(profileModal);
    });
  }

  // Close modals on close button click
  closeButtons.forEach(button => {
    button.addEventListener('click', function () {
      closeAllModals();
    });
  });

  // Close modals on overlay click
  overlays.forEach(overlay => {
    overlay.addEventListener('click', function () {
      closeAllModals();
    });
  });

  // Close modals on ESC key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeAllModals();
    }
  });

  // Handle login form submission via AJAX
  const loginForm = document.querySelector('#loginModal .modal__form');
  if (loginForm) {
    loginForm.addEventListener('submit', function (e) {
      e.preventDefault();

      // Remove previous error if exists
      const existingError = loginForm.querySelector('.modal__error');
      if (existingError) {
        existingError.remove();
      }

      const formData = new FormData(loginForm);
      const submitButton = loginForm.querySelector('button[type="submit"]');
      const originalButtonText = submitButton.textContent;

      // Disable button and show loading state
      submitButton.disabled = true;
      submitButton.textContent = 'Вход...';

      fetch(loginForm.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            // Success - reload page to show success message
            window.location.reload();
          } else {
            // Show error in modal
            const errorDiv = document.createElement('div');
            errorDiv.className = 'modal__error';
            errorDiv.textContent = data.error;
            loginForm.insertBefore(errorDiv, loginForm.firstChild);

            // Re-enable button
            submitButton.disabled = false;
            submitButton.textContent = originalButtonText;
          }
        })
        .catch(error => {
          console.error('Login error:', error);

          // Show generic error
          const errorDiv = document.createElement('div');
          errorDiv.className = 'modal__error';
          errorDiv.textContent = 'Произошла ошибка. Попробуйте еще раз.';
          loginForm.insertBefore(errorDiv, loginForm.firstChild);

          // Re-enable button
          submitButton.disabled = false;
          submitButton.textContent = originalButtonText;
        });
    });
  }

  function openModal(modal) {
    if (modal) {
      modal.classList.add('is-active');
      document.body.style.overflow = 'hidden';
    }
  }

  function closeAllModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
      modal.classList.remove('is-active');
    });
    document.body.style.overflow = '';
  }
};

// ========================================
// Messages Auto-dismiss
// ========================================
const initMessages = () => {
  // no-op: toast logic handled inline in base.html
};

// ========================================
// Toast helper
// ========================================
function showToast(type, label, text) {
  const DURATION = 4000;

  const icons = {
    success: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    error:   '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
    warning: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    info:    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>'
  };

  const toast = document.createElement('div');
  toast.className = 'toast toast--' + type;
  toast.setAttribute('role', 'alert');
  toast.innerHTML =
    '<div class="toast__icon">' + (icons[type] || icons.info) + '</div>' +
    '<div class="toast__body">' +
      '<p class="toast__label">' + label + '</p>' +
      '<p class="toast__text">' + text + '</p>' +
    '</div>' +
    '<button class="toast__close" aria-label="Закрыть">' +
      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>' +
    '</button>' +
    '<div class="toast__progress"></div>';

  let container = document.querySelector('.messages-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'messages-container';
    document.body.appendChild(container);
  }
  container.appendChild(toast);

  function dismiss() {
    toast.classList.add('toast--leaving');
    toast.addEventListener('animationend', function () { toast.remove(); }, { once: true });
  }

  let timer = setTimeout(dismiss, DURATION);

  toast.querySelector('.toast__close').addEventListener('click', function () {
    clearTimeout(timer);
    dismiss();
  });

  toast.addEventListener('mouseenter', function () {
    clearTimeout(timer);
    const bar = toast.querySelector('.toast__progress');
    if (bar) bar.style.animationPlayState = 'paused';
  });

  toast.addEventListener('mouseleave', function () {
    const bar = toast.querySelector('.toast__progress');
    if (bar) bar.style.animationPlayState = 'running';
    timer = setTimeout(dismiss, 1500);
  });
}

// ========================================
// Contact Form Handler
// ========================================
const initContactForm = () => {
  const form = document.getElementById('contact-form');
  if (!form) return;

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');
    const originalHTML = submitButton.innerHTML;

    form.querySelectorAll('.form-error').forEach(el => el.remove());

    submitButton.disabled = true;
    submitButton.innerHTML = 'Отправка...';

    try {
      const response = await fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });

      const data = await response.json();

      if (data.success) {
        form.reset();
        showToast('success', 'Успешно', data.message);
      } else {
        if (data.errors) {
          for (const [field, errors] of Object.entries(data.errors)) {
            const input = form.querySelector(`[name="${field}"]`);
            if (input) {
              const el = document.createElement('div');
              el.className = 'form-error';
              el.textContent = errors[0];
              input.parentElement.appendChild(el);
            }
          }
        }
        showToast('error', 'Ошибка', data.message || 'Пожалуйста, исправьте ошибки в форме.');
      }
    } catch (err) {
      showToast('error', 'Ошибка', 'Произошла ошибка при отправке. Попробуйте ещё раз.');
    } finally {
      submitButton.disabled = false;
      submitButton.innerHTML = originalHTML;
    }
  });
};

// ========================================
// FAQ Accordion
// ========================================
const initFAQAccordion = () => {
  const faqItems = document.querySelectorAll('.faq-item');

  if (faqItems.length === 0) return;

  faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    const answer = item.querySelector('.faq-answer');

    if (!question || !answer) return;

    question.addEventListener('click', () => {
      const isActive = item.classList.contains('active');

      // Close all other items
      faqItems.forEach(otherItem => {
        if (otherItem !== item) {
          otherItem.classList.remove('active');
          const otherAnswer = otherItem.querySelector('.faq-answer');
          const otherQuestion = otherItem.querySelector('.faq-question');
          if (otherAnswer) otherAnswer.style.maxHeight = '0';
          if (otherQuestion) otherQuestion.setAttribute('aria-expanded', 'false');
        }
      });

      // Toggle current item
      if (isActive) {
        item.classList.remove('active');
        answer.style.maxHeight = '0';
        question.setAttribute('aria-expanded', 'false');
      } else {
        item.classList.add('active');
        answer.style.maxHeight = answer.scrollHeight + 'px';
        question.setAttribute('aria-expanded', 'true');
      }
    });
  });

  // Set initial max-height for active item
  const activeItem = document.querySelector('.faq-item.active');
  if (activeItem) {
    const activeAnswer = activeItem.querySelector('.faq-answer');
    if (activeAnswer) {
      activeAnswer.style.maxHeight = activeAnswer.scrollHeight + 'px';
    }
  }
};

// ========================================
// Hero Slider Functionality
// ========================================
const initHeroSlider = () => {
  const sliderItems = document.querySelectorAll('.slide__item');

  if (sliderItems.length === 0) return;

  // Click handler for slide items
  sliderItems.forEach(item => {
    item.addEventListener('click', function () {
      // Only trigger if not already open
      if (!this.classList.contains('open')) {
        const currentOpen = document.querySelector('.slide__item.open');

        // If there's a currently open slide, add closing class
        if (currentOpen) {
          currentOpen.classList.add('closing');

          // Wait for closing animation before removing open class
          setTimeout(() => {
            currentOpen.classList.remove('open', 'closing');
          }, 300);
        }

        // Add 'open' class to clicked item with slight delay for smooth transition
        setTimeout(() => {
          this.classList.add('open');

          // Trigger reflow to restart animations
          const textElements = this.querySelectorAll('.slide__title, .slide__desc, .slide__text .btn');
          textElements.forEach(el => {
            el.style.animation = 'none';
            el.offsetHeight; // Trigger reflow
            el.style.animation = null;
          });
        }, currentOpen ? 150 : 0);
      }
    });
  });
};

// ========================================

// ========================================
// Team Tabs Functionality
// ========================================
const initTeamTabs = () => {
  const tabButtons = document.querySelectorAll('.team-tabs__btn');
  const tabPanels = document.querySelectorAll('.team-tabs__panel');

  if (tabButtons.length === 0 || tabPanels.length === 0) return;

  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      const targetTab = button.dataset.tab;

      // Remove active class from all
      tabButtons.forEach(btn => btn.classList.remove('active'));
      tabPanels.forEach(panel => panel.classList.remove('active'));

      // Add active class to clicked
      button.classList.add('active');
      const targetPanel = document.querySelector(`.team-tabs__panel[data-panel="${targetTab}"]`);
      if (targetPanel) {
        targetPanel.classList.add('active');
      }
    });
  });
};

// ========================================
// Auth Modal Functionality
// ========================================
function openAuthModal() {
  const modal = document.getElementById('auth-modal');
  if (modal) {
    modal.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  }
}

function closeAuthModal() {
  const modal = document.getElementById('auth-modal');
  if (modal) {
    modal.classList.remove('is-open');
    document.body.style.overflow = '';
  }
}

function openProfileModal() {
  const modal = document.getElementById('profile-modal');
  if (modal) {
    modal.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  }
}

function closeProfileModal() {
  const modal = document.getElementById('profile-modal');
  if (modal) {
    modal.classList.remove('is-open');
    document.body.style.overflow = '';
  }
}

const initAuthModal = () => {
  const modal = document.getElementById('auth-modal');
  if (!modal) return;

  const tabs = modal.querySelectorAll('.auth-tab');
  const panels = modal.querySelectorAll('.auth-panel');

  // Tab switching
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const targetPanel = tab.dataset.tab;

      // Update tabs
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      // Update panels
      panels.forEach(panel => {
        panel.classList.remove('active');
        if (panel.id === `${targetPanel}-panel`) {
          panel.classList.add('active');
        }
      });

      // Clear errors when switching tabs
      clearFormErrors(modal);
    });
  });

  // Close on ESC
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (modal && modal.classList.contains('is-open')) {
        closeAuthModal();
      }
      const profileModal = document.getElementById('profile-modal');
      if (profileModal && profileModal.classList.contains('is-open')) {
        closeProfileModal();
      }
    }
  });

  // Login form handler
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', handleAuthFormSubmit);
  }

  // Register form handler
  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.addEventListener('submit', handleAuthFormSubmit);
  }
};

// Clear form errors
function clearFormErrors(container) {
  const errors = container.querySelectorAll('.auth-form__error');
  errors.forEach(err => err.remove());

  const inputs = container.querySelectorAll('.auth-form__input.has-error');
  inputs.forEach(input => input.classList.remove('has-error'));

  const generalError = container.querySelector('.auth-form__general-error');
  if (generalError) generalError.remove();
}

// Handle auth form submission
async function handleAuthFormSubmit(e) {
  e.preventDefault();

  const form = e.target;
  const submitBtn = form.querySelector('.auth-form__submit');
  const originalBtnText = submitBtn.textContent;
  const isLogin = form.id === 'login-form';

  // Clear previous errors
  clearFormErrors(form);

  // Disable button and show loading
  submitBtn.disabled = true;
  submitBtn.textContent = isLogin ? 'Вход...' : 'Регистрация...';

  try {
    const formData = new FormData(form);

    const response = await fetch(form.action, {
      method: 'POST',
      body: formData,
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    });

    const data = await response.json();

    if (data.success) {
      // Success - reload page
      window.location.reload();
    } else {
      // Show field errors
      if (data.errors) {
        for (const [field, message] of Object.entries(data.errors)) {
          const input = form.querySelector(`[name="${field}"]`);
          if (input) {
            input.classList.add('has-error');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'auth-form__error';
            errorDiv.textContent = message;
            input.parentElement.appendChild(errorDiv);
          }
        }
      }

      // Show general error
      if (data.message || data.error) {
        const generalError = document.createElement('div');
        generalError.className = 'auth-form__general-error';
        generalError.textContent = data.message || data.error;
        form.insertBefore(generalError, form.firstChild);
      }
    }
  } catch (error) {
    console.error('Auth form error:', error);
    const generalError = document.createElement('div');
    generalError.className = 'auth-form__general-error';
    generalError.textContent = 'Произошла ошибка. Попробуйте ещё раз.';
    form.insertBefore(generalError, form.firstChild);
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = originalBtnText;
  }
}

// ========================================
// Initialize All Features
// ========================================
const init = () => {
  // Core functionality
  initMobileMenu();
  initSmoothScroll();
  initCounterAnimation();
  initNewsletterForm();
  initModals();
  initAuthModal();
  initMessages();
  initFAQAccordion();
  initContactForm();

  // Hero Slider
  initHeroSlider();

  // Team Tabs
  initTeamTabs();

  // Enhanced features
  initScrollAnimations();
  initGSAPAnimations();
  initActiveNavOnScroll();
  initHeaderScroll();
  initParallaxEffect();

  console.log('Business Consulting website initialized successfully!');
};

// Wait for DOM to be ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

// ========================================
// Utility Functions
// ========================================

// Debounce function for performance
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Throttle function for performance
function throttle(func, limit) {
  let inThrottle;
  return function (...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// Export for potential use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    debounce,
    throttle,
    init
  };
}
