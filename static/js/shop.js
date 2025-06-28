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

    if (data?.list_products?.length) {
      cart = data.list_products.map(([productId, productName, quantity]) => {
        const product = products.find(p => p.product_id === productId);
        if (!product) {
          console.warn("Продукт не найден по ID:", productId);
          return null;
        }
        if (productId == 1) {
          const starInput = document.getElementById('star-count');
          starInput.value = quantity;
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

// async function fetchExpectationStatusUser(userId) {
//   try {
//     await fetch("/api/expectation-basket-user", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//         "X-Telegram-InitData": Telegram.WebApp.initData,
//       },
//       body: JSON.stringify({ user_id: userId })
//     });
//   } catch (err) {
//     console.error("Ошибка при обновлении корзины в статус ожидание оплаты:", err);
//   }
// }

function goToHome() {
  window.location.href = "/"
}

function initializeShop() {
  const productsGrid = document.getElementById("products-grid")
  if (!productsGrid) return

  productsGrid.innerHTML = ""

  products.forEach((product) => {
    if (product.product_id == 1) {
      return;
    } else {
      const productCard = document.createElement("div")
      productCard.className = "product-card compact"

      const cartItem = cart.find((item) => item.id === product.product_id)
      const quantity = cartItem ? cartItem.quantity : 0
      productCard.innerHTML = `
          <div class="product-left">
            <div class="product-image">${product.image}</div>
            <div class="product-info">
              <div class="product-name">${product.name}</div>
              <div class="product-price">
                <span class="new-price">${product.new_price} ₽</span>
              </div>
            </div>
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
    }
  })
}

// Обработчик для поля ввода количества звёзд
const starInput = document.getElementById('star-count');
if (starInput) {
  starInput.addEventListener('input', function() {
    let value = parseInt(this.value);
    if (isNaN(value) || value < 0) {
      value = 0;
    }

    // Найдем товар-звезды, например, с product_id === 'stars'
    const starProduct = products.find(p => p.product_id === 'stars') || products[0];
    if (!starProduct) return;

    // Очистить корзину
    cart = [];

    // Если value > 0, добавляем звёздный товар
    if (value > 0) {
      cart.push({
        id: starProduct.product_id,
        name: starProduct.name,
        image: starProduct.image,
        price: starProduct.new_price,
        quantity: value,
        stars: starProduct.stars_price,
      });
    }

    updateCartCount();
    initializeShop();
  });
}

function addToCart(productId) {
  const starInput = document.getElementById('star-count');
  if (starInput) {
    starInput.value = ''; // сбросить поле ввода
  }

  // Удалить звёздный товар из корзины, если он есть
  const starProduct = products.find(p => p.product_id === 'stars') || products[0];
  if (starProduct) {
    cart = cart.filter(item => item.id !== starProduct.product_id);
  }

  const product = products.find((p) => p.product_id === productId);
  if (!product) return;

  const existingItem = cart.find((item) => item.id === productId);

  if (existingItem) {
    existingItem.quantity += 1;
  } else {
    cart.push({
      id: product.product_id,
      name: product.name,
      image: product.image,
      price: product.new_price,
      quantity: 1,
      stars: product.stars_price,
    });
  }

  updateCartCount();
  initializeShop();
}

function removeFromCart(productId) {
  const starInput = document.getElementById('star-count');
  if (starInput) {
    starInput.value = ''; // сбросить поле ввода
  }

  cart = cart.filter(item => item.id !== productId);

  updateCartCount();
  initializeShop();
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
    const itemTotal = Math.round(item.price * item.quantity * 100) / 100;
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
    const itemTotal = Math.round(item.price * item.quantity * 100) / 100;
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
  if (method === "card") {
    const bankDetails = document.getElementById("bank-transfer-details");
    if (bankDetails) {
      bankDetails.style.display = "block";

      const userIdDisplay = document.getElementById("bank-user-id");
      if (userIdDisplay && userId) {
        userIdDisplay.textContent = userId;
      }
    }
    return; // Не завершаем заказ, ждем чек
  }

  try {
    await fetch("/api/add-order", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Telegram-InitData": Telegram.WebApp.initData,
      },
      body: JSON.stringify({
        user_id: userId,
        list_products: cart.map(item => [item.id, item.name, item.quantity]),
        payment_method: method,
      }),
    });

    cart = [];
    updateCartCount();
    initializeShop();
    closeCheckoutModal();
  } catch (err) {
    console.error("Ошибка при оформлении заказа:", err);
  }
}

async function init() {
  userId = Telegram.WebApp.initDataUnsafe.user.id;
  if (!userId) {
    console.error("Не удалось получить userId");
    return;
  }

  await fetchProducts();
  await fetchUserData(userId);
  await fetchUserBasket(userId);
  await fetchUserDownloadBasket(userId);

  updateCartCount();
  initializeShop();

  // Инициализация обработчика для поля ввода (вызовется в конце init)
  const starInput = document.getElementById('star-count');
  if (starInput) {
    starInput.addEventListener('input', function() {
      let value = parseInt(this.value);
      if (isNaN(value) || value < 0) {
        value = 0;
      }

      const starProduct = products.find(p => p.product_id === 'stars') || products[0];
      if (!starProduct) return;

      cart = [];

      if (value > 0) {
        cart.push({
          id: starProduct.product_id,
          name: starProduct.name,
          image: starProduct.image,
          price: starProduct.new_price,
          quantity: value,
          stars: starProduct.stars_price,
        });
      }

      updateCartCount();
      initializeShop();
    });
  }
}

init();

function selectPaymentMethod(method) {
  if (method === 'card') {
    document.getElementById('payment-details').style.display = 'block';
  }
}

async function submitPaymentProof() {
  const fileInput = document.getElementById('payment-proof');
  const file = fileInput.files[0];

  if (!file) {
    alert('Пожалуйста, загрузите чек.');
    return;
  }

  const formData = new FormData();
  formData.append('user_id', userId);
  formData.append('proof', file);
  console.log(formData);

  try {
    const response = await fetch('/api/upload-proof', {
      method: 'POST',
      headers: {
        'X-Telegram-InitData': Telegram.WebApp.initData,
      },
      body: formData,
    });

    if (!response.ok) throw new Error('Upload failed');

    alert('Звезды скоро поступят вам на баланс.');
    updateCartCount();
    closeCheckoutModal();
    // await fetchExpectationStatusUser(userId);
    window.location.href = "/";
  } catch (err) {
    alert('Ошибка при загрузке файла');
    console.error(err);
  }
}

// JavaScript для отображения информации о файле
document.getElementById('payment-proof').addEventListener('change', function(e) {
    const file = e.target.files[0];
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    
    if (file) {
        this.classList.add('has-file');
        fileName.textContent = file.name;
        fileSize.textContent = `Размер: ${(file.size / 1024 / 1024).toFixed(2)} MB`;
        fileInfo.classList.add('show');
    } else {
        this.classList.remove('has-file');
        fileInfo.classList.remove('show');
    }
});