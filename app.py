<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>QR-сканнер</title>
    <script src="https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; }
        #video { width: 100%; max-width: 400px; }
        canvas { display: none; }
        #result { font-size: 18px; margin-top: 10px; color: green; }
        #error { font-size: 16px; color: red; margin-top: 10px; }
    </style>
</head>
<body>
    <h2>Сканируйте QR-код</h2>
    <video id="video" autoplay playsinline></video>
    <canvas id="canvas"></canvas>
    <p id="result">Ожидание сканирования...</p>
    <p id="error"></p>

    <script>
        const video = document.getElementById("video");
        const canvas = document.getElementById("canvas");
        const context = canvas.getContext("2d");
        const resultText = document.getElementById("result");
        const errorText = document.getElementById("error");

        // ВСТАВЬТЕ СЮДА ВАШ URL из Google Apps Script (Web App)
        const SCRIPT_URL = "https://script.google.com/macros/s/XXX_ВАШ_WEB_APP_ID_XXX/exec";

        async function startScanner() {
            try {
                // Запрашиваем доступ к камере (задняя, если доступно)
                const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
                video.srcObject = stream;

                video.onloadedmetadata = () => {
                    console.log("Камера запущена:", video.videoWidth, "x", video.videoHeight);
                    // Начинаем циклическое сканирование каждые 1.5 секунды
                    scanQRCode();
                };
            } catch (error) {
                console.error("Ошибка доступа к камере:", error);
                errorText.innerText = "❌ Ошибка доступа к камере! Разрешите доступ в настройках браузера.";
            }
        }

        function scanQRCode() {
            // Захватываем кадр с камеры
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);

            const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
            const code = jsQR(imageData.data, imageData.width, imageData.height, { inversionAttempts: "dontInvert" });

            if (code) {
                console.log("QR-код найден:", code.data);
                resultText.innerText = "✅ QR-код: " + code.data;
                errorText.innerText = "";

                // Предположим, что QR-код хранит данные через запятую: "Name,Phone,Email"
                const parts = code.data.split(",");
                // Стараемся аккуратно извлечь три поля
                const name  = parts[0] ? parts[0].trim() : "";
                const phone = parts[1] ? parts[1].trim() : "";
                const email = parts[2] ? parts[2].trim() : "";

                // Отправляем данные в Google Apps Script
                fetch(SCRIPT_URL, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        Name: name,
                        Phone: phone,
                        Email: email
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        resultText.innerText = data.message;
                    } else {
                        errorText.innerText = "❌ " + (data.message || "Ошибка отправки данных!");
                    }
                })
                .catch(error => {
                    console.error("Ошибка:", error);
                    errorText.innerText = "❌ Ошибка отправки данных!";
                });
            } else {
                console.log("QR-код не найден, продолжаем сканирование...");
            }

            // Повторяем сканирование через 1.5 секунды
            setTimeout(scanQRCode, 1500);
        }

        // Запуск сканера
        startScanner();
    </script>
</body>
</html>
