// main.js - funcionalidades comunes
document.addEventListener('DOMContentLoaded', () => {
    // Toggle tema oscuro
    const toggle = document.getElementById('themeToggle');
    if (toggle) {
        toggle.addEventListener('click', () => {
            const html = document.documentElement;
            const current = html.getAttribute('data-bs-theme');
            html.setAttribute('data-bs-theme', current === 'dark' ? 'light' : 'dark');
            localStorage.setItem('theme', current === 'dark' ? 'light' : 'dark');
            toggle.innerHTML = current === 'dark' 
                ? '<i class="bi bi-moon-stars"></i> Modo Oscuro' 
                : '<i class="bi bi-sun"></i> Modo Claro';
        });
        // Aplicar tema guardado
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-bs-theme', savedTheme);
        if (savedTheme === 'dark') toggle.click();
    }
});
