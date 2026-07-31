/**
 * EcoReminder Theme Switcher (Light / Dark Mode)
 */

(function () {
  const currentTheme = localStorage.getItem('theme') || 'light';
  if (currentTheme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
  }

  document.addEventListener('DOMContentLoaded', () => {
    const themeBtn = document.getElementById('themeToggleBtn');
    if (!themeBtn) return;

    updateBtnIcon(themeBtn, currentTheme);

    themeBtn.addEventListener('click', () => {
      const activeTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
      const newTheme = activeTheme === 'dark' ? 'light' : 'dark';

      if (newTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
      } else {
        document.documentElement.removeAttribute('data-theme');
      }

      localStorage.setItem('theme', newTheme);
      updateBtnIcon(themeBtn, newTheme);
    });
  });

  function updateBtnIcon(btn, theme) {
    if (theme === 'dark') {
      btn.innerHTML = '<i class="bi bi-sun-fill text-warning"></i>';
      btn.setAttribute('title', 'Switch to Light Mode');
    } else {
      btn.innerHTML = '<i class="bi bi-moon-stars-fill text-white"></i>';
      btn.setAttribute('title', 'Switch to Dark Mode');
    }
  }
})();
