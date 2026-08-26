// Click-to-enlarge lightbox for post images, with scroll/pinch zoom + drag pan
(function () {
    var overlay = document.createElement('div');
    overlay.className = 'lightbox-overlay';
    var img = document.createElement('img');
    var closeBtn = document.createElement('button');
    closeBtn.className = 'lightbox-close';
    closeBtn.setAttribute('aria-label', 'Close');
    closeBtn.textContent = '\u00D7';
    overlay.appendChild(img);
    overlay.appendChild(closeBtn);
    document.body.appendChild(overlay);

    var MIN_SCALE = 1;
    var MAX_SCALE = 4;
    var scale = 1;
    var originX = 0; // pan offset in px
    var originY = 0;

    function applyTransform() {
        img.style.transform = 'translate(' + originX + 'px, ' + originY + 'px) scale(' + scale + ')';
    }

    function resetZoom() {
        scale = 1;
        originX = 0;
        originY = 0;
        applyTransform();
    }

    function clampScale(s) {
        return Math.min(MAX_SCALE, Math.max(MIN_SCALE, s));
    }

    function open(src, alt) {
        img.src = src;
        img.alt = alt || '';
        resetZoom();
        overlay.classList.add('open');
    }

    function close() {
        overlay.classList.remove('open');
        img.src = '';
        resetZoom();
    }

    document.addEventListener('click', function (e) {
        if (scale !== 1) return; // avoid closing while zoomed in / after a drag
        var target = e.target.closest('.post img');
        if (target) {
            open(target.src, target.alt);
            return;
        }
        if (e.target === overlay || e.target === img) {
            close();
        }
    });

    closeBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        close();
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') close();
    });

    // Desktop: scroll/trackpad wheel to zoom, centered on the cursor
    img.addEventListener('wheel', function (e) {
        e.preventDefault();
        var prevScale = scale;
        scale = clampScale(scale - e.deltaY * 0.01);

        var rect = img.getBoundingClientRect();
        var cx = e.clientX - rect.left - rect.width / 2;
        var cy = e.clientY - rect.top - rect.height / 2;
        var ratio = scale / prevScale;
        originX -= cx * (ratio - 1);
        originY -= cy * (ratio - 1);

        if (scale === MIN_SCALE) {
            originX = 0;
            originY = 0;
        }
        applyTransform();
    }, { passive: false });

    // Touch: pinch to zoom, single-finger drag to pan while zoomed
    var pointers = {};
    var pinchStartDist = 0;
    var pinchStartScale = 1;
    var panStart = null;
    var panOrigin = { x: 0, y: 0 };

    function distance(p1, p2) {
        return Math.hypot(p1.x - p2.x, p1.y - p2.y);
    }

    img.addEventListener('pointerdown', function (e) {
        pointers[e.pointerId] = { x: e.clientX, y: e.clientY };
        var ids = Object.keys(pointers);
        if (ids.length === 2) {
            pinchStartDist = distance(pointers[ids[0]], pointers[ids[1]]);
            pinchStartScale = scale;
        } else if (ids.length === 1) {
            panStart = { x: e.clientX, y: e.clientY };
            panOrigin = { x: originX, y: originY };
        }
    });

    img.addEventListener('pointermove', function (e) {
        if (!pointers[e.pointerId]) return;
        pointers[e.pointerId] = { x: e.clientX, y: e.clientY };
        var ids = Object.keys(pointers);

        if (ids.length === 2) {
            var dist = distance(pointers[ids[0]], pointers[ids[1]]);
            scale = clampScale(pinchStartScale * (dist / pinchStartDist));
            if (scale === MIN_SCALE) {
                originX = 0;
                originY = 0;
            }
            applyTransform();
        } else if (ids.length === 1 && panStart && scale > 1) {
            originX = panOrigin.x + (e.clientX - panStart.x);
            originY = panOrigin.y + (e.clientY - panStart.y);
            applyTransform();
        }
    });

    function endPointer(e) {
        delete pointers[e.pointerId];
        panStart = null;
    }

    img.addEventListener('pointerup', endPointer);
    img.addEventListener('pointercancel', endPointer);
    img.addEventListener('pointerleave', endPointer);

    // Double-click / double-tap to reset zoom
    img.addEventListener('dblclick', resetZoom);
})();
