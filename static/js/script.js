$(function () {
  $('.chat-area > .chat-list').jScrollPane({
    mouseWheelSpeed: 30,
  })
})
function rejectMessage(messageId) {
  const reason = prompt('Enter rejection reason:')
  if (!reason) {
    alert('Rejection reason is required.')
    return
  }

  fetch(`/reject_message/${messageId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ reason: reason }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        alert('Message rejected successfully!')
        location.reload() // Refresh the page or update UI dynamically
      } else {
        alert('Error: ' + data.error)
      }
    })
    .catch((error) => console.error('Error:', error))
}
