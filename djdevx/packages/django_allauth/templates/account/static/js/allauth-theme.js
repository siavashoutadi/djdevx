
    (function () {
      const theme = localStorage.getItem("theme");
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

      document.documentElement.classList.toggle("dark", theme === "dark" || (!theme && prefersDark));
    })();
    function setTheme(mode) {
      if (mode === "dark") {
        localStorage.setItem("theme", "dark");
        document.documentElement.classList.add("dark");
      } else if (mode === "light") {
        localStorage.setItem("theme", "light");
        document.documentElement.classList.remove("dark");
      } else {
        localStorage.removeItem("theme");
        document.documentElement.classList.toggle(
          "dark",
          window.matchMedia("(prefers-color-scheme: dark)").matches
        );
      }
    }

    (function () {
      const sunSvg = '<svg aria-hidden="true" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="10" cy="10" r="3" fill="currentColor"/><path d="M10 1v2M10 17v2M1 10h2M17 10h2M3.22 3.22l1.42 1.42M15.36 15.36l1.42 1.42M3.22 16.78l1.42-1.42M15.36 4.64l1.42-1.42" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
      const moonSvg = '<svg aria-hidden="true" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M14.5 11.5a5.5 5.5 0 11-5.5-5.5 4 4 0 005.5 5.5z" fill="currentColor"/></svg>';

      const toggleBtn = document.getElementById('theme-toggle');
      const iconSpan = document.getElementById('theme-toggle-icon');
      if (!toggleBtn || !iconSpan) return;

      function isDarkMode() {
        const theme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        return theme === 'dark' || (!theme && prefersDark);
      }

      function updateToggleIcon() {
        iconSpan.innerHTML = isDarkMode() ? moonSvg : sunSvg;
        toggleBtn.title = isDarkMode() ? 'Switch to light theme' : 'Switch to dark theme';
        toggleBtn.setAttribute('aria-pressed', String(isDarkMode()));
      }

      toggleBtn.addEventListener('click', () => {
        // use existing setTheme function defined in the page
        if (isDarkMode()) {
          setTheme('light');
        } else {
          setTheme('dark');
        }
        updateToggleIcon();
      });

      // react to system preference changes
      const mq = window.matchMedia('(prefers-color-scheme: dark)');
      if (mq.addEventListener) {
        mq.addEventListener('change', updateToggleIcon);
      } else if (mq.addListener) {
        mq.addListener(updateToggleIcon);
      }

      // initialize icon on load
      document.addEventListener('DOMContentLoaded', updateToggleIcon);
      // also run immediately in case DOMContentLoaded already fired
      updateToggleIcon();
    })();
