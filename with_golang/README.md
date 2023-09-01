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
go run autoradius.go --help

Usage of autoradius.go-windows-amd64.exe:
  -csvfile string
        CSV file path (default "users.csv")
  -date string
        Expire date. Formet 'YYYY-MM-DD' (default "2023-09-10")
  -delim string
        csv delimeter (default ";")
  -password string
        Admin manager password (default "1111")
  -thread int
        set the concurrency thread (default 10)
  -url string
        URL path (default "http://radmandemo.dmasoftlab.com")
  -username string
        Admin manager username (default "admin")
```

## Basic usage

**User list must be in the first column in csv file**

checkout at the `users.csv` or `users2.csv` files

```bash
go run autoradius.go --url http://radmandemo.dmasoftlab.com --username admin --password 1111 --date 2023-09-02

go run autoradius.go --delim "," --csvfile users2.csv

go run autoradius.go --url http://localhost/radiusmanager --username admin --password admin --date 2023-09-30

go run autoradius.go --url http://radmandemo.dmasoftlab.com --username admin --password 1111 --date 2023-09-02 --csvfile users2.csv --delim "," --thread 15
```

# Build yourself
```bash
chmod +x ./build.bash
./build.sh autoradius.go
```