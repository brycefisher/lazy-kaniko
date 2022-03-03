Feature: Lazy Builds

  Scenario: CI Builds And Pushes New Image to Registry
    Given an empty docker registry
    And the Dockerfile and build context "simple" image "simple"
    When Dockerfile and build context are passed to lazy-kaniko
    Then the new image exists in the docker registry

  Scenario: CI Builds And Pushes New Image to an Authenticated Registry
    Given an authenticated docker registry
    And the Dockerfile and build context "simple" image "simple"
    And valid authentication
    When Dockerfile and build context are passed to lazy-kaniko
    Then the new image exists in the docker registry

  Scenario: CI skips build when image already in unauthenticated registry
    Given an empty docker registry
    And the Dockerfile and build context "simple" image "simple"
    And the docker registry already has the tag for the build
    When Dockerfile and build context are passed to lazy-kaniko
    Then lazy-kaniko logs that it skipped the build
