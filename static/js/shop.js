// Корзина
let cart = []

// Глобальная переменная userId
let userId = null;

// Товары (будут загружены через POST)
const products = []

// Загрузка товаров с сервера
async function fetchProducts() {
  try {
    const res = await fetch("/api/get-products", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Telegram-InitData": Telegram.WebApp.initData,
      },
    });

    const data = await res.json();
    if (Array.isArray(data.products)) {
      products.length = 0;
      products.push(...data.products);
    } else {
      console.error("Неверный формат данных:", data);
    }
  } catch (err) {
    console.error("Ошибка при получении товаров:", err);
  }
}

// Загрузка пользователя с сервера
async function fetchUserData(userId) {
  try {
    const response = await fetch("/api/get_username", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Telegram-InitData": Telegram.WebApp.initData,
      },
      body: JSON.stringify({ user_id: userId })
    });

    const data = await response.json();

    if (data.name && data.telegram) {
      const nameElement = document.getElementById("user-name");
      const telegramElement = document.getElementById("user-telegram");

      if (nameElement) nameElement.textContent = data.name;
      if (telegramElement) telegramElement.textContent = data.telegram;
    }
  } catch (err) {
    console.error("Ошибка при получении пользователя:", err);
  }
}

async function fetchUserBasket(userId) {
  try {
    const response = await fetch("/api/add-busket-user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Telegram-InitData": Telegram.WebApp.initData,
      },
      body: JSON.stringify({ user_id: userId })
    });
  } catch (err) {
    console.error("Ошибка при получении пользователя:", err);
  }
}

async function fetchUserDownloadBasket(userId) {
  try {
    const response = await fetch("/api/get-busket-user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Telegram-InitData": Telegram.WebApp.initData,
      },
      body: JSON.stringify({ user_id: userId })
    });

    const data = await response.json();
    console.log(data);

    if (data?.list_products?.length) {
      cart = data.list_products.map(([productId, productName, quantity]) => {
        const product = products.find(p => p.product_id === productId);
        if (!product) {
          console.warn("Продукт не найден по ID:", productId);
          return null;
        }
        return {
          id: product.product_id,
          name: product.name,
          image: product.image,
          price: product.new_price,
          quantity,
          stars: product.stars_price,
        };
      }).filter(Boolean);
    }
  } catch (err) {
    console.error("Ошибка при получении корзины:", err);
  }
}

async function fetchExpectationStatusUser(userId) {
  try {
    await fetch("/api/expectation-basket-user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Telegram-InitData": Telegram.WebApp.initData,
      },
      body: JSON.stringify({ user_id: userId })
    });
  } catch (err) {
    console.error("Ошибка при обновлении корзины в статус ожидание оплаты:", err);
  }
}

function goToHome() {
  window.location.href = "/"
}

function initializeShop() {
  const productsGrid = document.getElementById("products-grid")
  if (!productsGrid) return

  productsGrid.innerHTML = ""

  products.forEach((product) => {
    const productCard = document.createElement("div")
    productCard.className = "product-card"

    const cartItem = cart.find((item) => item.id === product.product_id)
    const quantity = cartItem ? cartItem.quantity : 0

    productCard.innerHTML = `
      <div class="product-image">${product.image}</div>
      <div class="product-name">${product.name}</div>
      <div class="product-price">
        <span class="old-price">${product.old_price} ₽</span>
        <span class="new-price">${product.new_price} ₽</span>
      </div>
      <div class="product-controls">
        ${
          quantity === 0
            ? `<button class="add-btn" onclick="addToCart(${product.product_id})">+</button>`
            : `
              <button class="quantity-btn" onclick="removeFromCart(${product.product_id})">−</button>
              <span class="quantity-display">${quantity}</span>
              <button class="quantity-btn" onclick="addToCart(${product.product_id})">+</button>
            `
        }
      </div>
    `
    productsGrid.appendChild(productCard)
  })
}

function addToCart(productId) {
  const product = products.find((p) => p.product_id === productId)
  if (!product) return

  const existingItem = cart.find((item) => item.id === productId)

  if (existingItem) {
    existingItem.quantity += 1
  } else {
    cart.push({
      id: product.product_id,
      name: product.name,
      image: product.image,
      price: product.new_price,
      quantity: 1,
      stars: product.stars_price,
    })
  }

  updateCartCount()
  if (document.getElementById("products-grid")) {
    initializeShop()
  }
}

function removeFromCart(productId) {
  const existingItem = cart.find((item) => item.id === productId)
  if (existingItem) {
    existingItem.quantity -= 1
    if (existingItem.quantity <= 0) {
      cart = cart.filter((item) => item.id !== productId)
    }
  }
  updateCartCount()
  updateCartDisplay()
  if (document.getElementById("products-grid")) {
    initializeShop()
  }
}

function updateCartCount() {
  const cartCountElement = document.getElementById("cart-count")
  if (cartCountElement) {
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0)
    cartCountElement.textContent = totalItems
    cartCountElement.style.display = totalItems > 0 ? "flex" : "none"
  }
}

