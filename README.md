# div-linuwu-sense-akmod

Automated **Akmod package** for the [Div-Linuwu-Sense](https://github.com/fgeroldi/Div-Linuwu-Sense) Linux kernel module (Acer Predator & Nitro fan curves, RGB lighting, and turbo mode).

Designed specifically for **Kaeteh OS** and **Fedora Kinoite / Silverblue** (`rpm-ostree`), but also compatible with standard Fedora Workstation (`dnf`).

---

## Features

- **Automated Kernel Module Rebuilding (`akmods`):** Rebuilds automatically across kernel updates on immutable/ostree and classic Fedora installations.
- **Secure Boot MOK Support:** Compatible with automatic MOK signing provided by `akmods` and Kaeteh OS.
- **System Integration:**
  - Installs systemd service (`linuwu_sense.service`) to safely unload modules on shutdown.
  - Automatically loads module at boot via `/etc/modules-load.d/linuwu_sense.conf`.
  - Blacklists conflicting `acer_wmi` module via `/etc/modprobe.d/linuwu_sense-blacklist.conf`.
  - Grants user/group permissions to sysfs controls via `/etc/tmpfiles.d/linuwu_sense.conf`.
  - Configures module aliases (`div_linuwu_sense` and `div-linuwu-sense`).

---

## Installation

### Option 1: Via Fedora COPR (Recommended)

Enable the COPR repository and layer the package using `rpm-ostree`:

```bash
# 1. Add COPR repository
sudo curl -o /etc/yum.repos.d/_copr:fgeroldi:div-linuwu-sense.repo \
  https://copr.fedorainfracloud.org/coprs/fgeroldi/div-linuwu-sense/repo/fedora-41/fgeroldi-div-linuwu-sense-fedora-41.repo

# 2. Install package
rpm-ostree install akmod-div-linuwu-sense

# 3. Reboot into new deployment
systemctl reboot
```

*(On standard Fedora Workstation, replace `rpm-ostree install` with `sudo dnf install -y akmod-div-linuwu-sense`).*

---

### Option 2: Via GitHub Actions Artifacts / Local RPM

Download `akmod-div-linuwu-sense-*.rpm` and `div-linuwu-sense-common-*.rpm`:

```bash
rpm-ostree install ./akmod-div-linuwu-sense-*.rpm ./div-linuwu-sense-common-*.rpm
systemctl reboot
```

---

## Verification

After rebooting:

1. **Secure Boot (Shim MOK):** If prompted with the blue MOK screen, select **Enroll MOK** -> **Continue** -> **Confirm** (default Kaeteh password: `kaeteh`).
2. **Verify Module Status:**
   ```bash
   lsmod | grep linuwu_sense
   ```
3. **Verify Service Status:**
   ```bash
   systemctl status linuwu_sense
   ```

---

## Building Locally

To build inside a Fedora 41 container or toolbox:

```bash
sudo dnf install -y rpmdevtools rpmlint kmodtool akmods gcc make systemd-rpm-macros elfutils-libelf-devel
spectool -g -R div-linuwu-sense.spec
rpmbuild -ba --define "buildforkernels akmod" div-linuwu-sense.spec
```

The resulting packages will be in:
- `~/rpmbuild/RPMS/noarch/akmod-div-linuwu-sense-*.noarch.rpm`
- `~/rpmbuild/RPMS/noarch/div-linuwu-sense-common-*.noarch.rpm`
- `~/rpmbuild/SRPMS/div-linuwu-sense-*.src.rpm`
