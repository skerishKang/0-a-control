// The Golden Flood - Interactive Features
class GoldenFloodReader {
    constructor() {
        this.init();
    }

    init() {
        this.setupLanguageToggle();
        this.setupNavigation();
        this.setupScrollProgress();
        this.setupScrollSync();
        this.setupSmoothScrolling();
        this.observeVisibleSections();
    }

    // Language Toggle Functionality
    setupLanguageToggle() {
        const englishBtn = document.getElementById('showEnglish');
        const koreanBtn = document.getElementById('showKorean');
        const bothBtn = document.getElementById('showBoth');
        const body = document.body;

        englishBtn.addEventListener('click', () => {
            this.setLanguageMode('english');
            this.updateActiveButton([englishBtn], [koreanBtn, bothBtn]);
        });

        koreanBtn.addEventListener('click', () => {
            this.setLanguageMode('korean');
            this.updateActiveButton([koreanBtn], [englishBtn, bothBtn]);
        });

        bothBtn.addEventListener('click', () => {
            this.setLanguageMode('both');
            this.updateActiveButton([bothBtn], [englishBtn, koreanBtn]);
        });
    }

    setLanguageMode(mode) {
        const body = document.body;
        body.className = body.className.replace(/lang-\w+/g, '');
        
        if (mode !== 'both') {
            body.classList.add(`lang-${mode}`);
        }

        // Store preference in localStorage
        localStorage.setItem('goldenFlood_language', mode);
    }

    updateActiveButton(activeButtons, inactiveButtons) {
        // Remove active class from all buttons
        inactiveButtons.forEach(btn => btn.classList.remove('active'));
        
        // Add active class to selected buttons
        activeButtons.forEach(btn => btn.classList.add('active'));
    }

    // Navigation System
    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href');
                
