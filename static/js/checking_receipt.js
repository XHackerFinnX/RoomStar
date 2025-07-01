class PaymentConfirmation {
  constructor() {
    this.state = "form"
    this.timeLeft = window.initialTimeLeft
    this.file = null
    this.processingProgress = 0
    this.timer = null
    this.processingTimer = null

    this.init()
  }

  init() {
    const stateMap = {
        "Ожидание чека": "form",
        "Проверяется": "processing",
        "Успешно": "success",
        "Ошибка": "error",
        "Время вышло": "expired"
    };
    let statusState = stateMap[statusPay] || "form";
    this.setupEventListeners()
    this.startTimer()
    if (statusState === 'processing') {
      this.startProcessing()
    }
    this.showState(statusState)
  }

  setupEventListeners() {
    const fileInput = document.getElementById("file-input")
    fileInput.addEventListener("change", (e) => this.handleFileUpload(e))

    // Prevent form submission on enter
    document.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        e.preventDefault()
      }
    })
  }

  startTimer() {
    this.timer = setInterval(() => {
      if (this.state !== "form" || this.timeLeft <= 0) return

      this.timeLeft--
      this.updateTimerDisplay()

      if (this.timeLeft <= 0) {
        this.setState("expired")
      }
    }, 1000)
  }

  updateTimerDisplay() {
    const mins = Math.floor(this.timeLeft / 60)
    const secs = this.timeLeft % 60
    const timeString = `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`

    const timerElement = document.getElementById("timer-text")
    if (timerElement) {
      timerElement.textContent = `Время на оплату: ${timeString}`
    }
  }

  handleFileUpload(event) {
    const file = event.target.files[0]
    if (!file) return

    const validTypes = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if (!validTypes.includes(file.type)) {
      alert("Пожалуйста, загрузите файл в формате JPG, PNG или PDF")
      return
    }

    this.file = file
    this.updateFileDisplay()
    this.updateSubmitButton()
  }

  updateFileDisplay() {
    const uploadIcon = document.getElementById("upload-icon")
    const uploadText = document.getElementById("upload-text")
    const uploadBtn = document.querySelector(".upload-btn")

    if (this.file) {
      uploadIcon.innerHTML = `
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14,2 14,8 20,8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                    <polyline points="10,9 9,9 8,9"/>
                </svg>
            `
      uploadIcon.querySelector(".icon").style.color = "#10b981"

      uploadText.innerHTML = `
                <div class="upload-main-text" style="color: #10b981; font-weight: 500;">${this.file.name}</div>
            `

      uploadBtn.classList.add("file-selected")
    }
  }

  updateSubmitButton() {
    const submitBtn = document.getElementById("submit-btn")
    if (this.file) {
      submitBtn.disabled = false
      submitBtn.textContent = "Отправить чек"
    } else {
      submitBtn.disabled = true
      submitBtn.textContent = "Сначала загрузите чек"
    }
  }

  setState(newState) {
    this.state = newState
    this.showState(newState)

    if (newState === "processing") {
      this.startProcessing()
    }
  }

  showState(state) {
    // Hide all states
    const states = ["form", "processing", "success", "error", "expired"]
    states.forEach((s) => {
      const element = document.getElementById(`${s}-state`)
      if (element) {
        element.style.display = "none"
      }
    })

    // Show current state
    const currentElement = document.getElementById(`${state}-state`)
    if (currentElement) {
      currentElement.style.display = "flex"
    }
  }

  async startProcessing() {
    const checkInterval = 10000; // 10 секунд
    let isProcessing = true;

    while (isProcessing) {
      try {
        const response = await fetch('/api/check-status', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Telegram-InitData': Telegram.WebApp.initData
          },
          body: JSON.stringify({
            user_id: userId,
            secret_id: secretId
          }),
        });

        if (!response.ok) {
          throw new Error(`Ошибка при запросе: ${response.status}`);
        }

        const data = await response.json();
        console.log('Статус:', data.status);

        if (data.status === 'Успешно') {
          isProcessing = false;
          this.setState("success");
        } 
        if (data.status === 'Ошибка') {
          isProcessing = false;
          this.setState("error");
        }
        else {
          await new Promise(resolve => setTimeout(resolve, checkInterval));
        }

      } catch (error) {
        console.error('Ошибка при проверке статуса:', error);
        isProcessing = false;
        this.setState("error");
      }
    }
  }


  copyToClipboard(text) {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(() => {
        // Could add a toast notification here
        console.log("Copied to clipboard")
      })
    } else {
      // Fallback for older browsers
      const textArea = document.createElement("textarea")
      textArea.value = text
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand("copy")
      document.body.removeChild(textArea)
    }
  }

  async handleSubmit() {
    if (!this.file) {
      alert("Пожалуйста, загрузите чек об оплате")
      return
    }

    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('proof', this.file);
    formData.append('secret_id', secretId);
    formData.append('basket_id', basketId);

    try {
      const response = await fetch('/api/upload-proof', {
        method: 'POST',
        headers: {
          'X-Telegram-InitData': Telegram.WebApp.initData,
        },
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');

    } catch (err) {
      console.error("Upload error:", err);
      alert("Ошибка при загрузке чека!")
      return
    }

    this.setState("processing")
  }

  async handleCancel() {
    try {
      const response = await fetch(`/api/delete_checking_payment?basket_id=${basketId}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          "X-Telegram-InitData": Telegram.WebApp.initData
        }
      });

      if (response.ok) {
        console.log("Чек удалён");
        window.location.href = '/'
      } else {
        console.error("Ошибка при удалении чека");
        window.location.href = "/error";
      }
    } catch (error) {
      console.error("Ошибка запроса:", error);
      window.location.href = "/error";
    }
  }

  resetForm() {
    window.location.href = '/shop'
  }
}

// Global functions for onclick handlers
function handleSubmit() {
  window.paymentApp.handleSubmit()
}

function handleCancel() {
  window.paymentApp.handleCancel()
}

function resetForm() {
  window.paymentApp.resetForm()
}

function copyToClipboard(text) {
  window.paymentApp.copyToClipboard(text)
}

// Initialize the app when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  const tg = window.Telegram?.WebApp;
    const userId = tg?.initDataUnsafe?.user?.id || null;
    if (!userId) {
        window.location.href = "/error";
        return;
    }
  window.paymentApp = new PaymentConfirmation()
})