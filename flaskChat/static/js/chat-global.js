$(document).ready( () => {
    var socket = io.connect('http://127.0.0.1:5000/chat/global')
    
    socket.on('connect', () => {
        socket.emit('userConnected-global')

        socket.on('joined-global', (username) => {
            $('.messages').append(`<div class="message"><strong>${username} is connected</strong></div>`)
        })
    })

    socket.on('userMessage', (msg) => {
        $('.messages').append(`<div class="message"><strong>${msg['User']}</strong>: ${msg['Message']}</div>`)
    })


    $('#send').on('click', (event) => {
        event.preventDefault() 
        message = $('input[name=message]').val()
        msgObject = {
            message : message,
        }

        socket.emit('sendMessage', msgObject)
        $('input[name=message]').val(' ')
    })

    socket.on('userDisconnected', (username) => {
        $('.messages').append(`<div class="message"><strong>${username} disconnected</strong></div>`)
    })

})