function openCartModal() {
  document.getElementById("cartModal").style.display = "block"
  document.body.classList.add("no-scroll")
  updateCartDisplay()
}

function closeCartModal() {
  document.getElementById("cartModal").style.display = "none"
  document.body.classList.remove("no-scroll")
}

async function updateCartDisplay() {
  const cartItemsElement = document.getElementById("cart-items");
  const cartTotalElement = document.getElementById("cart-total");
  const totalAmountElement = document.getElementById("total-amount");
  const totalAmountElementStars = document.getElementById("total-amount-stars");

  if (cart.length === 0) {
    cartItemsElement.innerHTML = '<p class="empty-cart">Корзина пуста</p>';
    cartTotalElement.style.display = "none";
    return;
  }

  cartItemsElement.innerHTML = "";
  let totalAmount = 0;
  let totalAmountStars = 0;
  const list_products = [];

  cart.forEach((item) => {
    const itemTotal = item.price * item.quantity;
    const itemTotalStars = item.stars * item.quantity;
    totalAmount += itemTotal;
    totalAmountStars += itemTotalStars;

    list_products.push([item.id, item.name, item.quantity]);

    const cartItemElement = document.createElement("div");
    cartItemElement.className = "cart-item";
    cartItemElement.innerHTML = `
      <div class="cart-item-info">
        <div class="cart-item-image">${item.image}</div>
        <div class="cart-item-details">
          <h4>${item.name}</h4>
          <div class="cart-item-quantity">Количество: ${item.quantity}</div>
        </div>
      </div>
      <div class="cart-item-price">Звезд: ${itemTotalStars} ⭐</div>
      <div class="cart-item-price">Рублей: ${itemTotal} ₽</div>
    `;
    cartItemsElement.appendChild(cartItemElement);
  });

  totalAmountElementStars.textContent = `${totalAmountStars} ⭐`;
  totalAmountElement.textContent = `${totalAmount} ₽`;
  cartTotalElement.style.display = "block";

  try {
    await fetch("/api/save-busket-user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Telegram-InitData": Telegram.WebApp.initData,
      },
      body: JSON.stringify({
        user_id: userId,
        list_products: list_products,
        total_sum_rub: totalAmount,
        total_sum_star: totalAmountStars
      })
    });
  } catch (err) {
    console.error("Ошибка при сохранении корзины:", err);
  }
}

function proceedToCheckout() {
  if (cart.length === 0) return

  closeCartModal()
  document.getElementById("checkoutModal").style.display = "block"
  document.body.classList.add("no-scroll")
  updateCheckoutDisplay()
}

function closeCheckoutModal() {
  document.getElementById("checkoutModal").style.display = "none"
  document.body.classList.remove("no-scroll")
}

function updateCheckoutDisplay() {
  const checkoutItemsElement = document.getElementById("checkout-items")
  const checkoutTotalElement = document.getElementById("checkout-total-amount")
  const checkoutTotalElementStars = document.getElementById("checkout-total-amount-stars")

  checkoutItemsElement.innerHTML = ""
  let totalAmount = 0
  let totalAmountStars = 0

  cart.forEach((item) => {
    const itemTotal = item.price * item.quantity
    const itemTotalStars = item.stars * item.quantity
    totalAmount += itemTotal
    totalAmountStars += itemTotalStars

    const checkoutItemElement = document.createElement("div")
    checkoutItemElement.innerHTML = `
      <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
        <span>${item.name} × ${item.quantity}</span>
        <span>${itemTotal} ₽</span>
      </div>
    `
    checkoutItemsElement.appendChild(checkoutItemElement)
  })

  checkoutTotalElementStars.textContent = `${totalAmountStars} ⭐`
  checkoutTotalElement.textContent = `${totalAmount} ₽`
}

async function processOrder(method) {
  cart = []
  updateCartCount()
  closeCheckoutModal()
  await fetchExpectationStatusUser(userId)
  alert(`Оплата прошла успешно! Спасибо за покупку. Способ оплаты: ${getPaymentMethodName(method)}`)
  window.location.href = "/"
}

function getPaymentMethodName(method) {
  switch (method) {
    case "card": return "Банковская карта"
    case "online": return "Онлайн оплата"
    case "crypto": return "Криптокошелек"
    default: return "Неизвестный способ"
  }
}

// Загрузка при старте страницы
document.addEventListener("DOMContentLoaded", async function () {
  const tg = window.Telegram?.WebApp;
  userId = tg?.initDataUnsafe?.user?.id || null;

  if (!userId) {
    window.location.href = "/error";
    return;
  }

  await fetchUserData(userId);

  await fetchProducts();                  // Ждем загрузки товаров
  await fetchUserBasket(userId);         // Создаем корзину для пользователя
  await fetchUserDownloadBasket(userId); // Загружаем содержимое корзины

  updateCartCount();
  initializeShop();                      // Обновляем интерфейс
});
