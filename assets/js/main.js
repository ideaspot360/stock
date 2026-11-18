// IdeaSpot360 Dev - Core Interactive Engine
// Dark Mode Toggle & One-Click Code Block Copy

document.addEventListener("DOMContentLoaded", () => {
  // 1. Dark Mode Management
  const themeToggle = document.getElementById("theme-toggle");
  const currentTheme = localStorage.getItem("theme");

  if (currentTheme) {
    document.documentElement.setAttribute("data-theme", currentTheme);
    updateThemeIcon(currentTheme);
  } else {
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    updateThemeIcon(prefersDark ? "dark" : "light");
  }

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      let theme = document.documentElement.getAttribute("data-theme");
      if (!theme) {
        theme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      }
      const newTheme = theme === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", newTheme);
      localStorage.setItem("theme", newTheme);
      updateThemeIcon(newTheme);
    });
  }

  function updateThemeIcon(theme) {
    if (!themeToggle) return;
    themeToggle.textContent = theme === "dark" ? "☀️ Light" : "🌙 Dark";
  }

  // 2. Add 'Copy' button to all <pre> code blocks
  const preBlocks = document.querySelectorAll("pre");
  preBlocks.forEach((pre) => {
    const button = document.createElement("button");
    button.className = "copy-code-btn";
    button.textContent = "Copy";

    button.addEventListener("click", async () => {
      const code = pre.querySelector("code");
      const textToCopy = code ? code.innerText : pre.innerText;

      try {
        await navigator.clipboard.writeText(textToCopy);
        button.textContent = "Copied!";
        button.style.backgroundColor = "#10b981";
        setTimeout(() => {
          button.textContent = "Copy";
          button.style.backgroundColor = "";
        }, 2000);
      } catch (err) {
        button.textContent = "Failed";
      }
    });

    pre.appendChild(button);
  });

  // 3. Ultra-Precision Pan & Zoom Image Lightbox Engine (초정밀 줌 & 팬 라이트박스 엔진)
  const postImages = document.querySelectorAll(".entry-content img, article.post-content img");
  if (postImages.length > 0) {
    const modal = document.createElement("div");
    modal.className = "image-lightbox-modal";
    modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");
    modal.setAttribute("aria-label", "차트 및 이미지 초정밀 확대 보기");

    modal.innerHTML = `
      <div class="lightbox-backdrop"></div>
      
      <!-- 상단 컨트롤 툴바 -->
      <div class="lightbox-toolbar">
        <button class="zoom-btn" id="zoom-out" title="축소 (-)" aria-label="축소">−</button>
        <button class="zoom-level-btn" id="zoom-level" title="클릭 시 100% 화면 맞춤">100%</button>
        <button class="zoom-btn" id="zoom-in" title="확대 (+)" aria-label="확대">+</button>
        <button class="zoom-btn" id="zoom-reset" title="화면 맞춤 (R)" aria-label="초기화">⛶</button>
        <div class="toolbar-divider"></div>
        <button class="lightbox-close-btn" id="lightbox-close" aria-label="닫기" title="닫기 (ESC)">✕</button>
      </div>

      <!-- 인터랙티브 스테이지 & 이미지 컨테이너 -->
      <div class="lightbox-stage">
        <div class="lightbox-pan-container">
          <img class="lightbox-img" src="" alt="확대된 이미지" draggable="false" />
        </div>
      </div>

      <!-- 하단 캡션 및 안내 바 -->
      <div class="lightbox-footer">
        <div class="lightbox-caption"></div>
        <div class="lightbox-hint">
          <span>🔍 마우스 휠: 100%~500% 초정밀 줌</span>
          <span class="hint-sep">|</span>
          <span>✋ 드래그: 자유 이동</span>
          <span class="hint-sep">|</span>
          <span>⚡ 더블클릭: 2.5배 확대 토글</span>
          <span class="hint-sep">|</span>
          <span>⌨️ ESC: 닫기</span>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    const panContainer = modal.querySelector(".lightbox-pan-container");
    const modalImg = modal.querySelector(".lightbox-img");
    const stage = modal.querySelector(".lightbox-stage");
    const caption = modal.querySelector(".lightbox-caption");
    const backdrop = modal.querySelector(".lightbox-backdrop");
    const zoomLevelBtn = modal.querySelector("#zoom-level");
    const zoomInBtn = modal.querySelector("#zoom-in");
    const zoomOutBtn = modal.querySelector("#zoom-out");
    const zoomResetBtn = modal.querySelector("#zoom-reset");
    const closeBtn = modal.querySelector("#lightbox-close");

    // Pan & Zoom Engine State
    let scale = 1.0;
    let translateX = 0;
    let translateY = 0;
    let isDragging = false;
    let startPointerX = 0;
    let startPointerY = 0;
    let initialPinchDist = 0;
    let initialPinchScale = 1.0;

    const MIN_SCALE = 0.8;
    const MAX_SCALE = 5.0;

    function updateTransform(smooth = false) {
      if (smooth) {
        panContainer.style.transition = "transform 0.22s cubic-bezier(0.16, 1, 0.3, 1)";
      } else {
        panContainer.style.transition = "none";
      }
      panContainer.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
      zoomLevelBtn.textContent = `${Math.round(scale * 100)}%`;

      // 커서 스타일 동적 변경
      if (scale > 1.0) {
        stage.style.cursor = isDragging ? "grabbing" : "grab";
      } else {
        stage.style.cursor = "default";
      }
    }

    function resetZoom(smooth = true) {
      scale = 1.0;
      translateX = 0;
      translateY = 0;
      updateTransform(smooth);
    }

    function zoomAround(cursorX, cursorY, factor) {
      const rect = stage.getBoundingClientRect();
      // 스테이지 중심 기준 상대 좌표
      const cx = cursorX - (rect.left + rect.width / 2);
      const cy = cursorY - (rect.top + rect.height / 2);

      let targetScale = scale * factor;
      if (targetScale < MIN_SCALE) targetScale = MIN_SCALE;
      if (targetScale > MAX_SCALE) targetScale = MAX_SCALE;
      if (Math.abs(targetScale - scale) < 0.001) return;

      const scaleRatio = targetScale / scale;
      translateX = cx - (cx - translateX) * scaleRatio;
      translateY = cy - (cy - translateY) * scaleRatio;
      scale = targetScale;
      updateTransform(false);
    }

    function openModal(img) {
      modalImg.src = img.src;
      modalImg.alt = img.alt || "확대된 도안 차트";
      caption.textContent = img.alt || "고해상도 도안 차트";
      resetZoom(false);
      modal.classList.add("active");
      document.body.style.overflow = "hidden";
    }

    function closeModal() {
      modal.classList.remove("active");
      document.body.style.overflow = "";
      setTimeout(() => {
        modalImg.src = "";
        resetZoom(false);
      }, 200);
    }

    // 모든 본문 이미지에 줌 커서 및 타이틀 부여
    postImages.forEach((img) => {
      img.classList.add("zoomable-image");
      img.setAttribute("title", "🔍 클릭하여 초정밀 줌 & 팬 모달 열기");
      img.addEventListener("click", () => openModal(img));
    });

    // 1. 마우스 휠 이벤트 (초정밀 연속 줌)
    stage.addEventListener("wheel", (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.15 : 0.87;
      zoomAround(e.clientX, e.clientY, zoomFactor);
    }, { passive: false });

    // 2. 마우스 드래그 앤 팬 (Free Pan)
    stage.addEventListener("mousedown", (e) => {
      if (e.button !== 0) return; // 좌클릭만
      isDragging = true;
      startPointerX = e.clientX - translateX;
      startPointerY = e.clientY - translateY;
      stage.style.cursor = "grabbing";
      e.preventDefault();
    });

    window.addEventListener("mousemove", (e) => {
      if (!isDragging) return;
      translateX = e.clientX - startPointerX;
      translateY = e.clientY - startPointerY;
      updateTransform(false);
    });

    window.addEventListener("mouseup", () => {
      if (isDragging) {
        isDragging = false;
        stage.style.cursor = scale > 1.0 ? "grab" : "default";
      }
    });

    // 3. 더블 클릭 (스마트 토글 줌: 1배 ↔ 2.5배)
    stage.addEventListener("dblclick", (e) => {
      e.preventDefault();
      if (scale > 1.2) {
        resetZoom(true);
      } else {
        zoomAround(e.clientX, e.clientY, 2.5 / scale);
        // 부드러운 전환
        panContainer.style.transition = "transform 0.25s cubic-bezier(0.16, 1, 0.3, 1)";
      }
    });

    // 4. 모바일 터치 이벤트 (한 손가락 팬 & 두 손가락 핀치 줌)
    stage.addEventListener("touchstart", (e) => {
      if (e.touches.length === 1) {
        isDragging = true;
        startPointerX = e.touches[0].clientX - translateX;
        startPointerY = e.touches[0].clientY - translateY;
      } else if (e.touches.length === 2) {
        isDragging = false;
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        initialPinchDist = Math.hypot(dx, dy);
        initialPinchScale = scale;
      }
    }, { passive: true });

    stage.addEventListener("touchmove", (e) => {
      if (e.touches.length === 1 && isDragging) {
        translateX = e.touches[0].clientX - startPointerX;
        translateY = e.touches[0].clientY - startPointerY;
        updateTransform(false);
        e.preventDefault();
      } else if (e.touches.length === 2 && initialPinchDist > 0) {
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        const currentDist = Math.hypot(dx, dy);
        const factor = currentDist / initialPinchDist;
        const midX = (e.touches[0].clientX + e.touches[1].clientX) / 2;
        const midY = (e.touches[0].clientY + e.touches[1].clientY) / 2;

        let targetScale = initialPinchScale * factor;
        if (targetScale < MIN_SCALE) targetScale = MIN_SCALE;
        if (targetScale > MAX_SCALE) targetScale = MAX_SCALE;

        scale = targetScale;
        updateTransform(false);
        e.preventDefault();
      }
    }, { passive: false });

    stage.addEventListener("touchend", () => {
      isDragging = false;
      initialPinchDist = 0;
    });

    // 5. 툴바 버튼 이벤트
    zoomInBtn.addEventListener("click", () => {
      const rect = stage.getBoundingClientRect();
      zoomAround(rect.left + rect.width / 2, rect.top + rect.height / 2, 1.3);
      panContainer.style.transition = "transform 0.18s ease";
    });

    zoomOutBtn.addEventListener("click", () => {
      const rect = stage.getBoundingClientRect();
      zoomAround(rect.left + rect.width / 2, rect.top + rect.height / 2, 0.77);
      panContainer.style.transition = "transform 0.18s ease";
    });

    zoomResetBtn.addEventListener("click", () => resetZoom(true));
    zoomLevelBtn.addEventListener("click", () => resetZoom(true));
    closeBtn.addEventListener("click", closeModal);
    backdrop.addEventListener("click", closeModal);

    // 6. 키보드 단축키 지원
    document.addEventListener("keydown", (e) => {
      if (!modal.classList.contains("active")) return;

      if (e.key === "Escape") {
        closeModal();
      } else if (e.key === "+" || e.key === "=") {
        zoomInBtn.click();
      } else if (e.key === "-" || e.key === "_") {
        zoomOutBtn.click();
      } else if (e.key === "0" || e.key === "r" || e.key === "R") {
        resetZoom(true);
      } else if (e.key === "ArrowLeft") {
        translateX += 60;
        updateTransform(true);
      } else if (e.key === "ArrowRight") {
        translateX -= 60;
        updateTransform(true);
      } else if (e.key === "ArrowUp") {
        translateY += 60;
        updateTransform(true);
      } else if (e.key === "ArrowDown") {
        translateY -= 60;
        updateTransform(true);
      }
    });
  }

  // 4. Responsive Table Wrapper (모바일 가로 스크롤 및 데스크톱 100% 꽉 채움)
  const tables = document.querySelectorAll("article.post-content table, .entry-content table");
  tables.forEach((table) => {
    if (!table.parentElement.classList.contains("table-responsive")) {
      const wrapper = document.createElement("div");
      wrapper.className = "table-responsive";
      table.parentNode.insertBefore(wrapper, table);
      wrapper.appendChild(table);
    }
  });

  // 5. Scrollspy TOC Engine (우측 목차 자동 수집 및 실시간 감지)
  const headings = Array.from(document.querySelectorAll(".entry-content h2, .entry-content h3, article.post-content h2, article.post-content h3"));
  const tocNav = document.getElementById("toc-nav");
  if (headings.length > 0 && tocNav) {
    const list = document.createElement("ul");
    list.className = "toc-list";

    headings.forEach((heading, idx) => {
      if (!heading.id) {
        heading.id = `heading-sec-${idx + 1}`;
      }
      const item = document.createElement("li");
      item.className = `toc-item toc-${heading.tagName.toLowerCase()}`;

      const link = document.createElement("a");
      link.href = `#${heading.id}`;
      link.className = "toc-link";
      link.textContent = heading.textContent.replace(/^[#\s]+/, "").trim();

      link.addEventListener("click", (e) => {
        e.preventDefault();
        const target = document.getElementById(heading.id);
        if (target) {
          target.scrollIntoView({ behavior: "smooth", block: "start" });
          history.pushState(null, null, `#${heading.id}`);
        }
      });

      item.appendChild(link);
      list.appendChild(item);
    });

    tocNav.appendChild(list);

    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const id = entry.target.id;
            document.querySelectorAll(".toc-link").forEach((l) => {
              l.classList.toggle("active", l.getAttribute("href") === `#${id}`);
            });
          }
        });
      }, {
        rootMargin: "-80px 0px -60% 0px",
        threshold: 0
      });

      headings.forEach((h) => observer.observe(h));
    }
  }

  // 6. Back-to-Top Button
  const backToTopBtn = document.getElementById("back-to-top-btn");
  if (backToTopBtn) {
    backToTopBtn.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // 7. Off-Canvas Drawer Engine (모바일/태블릿 드로어)
  const menuToggle = document.getElementById("mobile-menu-toggle");
  const drawer = document.getElementById("mobile-drawer");
  const backdrop = document.getElementById("drawer-backdrop");
  const drawerCloseBtn = document.getElementById("drawer-close-btn");

  function openDrawer() {
    if (drawer && backdrop) {
      drawer.classList.add("is-open");
      backdrop.classList.add("is-visible");
      document.body.style.overflow = "hidden";
      if (menuToggle) menuToggle.setAttribute("aria-expanded", "true");
    }
  }

  function closeDrawer() {
    if (drawer && backdrop) {
      drawer.classList.remove("is-open");
      backdrop.classList.remove("is-visible");
      document.body.style.overflow = "";
      if (menuToggle) menuToggle.setAttribute("aria-expanded", "false");
    }
  }

  if (menuToggle) menuToggle.addEventListener("click", openDrawer);
  if (drawerCloseBtn) drawerCloseBtn.addEventListener("click", closeDrawer);
  if (backdrop) backdrop.addEventListener("click", closeDrawer);

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && drawer && drawer.classList.contains("is-open")) {
      closeDrawer();
    }
  });

  // Responsive resize: 데스크톱(>=1200px) 복귀 시 드로어 자동 닫힘 및 스크롤락 해제
  window.addEventListener("resize", () => {
    if (window.innerWidth >= 1200 && drawer && drawer.classList.contains("is-open")) {
      closeDrawer();
    }
  });

  // 8. Sidebar Scroll Position Restoration (Safari 시크릿 모드 예외 안전 방어)
  const sidebar = document.querySelector(".sidebar-desktop");
  if (sidebar) {
    try {
      const savedPos = sessionStorage.getItem("sidebar_scroll_pos");
      if (savedPos !== null) {
        sidebar.scrollTop = parseInt(savedPos, 10);
      }
      sidebar.addEventListener("scroll", () => {
        try {
          sessionStorage.setItem("sidebar_scroll_pos", sidebar.scrollTop.toString());
        } catch (e) {}
      }, { passive: true });
    } catch (e) {}
  }

  // 9. Category Pills Horizontal Scroll (Active Pill Center Alignment)
  const activePill = document.querySelector(".category-pill.active");
  if (activePill) {
    setTimeout(() => {
      activePill.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
    }, 150);
  }
});

