import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

const ChatBot = () => {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [lastFeedback, setLastFeedback] = useState(null); // to disable feedback after vote

  const sendMessage = async () => {
    if (!userInput.trim()) return;

    const newMessages = [...messages, { role: 'user', text: userInput }];
    setMessages(newMessages);
    setUserInput('');
    setLoading(true);
    setLastFeedback(null); // reset feedback on new message

    try {
      const res = await axios.post('http://localhost:5000/api/chat', {
        messages: newMessages.map(msg => msg.text),
      });

      setMessages([
        ...newMessages,
        { role: 'bot', text: res.data.reply || 'No response' },
      ]);
    } catch (err) {
      console.error(err);
      setMessages([...newMessages, { role: 'bot', text: 'Error talking to AI.' }]);
    } finally {
      setLoading(false);
    }
  };

  const sendFeedback = async (type) => {
    const lastUserMsg = messages.filter(m => m.role === 'user').slice(-1)[0];
    const lastBotMsg = messages.filter(m => m.role === 'bot').slice(-1)[0];
    if (!lastUserMsg || !lastBotMsg) return;

    try {
      await axios.post('http://localhost:5000/api/feedback', {
        question: lastUserMsg.text,
        reply: lastBotMsg.text,
        feedback: type, // "up" or "down"
      });
      setLastFeedback(type); // disable buttons after click
    } catch (err) {
      console.error("Failed to submit feedback:", err);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') sendMessage();
  };

  return (
    <div style={styles.container}>
      <h2>🤖 Gemini Chatbot</h2>
      <div style={styles.chatBox}>
        {messages.map((msg, i) => (
          <div key={i} style={{ ...styles.msg, alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start', background: msg.role === 'user' ? '#dcf8c6' : '#e6e6e6' }}>
            <strong>{msg.role === 'user' ? 'You' : 'Gemini'}:</strong> <ReactMarkdown>{msg.text}</ReactMarkdown>
          </div>
        ))}

        {/* Feedback buttons after last bot response */}
        {!loading && messages.length >= 2 && messages[messages.length - 1].role === 'bot' && (
          <div style={{ alignSelf: 'flex-start', marginTop: 8 }}>
            {lastFeedback ? (
              <span>Thanks for your feedback! 👍</span>
            ) : (
              <>
                <button style={styles.fbBtn} onClick={() => sendFeedback("up")}>👍</button>
                <button style={styles.fbBtn} onClick={() => sendFeedback("down")}>👎</button>
              </>
            )}
          </div>
        )}

        {loading && <div style={styles.typing}>Gemini is thinking...</div>}
      </div>

      <div style={styles.inputArea}>
        <input
          style={styles.input}
          placeholder="Ask something..."
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button style={styles.button} onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
};

const styles = {
  container: { maxWidth: 600, margin: '50px auto', fontFamily: 'Arial' },
  chatBox: { display: 'flex', flexDirection: 'column', border: '1px solid #ccc', padding: 20, height: 400, overflowY: 'auto', marginBottom: 10, borderRadius: 8, color: 'black' },
  msg: { padding: '8px 12px', borderRadius: 10, marginBottom: 6, maxWidth: '80%' },
  inputArea: { display: 'flex' },
  input: { flex: 1, padding: 10, fontSize: 16, border: '1px solid #ccc', borderRadius: 5 },
  button: { marginLeft: 8, padding: '10px 20px', fontSize: 16, backgroundColor: '#007bff', color: '#fff', border: 'none', borderRadius: 5 },
  typing: { fontStyle: 'italic', color: '#777' },
  fbBtn: { fontSize: 18, marginRight: 10, cursor: 'pointer', background: 'none', border: 'none' },
};

export default ChatBot;
