// https://github.com/bloodorangeio/reggie#making-requests
package main

import (
  "encoding/json"
  "fmt"
  "os"

  "github.com/bloodorangeio/reggie"
)

type ImageTags struct {
  Name string `json:"name"`
  Tags []string `json:"tags"`
}

func main() {
  client, err := reggie.NewClient("http://registry:5000",
    //reggie.WithUsernamePassword("myuser", "mypass"),  // registry credentials
    reggie.WithDefaultName("simple"),           // default repo name
    //reggie.WithDebug(true)
  )

  if err != nil {
    fmt.Printf("Err making client: %v", err);
    os.Exit(1)
  }

  req := client.NewRequest(reggie.GET, "/v2/<name>/tags/list")
  resp, err := client.Do(req)
  if err != nil {
    fmt.Printf("Err making request: %v", err);
    os.Exit(1)
  }
  fmt.Println("Status Code:", resp.StatusCode())

  var tags ImageTags
  err = json.Unmarshal(resp.Body(), &tags)
  if err != nil {
    fmt.Printf("Could not unmarshal response: %v", err)
    os.Exit(1)
  }

  for _, tag := range tags.Tags {
    fmt.Println(tag)
  }
}
