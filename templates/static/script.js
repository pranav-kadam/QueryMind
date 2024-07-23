function downloadChat() {
    const chatContainer = document.getElementById('chat-container');
    let chatContent = {
        success: true,
        chat: [],
        apiResponses: [] // New array to store API responses
    };

    chatContainer.querySelectorAll('.message').forEach((messageElement) => {
        const isUserMessage = messageElement.classList.contains('user-message');
        const author = isUserMessage ? "User" : "Claude";
        const messageText = messageElement.textContent.trim();

        chatContent.chat.push({
            author: author,
            message: messageText
        });

        // If it's a Claude message, check for associated API response
        if (!isUserMessage) {
            const apiResponseElement = messageElement.querySelector('.api-response');
            if (apiResponseElement) {
                const apiResponse = JSON.parse(apiResponseElement.dataset.apiResponse);
                chatContent.apiResponses.push(apiResponse);
            }
        }
    });

    // Fetch any stored API responses from the server
    fetch('/get_api_responses')
        .then(response => response.json())
        .then(data => {
            // Merge the fetched API responses with the existing ones
            chatContent.apiResponses = chatContent.apiResponses.concat(data.api_responses);

            // Create and download the file
            const blob = new Blob([JSON.stringify(chatContent, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'chat_history.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        })
        .catch(error => console.error('Error fetching API responses:', error));
}

function executeQuery() {
    const query = document.getElementById('query-input').value;
    const chatContainer = document.getElementById('chat-container');
    
    if (!query.trim()) return;

    chatContainer.innerHTML += `<div class="message user-message">${query}</div>`;
    document.getElementById('query-input').value = '';
    
    const loaderHTML = `
        <div class="loader" id="loader">
            <span></span><span></span><span></span>
        </div>
    `;
    chatContainer.innerHTML += loaderHTML;

    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    axios.post('/query', { query: query })
        .then(function (response) {
            const loader = document.getElementById('loader');
            if (loader) {
                loader.remove();
            }

            if (response.data.success) {
                const table = createTable(response.data.result);
                const insights = formatInsights(response.data.insights);
                
                chatContainer.innerHTML += `
                    <div class="message system-message">
                        <h4>Query Result:</h4>
                        ${table}
                        <h4>Insights:</h4>
                        ${insights}
                    </div>
                `;
            } else {
                chatContainer.innerHTML += `
                    <div class="message system-message">
                        <p class="error">${response.data.error}</p>
                    </div>
                `;
            }
            
            chatContainer.scrollTop = chatContainer.scrollHeight;
        })
        .catch(function (error) {
            console.error('Error:', error);
            const loader = document.getElementById('loader');
            if (loader) {
                loader.remove();
            }

            chatContainer.innerHTML += `
                <div class="message system-message">
                    <p class="error">${JSON.stringify(error.response ? error.response.data : error.message)}</p>
                </div>
            `;
            
            chatContainer.scrollTop = chatContainer.scrollHeight;
        });
}

function createTable(data) {
    if (data.length === 0) {
        return '<p>No results found.</p>';
    }
    
    let table = '<table>';
    table += '<thead><tr>';
    for (let key in data[0]) {
        table += `<th>${key}</th>`;
    }
    table += '</tr></thead><tbody>';
    
    data.forEach(row => {
        table += '<tr>';
        for (let key in row) {
            table += `<td>${row[key]}</td>`;
        }
        table += '</tr>';
    });
    
    table += '</tbody></table>';
    return table;
}

function formatInsights(insights) {
    return `
        <div class="insights-container">
            <div class="insights-title">Insights</div>
            ${insights.split('\n').map(line => `<div class="insight">${line}</div>`).join('')}
        </div>
    `;
}

document.getElementById('query-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        executeQuery();
    }
});

document.getElementById('query-input').addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});