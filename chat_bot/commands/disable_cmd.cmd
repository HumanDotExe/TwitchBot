name: "disable_command"
aliases: "disable-cmd"
rights:
    user: false
    moderator: true
output:
    message:
        success: "Command '{param0}' disabled."
        fail: "Command '{param0}' is already disabled."
        not_found: "Command '{param0}' not found!"
parameter-count: 1