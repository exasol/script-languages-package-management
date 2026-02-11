import re

"""
This is how the apt-cache madison output looks
apt-cache madison gpg vim
gpg | 2.4.4-2ubuntu17.4 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages
gpg | 2.4.4-2ubuntu17.4 | http://security.ubuntu.com/ubuntu noble-security/main amd64 Packages
gpg | 2.4.4-2ubuntu17 | http://archive.ubuntu.com/ubuntu noble/main amd64 Packages
vim | 2:9.1.0016-1ubuntu7.9 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages
vim | 2:9.1.0016-1ubuntu7.9 | http://security.ubuntu.com/ubuntu noble-security/main amd64 Packages
vim | 2:9.1.0016-1ubuntu7 | http://archive.ubuntu.com/ubuntu noble/main amd64 Packages
"""


class MadisonParser:
    @staticmethod
    def split_n_trim_madison_out(madison_out: str) -> list[str]:
        stripped_madison = madison_out.strip()
        splitted_out = re.split(r"\||\n", stripped_madison)
        trimmed_out = [x.strip() for x in splitted_out]
        return trimmed_out

    @staticmethod
    def parse_version(madison_out: list[str], pkg_list: list[str]) -> list[str]:
        vers = []
        for pkg in pkg_list:
            try:
                pkg_index = madison_out.index(pkg)
                ver = madison_out[pkg_index + 1]
                vers.append(ver)
            except (ValueError, IndexError):
                pass
        return vers
    # correlate pkg and ver
    # maintain the order in which we pass the pkg to madison; same as the pkg_list param
    # return is dict of str (pkg_name) and data-class
    # 
