// ============================================
// Siemens Signia Hearing Solutions - Main JS
// ============================================

document.addEventListener('DOMContentLoaded', () => {
  // Navbar scroll effect
  const navbar = document.querySelector('.navbar');
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 50);
  });

  // Mobile menu toggle
  const hamburger = document.querySelector('.hamburger');
  const navLinks = document.querySelector('.nav-links');
  if (hamburger) {
    hamburger.addEventListener('click', () => {
      hamburger.classList.toggle('active');
      navLinks.classList.toggle('active');
    });

    // Close menu on link click
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navLinks.classList.remove('active');
      });
    });
  }

  // Fade-up animation on scroll
  const fadeElements = document.querySelectorAll('.fade-up');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

  fadeElements.forEach(el => observer.observe(el));

  // Product filter tabs
  const filterTabs = document.querySelectorAll('.filter-tab');
  const categories = document.querySelectorAll('.price-category');

  filterTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const filter = tab.dataset.filter;

      filterTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      categories.forEach(cat => {
        if (filter === 'all' || cat.dataset.category === filter) {
          cat.style.display = 'block';
          cat.style.animation = 'fadeIn 0.4s ease';
        } else {
          cat.style.display = 'none';
        }
      });
    });
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // Active nav link highlight
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPage || (currentPage === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });

  // FAQ accordion functionality
  const faqQuestions = document.querySelectorAll('.faq-question');
  faqQuestions.forEach(question => {
    question.addEventListener('click', () => {
      const faqItem = question.parentElement;
      const answer = faqItem.querySelector('.faq-answer');
      const isActive = faqItem.classList.contains('active');

      // Close all other FAQs
      document.querySelectorAll('.faq-item').forEach(item => {
        if (item !== faqItem) {
          item.classList.remove('active');
          item.querySelector('.faq-answer').style.display = 'none';
        }
      });

      // Toggle current FAQ
      if (isActive) {
        faqItem.classList.remove('active');
        answer.style.display = 'none';
      } else {
        faqItem.classList.add('active');
        answer.style.display = 'block';
      }
    });
  });
});

// Fade-in keyframe for filter animation
const style = document.createElement('style');
style.textContent = `@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }`;
document.head.appendChild(style);

// ============================================
// Currency Switcher
// ============================================
const CURRENCY_RATES = {
  PKR: { rate: 1, symbol: 'Rs.', prefix: 'Rs.', name: 'PKR' },
  USD: { rate: 0.003583, symbol: '$', prefix: '$', name: 'USD' },
  EUR: { rate: 0.003116, symbol: '€', prefix: '€', name: 'EUR' }
};

let currentCurrency = 'PKR';
let originalPrices = [];

function initCurrencySwitcher() {
  // Support both table prices and product page price cards
  const priceCells = document.querySelectorAll('.price-table .price, .price-amount.price');
  if (!priceCells.length) return;

  // Store original PKR values
  priceCells.forEach((cell, i) => {
    const text = cell.textContent;
    const unitSpan = cell.querySelector('.price-unit');
    const unitText = unitSpan ? unitSpan.textContent : '';

    // Extract numbers - handle ranges like "Rs.120,000-280,000"
    const priceText = text.replace(unitText, '').trim();
    const numbers = priceText.match(/[\d,]+/g);

    originalPrices[i] = {
      values: numbers ? numbers.map(n => parseInt(n.replace(/,/g, ''))) : [],
      unit: unitText,
      isRange: numbers && numbers.length > 1
    };
  });

  // Add click handlers to currency buttons
  document.querySelectorAll('.currency-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const currency = btn.dataset.currency;
      if (currency === currentCurrency) return;

      document.querySelectorAll('.currency-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentCurrency = currency;
      convertPrices(currency);
    });
  });
}

