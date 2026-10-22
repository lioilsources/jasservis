/**
 * Mobile navigation for the static site. Keep the desktop menu unchanged.
 */
(function ($) {
    $.fn.mobileMenu = function () {
        return this.each(function (index) {
            var source = $(this);
            if (source.data('mobile-menu-ready')) return;
            source.data('mobile-menu-ready', true);

            var menuId = 'mobile-menu-' + index;
            // Copy links without the desktop handlers, IDs or Superfish classes.
            var menu = source.clone();
            menu.find('*').andSelf().removeAttr('id class style');
            menu.attr({id: menuId, 'class': 'mobile-menu-list'});
            var button = $('<button type="button" class="mobile-menu-toggle" aria-expanded="false"></button>')
                .attr('aria-controls', menuId)
                .append('<span class="mobile-menu-icon" aria-hidden="true"><span></span><span></span><span></span></span>')
                .append('<span class="mobile-menu-label">MENU</span>');
            source.after(menu);
            menu.before(button);

            function setOpen(open) {
                button.attr('aria-expanded', open ? 'true' : 'false');
                button.find('.mobile-menu-label').text(open ? 'ZAVŘÍT MENU' : 'MENU');
                menu.toggleClass('is-open', open);
            }

            button.on('click', function () {
                setOpen(button.attr('aria-expanded') !== 'true');
            });
            button.add(menu).on('keydown', function (event) {
                if (event.key === 'Escape' && button.attr('aria-expanded') === 'true') {
                    event.preventDefault();
                    setOpen(false);
                    button.focus();
                }
            });
            var mobile = window.matchMedia('(max-width: 767px)');
            function resetMenu() {
                var restoreFocus = !mobile.matches &&
                    (button[0] === document.activeElement || $.contains(menu[0], document.activeElement));
                setOpen(false);
                if (restoreFocus) source.find('a').first().focus();
            }
            if (mobile.addEventListener) mobile.addEventListener('change', resetMenu);
            else mobile.addListener(resetMenu);
        });
    };
})(jQuery);
