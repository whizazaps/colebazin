(function () {
    var feature = document.querySelector('.home-feature');

    if (!feature) return;

    function toggleImage() {
        var isAlt = feature.classList.toggle('is-alt');
        feature.setAttribute('aria-pressed', String(isAlt));
    }

    feature.addEventListener('click', function (event) {
        event.stopPropagation();
        toggleImage();
    });

    feature.addEventListener('keydown', function (event) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            toggleImage();
        }
    });
})();