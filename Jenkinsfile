//
// Jenkinsfile
//
// Jenkins pipeline file for Example Docker image builds. This defines the
// Jenkins job that builds your Docker image.
//
// @author Nick Hentschel <nhentschel@wayfair.com>
// @copyright 2018 Wayfair, LLC. -- All rights reserved.

@Library('jenkins-pipeline-library') _

dockerBuildPipeline {
  // Optional parameters below affect builds. All settings have defaults, and
  // it's highly likely the defaults will work for you. Uncomment anything you
  // need to change.

  imagesToSkip = ['devbox', 'test']     // Images that should be skipped for CI builds.
  runGossTests = false     // Whether Goss tests should be run.
  // buildsToKeep = 25     // Number of builds to store in job history, must be an integer.
  // rebuildAll   = false  // Whether to rebuild all images every time a commit is pushed.
  // skipPublish  = false  // Whether the publishing of images should be skipped. Useful for testing.
  // slaveLabel   = 'ci'   // Slave label to build on.
}


