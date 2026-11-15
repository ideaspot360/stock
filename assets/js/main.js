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

  // 3. Image Lightbox Zoom Modal (그래프 클릭 시 고해상도 확대 모달)
  const postImages = document.querySelectorAll(".entry-content img, article.post-content img");
  if (postImages.length > 0) {
    const modal = document.createElement("div");
    modal.className = "image-lightbox-modal";
    modal.setAttribute("role", "dialog");
    modal.setAttribute("aria-modal", "true");
    modal.setAttribute("aria-label", "차트 및 이미지 확대 보기");

    modal.innerHTML = `
      <div class="lightbox-backdrop"></div>
      <div class="lightbox-content">
        <button class="lightbox-close" aria-label="닫기" title="닫기 (ESC)">✕</button>
        <img class="lightbox-img" src="" alt="확대된 이미지" />
        <div class="lightbox-caption"></div>
        <div class="lightbox-hint">💡 ESC 키를 누르거나 바깥 영역을 클릭하면 닫힙니다</div>
      </div>
    `;
    document.body.appendChild(modal);

    const modalImg = modal.querySelector(".lightbox-img");
    const caption = modal.querySelector(".lightbox-caption");
    const closeBtn = modal.querySelector(".lightbox-close");
    const backdrop = modal.querySelector(".lightbox-backdrop");
    const content = modal.querySelector(".lightbox-content");

    function openModal(img) {
      modalImg.src = img.src;
      modalImg.alt = img.alt || "확대된 차트";
      caption.textContent = img.alt || "";
      modal.classList.add("active");
      document.body.style.overflow = "hidden";
    }

    function closeModal() {
      modal.classList.remove("active");
      document.body.style.overflow = "";
      setTimeout(() => {
        modalImg.src = "";
      }, 250);
    }

    postImages.forEach((img) => {
      img.classList.add("zoomable-image");
      img.setAttribute("title", "🔍 클릭하여 고해상도 전체화면 확대");
      img.addEventListener("click", () => openModal(img));
    });

    closeBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      closeModal();
    });
    backdrop.addEventListener("click", closeModal);
    content.addEventListener("click", (e) => {
      if (e.target === content) {
        closeModal();
      }
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && modal.classList.contains("active")) {
        closeModal();
      }
    });
  }
});

