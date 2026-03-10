document.addEventListener("DOMContentLoaded", function () {
  let activeDropdown = null;
  let activeMenu = null;
  let activePlaceholder = null;

  function closeAllDropdowns() {
    document.querySelectorAll(".pixel-dropdown").forEach(drop => {
      drop.classList.remove("open");
    });

    if (activeMenu && activePlaceholder) {
      activePlaceholder.parentNode.insertBefore(activeMenu, activePlaceholder);
      activePlaceholder.remove();
      activeMenu.classList.remove("portal-open");
      activeMenu.style.top = "";
      activeMenu.style.left = "";
      activeMenu.style.width = "";
    }

    activeDropdown = null;
    activeMenu = null;
    activePlaceholder = null;
  }

  document.querySelectorAll(".pixel-dropdown-toggle").forEach(toggle => {
    toggle.addEventListener("click", function (e) {
      e.stopPropagation();

      const dropdown = this.closest(".pixel-dropdown");
      const menu = dropdown.querySelector(".pixel-dropdown-menu");
      const isOpen = dropdown.classList.contains("open");

      closeAllDropdowns();

      if (isOpen) return;

      dropdown.classList.add("open");

      const rect = this.getBoundingClientRect();

      const placeholder = document.createComment("dropdown-placeholder");
      menu.parentNode.insertBefore(placeholder, menu);

      document.body.appendChild(menu);
      menu.classList.add("portal-open");

      const menuWidth = Math.max(rect.width, 220);
      let left = window.scrollX + rect.left;
      const top = window.scrollY + rect.bottom + 6;

      /* keep menu inside viewport horizontally */
      const maxLeft = window.scrollX + window.innerWidth - menuWidth - 12;
      if (left > maxLeft) {
        left = Math.max(window.scrollX + 12, maxLeft);
      }

      menu.style.width = menuWidth + "px";
      menu.style.left = left + "px";
      menu.style.top = top + "px";

      activeDropdown = dropdown;
      activeMenu = menu;
      activePlaceholder = placeholder;
    });
  });

  document.querySelectorAll(".pixel-dropdown-item").forEach(item => {
    item.addEventListener("click", function (e) {
      e.stopPropagation();

      const menu = this.closest(".pixel-dropdown-menu");
      const dropdown =
        activeDropdown ||
        document.querySelector(".pixel-dropdown.open");

      if (!dropdown) return;

      const labelTarget = dropdown.querySelector("[data-dropdown-label]");
      const hiddenInput = dropdown.querySelector('input[type="hidden"]');

      if (labelTarget) {
        const caret = labelTarget.querySelector(".pixel-caret");
        labelTarget.innerHTML = "";
        labelTarget.appendChild(
          document.createTextNode((this.dataset.label || this.textContent).trim() + " ")
        );
        if (caret) {
          labelTarget.appendChild(caret);
        } else {
          const span = document.createElement("span");
          span.className = "pixel-caret";
          span.textContent = "▼";
          labelTarget.appendChild(span);
        }
      }

      if (hiddenInput) {
        hiddenInput.value = this.dataset.value;
      }

      dropdown.querySelectorAll(".pixel-dropdown-item").forEach(opt => {
        opt.classList.remove("active");
      });

      this.classList.add("active");
      closeAllDropdowns();
    });
  });

  document.addEventListener("click", function () {
    closeAllDropdowns();
  });

  window.addEventListener("resize", function () {
    closeAllDropdowns();
  });

  window.addEventListener("scroll", function () {
    closeAllDropdowns();
  }, true);
});