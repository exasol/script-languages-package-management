def prepare_ldconfig_cmd() -> list[str]:
    ldconfig_cmd = ["ldconfig"]
    return ldconfig_cmd


def prepare_locale_cmd() -> list[str]:
    locale_cmd = ["locale-gen", "en_US.UTF-8"]
    # locale_cmd.append("update-locale", "LC_ALL=en_US.UTF-8")
    return locale_cmd
