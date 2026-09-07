# Some older systemd-rpm-macros do not define these.
%{!?_unitdir:       %global _unitdir       %{_prefix}/lib/systemd/system}
%{!?_udevrulesdir:  %global _udevrulesdir  %{_prefix}/lib/udev/rules.d}
%{!?_modulesloaddir:%global _modulesloaddir %{_prefix}/lib/modules-load.d}

Name:           scuf-controller
Version:        2.0
Release:        1%{?dist}
Summary:        Present DualShock-style gamepads to Linux as Xbox 360 controllers

License:        GPL-3.0-or-later
URL:            https://github.com/saieno/scuf-controller
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  make
BuildRequires:  python3
BuildRequires:  python3-evdev
BuildRequires:  systemd-rpm-macros
Requires:       python3
Requires:       python3-evdev
%{?systemd_requires}

%description
Presents a SCUF, DualShock 4, DualSense or generic DualShock-clone gamepad to
Linux as a Microsoft Xbox 360 controller, so that games and launchers which
only understand XInput see the correct buttons and axes.

A systemd service takes exclusive control of the physical pad and re-emits
corrected events on a virtual controller. Because the physical device is
grabbed, its raw events stop reaching applications, which removes the
duplicated input that these controllers otherwise produce.

Controller layouts are profile files rather than code, so support for a new
pad is a matter of dropping a file into /etc/scuf-controller.d.

%prep
%autosetup

%build
# Nothing to build; the daemon is a Python script.

%check
make check

%install
make install DESTDIR=%{buildroot} \
	PREFIX=%{_prefix} \
	SYSCONFDIR=%{_sysconfdir} \
	BINDIR=%{_bindir} \
	DATADIR=%{_datadir} \
	MANDIR=%{_mandir} \
	UNITDIR=%{_unitdir} \
	UDEVDIR=%{_udevrulesdir} \
	MODLOADDIR=%{_modulesloaddir}

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%license LICENSE
%doc README.md
%config(noreplace) %{_sysconfdir}/scuf-controller.conf
%dir %{_sysconfdir}/scuf-controller.d
%{_bindir}/scuf-controller
%{_unitdir}/scuf-controller.service
%{_udevrulesdir}/60-scuf-controller.rules
%{_modulesloaddir}/scuf-controller.conf
%dir %{_datadir}/scuf-controller
%dir %{_datadir}/scuf-controller/profiles
%{_datadir}/scuf-controller/profiles/*.conf
%{_mandir}/man1/scuf-controller.1*

%changelog
* Sun Sep 06 2026 Saieno <saieno86@gmail.com> - 2.0-1
- Replace xboxdrv, removed from distributions during the Python 2 deprecation,
  with a self-contained python3-evdev daemon
- Grab the pad instead of deleting /dev/input/js0 from a cron job
- Describe controller layouts in profile files; adding a pad needs no code change
- Add --dump-profile, --list-profiles, --profile-dir, --list and --debug
- Install through a Makefile shared with the Debian and Arch packaging
