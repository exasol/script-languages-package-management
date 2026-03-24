# Unreleased

## Summary

Runs `apt update` before `apt-cache madison` to ensure the package index is fresh when querying available package versions.

## Bugs

 * #110: Run `apt update` before `apt-cache madison` to fix stale package index lookups
