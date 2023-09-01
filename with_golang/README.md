# Radius user expire date updater with golang
We love more speed so why not? 🤣

Let's overkill it.

# Install golang
https://go.dev/doc/install

**OR**

# Download the compile executable in the release
We will provide later

# Usage

## Help
```bash
go run automat.go --help
```

## Basic usage

```bash
go run automate.go --url http://radmandemo.dmasoftlab.com --username admin --password 1111 --date 2023-09-02

go run automate.go --delim "," --csvfile users2.csv

go run automat.go --url http://localhost/radiusmanager --username admin --password admin --date 2023-09-30

go run automate.go --url http://localhost/ --username admin --password 1111 --date 2023-09-02 --userfile mybackupuser.csv --userfield user --delim , --thread 20
```
