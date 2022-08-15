name: "enable_command"
aliases: "enable-cmd"
rights:
    user: false
    moderator: true
output:
    message:
        success: "Command '{param0}' enabled."
        fail: "Command '{param0}' is already enabled."
        not_found: "Command '{param0}' not found!"
parameter-count: 1