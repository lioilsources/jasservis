(function () {
    'use strict';
    var menu = document.getElementById('topnav');
    if (!menu) return;
    var nav = menu.parentElement;
    var compact = window.matchMedia('(max-width:1199px)');
    var tablet = window.matchMedia('(min-width:768px) and (max-width:1199px) and (min-height:501px)');
    var canHover = window.matchMedia('(hover:hover) and (pointer:fine)');
    var controls = [];
    var arrangingHeader = false;
    function isCompactMenu() { return (compact.matches || tablet.matches || nav.classList.contains('desktop-menu-collapsed')) && !nav.classList.contains('short-header-full-nav'); }
    // The rendered upper menu is the shared service list. Keep the static home
    // overview as a no-JavaScript fallback, and refresh it from that list here.
    var offered = document.querySelector('.home-service-index');
    if (offered) {
        Array.prototype.forEach.call(offered.querySelectorAll('[data-service-links]'), function (target) {
            var list = target.querySelector('ul');
            Array.prototype.forEach.call(target.getAttribute('data-service-links').split(' '), function (path, index) {
                var link = menu.querySelector('a[href="' + path + '"]');
                if (!link) return; // Retain the corresponding static fallback if a source link is absent.
                var item = document.createElement('li');
                var copy = document.createElement('a');
                copy.setAttribute('href', link.getAttribute('href'));
                copy.textContent = link.textContent;
                item.appendChild(copy);
                list.replaceChild(item, list.children[index]);
            });
        });
        var phoneOverview = window.matchMedia('(max-width:767px)');
        function resetOfferedGroups() {
            Array.prototype.forEach.call(offered.querySelectorAll('details'), function (group) {
                group.open = !phoneOverview.matches;
            });
        }
        resetOfferedGroups();
        if (phoneOverview.addEventListener) phoneOverview.addEventListener('change', resetOfferedGroups);
        else phoneOverview.addListener(resetOfferedGroups);
    }
    var toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'navigation-toggle';
    toggle.innerHTML = '<span class="mobile-menu-icon" aria-hidden="true"><span></span><span></span><span></span></span><span class="mobile-menu-label">MENU</span>';
    function syncToggle() {
        toggle.setAttribute('aria-expanded', String(!menu.hidden));
        toggle.querySelector('.mobile-menu-label').textContent = menu.hidden ? 'MENU' : 'ZAVŘÍT MENU';
    }
    toggle.setAttribute('aria-controls', menu.id);
    nav.insertBefore(toggle, menu);

    // Move the original navigation into a native modal; never duplicate links.
    var mobilePanel = document.createElement('dialog');
    mobilePanel.className = 'mobile-nav-panel';
    mobilePanel.id = 'mobile-nav-panel';
    toggle.setAttribute('aria-controls', mobilePanel.id);
    toggle.setAttribute('aria-haspopup', 'dialog');
    mobilePanel.setAttribute('aria-labelledby', 'mobile-nav-title');
    mobilePanel.innerHTML = '<div class="mobile-nav-toolbar"><h2 id="mobile-nav-title">Menu</h2><button type="button" class="mobile-nav-close">Zavřít <span aria-hidden="true">×</span></button></div><div class="mobile-nav-scroll"></div>';
    document.body.appendChild(mobilePanel);
    var menuSlot = document.createComment('original navigation position');
    var savedScroll;
    var booking = document.createElement('button');
    booking.type = 'button';
    booking.className = 'mobile-nav-booking';
    booking.textContent = 'Zavolat a objednat servis';
    var menuScroll = mobilePanel.querySelector('.mobile-nav-scroll');
    menuScroll.appendChild(booking);
    function closeMobilePanel(restoreFocus) {
        if (!mobilePanel.open) return;
        mobilePanel.close();
        menuSlot.parentNode.insertBefore(menu, menuSlot);
        menuSlot.remove();
        menu.hidden = true;
        controls.forEach(close);
        syncToggle();
        if (savedScroll) {
            var state = savedScroll;
            savedScroll = null;
            document.body.style.cssText = state.body;
            document.documentElement.style.overflow = state.overflow;
            window.scrollTo(state.x, state.y);
        }
        if (restoreFocus !== false) toggle.focus({preventScroll:true});
        window.requestAnimationFrame(arrangeShortHeader);
    }
    function openMobilePanel() {
        closeLanguage(false);
        controls.forEach(close);
        menu.parentNode.insertBefore(menuSlot, menu);
        menuScroll.insertBefore(menu, booking);
        menu.hidden = false;
        syncToggle();
        savedScroll = {x:window.scrollX,y:window.scrollY,body:document.body.style.cssText,overflow:document.documentElement.style.overflow};
        document.body.style.position = 'fixed';
        document.body.style.top = -savedScroll.y + 'px';
        document.body.style.left = -savedScroll.x + 'px';
        document.body.style.width = '100%';
        document.documentElement.style.overflow = 'hidden';
        mobilePanel.showModal();
        menuScroll.scrollTop = 0;
        mobilePanel.querySelector('.mobile-nav-close').focus();
    }
    mobilePanel.querySelector('.mobile-nav-close').addEventListener('click', function () { closeMobilePanel(); });
    mobilePanel.addEventListener('cancel', function (event) { event.preventDefault(); closeMobilePanel(); });
    mobilePanel.addEventListener('keydown', function (event) {
        if (event.key !== 'Tab') return;
        var focusable = Array.prototype.filter.call(mobilePanel.querySelectorAll('a[href],button:not([disabled])'), function (element) {
            return element.getClientRects().length && element.tabIndex >= 0;
        });
        var first = focusable[0], last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    });
    booking.addEventListener('click', function () {
        closeMobilePanel();
        var original = document.querySelector('.header [data-booking-panel]');
        if (original) original.click();
    });
    mobilePanel.addEventListener('click', function (event) {
        if (event.target.closest('a[href]')) closeMobilePanel(false);
    });
    function close(control) {
        window.clearTimeout(control.leaveTimer);
        control.hoverOpened = false;
        control.button.setAttribute('aria-expanded', 'false');
        control.button.setAttribute('aria-label', 'Rozbalit nabídku: ' + control.label);
        control.item.classList.remove('is-open');
        control.panel.hidden = true;
    }
    function fitDropdown(control) {
        if (isCompactMenu()) {
            control.panel.style.removeProperty('--menu-available');
            control.item.style.removeProperty('--service-menu-offset');
            return;
        }
        if (control.panel.classList.contains('service-groups')) {
            var header = nav.closest('header');
            var offset = header ? Math.max(0, header.getBoundingClientRect().bottom - control.item.getBoundingClientRect().bottom) : 0;
            control.item.style.setProperty('--service-menu-offset', Math.ceil(offset) + 'px');
        }
        var viewport = window.visualViewport;
        var bottom = viewport ? viewport.offsetTop + viewport.height : window.innerHeight;
        var banner = document.getElementById('cf-cookie-banner');
        if (banner && !banner.hidden) {
            var bannerBounds = banner.getBoundingClientRect();
            if (bannerBounds.height > 0) bottom = Math.min(bottom, bannerBounds.top);
        }
        var height = bottom - control.panel.getBoundingClientRect().top - 12;
        control.panel.style.setProperty('--menu-available', Math.max(44, Math.floor(height)) + 'px');
    }
    function open(control) {
        closeLanguage(false);
        controls.forEach(function (other) {
            if (other !== control) close(other);
        });
        window.clearTimeout(control.leaveTimer);
        control.panel.hidden = false;
        control.button.setAttribute('aria-expanded', 'true');
        control.button.setAttribute('aria-label', 'Zavřít nabídku: ' + control.label);
        control.item.classList.add('is-open');
        fitDropdown(control);
    }
    Array.prototype.forEach.call(menu.querySelectorAll('a[href]'), function (link) {
        var target = new URL(link.href, document.baseURI);
        if (target.origin === location.origin && target.pathname === location.pathname) link.setAttribute('aria-current', 'page');
        else link.removeAttribute('aria-current');
    });
    Array.prototype.forEach.call(menu.children, function (item) {
        var panel = item.querySelector('.sub-menu');
        if (!panel) return;
        var link = item.querySelector('.reviews-toggle') || item.querySelector('a');
        var button = item.querySelector('.reviews-toggle');
        if (!button) {
            button = document.createElement('button');
            button.type = 'button';
            button.className = 'submenu-toggle';
            button.textContent = '⌄';
            item.insertBefore(button, panel);
        }
        button.setAttribute('aria-label', 'Rozbalit nabídku: ' + link.textContent.replace(/\s*⌄\s*$/, ''));
        panel.id = item.id + '-submenu';
        button.setAttribute('aria-controls', panel.id);
        var control = {item: item, button: button, panel: panel, label: link.textContent.replace(/\s*⌄\s*$/, '').trim(), leaveTimer: null};
        controls.push(control);
        close(control);
        function toggle() {
            if (panel.hidden) open(control);
            else close(control);
        }
        button.addEventListener('click', function () {
            // Recenze is one tile that hover already opened; the click that follows keeps it open.
            if (control.hoverOpened && !panel.hidden) { control.hoverOpened = false; return; }
            toggle();
        });
        if (link !== button) {
            // A label is always a page link; the separate arrow controls its submenu.
            var overview = document.createElement('li');
            overview.className = 'menu-overview';
            var overviewLink = document.createElement('a');
            overviewLink.href = link.getAttribute('href');
            overviewLink.textContent = 'Přehled – ' + link.textContent.trim() + ' →';
            overview.appendChild(overviewLink);
            panel.insertBefore(overview, panel.firstChild);
        }
        item.addEventListener('pointerenter', function (event) {
            // Entering the arrow must leave its first click free to open the panel.
            // Entering the label (or the whole Recenze tile) opens the desktop menu on hover.
            var pointed = document.elementFromPoint(event.clientX, event.clientY);
            if (!canHover.matches || event.pointerType !== 'mouse' || isCompactMenu() || (languageDetails && languageDetails.open)) return;
            if (link === button) { if (panel.hidden) { open(control); control.hoverOpened = true; } }
            else if (!(pointed && button.contains(pointed))) open(control);
        });
        item.addEventListener('pointerleave', function (event) {
            if (!canHover.matches || event.pointerType !== 'mouse' || isCompactMenu()) return;
            control.leaveTimer = window.setTimeout(function () {
                if (!item.contains(document.activeElement)) close(control);
            }, 200);
        });
        item.addEventListener('focusout', function (event) {
            if (arrangingHeader) return;
            // In the mobile list, closing on blur moves the next button before its click.
            // The next category closes this panel atomically in open().
            if (!isCompactMenu() && !item.contains(event.relatedTarget)) close(control);
        });
        item.addEventListener('keydown', function (event) {
            if (event.key !== 'ArrowDown' || (event.target !== link && event.target !== button)) return;
            event.preventDefault();
            open(control);
            var first = panel.querySelector('a, button');
            if (first) first.focus();
        });
    });
    function reset() {
        if (mobilePanel.open) return;
        controls.forEach(close);
        menu.hidden = isCompactMenu();
        syncToggle();
    }
    toggle.addEventListener('click', function () {
        if (isCompactMenu()) { if (mobilePanel.open) closeMobilePanel(); else openMobilePanel(); return; }
        menu.hidden = !menu.hidden;
        syncToggle();
        if (menu.hidden) controls.forEach(close);
    });
    document.addEventListener('click', function (event) {
        if (!nav.contains(event.target) && !mobilePanel.contains(event.target)) {
            controls.forEach(close);
            if (isCompactMenu()) {
                menu.hidden = true;
                syncToggle();
            }
        }
    });
    nav.addEventListener('focusout', function (event) {
        if (arrangingHeader) return;
        if (!nav.contains(event.relatedTarget)) controls.forEach(close);
    });
    nav.addEventListener('keydown', function (event) {
        if (event.key !== 'Escape') return;
        var open = controls.filter(function (control) { return !control.panel.hidden; })[0];
        if (open) { close(open); open.button.focus(); }
        else if (isCompactMenu() && !menu.hidden) { menu.hidden = true; syncToggle(); toggle.focus(); }
    });
    function onNavigationBreakpoint() {
        if (!tablet.matches && !shortLandscape.matches) reset();
        arrangeShortHeader();
    }
    if (compact.addEventListener) compact.addEventListener('change', onNavigationBreakpoint);
    else compact.addListener(onNavigationBreakpoint);
    function fitOpenDropdowns() {
        controls.forEach(function (control) {
            if (!control.panel.hidden) fitDropdown(control);
        });
    }
    window.addEventListener('resize', fitOpenDropdowns);
    window.addEventListener('scroll', fitOpenDropdowns, {passive:true});
    if (window.visualViewport) {
        window.visualViewport.addEventListener('resize', fitOpenDropdowns);
        window.visualViewport.addEventListener('scroll', fitOpenDropdowns, {passive:true});
    }
    // Landscape uses a contact strip above a brand/navigation strip.
    // Move the original logo and controls, never copies of links or menu state.
    var shortLandscape = window.matchMedia('(max-width:1199px) and (max-height:500px) and (orientation:landscape)');
    var logo = document.querySelector('.header .logo');
    var logoHome = document.createComment('logo original position');
    var landscapeRow;
    var languageSwitch = document.querySelector('.language-switcher');
    var languageCompact = window.matchMedia('(max-width:1199px), (max-width:1399px) and (any-pointer:coarse)');
    var languageHome = document.createComment('language original position');
    var languageDetails = languageSwitch && languageSwitch.querySelector('.language-mobile');
    var languageSummary = languageDetails && languageDetails.querySelector('summary');
    if (languageSwitch) languageSwitch.parentNode.insertBefore(languageHome, languageSwitch);
    function closeLanguage(restoreFocus) {
        if (!languageDetails || !languageDetails.open) return;
        languageDetails.open = false;
        if (restoreFocus) languageSummary.focus({preventScroll:true});
    }
    function fitLanguagePanel() {
        if (!languageDetails || !languageDetails.open) return;
        var panel = languageDetails.querySelector('.language-options');
        var anchorBottom = languageSummary.getBoundingClientRect().bottom;
        Array.prototype.forEach.call(languageSwitch.closest('.header').querySelectorAll('a,button,summary'), function (element) {
            if (!languageSwitch.contains(element) && element.getClientRects().length) anchorBottom = Math.max(anchorBottom, element.getBoundingClientRect().bottom);
        });
        languageDetails.style.setProperty('--language-panel-gap', Math.max(6, anchorBottom - languageDetails.getBoundingClientRect().bottom + 6) + 'px');
        var viewport = window.visualViewport;
        var bottom = viewport ? viewport.offsetTop + viewport.height : window.innerHeight;
        languageDetails.style.setProperty('--language-available', Math.max(48, Math.min(240, bottom - panel.getBoundingClientRect().top - 8)) + 'px');
    }
    if (languageDetails) {
        languageDetails.addEventListener('toggle', function () {
            if (languageDetails.open) { controls.forEach(close); fitLanguagePanel(); }
        });
        languageDetails.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && languageDetails.open) {
                event.preventDefault(); event.stopPropagation(); closeLanguage(true);
            }
        });
        languageDetails.querySelector('.language-current').addEventListener('click', function () { closeLanguage(true); });
        document.addEventListener('click', function (event) { if (!languageSwitch.contains(event.target)) closeLanguage(false); });
        window.addEventListener('resize', fitLanguagePanel);
        if (window.visualViewport) window.visualViewport.addEventListener('resize', fitLanguagePanel);
    }

    if (logo) logo.parentNode.insertBefore(logoHome, logo);
    function arrangeShortHeader() {
        if (!logo) return;
        if (mobilePanel.open) { if (compact.matches) return; closeMobilePanel(false); }
        arrangingHeader = true;
        var focused = document.activeElement;
        var moved = false;
        var wasFull = nav.classList.contains('short-header-full-nav');
        var wasHidden = menu.hidden;
        if (shortLandscape.matches && !landscapeRow) {
            landscapeRow = document.createElement('div');
            landscapeRow.className = 'landscape-nav-row';
            nav.insertBefore(landscapeRow, menu);
            landscapeRow.appendChild(logo);
            landscapeRow.appendChild(toggle);
            moved = true;
        } else if (!shortLandscape.matches && landscapeRow) {
            logoHome.parentNode.insertBefore(logo, logoHome.nextSibling);
            if (menu.parentElement === landscapeRow) nav.insertBefore(menu, landscapeRow.nextSibling);
            nav.insertBefore(toggle, menu);
            if (languageSwitch && languageSwitch.parentNode === landscapeRow) nav.appendChild(languageSwitch);
            landscapeRow.remove();
            landscapeRow = null;
            moved = true;
        }
        if (languageSwitch) {
            var languageTarget = shortLandscape.matches ? landscapeRow : (compact.matches ? nav : languageHome.parentNode);
            if (languageSwitch.parentNode !== languageTarget) {
                languageTarget.appendChild(languageSwitch);
                moved = true;
            }
            languageSwitch.classList.add('language-ready');
            nav.classList.toggle('has-language-control', languageSwitch.parentNode === nav);
            if (!languageCompact.matches) closeLanguage(false);
        }
        nav.classList.toggle('tablet-navigation', tablet.matches);
        var wasCollapsed = nav.classList.contains('desktop-menu-collapsed');
        nav.classList.remove('desktop-menu-collapsed');
        if (shortLandscape.matches || tablet.matches) {
            // Measure actual labels and original touch areas, rather than device names.
            nav.classList.add('measuring-short-nav');
            menu.hidden = false;
            var needed = menu.getBoundingClientRect().width;
            var available = shortLandscape.matches ? landscapeRow.clientWidth - logo.getBoundingClientRect().width - 16 : nav.clientWidth;
            if (languageSwitch) available -= languageSwitch.getBoundingClientRect().width + 16;
            nav.classList.remove('measuring-short-nav');
            var fits = needed <= available;
            nav.classList.toggle('short-header-full-nav', fits);
            if (shortLandscape.matches && fits && menu.parentElement !== landscapeRow) {
                landscapeRow.appendChild(menu);
                moved = true;
            } else if (landscapeRow && !fits && menu.parentElement === landscapeRow) {
                nav.insertBefore(menu, landscapeRow.nextSibling);
                moved = true;
            }
            menu.hidden = fits ? false : (wasFull ? controls.every(function (control) { return control.panel.hidden; }) : wasHidden);
        } else {
            nav.classList.remove('short-header-full-nav');
            if (!compact.matches) {
                nav.classList.add('desktop-menu-measuring');
                menu.hidden = false;
                var desktopNeeded = menu.getBoundingClientRect().width;
                nav.classList.remove('desktop-menu-measuring');
                var desktopFits = desktopNeeded <= nav.clientWidth;
                nav.classList.toggle('desktop-menu-collapsed', !desktopFits);
                menu.hidden = desktopFits ? false : (wasCollapsed ? wasHidden : true);
            }
            else if (wasFull) menu.hidden = controls.every(function (control) { return control.panel.hidden; });
        }
        if (menu.hidden) controls.forEach(close);
        syncToggle();
        fitOpenDropdowns();
        fitLanguagePanel();
        var restoreFocus = moved || document.activeElement !== focused;
        if (restoreFocus && focused === toggle && !isCompactMenu()) menu.querySelector('a, button').focus({preventScroll: true});
        else if (restoreFocus && focused && focused.isConnected && (focused === toggle || logo.contains(focused) || (languageSwitch && languageSwitch.contains(focused) && languageSummary.getClientRects().length) || (!menu.hidden && menu.contains(focused)))) focused.focus({preventScroll: true});
        arrangingHeader = false;
    }
    if (tablet.addEventListener) tablet.addEventListener('change', arrangeShortHeader);
    else tablet.addListener(arrangeShortHeader);
    if (shortLandscape.addEventListener) shortLandscape.addEventListener('change', arrangeShortHeader);
    else shortLandscape.addListener(arrangeShortHeader);
    window.addEventListener('resize', arrangeShortHeader);
    if (window.visualViewport) window.visualViewport.addEventListener('resize', arrangeShortHeader);
    window.addEventListener('orientationchange', function () { window.requestAnimationFrame(arrangeShortHeader); });
    // Safari may restore an expanded menu from the back/forward cache.
    window.addEventListener('pageshow', function (event) { if (event.persisted) { closeMobilePanel(false); reset(); arrangeShortHeader(); } });
    nav.classList.add('navigation-ready');
    reset();
    arrangeShortHeader();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(arrangeShortHeader);
}());
