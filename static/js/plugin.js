// plugin.js

$(document).ready(function() {
    // Sticky 功能
    if ($('.sticky').length && $.fn.sticky) {
        $('.sticky').sticky();
    }

    // Slick 輪播
    if ($('.slick-slider').length && $.fn.slick) {
        $('.slick-slider').slick({
            autoplay: true,
            dots: true,
            arrows: false
            // 可依需求新增參數
        });
    }

    // Owl Carousel 輪播
    if ($('.owl-carousel').length && $.fn.owlCarousel) {
        $('.owl-carousel').owlCarousel({
            loop: true,
            margin: 10,
            nav: true,
            items: 1,
            autoplay: true,
            autoplayTimeout: 3000
            // 依需求調整
        });
    }

    // Counter Up 數字動畫
    if ($('.counter').length && $.fn.counterUp && typeof $.fn.counterUp === "function") {
        $('.counter').counterUp({
            delay: 10,
            time: 1000
        });
    }

    // Magnific Popup 燈箱
    if ($('.popup-link').length && $.fn.magnificPopup) {
        $('.popup-link').magnificPopup({
            type: 'image',
            gallery: {
                enabled: true
            }
            // 也可設定type: 'iframe' 等
        });
    }

    // niceSelect 美化 select
    if ($('select').length && $.fn.niceSelect) {
        $('select').niceSelect();
    }

    // Parallax 視差滾動
    if ($('.parallax').length && $.fn.parallax) {
        $('.parallax').parallax();
    }

    // Waypoints 動畫觸發或其他滾動事件
    if ($('.animate-on-scroll').length && window.Waypoint) {
        $('.animate-on-scroll').each(function(){
            var element = $(this);
            new Waypoint({
                element: this,
                handler: function(direction) {
                    element.addClass('in-view');
                    // 滾動進入畫面時加上動畫 class
                },
                offset: '75%'
            });
        });
    }

    // Mailchimp 郵件信箱 ajax 訂閱
    if ($('#mc-embedded-subscribe-form').length && $.fn.ajaxChimp) {
        $('#mc-embedded-subscribe-form').ajaxChimp();
    }

    
});
