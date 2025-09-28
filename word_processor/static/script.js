        const editor = document.getElementById('editor');
        const htmlSource = document.getElementById('html-source');
        const chatContainer = document.getElementById('chat-container');
        const chatInput = document.getElementById('chat-input');
        const chatSend = document.getElementById('chat-send');

        let chatHistory = [];

        async function refreshDocument() {
            const [jsonResponse, htmlResponse] = await Promise.all([
                fetch('/document'),
                fetch('/document/html')
            ]);

            const jsonData = await jsonResponse.json();
            const htmlData = await htmlResponse.text();

            htmlSource.value = JSON.stringify(jsonData, null, 2);
            editor.innerHTML = htmlData;
        }

        async function sendMessage() {
            const message = chatInput.value;
            if (!message) return;

            appendMessage('user', message);
            chatInput.value = '';

            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message, history: chatHistory })
            });

            const data = await response.json();
            chatHistory.push({ role: 'user', content: message });
            chatHistory.push(data.message);

            appendMessage('assistant', data.message.content);
        }

        function appendMessage(role, content) {
            const messageElement = document.createElement('div');
            messageElement.innerHTML = `<strong>${role}:</strong> ${content}`;
            chatContainer.appendChild(messageElement);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        chatSend.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        let currentVersion = 0;

        async function pollForChanges() {
            try {
                const response = await fetch(`/document/wait-for-change/${currentVersion}`);
                if (response.status === 200) {
                    const data = await response.json();
                    if (data.version > currentVersion) {
                        currentVersion = data.version;
                        await refreshDocument();
                    }
                }
            } catch (e) {
                console.error("Polling error:", e);
                // Add a delay before retrying to avoid spamming the server in case of errors
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
            // Use requestAnimationFrame to avoid tight loop in case of immediate responses
            requestAnimationFrame(pollForChanges);
        }

        window.onload = async () => {
            const response = await fetch('/document/version');
            const data = await response.json();
            currentVersion = data.version;
            await refreshDocument();
            pollForChanges();
        };