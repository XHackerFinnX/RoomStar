let starsBalance = 0;
let freeSpinsLeft = 0;
const spinCost = 5;
let userId = null;

let prizes = [];

const wheel = document.querySelector(".deal-wheel");
const spinner = wheel.querySelector(".spinner");
const trigger = wheel.querySelector(".btn-spin");
const ticker = wheel.querySelector(".ticker");

let prizeSlice;
let prizeOffset;
const spinClass = "is-spinning";
const selectedClass = "selected";
const spinnerStyles = window.getComputedStyle(spinner);

let tickerAnim;
let rotation = 0;
let currentSlice = 0;
let prizeNodes;

document.addEventListener("DOMContentLoaded", async () => {
  const tg = window.Telegram?.WebApp;
  userId = tg?.initDataUnsafe?.user?.id || null;

  if (!userId) {
    window.location.href = "/error";
    return;
  }

  await loadPrizes();
  await loadUserData();

  animateElements();
  setupWheel();

  updateSpinButtonText();

  trigger.addEventListener("click", async () => {
    if (freeSpinsLeft > 0) {
      freeSpinsLeft--;
    } else {
      if (starsBalance < spinCost) {
        alert("Недостаточно звезд для вращения!");
        return;
      }
      starsBalance -= spinCost;
    }

    updateSpinButtonText();
    trigger.disabled = true;

    const targetIndex = chooseWeightedPrizeIndex();
    const extraSpins = spinertia(5, 8);
    const randomOffset = Math.random() * (prizeSlice / 2) - prizeSlice / 4;
    rotation = extraSpins * 360 + targetIndex * prizeSlice + prizeSlice / 2 + randomOffset;

    prizeNodes.forEach((prize) => prize.classList.remove(selectedClass));
    wheel.classList.add(spinClass);
    spinner.style.setProperty("--rotate", rotation);
    ticker.style.animation = "none";
    runTickerAnimation();
  });
});

spinner.addEventListener("transitionend", async () => {
  cancelAnimationFrame(tickerAnim);
  rotation %= 360;
  const selected = Math.floor(rotation / prizeSlice);
  const winAmount = prizes[selected].amount;

  prizeNodes[selected].classList.add(selectedClass);
  starsBalance += winAmount;

  await updateUserData(starsBalance, freeSpinsLeft);
  updateBalance();
  showResult(winAmount);

  wheel.classList.remove(spinClass);
  spinner.style.setProperty("--rotate", rotation);
  trigger.disabled = false;
  updateSpinButtonText();
});

function animateElements() {
  const elements = document.querySelectorAll(".page-title, .page-subtitle, .deal-wheel, .game-info, .recent-wins");
  elements.forEach((element, index) => {
    element.style.opacity = "0";
    element.style.transform = "translateY(20px)";
    setTimeout(() => {
      element.style.transition = "all 0.6s ease";
      element.style.opacity = "1";
      element.style.transform = "translateY(0)";
    }, 200 * index);
  });
}

async function loadPrizes() {
  try {
    const response = await fetch("/api/get_prizes_wheel", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Telegram-InitData": Telegram.WebApp.initData,
      },
      body: JSON.stringify({ user_id: userId }),
    });
    const data = await response.json();

    prizes = data.prizes;

    prizeSlice = 360 / prizes.length;
    prizeOffset = Math.floor(180 / prizes.length);
  } catch (err) {
    console.error("Ошибка загрузки призов:", err);
  }
}

async function loadUserData() {
  try {
    const [balanceData, spinsData] = await Promise.all([
      fetch("/api/get_balance_wheel", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Telegram-InitData": Telegram.WebApp.initData,
        },
        body: JSON.stringify({ user_id: userId }),
      }).then((res) => res.json()),
      fetch("/api/get_free_spins_wheel", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Telegram-InitData": Telegram.WebApp.initData,
        },
        body: JSON.stringify({ user_id: userId }),
      }).then((res) => res.json()),
    ]);
    starsBalance = balanceData.balance.stars ?? 0;
    freeSpinsLeft = spinsData.freeSpins.wheel_attempt ?? 0;

    updateBalance();
  } catch (err) {
    console.error("Ошибка загрузки данных:", err);
  }
}