function formatPrice(value, currency) {
  const c = CURRENCY_RATES[currency];
  const converted = Math.round(value * c.rate);

  if (currency === 'PKR') {
    return c.prefix + converted.toLocaleString('en-PK');
  } else if (currency === 'USD') {
    return c.prefix + converted.toLocaleString('en-US');
  } else {
    return c.prefix + converted.toLocaleString('de-DE');
  }
}

function convertPrices(currency) {
  const priceCells = document.querySelectorAll('.price-table .price, .price-amount.price');

  priceCells.forEach((cell, i) => {
    const data = originalPrices[i];
    if (!data || !data.values.length) return;

    let priceStr;
    if (data.isRange) {
      priceStr = formatPrice(data.values[0], currency) + '-' + formatPrice(data.values[1], currency).replace(CURRENCY_RATES[currency].prefix, '');
    } else {
      priceStr = formatPrice(data.values[0], currency);
    }

    // For product page price cards (no unit span)
    if (cell.classList.contains('price-amount')) {
      cell.textContent = priceStr;
    } else {
      cell.innerHTML = priceStr + ' <span class="price-unit">' + data.unit + '</span>';
    }
  });
}

document.addEventListener('DOMContentLoaded', initCurrencySwitcher);

// ============================================
// Conversion Tracking - WhatsApp & Call Clicks
// ============================================
document.addEventListener('DOMContentLoaded', () => {
  window.dataLayer = window.dataLayer || [];

  // Track all WhatsApp link clicks
  document.querySelectorAll('a[href*="wa.me"]').forEach(link => {
    link.addEventListener('click', () => {
      dataLayer.push({
        event: 'whatsapp_click',
        click_location: link.closest('nav') ? 'navbar' :
                        link.classList.contains('whatsapp-float') ? 'floating_button' :
                        link.closest('footer') ? 'footer' :
                        link.closest('.hero') ? 'hero' : 'page_body',
        page_url: window.location.href
      });
    });
  });

  // Track all Call link clicks
  document.querySelectorAll('a[href^="tel:"]').forEach(link => {
    link.addEventListener('click', () => {
      dataLayer.push({
        event: 'call_click',
        click_location: link.closest('footer') ? 'footer' : 'page_body',
        page_url: window.location.href
      });
    });
  });
});

// ============================================
// Testimonial Mobile Carousel Dots
// ============================================
function initTestimonialCarousel() {
  if (window.innerWidth > 768) return;
  const grid = document.querySelector('.testimonials-grid');
  if (!grid) return;

  const cards = grid.querySelectorAll('.testimonial-card');
  if (cards.length === 0) return;

  // Create dots container
  let dotsContainer = document.querySelector('.testimonial-dots');
  if (!dotsContainer) {
    dotsContainer = document.createElement('div');
    dotsContainer.className = 'testimonial-dots';
    dotsContainer.style.cssText = 'display:flex;justify-content:center;gap:8px;margin-top:16px;';
    grid.parentNode.insertBefore(dotsContainer, grid.nextSibling);

    cards.forEach((_, i) => {
      const dot = document.createElement('div');
      dot.style.cssText = `width:8px;height:8px;border-radius:50%;background:${i === 0 ? 'var(--signia-red)' : 'rgba(255,255,255,0.2)'};transition:all 0.3s;cursor:pointer;`;
      dot.addEventListener('click', () => {
        cards[i].scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
      });
      dotsContainer.appendChild(dot);
    });
  }

  // Update dots on scroll
  grid.addEventListener('scroll', () => {
    const scrollLeft = grid.scrollLeft;
    const cardWidth = cards[0].offsetWidth + 16;
    const activeIndex = Math.round(scrollLeft / cardWidth);
    dotsContainer.querySelectorAll('div').forEach((dot, i) => {
      dot.style.background = i === activeIndex ? 'var(--signia-red)' : 'rgba(255,255,255,0.2)';
    });
  });
}

document.addEventListener('DOMContentLoaded', initTestimonialCarousel);
window.addEventListener('resize', initTestimonialCarousel);
