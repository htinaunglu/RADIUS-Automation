# Radius user expire date updater
Using 
- requests
- bs4

# Install requirement
```bash
pip install -r requirements.txt
```

# Usage

## Help
```bash
python automate.py --help
```

## Basic usage

```bash
python automate.py --url http://localhost/radiusmanager --username admin --password admin --date 2023-09-30

python automate.py --url http://localhost/ --username admin --password 1111 --date 2023-09-02

python automate.py --url http://localhost/ --username admin --password 1111 --date 2023-09-02 --userfile mybackupuser.csv --userfield user --delim , --thread 20
```
