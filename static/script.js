function downloadChat() {
    const chatContainer = document.getElementById('chat-container');
    let chatContent = "";
    
    chatContainer.querySelectorAll('.message').forEach((messageElement) => {
        if (messageElement.classList.contains('user-message')) {
            chatContent += "User: " + messageElement.textContent + "\n\n";
        } else if (messageElement.classList.contains('system-message')) {
            chatContent += "Claude: " + messageElement.textContent + "\n\n";
        }
    });

    const blob = new Blob([chatContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = 'chat_conversation.txt';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
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