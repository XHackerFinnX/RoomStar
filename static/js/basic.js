// Навигация
function goToShop() {
  window.location.href = "/shop"
}

// Функции для модального окна игры
function openGame() {
  window.location.href = "/wheel"
}

// Инициализация при загрузке страницы
document.addEventListener("DOMContentLoaded", () => {
  document.body.classList.add("no-scroll"); // Блокируем скролл
  // Анимация при загрузке страницы
  const gameButtons = document.querySelectorAll(".game-btn")
  gameButtons.forEach((btn, index) => {
    btn.style.opacity = "0"
    btn.style.transform = "translateY(50px)"

    setTimeout(() => {
      btn.style.transition = "all 0.6s ease"
      btn.style.opacity = "1"
      btn.style.transform = "translateY(0)"
    }, index * 200)
  })

  // Эффект частиц при наведении на кнопки
  document.querySelectorAll(".game-btn").forEach((btn) => {
    btn.addEventListener("mouseenter", function () {
      this.style.transform = "translateY(-3px) scale(1.02)"
    })

    btn.addEventListener("mouseleave", function () {
      this.style.transform = "translateY(0) scale(1)"
    })
  })
})