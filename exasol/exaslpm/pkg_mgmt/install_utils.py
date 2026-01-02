def prepare_ldconfig_cmd() -> list[str]:
    ldconfig_cmd = ["ldconfig"]
    return ldconfig_cmd


def prepare_locale_cmd() -> list[str]:
    locale_cmd = ["locale-gen", "&&", "update-locale", "LANG=en_US.UTF8"]
    return locale_cmd
