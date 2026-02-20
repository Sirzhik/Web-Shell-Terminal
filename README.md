# Web Shell Terminal

## Description

Web Shell Terminal (WST) is a web-based SSH client for system administrators. If you manage many machines and users with different access levels, WST helps centralize account management by linking web and SSH accounts to your own groups and managing permissions through a convenient admin panel. The project supports PostgreSQL and SQLite databases.

### Example of CLI in WST
![CLI in the web](images/cli-in-web.png)

## Installation

### Important
Before running WST, update the `admin` passkey and the encryption key in `src/.env` to your own values.

### Run via Docker
Clone the repository and run the included script:

```bash
git clone https://github.com/Sirzhik/Web-Shell-Terminal.git
cd Web-Shell-Terminal
sh run.sh
```

### Run without Docker
Clone the repository, create a Python virtual environment, install dependencies, and run the server from `src/`:

```bash
git clone https://github.com/Sirzhik/Web-Shell-Terminal.git
cd Web-Shell-Terminal

# Create and activate a virtual environment
python3 -m venv .
source ./bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install JavaScript dependencies (from the src directory)
cd src/
npm install @xterm/xterm

# Run the application
python3 main.py
```

Make sure you have both Python and npm available on your system before proceeding.
