function dark_mode() {
   var element = document.body;
   element.classList.toggle("dark-mode");
}

// Save personality preference when user picks one
document.querySelectorAll('.PersOpt').forEach(radio => {
    radio.addEventListener('change', () => {
        localStorage.setItem('aiPersonality', radio.id); // 'brief', 'detailed', or 'diagram'
    });
});

// Restore selection on page load
const saved = localStorage.getItem('aiPersonality');
if (saved) {
    const el = document.getElementById(saved);
    if (el) el.checked = true;
}