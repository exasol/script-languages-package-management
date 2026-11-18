# 2.0.0 - 2026-11-17

## Summary

Drop support for Python 3.10; the minimum supported Python version is now 3.11.

Other changes: update dependencies, Nox and CI workflows, and integration-test package pins.

## Security Issues

This release fixes vulnerabilities by updating dependencies:

| Dependency | Vulnerability | Affected | Fixed in |
|------------|---------------|----------|----------|
| black | CVE-2026-114134 | 26.5.1 | 26.10.1 |
| certifi | PYSEC-2026-4320 | 2026.5.20 | 2026.10.18 |
| certifi | PYSEC-2026-4320 | 2026.5.20 | 2026.10.18 |
| cryptography | PYSEC-2026-3554 | 48.0.0 | 49.0.0 |
| cryptography | PYSEC-2026-3552 | 48.0.0 | 50.0.0 |
| cryptography | PYSEC-2026-3553 | 48.0.0 | 49.0.0 |
| cryptography | PYSEC-2026-3552 | 48.0.0 | 50.0.0 |
| cryptography | PYSEC-2026-3553 | 48.0.0 | 49.0.0 |
| cryptography | PYSEC-2026-3554 | 48.0.0 | 49.0.0 |
| cryptography | GHSA-537c-gmf6-5ccf | 48.0.0 | 48.0.1 |
| filelock | CVE-2026-112940 | 3.29.1 | 4.2.1 |
| filelock | CVE-2026-112913 | 3.29.1 | 4.2.1 |
| filelock | CVE-2026-112907 | 3.29.1 | 4.2.1 |
| filelock | CVE-2026-112936 | 3.29.1 | 4.0.9 |
| filelock | CVE-2026-112910 | 3.29.1 | 4.2.1 |
| filelock | CVE-2026-112909 | 3.29.1 | 4.2.1 |
| filelock | CVE-2026-112939 | 3.29.1 | 4.2.1 |
| filelock | CVE-2026-112915 | 3.29.1 | 4.2.1 |
| filelock | CVE-2026-112935 | 3.29.1 | 4.2.1 |
| msgpack | PYSEC-2026-3625 | 1.1.2 | 1.2.1 |
| msgpack | PYSEC-2026-3625 | 1.1.2 | 1.2.1 |
| msgpack | CVE-2026-114613 | 1.1.2 | 1.2.3 |
| pip | PYSEC-2026-3721 | 26.1.2 | 26.2 |
| pip | PYSEC-2026-3721 | 26.1.2 | 26.2.0 |
| pylint | CVE-2026-114608 | 4.0.5 | 4.0.9 |
| setuptools | PYSEC-2026-3447 | 82.0.1 | 83.0.0 |
| setuptools | PYSEC-2026-3447 | 82.0.1 | 83.0.0 |
| setuptools | GHSA-xmj3-9gf7-h52w | 82.0.1 | 84.1.0 |
| soupsieve | PYSEC-2026-4170 | 2.8.4 | 2.9.0 |
| soupsieve | PYSEC-2026-4171 | 2.8.4 | 2.9.0 |
| soupsieve | CVE-2026-126192 | 2.8.4 | 2.10.0 |
| soupsieve | CVE-2026-126190 | 2.8.4 | 4.0.0 |
| soupsieve | CVE-2026-126193 | 2.8.4 | 3.0.2 |
| soupsieve | CVE-2026-126191 | 2.8.4 | 3.0.2 |
| urllib3 | PYSEC-2026-4177 | 2.7.0 | 2.8.0 |
| urllib3 | PYSEC-2026-4176 | 2.7.0 | 2.8.0 |
| urllib3 | PYSEC-2026-4175 | 2.7.0 | 2.8.0 |
| virtualenv | PYSEC-2026-4011 | 21.4.2 | 21.7.12 |
| virtualenv | PYSEC-2026-4012 | 21.4.2 | 21.7.11 |
| virtualenv | PYSEC-2026-4014 | 21.4.2 | 21.7.12 |
| virtualenv | PYSEC-2026-4013 | 21.4.2 | 21.7.13 |
| virtualenv | PYSEC-2026-4011 | 21.4.2 | 21.7.12 |
| virtualenv | PYSEC-2026-4012 | 21.4.2 | 21.7.11 |
| virtualenv | PYSEC-2026-4013 | 21.4.2 | 21.7.13 |
| virtualenv | PYSEC-2026-4014 | 21.4.2 | 21.7.12 |
| virtualenv | CVE-2026-113726 | 21.4.2 | 21.14.4 |
| virtualenv | CVE-2026-113776 | 21.4.2 | 21.14.2 |
| virtualenv | CVE-2026-113732 | 21.4.2 | 21.14.2 |
| virtualenv | CVE-2026-113725 | 21.4.2 | 21.14.7 |
| virtualenv | CVE-2026-113722 | 21.4.2 | 21.14.9 |
| virtualenv | CVE-2026-113714 | 21.4.2 | 21.14.9 |
| virtualenv | CVE-2026-113723 | 21.4.2 | 21.14.9 |
| virtualenv | CVE-2026-113715 | 21.4.2 | 21.14.9 |
| virtualenv | CVE-2026-113720 | 21.4.2 | 21.14.9 |
| virtualenv | CVE-2026-113717 | 21.4.2 | 21.14.9 |
| virtualenv | CVE-2026-113718 | 21.4.2 | 21.14.9 |

## Refactorings

 - #155: Drop Python 3.10 support; update dependencies, Nox/CI workflows, and integration-test package pins.
 - #140: Allowed install_pip to run without definition of tools.pip
 - #144: Remove python script in pyproject.toml and changed exaslpm install path
 - #145: Add a version parameter and version to help message
 - #148: Update to exasol-toolbox 10.2.0
 - #149: Update to exasol-toolbox 10.2.1 and restore check-workflows in checks.yml
 - Run `apt-get -y update && apt-get -y upgrade` when creating the exaslpm base image

## Dependency Updates

### `main`

* Updated dependency `click:8.4.1` to `8.5.1`
* Updated dependency `pydantic:2.13.4` to `2.14.3`
* Updated dependency `types-pyyaml:6.0.12.20260518` to `6.0.12.20261113`

### `dev`

* Updated dependency `docker:7.1.0` to `7.2.0`
* Updated dependency `exasol-toolbox:7.0.0` to `10.5.0`
* Updated dependency `pyinstaller:6.20.0` to `6.22.3`
* Updated dependency `types-docker:7.1.0.20260518` to `7.2.0.20261102`
* Updated dependency `types-pyinstaller:6.20.0.20260518` to `6.22.1.20260827`
* Updated dependency `types-requests:2.33.0.20260518` to `2.33.0.20261030`
