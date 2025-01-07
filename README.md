# BookChat - Git-Backed Messaging Application

A simple web-based messaging application that uses Git as a backend storage system. This application allows users to send and receive messages while maintaining a complete history of conversations using Git.

## Features

- Simple and clean web interface
- Message persistence using Git
- SQLite database for user management
- Real-time message updates
- Message history viewing
- No complex frameworks - pure Python, HTML, CSS, and JavaScript

## Technical Stack

- Backend: Python (with built-in `http.server`)
- Database: SQLite3
- Frontend: HTML5, CSS3, JavaScript
- Version Control: Git (via GitHub API)
- Authentication: Basic user authentication

## Project Structure

```
bookchat/
├── README.md
├── requirements.txt
├── .env
├── .gitignore
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── templates/
│   ├── index.html
│   └── login.html
└── src/
    ├── server.py
    ├── database.py
    ├── git_handler.py
    └── message_handler.py
```

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd bookchat
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your GitHub credentials in `.env` file:
   ```
   GITHUB_TOKEN=your_github_token
   ```

5. Initialize the database:
   ```bash
   python src/database.py
   ```

6. Run the server:
   ```bash
   python src/server.py
   ```

7. Access the application at `http://localhost:8000`

## Development

This project is built incrementally with a focus on simplicity and maintainability. Each component is designed to be independent and easily modifiable.

## Security Notes

- Store your GitHub token securely
- Never commit the `.env` file
- Use HTTPS in production
- Implement proper input validation

## License

MIT License
