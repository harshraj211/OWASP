document.querySelectorAll('.notice-close').forEach((button) => {
    button.addEventListener('click', () => button.parentElement.remove());
});