async function updateUserData(balance, freeSpins) {
  try {
    await fetch("/api/update_after_spin", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Telegram-InitData": Telegram.WebApp.initData,
      },
      body: JSON.stringify({ user_id: userId, stars: balance, spins: freeSpins }),
    });
  } catch (err) {
    console.error("Ошибка обновления данных:", err);
  }
}

function updateBalance() {
  document.getElementById("stars-balance").textContent = starsBalance;
}

function updateSpinButtonText() {
  const costSpan = trigger.querySelector(".spin-cost");
  const attemptsSpan = trigger.querySelector(".spin-attempts");
  if (freeSpinsLeft > 0) {
    costSpan.textContent = `Крутить за 0 ⭐`;
    attemptsSpan.textContent = `(Попыток: ${freeSpinsLeft})`;
  } else {
    costSpan.textContent = `Крутить за ${spinCost} ⭐`;
    attemptsSpan.textContent = ``;
  }
}

function setupWheel() {
  createConicGradient();
  createPrizeNodes();
  prizeNodes = wheel.querySelectorAll(".prize");
}

function createPrizeNodes() {
  spinner.innerHTML = '';
  prizes.forEach(({ text }, i) => {
    const rotation = prizeSlice * i * -1 - prizeOffset;
    spinner.insertAdjacentHTML(
      "beforeend",
      `<li class="prize" style="--rotate: ${rotation}deg"><span class="text">${text}</span></li>`
    );
  });
}

function createConicGradient() {
  spinner.style.background = `conic-gradient(
    from -90deg,
    ${prizes.map(({ color }, i) => `${color} 0 ${(100 / prizes.length) * (prizes.length - i)}%`).reverse()}
  )`;
}

function chooseWeightedPrizeIndex() {
  const totalWeight = prizes.reduce((acc, prize) => acc + prize.win, 0);
  const random = Math.random() * totalWeight;
  let cumulative = 0;
  for (let i = 0; i < prizes.length; i++) {
    cumulative += prizes[i].win;
    if (random < cumulative) return i;
  }
  return prizes.length - 1;
}

function spinertia(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function runTickerAnimation() {
  const values = spinnerStyles.transform.split("(")[1].split(")")[0].split(",");
  const a = values[0];
  const b = values[1];
  let rad = Math.atan2(b, a);
  if (rad < 0) rad += 2 * Math.PI;
  const angle = Math.round(rad * (180 / Math.PI));
  const slice = Math.floor(angle / prizeSlice);

  if (currentSlice !== slice) {
    ticker.style.animation = "none";
    setTimeout(() => (ticker.style.animation = null), 10);
    currentSlice = slice;
  }

  tickerAnim = requestAnimationFrame(runTickerAnimation);
}

function showResult(amount) {
  const modal = document.getElementById("result-modal");
  document.getElementById("result-amount").textContent = amount;
  document.getElementById("result-message").textContent = amount === 0
    ? "Не повезло! Попробуйте еще раз!"
    : "Вы выиграли звезды!";
  modal.style.display = "block";

  const modalContent = modal.querySelector(".modal-content");
  modalContent.style.transform = "scale(0.8)";
  modalContent.style.opacity = "0";
  setTimeout(() => {
    modalContent.style.transition = "all 0.5s ease";
    modalContent.style.transform = "scale(1)";
    modalContent.style.opacity = "1";
  }, 100);
}

function closeResultModal() {
  const modal = document.getElementById("result-modal");
  const modalContent = modal.querySelector(".modal-content");
  modalContent.style.transform = "scale(0.8)";
  modalContent.style.opacity = "0";
  setTimeout(() => (modal.style.display = "none"), 300);
}

function goToHome() {
  window.location.href = "/";
}

window.onclick = (e) => {
  const modal = document.getElementById("result-modal");
  if (e.target === modal) closeResultModal();
};
