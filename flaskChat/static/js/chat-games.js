$(document).ready( () => {
    var socket = io.connect('http://127.0.0.1:5000/chat/games')

    socket.on('connect', () => {
        socket.emit('userConnected-games')

        socket.on('joined-games', (username) => {
            $('.messages').append(`<div class="message"><strong>${username} is connected</strong></div>`)
        })
    })


    $('#send').on('click', (event) => {
        event.preventDefault()
        msg = $('input[name=message]').val()

        socket.emit('sendMessage', msg)
        $('input[name=message]').val(' ') 
    })

    socket.on('userMessage', (msg) => {
        $('.messages').append(`<div class="message"><strong>${msg['user']}</strong>: ${msg['message']}</div>`)
    })

    socket.on('userDisconnected', (username) => {
        $('.messages').append(`<div class="message"><strong>${username} disconnected</strong></div>`)
    })


})