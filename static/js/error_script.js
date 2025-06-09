document.addEventListener("DOMContentLoaded", () => {
  animateElements()
})

// Функция для анимации элементов
function animateElements() {
  const elements = document.querySelectorAll(
    ".error-icon, .error-title, .error-message, .error-code",
  )

  elements.forEach((element, index) => {
    element.style.opacity = "0"
    element.style.transform = "translateY(20px)"

    setTimeout(() => {
      element.style.transition = "all 0.5s ease"
      element.style.opacity = "1"
      element.style.transform = "translateY(0)"
    }, 100 * index)
  })
}

// Создаем эффект "плавающих" элементов
document.addEventListener("mousemove", (e) => {
  const moveX = (e.clientX - window.innerWidth / 2) / 50
  const moveY = (e.clientY - window.innerHeight / 2) / 50

  const errorIcon = document.querySelector(".error-icon")
  errorIcon.style.transform = `translate(${moveX}px, ${moveY}px)`

  const errorCode = document.querySelector(".error-code")
  errorCode.style.transform = `translate(${-moveX * 0.5}px, ${-moveY * 0.5}px)`
})
