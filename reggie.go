// https://github.com/bloodorangeio/reggie#making-requests
package main

import (
  "encoding/json"
  "flag"
  "fmt"
  "os"

  "github.com/bloodorangeio/reggie"
)

var (
  registry = flag.String("registry", "https://index.docker.io", "remote registry to list tags from")
  target_image = flag.String("target_image", "", "image to scan for tags")
)

type ImageTags struct {
  Name string `json:"name"`
  Tags []string `json:"tags"`
}

func main() {
  flag.Parse()

  // Optional
  user := os.Getenv("REGISTRY_USER")
  password := os.Getenv("REGISTRY_PASSWORD")

  fmt.Printf("registry: %s\n", *registry)
  fmt.Printf("target_image: %s\n", *target_image)

  // Setup docker client
  client, err := reggie.NewClient(*registry,
    reggie.WithDefaultName(*target_image),
    reggie.WithDebug(true),
  )
  if err != nil {
    fmt.Printf("Err making client: %v\n", err);
    os.Exit(1)
  }
  if user != "" && password != "" {
    client.Config.Username = user
    client.Config.Password = password
  }

  // Talk to Docker registry
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
