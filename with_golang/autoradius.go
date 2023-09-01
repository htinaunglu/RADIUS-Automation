package main

import (
	"crypto/md5"
	"encoding/csv"
	"encoding/hex"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/http/cookiejar"
	"net/url"
	"os"
	"sync"
	"time"

	"github.com/anaskhan96/soup"
	"github.com/schollz/progressbar/v3"
	"gopkg.in/goyy/goyy.v0/util/crypto/hmac"
)

var users []string

var proxy, _ = url.Parse("http://127.0.0.1:8080")

var jar, _ = cookiejar.New(nil)

var client = &http.Client{
	// for debuging
	// Transport: &http.Transport{Proxy: http.ProxyURL(proxy)},
	Jar: jar,
}

func update_user_info(BASE_URL string, username string, date string) {
	getinfo_url := BASE_URL + "/admin.php?cont=edit_user&username=" + username
	resp, err := client.Get(getinfo_url)
	if err != nil {
		// handle error
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)

	v := url.Values{}

	// fmt.Println(string(body))

	doc := soup.HTMLParse(string(body))

	inputs := doc.FindAll("input")
	for _, input := range inputs {
		_, disabled := input.Attrs()["disabled"]
		if !disabled {
			if input.Attrs()["type"] == "text" {
				v.Add(input.Attrs()["name"], input.Attrs()["value"])
			}
			if (input.Attrs()["type"] == "checkbox") || (input.Attrs()["type"] == "radio") {
				_, checked := input.Attrs()["checked"]
				if checked {
					v.Add(input.Attrs()["name"], input.Attrs()["value"])
				}

			}
		}

	}

	select_list := doc.FindAll("select")

	for _, sel := range select_list {

		if (sel.Attrs()["name"] != "state") && (sel.Attrs()["name"] != "country") {
			options := sel.FindAll("option")
			for _, opt := range options {
				_, selected := opt.Attrs()["selected"]
				if selected {
					v.Add(sel.Attrs()["name"], opt.Attrs()["value"])
				}
			}

		}

	}

	group_select := doc.Find("select", "id", "groupid")
	group_select_opts := group_select.FindAll("option")
	v.Add(group_select.Attrs()["name"], group_select_opts[0].Attrs()["value"])
	owner_select := doc.Find("select", "id", "owner")
	owner_select_opts := owner_select.FindAll("option")
	v.Add(owner_select.Attrs()["name"], owner_select_opts[0].Attrs()["value"])

	// fmt.Println(v, len(v))
	v.Set("expiration", date)

	update_url := BASE_URL + "/admin.php?cont=update_user&username=" + username

	resp, err = client.PostForm(update_url, v)

	if err != nil {
		// handle error
		defer resp.Body.Close()
	}
	defer resp.Body.Close()
	// body, _ = io.ReadAll(resp.Body)
	// fmt.Println(string(body))
}

func admin_login(BASE_URL string, username string, passwd string) {
	md5hex := md5.Sum([]byte(passwd))
	hex_hmac_md5, _ := hmac.Md5Hex(hex.EncodeToString(md5hex[:]), username)
	// fmt.Println(hex_hmac_md5)

	v := url.Values{}
	v.Add("managername", username)
	v.Add("password", passwd)
	v.Add("lang", "English")
	v.Add("Submit", "Login")
	v.Add("md5", hex_hmac_md5)

	loginURL := BASE_URL + "/admin.php?cont=login"
	resp, err := client.PostForm(loginURL, v)

	if err != nil {
		// handle error
		defer resp.Body.Close()
	}
	defer resp.Body.Close()
	// body, _ := io.ReadAll(resp.Body)
	// fmt.Println(string(body))
}

func main() {
	start := time.Now()
	var admin_user string
	flag.StringVar(&admin_user, "username", "admin", "Admin manager username")

	var admin_passwd string
	flag.StringVar(&admin_passwd, "password", "1111", "Admin manager password")

	var BASE_URL string
	flag.StringVar(&BASE_URL, "url", "http://radmandemo.dmasoftlab.com", "URL path")

	var csv_file string
	flag.StringVar(&csv_file, "csvfile", "users.csv", "CSV file path")

	var date string
	flag.StringVar(&date, "date", "2023-09-10", "Expire date. Formet 'YYYY-MM-DD'")

	var delim string
	// ; character = 59
	flag.StringVar(&delim, "delim", ";", "csv delimeter")

	// concurrency flag
	var concurrency int
	flag.IntVar(&concurrency, "thread", 10, "set the concurrency thread")

	flag.Parse()

	// read csv file
	f, err := os.Open(csv_file)
	if err != nil {
		log.Fatal(err)
	}

	// remember to close the file at the end of the program
	defer f.Close()

	// read csv values using csv.Reader
	csvReader := csv.NewReader(f)
	// ; character
	csvReader.Comma = []rune(delim)[0]
	csvReader.FieldsPerRecord = -1
	data, err := csvReader.ReadAll()
	if err != nil {
		log.Fatal(err)
	}
	// fmt.Println(data)

	for key, value := range data {
		if key == 0 {
			continue
		}
		users = append(users, value[0])
	}
	// fmt.Println(users)

	// admin login
	admin_login(BASE_URL, admin_user, admin_passwd)
	// fmt.Println(BASE_URL, admin_user, admin_passwd, date)

	// manual test
	// update_user_info(BASE_URL, "aksinada", date)

	// channels
	user_c := make(chan string, len(users))

	// fill user channel with work
	for _, user := range users {
		user_c <- user
	}
	// important to close channel after filled up
	close(user_c)

	// progressbar
	log.Printf("Total users %d", len(users))
	bar := progressbar.Default(int64(len(users)))
	// threading
	var httpsWG sync.WaitGroup

	for i := 0; i <= concurrency; i++ {
		httpsWG.Add(1)
		go func() {
			defer func() {
				httpsWG.Done()
			}()
			// Perform some task here
			for user := range user_c {
				bar.Add(1)
				update_user_info(BASE_URL, user, date)
			}
		}()
	}

	// wait wg
	httpsWG.Wait()

	fmt.Println("Automation completed successfully!")

	elapsed := time.Since(start)
	log.Printf("Total time %s", elapsed)
}
