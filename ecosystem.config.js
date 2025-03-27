module.exports = {
  apps: [{
    name: "FlaskApp",
    script: "gunicorn",
    args: "main:app -b 0.0.0.0:5000",
    interpreter: "python3"
  },{
    name: "NodeBot",
    script: "bot.js"
  }]
}
