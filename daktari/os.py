import distro


class OS:
    OS_X = "osx"
    GENERIC = "generic"
    UBUNTU = "ubuntu"


def detect_os() -> str:
    (id_name, _, _) = distro.linux_distribution()
    if id_name == "Darwin":
        return OS.OS_X
    elif id_name == "Ubuntu":
        return OS.UBUNTU
    else:
        return OS.GENERIC
