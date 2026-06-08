# 1.3.0 - 2026-06-08

## Summary

Besides the usual dependency/security updates, this release contains internal improvements, fixes a few bugs
and adds two new features, see below for more details.

## Security Issues

This release fixes vulnerabilities by updating dependencies:

| Dependency | Vulnerability | Affected | Fixed in |
|------------|---------------|----------|----------|
| black | CVE-2026-32274 | 25.12.0 | 26.3.1 |
| cryptography | PYSEC-2026-35 | 46.0.5 | 46.0.6 |
| cryptography | PYSEC-2026-36 | 46.0.5 | 46.0.7 |
| cryptography | PYSEC-2026-36 | 46.0.5 | 46.0.7 |
| cryptography | PYSEC-2026-35 | 46.0.5 | 46.0.6 |
| pytest | CVE-2025-71176 | 9.0.2 | 9.0.3 |
| starlette | PYSEC-2026-161 | 0.52.1 | 1.0.1 |
| starlette | PYSEC-2026-161 | 0.52.1 | 1.0.1 |
| urllib3 | PYSEC-2026-142 | 2.6.3 | 2.7.0 |
| urllib3 | PYSEC-2026-141 | 2.6.3 | 2.7.0 |
| idna | CVE-2026-45409 | 3.11 | 3.15 |
| pip | CVE-2026-3219 | 26.0.1 | 26.1 |
| pip | CVE-2026-6357 | 26.0.1 | 26.1 |
| pygments | CVE-2026-4539 | 2.19.2 | 2.20.0 |
| requests | CVE-2026-25645 | 2.32.5 | 2.33.0 |

## Bugs

 - #109: Convert conda channels from 'set' to 'list'
 - #86: Deadlock when an exception happens during stout/err
 - #135: Fixed docker image build nightly job

## Refactorings

 - #101: Added error handling to write temp requirements to logging
 - #100: Exported additional env variable
 - #81: Changed building docker image to use executable from release  

## Features:

 - #102: Provide a custom env_activate script
 - #119: Added 'list_all_installed_packages' command
 - 

## Dependency Updates

### `main`

* Updated dependency `click:8.3.1` to `8.4.1`
* Updated dependency `pydantic:2.12.5` to `2.13.4`
* Updated dependency `types-pyyaml:6.0.12.20250915` to `6.0.12.20260518`

### `dev`

* Updated dependency `exasol-toolbox:5.1.1` to `7.0.0`
* Updated dependency `pyinstaller:6.18.0` to `6.20.0`
* Updated dependency `types-docker:7.1.0.20260109` to `7.1.0.20260518`
* Updated dependency `types-pyinstaller:6.18.0.20260115` to `6.20.0.20260518`
* Updated dependency `types-requests:2.32.4.20260107` to `2.33.0.20260518`