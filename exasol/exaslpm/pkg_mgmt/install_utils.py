"""
package_mgmt_utils::execute("locale-gen en_US.UTF-8",$dry_run);
package_mgmt_utils::execute("update-locale LC_ALL=en_US.UTF-8",$dry_run);
package_mgmt_utils::execute("apt-get -y clean",$dry_run);
package_mgmt_utils::execute("apt-get -y autoremove",$dry_run);
package_mgmt_utils::execute("ldconfig",$dry_run);
"""


def prepare_ldconfig_cmd() -> list[str]:
    ldconfig_cmd = ["ldconfig"]
    return ldconfig_cmd


def prepare_locale_cmd() -> list[str]:
    locale_cmd = ["locale-gen", "en_US.UTF-8"]
    # locale_cmd.append("update-locale", "LC_ALL=en_US.UTF-8")
    return locale_cmd
