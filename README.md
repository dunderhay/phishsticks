# Background

![Version: 0.0.3-dev](https://img.shields.io/badge/version-0.0.3--dev-blue)

![image](phishsticks/static/images/logo.png)

A phishing framework for OAuth 2.0 device code authentication grant flow

# Getting Started

#### Create/activate virtual env and install requirements:

```
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

#### Running the program:

```
./run.sh
```

A self-signed certificate and default login credentials are generated on first run:

```
./run.sh
Generating a 4096 bit RSA private key
...............................<snip>
writing new private key to 'key.pem'
-----
 * Serving Flask app 'phishsticks' (lazy loading)
 * Environment: development
 * Debug mode: on
---------------------------
---Default login details---
---------------------------
Username: admin
Password: x3m8Y4MNyoqy5ylk
---------------------------
<snip>
```

# Acknowledgements

Thanks to my employer <a href='https://www.aurainfosec.com/'>Aura Information Security</a> for providing time for me to work on this project. 

![aura-logo](https://user-images.githubusercontent.com/27876907/188373880-8157648c-eb94-4054-81c8-7c61692b0367.png)

# Development

Pull requests are welcome! Apart from todos littered in the code + bad code that needs fixing / refactoring there is a [to-do list here](/todo.md)

![Python 3.9.13](https://img.shields.io/badge/python-3.9.13-blue)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Install code formatter before starting dev work and set up your editor to auto format code when you save a file

```
./venv/bin/python -m pip install -U black
```
