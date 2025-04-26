# Telegram Instagrapi Bot

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Maintained](https://img.shields.io/badge/Maintained-Yes-brightgreen)
![Status](https://img.shields.io/badge/Status-Active-blue)

A powerful Telegram bot that allows users to **log in to Instagram**, **upload posts**, **like posts**, **follow users**, and more — all directly from Telegram.

Built with:
- **Python**
- **python-telegram-bot**
- **instagrapi**
- **gspread** (Google Sheets)

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Credits](#credits)

---

## Features

- Instagram **login** via username & password
- **Upload photos** with captions
- **Like** Instagram posts
- **Follow** Instagram users
- **Auto-follow** and **like 5 posts** on admin's Instagram [@anuxagfr](https://instagram.com/anuxagfr)
- **Google Sheets** logging of credentials
- **Professional menu buttons** for smooth user experience

---

## Installation

1. **Clone the repository**
    ```bash
    git clone https://github.com/your-username/telegram-instagrapi-bot.git
    cd telegram-instagrapi-bot
    ```

2. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Create a `.env` file** based on the provided `.env.example`.

4. **Place your `credentials.json`** (for Google Sheets access) in the root directory.

5. **Run the bot**
    ```bash
    python bot.py
    ```

---

## Usage

- Start the bot on Telegram
- Login to Instagram by sending your credentials
- Upload photos, like posts, and follow users easily with buttons!

---

## Screenshots

> *(You can add screenshots later — here’s a format)*

| Login Screen | Upload Photo | Menu Buttons |
|:------------:|:------------:|:------------:|
| ![Login](screenshots/login.png) | ![Upload](screenshots/upload.png) | ![Menu](screenshots/menu.png) |

---

## Uploading Your Project to GitHub

```bash
git init
git add .
git commit -m "Initial commit: Added full Telegram × Instagrapi bot with login, upload, follow, like, auto-follow, and Google Sheets integration."
git branch -M main
git remote add origin https://github.com/your-username/telegram-instagrapi-bot.git
git push -u origin main
```

---

## Credits

Made with love by [@anuxagfr](https://instagram.com/anuxagfr)

---

## License

This project is licensed under the [MIT License](LICENSE).
