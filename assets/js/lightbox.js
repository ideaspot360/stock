/**
 * Pan & Zoom Interactive Lightbox Module (Master Shared Asset)
 *
 * Provides ultra-precision interactive pan-and-zoom inspection for technical
 * diagrams, charts, schematics, and architecture visuals across all ecosystem blogs.
 *
 * Features:
 * - Continuous smooth mouse wheel zoom with cursor focal-point tracking (delta = -e.deltaY * 0.002)
 * - Drag-pan with DRAG_THRESHOLD = 5px and 50ms delayed reset (prevents accidental backdrop closes)
 * - Double-click 2.5x toggle smart zoom with toolbar guard (.panzoom-toolbar)
 * - Smooth transition animation on button clicks (updateTransform(true))
 * - Full keyboard navigation (+, -, 0, R, Arrow keys, ESC)
 * - Mobile pinch-to-zoom and one-finger pan touch gestures
 * - Dynamic bilingual (Korean / English) i18n auto-detection (html lang or navigator.language)
 * - Idempotency guard (window.__panZoomLightboxInitialized)
 * - Standalone UMD wrapper compatible with direct script tags, AMD, and CommonJS
 */

(function (root, factory) {
  if (typeof define === "function" && define.amd) {
    define([], factory);
  } else if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.PanZoomLightbox = factory();
  }
}(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  const DEFAULT_IMAGE_SELECTORS = [
    ".entry-content img",
    "article.post-content img",
    ".post-content img",
    ".post-body img",
    ".markdown-body img"
  ].join(", ");

  const MIN_SCALE = 0.5;
  const MAX_SCALE = 6.0;
  const DRAG_THRESHOLD = 5; // Movement > 5px locks pan state to prevent backdrop click trigger

  /**
   * Detect language from document element or navigator
   * @returns {"ko" | "en"}
   */
  function detectLanguage() {
    try {
      if (typeof document !== "undefined" && document.documentElement && document.documentElement.lang) {
        if (document.documentElement.lang.toLowerCase().startsWith("ko")) {
          return "ko";
        }
      }
      if (typeof navigator !== "undefined") {
        if (navigator.language && navigator.language.toLowerCase().startsWith("ko")) {
          return "ko";
        }
        if (Array.isArray(navigator.languages)) {
          for (let i = 0; i < navigator.languages.length; i++) {
            if (navigator.languages[i].toLowerCase().startsWith("ko")) {
              return "ko";
            }
          }
        }
      }
    } catch (_) {}
    return "en";
  }

  /**
   * Get localized labels and helper strings
   * @param {"ko" | "en"} lang
   */
  function getI18nStrings(lang) {
    if (lang === "ko") {
      return {
        zoomIn: "확대 (+)",
        zoomOut: "축소 (−)",
        reset: "원래 크기 (리셋)",
        close: "닫기 (Esc)",
        hint: "🖱️ 휠: 줌 인/아웃 | 드래그/방향키: 이동 | 더블클릭: 2.5x | +, -: 줌 | 0/R: 리셋 | ESC: 닫기",
        defaultAlt: "기술 다이어그램"
      };
    }
    return {
      zoomIn: "Zoom In (+)",
      zoomOut: "Zoom Out (−)",
      reset: "Reset View (R)",
      close: "Close (Esc)",
      hint: "🖱️ Wheel / +, -: Zoom | Drag / Arrow Keys: Pan | Double-Click: 2.5x | 0 / R: Reset | ESC: Close",
      defaultAlt: "Technical Diagram"
    };
  }

  /**
   * Initialize Pan & Zoom Lightbox instance
   * @param {Object} [options]
   */
  function initPanZoomLightbox(options) {
    if (typeof window === "undefined" || typeof document === "undefined") {
      return null;
    }

    // Idempotency guard: prevent duplicate initialization
    if (window.__panZoomLightboxInitialized && window.__panZoomLightboxInstance) {
      return window.__panZoomLightboxInstance;
    }

    const opts = options || {};
    const selector = opts.selector || DEFAULT_IMAGE_SELECTORS;
    const images = document.querySelectorAll(selector);

    // If no target images found on this page, exit early but allow later manual invocation
    if (!images || images.length === 0) {
      return null;
    }

    const lang = opts.lang || detectLanguage();
    const i18n = getI18nStrings(lang);

    // Create Modal DOM Elements once
    let modal = document.querySelector(".panzoom-modal");
    if (!modal) {
      modal = document.createElement("div");
      modal.className = "panzoom-modal";
      modal.innerHTML = `
        <div class="panzoom-toolbar">
          <span class="panzoom-scale-badge" id="pz-scale">100%</span>
          <button class="panzoom-btn" id="pz-zoom-out" title="${i18n.zoomOut}">−</button>
          <button class="panzoom-btn" id="pz-zoom-in" title="${i18n.zoomIn}">+</button>
          <button class="panzoom-btn" id="pz-reset" title="${i18n.reset}">↺</button>
          <button class="panzoom-btn" id="pz-close" title="${i18n.close}" style="margin-left: 6px; font-weight: bold;">✕</button>
        </div>
        <div class="panzoom-viewport" id="pz-viewport">
          <img class="panzoom-image" id="pz-image" src="" alt="${i18n.defaultAlt}">
        </div>
        <div class="panzoom-hint">${i18n.hint}</div>
      `;
      document.body.appendChild(modal);
    }

    const viewport = modal.querySelector("#pz-viewport");
    const pzImage = modal.querySelector("#pz-image");
    const scaleBadge = modal.querySelector("#pz-scale");
    const btnIn = modal.querySelector("#pz-zoom-in");
    const btnOut = modal.querySelector("#pz-zoom-out");
    const btnReset = modal.querySelector("#pz-reset");
    const btnClose = modal.querySelector("#pz-close");

    let scale = 1.0;
    let translateX = 0;
    let translateY = 0;
    let isDragging = false;
    let hasDragged = false;
    let dragStartX = 0;
    let dragStartY = 0;
    let startX = 0;
    let startY = 0;
    let lastPinchDist = null;

    function updateTransform(smooth = false) {
      if (!pzImage) return;
      pzImage.style.transition = smooth ? "transform 0.2s cubic-bezier(0.16, 1, 0.3, 1)" : "none";
      pzImage.style.transform = `translate3d(${translateX}px, ${translateY}px, 0) scale(${scale})`;
      if (scaleBadge) {
        scaleBadge.textContent = `${Math.round(scale * 100)}%`;
      }
    }

    function resetZoom() {
      scale = 1.0;
      translateX = 0;
      translateY = 0;
      updateTransform(true);
    }

    function zoomAt(targetScale, focalX = 0, focalY = 0, smooth = false) {
      if (!Number.isFinite(targetScale)) return;
      const clampedScale = Math.min(Math.max(targetScale, MIN_SCALE), MAX_SCALE);
      if (clampedScale === scale) return;

      const ratio = clampedScale / scale;
      translateX = focalX - ratio * (focalX - translateX);
      translateY = focalY - ratio * (focalY - translateY);
      scale = clampedScale;

      updateTransform(smooth);
    }

    function openModal(src, alt) {
      if (!pzImage || !modal) return;
      pzImage.src = src;
      pzImage.alt = alt || i18n.defaultAlt;
      resetZoom();
      modal.classList.add("active");
      document.body.style.overflow = "hidden";
    }

    function closeModal() {
      if (!modal) return;
      modal.classList.remove("active");
      document.body.style.overflow = "";
      setTimeout(() => {
        if (pzImage && !modal.classList.contains("active")) {
          pzImage.src = "";
        }
      }, 250);
    }

    // Attach click listeners to all matching images
    images.forEach((img) => {
      if (img.dataset.panzoomBound) return;
      img.dataset.panzoomBound = "true";
      img.addEventListener("click", () => {
        openModal(img.src, img.alt);
      });
    });

    // 1. Mouse Wheel Continuous Zoom (focal point centered on cursor)
    viewport.addEventListener("wheel", (e) => {
      e.preventDefault();
      const rect = viewport.getBoundingClientRect();
      const focalX = e.clientX - rect.left - rect.width / 2;
      const focalY = e.clientY - rect.top - rect.height / 2;

      const delta = -e.deltaY * 0.002;
      const targetScale = scale * (1 + delta);
      zoomAt(targetScale, focalX, focalY, false);
    }, { passive: false });

    // 2. Mouse Drag Pan with DRAG_THRESHOLD = 5px
    viewport.addEventListener("mousedown", (e) => {
      if (e.button !== 0) return; // Only left click
      if (e.target.closest(".panzoom-toolbar, .lightbox-toolbar")) return;
      isDragging = true;
      hasDragged = false;
      dragStartX = e.clientX;
      dragStartY = e.clientY;
      startX = e.clientX - translateX;
      startY = e.clientY - translateY;
      viewport.classList.add("grabbing");
      viewport.classList.add("dragging");
    });

    window.addEventListener("mousemove", (e) => {
      if (!isDragging) return;
      const moveDist = Math.hypot(e.clientX - dragStartX, e.clientY - dragStartY);
      if (moveDist > DRAG_THRESHOLD) {
        hasDragged = true;
      }
      translateX = e.clientX - startX;
      translateY = e.clientY - startY;
      updateTransform(false);
    });

    window.addEventListener("mouseup", () => {
      if (isDragging) {
        isDragging = false;
        viewport.classList.remove("grabbing");
        viewport.classList.remove("dragging");
        setTimeout(() => {
          hasDragged = false;
        }, 50);
      }
    });

    // 3. Double Click Smart Zoom (2.5x Toggle) with toolbar guard
    viewport.addEventListener("dblclick", (e) => {
      if (e.target.closest(".panzoom-toolbar, .lightbox-toolbar")) return;
      e.preventDefault();
      if (scale > 1.2) {
        resetZoom();
      } else {
        const rect = viewport.getBoundingClientRect();
        const focalX = e.clientX - rect.left - rect.width / 2;
        const focalY = e.clientY - rect.top - rect.height / 2;
        zoomAt(2.5, focalX, focalY, true);
      }
    });

    // 4. Mobile Touch Pinch-to-zoom & Pan
    viewport.addEventListener("touchstart", (e) => {
      if (e.touches[0] && e.touches[0].target.closest(".panzoom-toolbar, .lightbox-toolbar")) return;
      if (e.touches.length === 1) {
        isDragging = true;
        hasDragged = false;
        dragStartX = e.touches[0].clientX;
        dragStartY = e.touches[0].clientY;
        startX = e.touches[0].clientX - translateX;
        startY = e.touches[0].clientY - translateY;
      } else if (e.touches.length === 2) {
        isDragging = false;
        lastPinchDist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
      }
    }, { passive: true });

    viewport.addEventListener("touchmove", (e) => {
      if (e.touches.length === 1 && isDragging) {
        const moveDist = Math.hypot(e.touches[0].clientX - dragStartX, e.touches[0].clientY - dragStartY);
        if (moveDist > DRAG_THRESHOLD) {
          hasDragged = true;
        }
        translateX = e.touches[0].clientX - startX;
        translateY = e.touches[0].clientY - startY;
        updateTransform(false);
      } else if (e.touches.length === 2 && lastPinchDist) {
        const currentDist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
        if (currentDist > 0 && lastPinchDist > 0) {
          const ratio = currentDist / lastPinchDist;
          zoomAt(scale * ratio, 0, 0, false);
          lastPinchDist = currentDist;
        }
      }
    }, { passive: true });

    viewport.addEventListener("touchend", () => {
      isDragging = false;
      lastPinchDist = null;
      setTimeout(() => {
        hasDragged = false;
      }, 50);
    });

    // 5. Toolbar Actions (Smooth Animation)
    if (btnIn) {
      btnIn.addEventListener("click", () => {
        zoomAt(scale * 1.3, 0, 0, true);
      });
    }
    if (btnOut) {
      btnOut.addEventListener("click", () => {
        zoomAt(scale * 0.7, 0, 0, true);
      });
    }
    if (btnReset) {
      btnReset.addEventListener("click", resetZoom);
    }
    if (btnClose) {
      btnClose.addEventListener("click", closeModal);
    }

    // 6. Close on Backdrop Click (guarded against dragging)
    viewport.addEventListener("click", (e) => {
      if (hasDragged) {
        e.stopPropagation();
        return;
      }
      if (e.target === viewport) {
        closeModal();
      }
    });

    // 7. Full Keyboard Navigation & Shortcuts
    window.addEventListener("keydown", (e) => {
      if (!modal.classList.contains("active")) return;

      if (e.key === "Escape") {
        closeModal();
      } else if (e.key === "+" || e.key === "=") {
        e.preventDefault();
        zoomAt(scale * 1.25, 0, 0, true);
      } else if (e.key === "-" || e.key === "_") {
        e.preventDefault();
        zoomAt(scale * 0.8, 0, 0, true);
      } else if (e.key === "0" || e.key === "r" || e.key === "R") {
        e.preventDefault();
        resetZoom();
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        translateX += 50;
        updateTransform(true);
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        translateX -= 50;
        updateTransform(true);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        translateY += 50;
        updateTransform(true);
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        translateY -= 50;
        updateTransform(true);
      }
    });

    const instance = {
      open: openModal,
      close: closeModal,
      reset: resetZoom,
      zoomAt: zoomAt,
      getScale: () => scale,
      getTranslation: () => ({ x: translateX, y: translateY })
    };

    window.__panZoomLightboxInitialized = true;
    window.__panZoomLightboxInstance = instance;

    return instance;
  }

  // Auto-initialize when loaded in browser
  if (typeof window !== "undefined") {
    window.initPanZoomLightbox = initPanZoomLightbox;
    if (typeof document !== "undefined") {
      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", function () {
          initPanZoomLightbox();
        });
      } else {
        initPanZoomLightbox();
      }
    }
  }

  return {
    init: initPanZoomLightbox,
    detectLanguage: detectLanguage,
    getI18nStrings: getI18nStrings,
    DRAG_THRESHOLD: DRAG_THRESHOLD,
    MIN_SCALE: MIN_SCALE,
    MAX_SCALE: MAX_SCALE
  };
}));
