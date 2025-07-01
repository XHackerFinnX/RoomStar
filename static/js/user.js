document.addEventListener("DOMContentLoaded", async function () {
    const tg = window.Telegram?.WebApp;
    const userId = tg?.initDataUnsafe?.user?.id || null;
    if (!userId) {
        window.location.href = "/error";
        return;
    }

    try {
        const response = await fetch("/api/get_user_info", {
            method: "POST",
            headers: {
            "Content-Type": "application/json",
            "X-Telegram-InitData": Telegram.WebApp.initData,
            },
            body: JSON.stringify({ user_id: userId })
        });

        if (!response.ok) throw new Error("Не удалось получить данные");

        const data = await response.json();

        document.querySelector(".user-info h3").textContent = data.name;

        if (data.avatar_base64) {
            const avatarDiv = document.querySelector(".avatar");
            avatarDiv.innerHTML = `<img src="data:image/jpeg;base64,${data.avatar_base64}" alt="avatar" style="width:40px; height:40px; border-radius:50%;">`;
        }

        if (data.redirect_url) {
            window.location.href = data.redirect_url;
        }

    } catch (err) {
        console.error("Ошибка загрузки профиля:", err);
    }
});
