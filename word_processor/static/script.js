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
            await refreshDocument();
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

        window.onload = refreshDocument;