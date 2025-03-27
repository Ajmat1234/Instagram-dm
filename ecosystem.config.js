module.exports = {
  apps: [
    {
      name: "FlaskApp",
      script: "gunicorn",
      args: "main:app --bind 0.0.0.0:5000",
      interpreter: "python3",
    },
    {
      name: "NodeBot",
      script: "bot.js",
      interpreter: "node",
      env: {
        CHROME_BIN: "/usr/bin/google-chrome-stable"
      }
    }
  ]
};
