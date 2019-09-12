# Script-Runner
Web application that runs scripts

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Prerequisites
You'll need to have Python installed in order to run `Script-Runner`. Start by downloading and installing [Python](https://www.python.org/downloads/).
> *Note: Python 3 is recommended, `Script-Runner` has not been tested with Python 2 and may not work without chaning things*


## Installation
Download the latest version from GitHub using Git.
```
git clone https://github.com/zloether/Script-Runner.git
```
This will create a directory called *Script-Runner* and all the code will be in it.

Switch to the *Script-Runner* directory:
```
cd Script-Runner
```

Install the required packages:
```
pip install -r requirements
```

## Usage
Place any scripts you want to run in the *script_runner/scripts* directory.
The logs when these scripts are run will get written to the *script_runner/logs* directory.

Run the app in DEV mode with this command:
```
python script_runner/app.py
```

Access the webapp at: [http://localhost:5000](http://localhost:5000)

## License
`Script Runner` is not licensed for commercial use. If you want to use `Script Runner` for commercial purposes, please contact me.