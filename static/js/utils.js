// Get the theme toggle checkbox
var themeToggle = document.getElementById('theme-toggle');

// Set initial state based on previous settings or system preference
if (localStorage.getItem('color-theme') === 'dark' || (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark');
    themeToggle.checked = true;
} else {
    document.documentElement.classList.remove('dark');
    themeToggle.checked = false;
}

// Add event listener to toggle
themeToggle.addEventListener('change', function () {
    if (this.checked) {
        document.documentElement.classList.add('dark');
        localStorage.setItem('color-theme', 'dark');
    } else {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('color-theme', 'light');
    }
});