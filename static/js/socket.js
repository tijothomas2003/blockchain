const socket = io('https://blockchain-2-1ig3.onrender.com', {
  transports: ['websocket', 'polling'],
})

socket.on('connect', () => {
  console.log('Connected to WebSocket server')
})

socket.on('message_approved', (data) => {
  console.log('Message Approved:', data)
  // Update the chat UI dynamically
})

socket.on('message_rejected', (data) => {
  console.log('Message Rejected:', data)
  // Handle rejected messages in the UI
})

function sendMessage(message, userid) {
  socket.emit('send_message', { message, userid })
}
