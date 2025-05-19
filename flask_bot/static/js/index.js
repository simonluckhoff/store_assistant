let sessionId = null;

// start chat when page loads. 
window.onload = async function() {
    try {
        const response = await fetch('/start_chat', {
            method: 'POST'
        });
        const data = await response.json();
        sessionId = data.session_id;
        addMessage(data.response, 'bot');
    } catch (error) {
        console.error('Error starting chat:', error);
    }
}

async function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    if (!message) return;

    // Display user message
    addMessage(message, 'user');
    input.value = '';

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();
        addMessage(data.response, 'bot');
    } catch (error) {
        console.error('Error:', error);
        addMessage('Sorry, there was an error processing your message.', 'bot');
    }
}

function addMessage(text, sender){
    const messages = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;  
    messageDiv.textContent = text;
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}

// Allowing enter key to send message
document.getElementById('userInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
})


// Speech - to - Text -------------------------------------

const micButton = document.getElementById('micButton');

let recognition;
if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.lang = 'en-ZA'; // South African English
    recognition.interimResults = false;
    recognition.continuous = false;

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById('userInput').value = transcript;
        sendMessage();
    };

    recognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
    };
} else {
    alert("Sorry, your browser doesn't support speech recognition.");
}

micButton.addEventListener('click', function () {
    if (recognition) {
        recognition.start();
    }
});