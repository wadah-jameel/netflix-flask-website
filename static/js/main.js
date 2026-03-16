// ── Navbar scroll effect ──
window.addEventListener('scroll', () => {
    const navbar = document.getElementById('navbar');
    navbar.classList.toggle('scrolled', window.scrollY > 50);
});

// ── Modal ──
const overlay  = document.getElementById('modalOverlay');
const modal    = document.getElementById('movieModal');
const closeBtn = document.getElementById('modalClose');

// In main.js — build picsum URL from movie ID
function openModal(title, desc, genre, year, rating, duration, tags, movieId, color) {
    const poster = `https://picsum.photos/seed/movie${movieId}/680/220`;
    const modalHero = document.getElementById('modalHero');
    modalHero.innerHTML = `<img src="${poster}" alt="${title}" 
        style="width:100%;height:220px;object-fit:cover;border-radius:10px 10px 0 0;">`;
    // ... rest stays the same
}

    // Show poster in modal hero if available, otherwise use gradient
    const modalHero = document.getElementById('modalHero');
    if (poster) {
        modalHero.innerHTML = `<img src="${poster}" alt="${title}" style="width:100%;height:220px;object-fit:cover;border-radius:10px 10px 0 0;">`;
    } else {
        modalHero.style.background = `radial-gradient(ellipse at center, ${color} 0%, #000 100%)`;
    }

    document.getElementById('modalMeta').innerHTML = `
        <span class="star-rating">⭐ ${rating}</span>
        <span>${year}</span>
        <span>${duration}</span>
        <span>${genre}</span>
    `;

    const tagsHtml = tags.map(t => `<span class="tag">${t}</span>`).join('');
    document.getElementById('modalTags').innerHTML = tagsHtml;
    document.getElementById('modalLink').href = `/movie/${movieId}`;

    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    overlay.classList.remove('active');
    document.body.style.overflow = '';
}

closeBtn.addEventListener('click', closeModal);
overlay.addEventListener('click', (e) => {
    if (e.target === overlay) closeModal();
});
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
});
```

---

**`requirements.txt`**:
```
Flask==3.0.3
gunicorn==22.0.0
