document.addEventListener("DOMContentLoaded", function () {
  let activeDropdown = null;
  let activeMenu = null;
  let activePlaceholder = null;
  let enhancedCounter = 0;

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

  function updateNativeDropdownLabel(dropdown, select) {
    const labelTarget = dropdown.querySelector("[data-dropdown-label]");
    if (!labelTarget) return;

    const selectedOption = select.options[select.selectedIndex];
    const labelText = selectedOption ? selectedOption.textContent.trim() : "Select";
    labelTarget.innerHTML = "";
    labelTarget.appendChild(document.createTextNode(labelText + " "));

    const caret = document.createElement("span");
    caret.className = "pixel-caret";
    caret.textContent = "▼";
    labelTarget.appendChild(caret);
  }

  function enhanceNativeSelect(select) {
    if (!select || select.dataset.pixelDropdownReady === "true") return;
    if (select.multiple || select.size > 1) return;
    if (select.closest(".pixel-dropdown")) return;

    select.dataset.pixelDropdownReady = "true";
    enhancedCounter += 1;

    const wrapper = document.createElement("div");
    wrapper.className = "pixel-native-select";

    const dropdown = document.createElement("div");
    dropdown.className = "pixel-dropdown";
    dropdown.dataset.dropdown = "";
    if (select.classList.contains("form-select-sm")) {
      dropdown.classList.add("pixel-dropdown-inline");
    }

    const button = document.createElement("button");
    button.type = "button";
    button.className = "pixel-dropdown-toggle";
    button.setAttribute("data-dropdown-label", "");
    if (select.disabled) {
      button.disabled = true;
      button.classList.add("disabled");
    }

    const menu = document.createElement("div");
    menu.className = "pixel-dropdown-menu";
    menu.setAttribute("data-dropdown-menu", "");

    Array.from(select.options).forEach((option) => {
      const item = document.createElement("button");
      item.type = "button";
      item.className = "pixel-dropdown-item";
      item.dataset.value = option.value;
      item.dataset.label = option.textContent.trim();
      item.textContent = option.textContent.trim();

      if (option.selected) {
        item.classList.add("active");
      }

      if (option.disabled) {
        item.disabled = true;
        item.classList.add("disabled");
      }

      item.addEventListener("click", function (e) {
        e.stopPropagation();
        if (option.disabled || select.disabled) return;

        select.value = option.value;
        Array.from(select.options).forEach((opt) => {
          opt.selected = opt.value === option.value;
        });

        menu.querySelectorAll(".pixel-dropdown-item").forEach((opt) => {
          opt.classList.toggle("active", opt === item);
        });

        updateNativeDropdownLabel(dropdown, select);
        select.dispatchEvent(new Event("change", { bubbles: true }));
        closeAllDropdowns();
      });

      menu.appendChild(item);
    });

    button.addEventListener("click", function (e) {
      if (button.disabled) return;
      e.stopPropagation();

      const isOpen = dropdown.classList.contains("open");
      closeAllDropdowns();
      if (isOpen) return;

      dropdown.classList.add("open");

      const rect = button.getBoundingClientRect();
      const placeholder = document.createComment("dropdown-placeholder");
      menu.parentNode.insertBefore(placeholder, menu);

      document.body.appendChild(menu);
      menu.classList.add("portal-open");

      const menuWidth = Math.max(rect.width, 220);
      let left = window.scrollX + rect.left;
      const top = window.scrollY + rect.bottom + 6;
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

    select.addEventListener("change", function () {
      menu.querySelectorAll(".pixel-dropdown-item").forEach((item) => {
        item.classList.toggle("active", item.dataset.value === select.value);
      });
      updateNativeDropdownLabel(dropdown, select);
    });

    select.parentNode.insertBefore(wrapper, select);
    wrapper.appendChild(select);
    wrapper.appendChild(dropdown);
    select.classList.add("pixel-native-select-source");
    dropdown.appendChild(button);
    dropdown.appendChild(menu);
    updateNativeDropdownLabel(dropdown, select);
  }

  document
    .querySelectorAll("select.form-select, select.form-control, select:not([multiple])")
    .forEach(enhanceNativeSelect);
});
