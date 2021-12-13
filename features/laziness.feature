Feature: Lazy Builds

  Scenario: CI Builds And Pushes New Image to Registry
    Given an empty docker registry
    And the Dockerfile and build context "simple"
    When Dockerfile and build context are passed to lazy-kaniko
    Then the new image exists in the docker registry