                if (targetId && targetId.startsWith('#')) {
                    this.scrollToSection(targetId);
                    this.setActiveNavLink(link);
                }
            });
        });

        // Load saved language preference
        const savedLanguage = localStorage.getItem('goldenFlood_language');
        if (savedLanguage) {
            this.setLanguageMode(savedLanguage);
            this.updateLanguageButtons(savedLanguage);
        }
    }

    updateLanguageButtons(mode) {
        const englishBtn = document.getElementById('showEnglish');
        const koreanBtn = document.getElementById('showKorean');
        const bothBtn = document.getElementById('showBoth');

        // Reset all buttons
        [englishBtn, koreanBtn, bothBtn].forEach(btn => btn.classList.remove('active'));

        // Set active button based on mode
        switch(mode) {
            case 'english':
                englishBtn.classList.add('active');
                break;
            case 'korean':
                koreanBtn.classList.add('active');
                break;
            default:
                bothBtn.classList.add('active');
        }
    }

    scrollToSection(targetId) {
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            const headerHeight = document.querySelector('.header').offsetHeight;
            const offsetTop = targetElement.offsetTop - headerHeight - 20;
            
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        }
    }

    setActiveNavLink(activeLink) {
        // Remove active class from all nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // Add active class to clicked link
        activeLink.classList.add('active');
    }

    // Scroll Progress Indicator
    setupScrollProgress() {
        const progressFill = document.querySelector('.progress-fill');
        const progressText = document.querySelector('.progress-text');
        
        if (!progressFill || !progressText) return;

        window.addEventListener('scroll', () => {
            const scrollTop = window.pageYOffset;
            const docHeight = document.documentElement.scrollHeight - window.innerHeight;
            const scrollPercent = (scrollTop / docHeight) * 100;
            
            progressFill.style.width = Math.min(scrollPercent, 100) + '%';
            progressText.textContent = Math.round(Math.min(scrollPercent, 100)) + '%';
        });
    }

    // Scroll Synchronization between columns
    setupScrollSync() {
        const dualColumns = document.querySelectorAll('.dual-column');
        
        dualColumns.forEach(column => {
            const englishCol = column.querySelector('.english-column');
            const koreanCol = column.querySelector('.korean-column');
            
            if (englishCol && koreanCol) {
                this.syncColumnHeights(englishCol, koreanCol);
            }
        });

        // Re-sync on window resize
        window.addEventListener('resize', () => {
            this.resyncAllColumns();
        });
    }

    syncColumnHeights(col1, col2) {
        const height1 = col1.scrollHeight;
        const height2 = col2.scrollHeight;
        const maxHeight = Math.max(height1, height2);
        
        col1.style.minHeight = maxHeight + 'px';
        col2.style.minHeight = maxHeight + 'px';
    }

    resyncAllColumns() {
        const dualColumns = document.querySelectorAll('.dual-column');
        
        dualColumns.forEach(column => {
            const englishCol = column.querySelector('.english-column');
            const koreanCol = column.querySelector('.korean-column');
            
            if (englishCol && koreanCol) {
                // Reset heights first
                englishCol.style.minHeight = 'auto';
                koreanCol.style.minHeight = 'auto';
                
                // Re-sync
                setTimeout(() => {
                    this.syncColumnHeights(englishCol, koreanCol);
                }, 100);
            }
        });
    }

    // Smooth Scrolling Enhancement
    setupSmoothScrolling() {
        // Enhance smooth scrolling for better performance
        document.documentElement.style.scrollBehavior = 'smooth';
        
        // Add keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case '1':
                        e.preventDefault();
                        this.scrollToSection('#part1');
                        break;
                    case '2':
                        e.preventDefault();
                        this.scrollToSection('#part2');
                        break;
                    case '3':
                        e.preventDefault();
                        this.scrollToSection('#part3');
                        break;
                }
            }
        });
    }

    // Intersection Observer for active section highlighting
    observeVisibleSections() {
        // Disabled auto-highlighting to prevent unwanted active states
        // Users can manually click navigation links to highlight sections
        return;
        
        const sections = document.querySelectorAll('.content-section[id]');
        const navLinks = document.querySelectorAll('.nav-link');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const sectionId = entry.target.id;
                    this.updateActiveNavigation(sectionId);
                }
            });
        }, {
            rootMargin: '-20% 0px -70% 0px',
            threshold: 0
        });

        sections.forEach(section => observer.observe(section));
    }

    updateActiveNavigation(activeId) {
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            
            const href = link.getAttribute('href');
            if (href === `#${activeId}`) {
                link.classList.add('active');
            }
        });
    }

    // Utility Methods
    debounce(func, wait) {
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

    // Search functionality (bonus feature)
    setupSearch() {
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Search in text...';
        searchInput.className = 'search-input';
        
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.appendChild(searchInput);
            
            searchInput.addEventListener('input', this.debounce((e) => {
                this.performSearch(e.target.value);
            }, 300));
        }
    }

    performSearch(query) {
        // Remove previous highlights
        this.clearHighlights();
        
        if (query.length < 3) return;

        const textNodes = this.getTextNodes();
        const regex = new RegExp(query, 'gi');
        
        textNodes.forEach(node => {
            if (regex.test(node.textContent)) {
                this.highlightText(node, regex);
            }
        });
    }

    getTextNodes() {
        const walker = document.createTreeWalker(
            document.querySelector('.content-area'),
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        const textNodes = [];
        let node;
        
        while (node = walker.nextNode()) {
            textNodes.push(node);
        }
        
        return textNodes;
    }

    highlightText(node, regex) {
        const parent = node.parentNode;
        const wrapper = document.createElement('span');
        wrapper.innerHTML = node.textContent.replace(regex, '<mark class="search-highlight">$&</mark>');
        parent.replaceChild(wrapper, node);
    }

    clearHighlights() {
        const highlights = document.querySelectorAll('.search-highlight');
        highlights.forEach(highlight => {
            const parent = highlight.parentNode;
            parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
            parent.normalize();
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new GoldenFloodReader();
    
    // Add some visual enhancements
    const style = document.createElement('style');
    style.textContent = `
        .search-highlight {
            background: #ffeb3b;
            padding: 2px 4px;
            border-radius: 2px;
            font-weight: bold;
        }
        
        .search-input {
            width: 100%;
            padding: 0.5rem;
            margin: 1rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 0.9rem;
        }
        
        .nav-link.active {
            font-weight: 600;
            color: white !important;
        }
        
        @media (prefers-reduced-motion: reduce) {
            * {
                scroll-behavior: auto !important;
            }
        }
    `;
    document.head.appendChild(style);
});

// Export for potential external use
window.GoldenFloodReader = GoldenFloodReader;