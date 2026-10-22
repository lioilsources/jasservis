(function () {
    'use strict';
    var menu = document.getElementById('topnav');
    if (!menu) return;
    var nav = menu.parentElement;
    var compact = window.matchMedia('(max-width:1199px)');
    var controls = [];
    var groupControls = [];
    var toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'navigation-toggle';
    toggle.textContent = 'Menu';
    toggle.setAttribute('aria-controls', menu.id);
    nav.insertBefore(toggle, menu);

    function fit(panel) {
        if (!compact.matches && !panel.hidden) {
            var bottom = window.innerHeight;
            var banner = document.getElementById('cf-cookie-banner');
            if (banner && window.getComputedStyle(banner).position === 'fixed') {
                var rect = banner.getBoundingClientRect();
                if (rect.height > 0 && rect.top >= 0 && rect.top < bottom) bottom = rect.top;
            }
            panel.style.maxHeight = Math.max(0, bottom - panel.getBoundingClientRect().top - 16) + 'px';
        }
    }
    function close(control) {
        control.button.setAttribute('aria-expanded', 'false');
        control.panel.hidden = true;
        groupControls.forEach(function (group) {
            if (control.panel.contains(group.panel)) {
                group.panel.hidden = true;
                group.button.setAttribute('aria-expanded', 'false');
            }
        });
    }
    Array.prototype.forEach.call(menu.children, function (item) {
        var panel = item.querySelector('.sub-menu');
        if (!panel) return;
        var link = item.querySelector('a');
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'submenu-toggle';
        button.textContent = '⌄';
        button.setAttribute('aria-label', 'Rozbalit nabídku: ' + link.textContent);
        panel.id = item.id + '-submenu';
        button.setAttribute('aria-controls', panel.id);
        item.insertBefore(button, panel);
        var control = {button: button, panel: panel};
        controls.push(control);
        close(control);
        button.addEventListener('click', function () {
            var open = panel.hidden;
            controls.forEach(close);
            panel.hidden = !open;
            button.setAttribute('aria-expanded', String(open));
            fit(panel);
        });
    });
    Array.prototype.forEach.call(menu.querySelectorAll('.service-group'), function (group, index) {
        var title = group.querySelector('.service-group-title');
        var list = group.querySelector('ul');
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'service-group-title';
        button.textContent = title.textContent;
        list.id = 'service-group-' + index;
        list.hidden = true;
        button.setAttribute('aria-controls', list.id);
        button.setAttribute('aria-expanded', 'false');
        title.parentNode.replaceChild(button, title);
        groupControls.push({button: button, panel: list});
        button.addEventListener('click', function () {
            var open = list.hidden;
            groupControls.forEach(function (control) {
                control.panel.hidden = true;
                control.button.setAttribute('aria-expanded', 'false');
            });
            list.hidden = !open;
            button.setAttribute('aria-expanded', String(open));
            var panel = group.parentElement;
            panel.scrollTop = 0;
            fit(panel);
        });
    });
    function reset() {
        controls.forEach(close);
        menu.hidden = compact.matches;
        toggle.setAttribute('aria-expanded', String(!menu.hidden));
    }
    toggle.addEventListener('click', function () {
        menu.hidden = !menu.hidden;
        toggle.setAttribute('aria-expanded', String(!menu.hidden));
        if (menu.hidden) controls.forEach(close);
    });
    document.addEventListener('click', function (event) {
        if (!nav.contains(event.target)) controls.forEach(close);
    });
    nav.addEventListener('focusout', function (event) {
        if (!nav.contains(event.relatedTarget)) controls.forEach(close);
    });
    nav.addEventListener('keydown', function (event) {
        if (event.key !== 'Escape') return;
        var group = groupControls.filter(function (control) { return !control.panel.hidden; })[0];
        if (group) {
            group.panel.hidden = true;
            group.button.setAttribute('aria-expanded', 'false');
            group.button.focus();
            event.preventDefault();
            return;
        }
        var open = controls.filter(function (control) { return !control.panel.hidden; })[0];
        if (open) { close(open); open.button.focus(); }
        else if (compact.matches && !menu.hidden) { menu.hidden = true; toggle.setAttribute('aria-expanded', 'false'); toggle.focus(); }
    });
    window.addEventListener('resize', function () { controls.forEach(function (control) { fit(control.panel); }); });
    window.addEventListener('scroll', function () { controls.forEach(function (control) { fit(control.panel); }); }, {passive:true});
    if (compact.addEventListener) compact.addEventListener('change', reset);
    else compact.addListener(reset);
    nav.classList.add('navigation-ready');
    reset();
}());
