%{!?buildforkernels:%global buildforkernels akmod}
%global debug_package %{nil}

%global kmod_name div-linuwu-sense

Name:           %{kmod_name}
Version:        1.0.0
Release:        2%{?dist}
Summary:        Kernel module for Acer Predator & Nitro fan/RGB/turbo control

License:        GPL-3.0-only
URL:            https://github.com/fgeroldi/Div-Linuwu-Sense
Source0:        https://github.com/fgeroldi/Div-Linuwu-Sense/archive/refs/heads/main.tar.gz

BuildRequires:  %{_bindir}/kmodtool
BuildRequires:  systemd-rpm-macros
BuildRequires:  elfutils-libelf-devel
BuildRequires:  gcc
BuildRequires:  make

# AkmodsBuildRequires is expanded by kmodtool into the Requires of akmod-%{kmod_name}
%global AkmodsBuildRequires %{_bindir}/kmodtool, elfutils-libelf-devel, gcc, make, %{name}-common = %{version}-%{release}

# Standard kernel-devel build requirement for binary kmod building
%{?kernels:BuildRequires: gcc, elfutils-libelf-devel, kernel-devel-uname-r = %{kernels}}

# kmodtool macro expansion
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{kmod_name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
Akmod package for Div-Linuwu-Sense. Provides out-of-tree kernel module support
for fan curves, RGB lighting, and turbo mode on Acer Predator and Nitro laptops.

%package -n %{name}-common
Summary:        Common configuration files and services for %{name}
BuildArch:      noarch
Provides:       %{name}-kmod-common = %{version}
Provides:       linuwu_sense-common = %{version}
Requires:       systemd

%description -n %{name}-common
This package contains common files for %{name}, such as the systemd
service, tmpfiles configuration for sysfs nodes, modules-load configuration,
and modprobe conflict blacklist.

%prep
# Error out if there was something wrong with kmodtool
%{?kmodtool_check}

# Print kmodtool output for debugging purposes
kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{kmod_name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%setup -q -c -T
tar -xzf %{SOURCE0}
mv Div-Linuwu-Sense-main src-tree

# Copy source directory for each kernel version to build
for kernel_version in %{?kernel_versions} ; do
    cp -a src-tree _kmod_build_${kernel_version%%___*}
done

%build
for kernel_version in %{?kernel_versions}; do
    pushd _kmod_build_${kernel_version%%___*}
    make %{?_smp_mflags} -C ${kernel_version##*___} M=$(pwd) modules
    popd
done

%install
rm -rf %{buildroot}

# Install kernel modules
for kernel_version in %{?kernel_versions}; do
    pushd _kmod_build_${kernel_version%%___*}
    mkdir -p %{buildroot}%{kmodinstdir_prefix}${kernel_version%%___*}%{kmodinstdir_postfix}
    install -m 0755 src/*.ko %{buildroot}%{kmodinstdir_prefix}${kernel_version%%___*}%{kmodinstdir_postfix}
    chmod 0755 %{buildroot}%{kmodinstdir_prefix}${kernel_version%%___*}%{kmodinstdir_postfix}/*.ko
    popd
done

%{?akmod_install}
# Ensure the SRPM expected by akmods-ostree-post on Kinoite/Silverblue/OSTree exists
if [ -f "%{buildroot}%{_usrsrc}/akmods/%{name}-%{version}-%{release}.src.rpm" ] && [ ! -e "%{buildroot}%{_usrsrc}/akmods/%{pkg_kmod_name}-%{version}-%{release}.src.rpm" ]; then
    ln %{buildroot}%{_usrsrc}/akmods/%{name}-%{version}-%{release}.src.rpm %{buildroot}%{_usrsrc}/akmods/%{pkg_kmod_name}-%{version}-%{release}.src.rpm 2>/dev/null || \
    cp -p %{buildroot}%{_usrsrc}/akmods/%{name}-%{version}-%{release}.src.rpm %{buildroot}%{_usrsrc}/akmods/%{pkg_kmod_name}-%{version}-%{release}.src.rpm
fi

# Install userland / common configuration files
install -D -m 0644 src-tree/linuwu_sense-tmpfiles.conf %{buildroot}%{_tmpfilesdir}/linuwu_sense.conf
install -D -m 0644 src-tree/linuwu_sense-modules-load.conf %{buildroot}%{_modulesloaddir}/linuwu_sense.conf
install -D -m 0644 src-tree/linuwu_sense-modprobe-blacklist.conf %{buildroot}%{_modprobedir}/linuwu_sense-blacklist.conf
install -D -m 0644 src-tree/linuwu_sense.service %{buildroot}%{_unitdir}/linuwu_sense.service

# Create alias drop-in so modprobe div_linuwu_sense or div-linuwu-sense works as alias
cat << 'EOF' > %{buildroot}%{_modprobedir}/div-linuwu-sense-alias.conf
alias div_linuwu_sense linuwu_sense
alias div-linuwu-sense linuwu_sense
EOF

%pre -n %{name}-common
getent group linuwu_sense >/dev/null || groupadd -r linuwu_sense

%post -n %{name}-common
%systemd_post linuwu_sense.service
systemd-tmpfiles --create %{_tmpfilesdir}/linuwu_sense.conf >/dev/null 2>&1 || :

%preun -n %{name}-common
%systemd_preun linuwu_sense.service

%postun -n %{name}-common
%systemd_postun_with_restart linuwu_sense.service

%files -n %{name}-common
%license src-tree/LICENSE
%doc src-tree/README.md
%{_tmpfilesdir}/linuwu_sense.conf
%{_modulesloaddir}/linuwu_sense.conf
%{_modprobedir}/linuwu_sense-blacklist.conf
%{_modprobedir}/div-linuwu-sense-alias.conf
%{_unitdir}/linuwu_sense.service

%changelog
* Fri Oct 09 2026 Felipe Geroldi <142124821+fgeroldi@users.noreply.github.com> - 1.0.0-2
- Ensure kmod SRPM is packaged with expected name for akmods-ostree-post on Kinoite/Silverblue

* Thu Oct 08 2026 Felipe Geroldi <142124821+fgeroldi@users.noreply.github.com> - 1.0.0-1
- Initial akmod packaging for Div-Linuwu-Sense on Fedora / Kaeteh OS
