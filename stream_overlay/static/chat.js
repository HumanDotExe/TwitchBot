var conn = null;
var messages = [];

function displayChat() {
  var chat = document.getElementById("chat");
  chat.innerHTML = ""
  for (var i = 0; i < messages.length; i++) {
    console.log(messages[i].message_formatted)
    var div = document.createElement("div");
    div.setAttribute("class", "chatMessage")
    div.innerHTML = messages[i].message_formatted;
    chat.appendChild(div)
  }
}
function updateChat(message) {
  var div = document.createElement("div");
  div.setAttribute("class", "chatMessage")
  div.innerHTML = message.message_formatted;
  chat.appendChild(div)
}
function connect() {
  disconnect();
  var wsUri = (window.location.protocol=='https:'&&'wss://'||'ws://')+window.location.host+window.location.pathname;
  conn = new WebSocket(wsUri);
  console.log('Connecting...');
  conn.onopen = function() {
    console.log('Connected.');
  };
  conn.onmessage = function(e) {
    json = JSON.parse(e.data)
    switch (json.type) {
      case "UPDATE":
        messages = json.messages
        displayChat();
        break;
      case "ADD":
        messages.push(json.message)
        updateChat(json.message)
        break;
      case "CLEAR":
        messages = []
        displayChat()
    }
  };
  conn.onclose = function() {
    console.log('Disconnected.');
    conn = null;
  };
}
function disconnect() {
  if (conn != null) {
    console.log('Disconnecting...');
    conn.close();
    conn = null;
  }
}
/*$('#send').click(function() {
var text = $('#text').val();
log('Sending: ' + text);
conn.send(text);
$('#text').val('').focus();
return false;
});*/