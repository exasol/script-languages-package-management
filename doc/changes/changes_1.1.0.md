# 1.1.0 - 2026-03-10

## Summary

This release adds the exaslpm version to the Docker image tag. 
Also, all variables from the package config file history are added as environment variables when running a conda command.
Besides, there is one internal fix for the CD. 

## Bugs

 * #98: Fixed latest tag creation in CD

## Refactorings

 * #105: Added version to docker tag

## Features

 * #103: Changed micromamba_env.conda_cmd_from_history() to add all variables from history when creating env variable for conda

## Dependency Updates

### `dev`
* Updated dependency `pyinstaller:6.18.0` to `6.19.0`
* Updated dependency `types-pyinstaller:6.18.0.20260115` to `6.19.0.20260215`
