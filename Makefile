# Distro-agnostic install rules. The Debian packaging, the Arch PKGBUILD and
# the RPM spec all call `make install` rather than repeating these paths, so
# there is one place to change when something moves.
#
#   sudo make install                 install to /
#   make install DESTDIR=/tmp/stage   stage into a package build root
#   sudo make uninstall               remove everything except /etc changes
#   make check                        validate the script and profiles

PREFIX     ?= /usr
SYSCONFDIR ?= /etc
BINDIR     ?= $(PREFIX)/bin
DATADIR    ?= $(PREFIX)/share
MANDIR     ?= $(DATADIR)/man
UNITDIR    ?= $(PREFIX)/lib/systemd/system
UDEVDIR    ?= $(PREFIX)/lib/udev/rules.d
MODLOADDIR ?= $(PREFIX)/lib/modules-load.d
PROFILEDIR ?= $(DATADIR)/scuf-controller/profiles
CONFDIR    ?= $(SYSCONFDIR)/scuf-controller.d

INSTALL ?= install
PYTHON  ?= python3

.PHONY: all install uninstall check clean

all:
	@echo "Nothing to build; this is a Python script."
	@echo "Run 'sudo make install', or 'make check' to validate."

check:
	@$(PYTHON) -c "import ast; ast.parse(open('scuf-controller').read())" \
		&& echo "script parses"
	@$(PYTHON) ./scuf-controller --profile-dir profiles --list-profiles
	@$(PYTHON) tests/check-profiles.py profiles

install:
	$(INSTALL) -D -m 0755 scuf-controller \
		$(DESTDIR)$(BINDIR)/scuf-controller
	$(INSTALL) -D -m 0644 scuf-controller.conf \
		$(DESTDIR)$(SYSCONFDIR)/scuf-controller.conf
	$(INSTALL) -d -m 0755 $(DESTDIR)$(CONFDIR)
	$(INSTALL) -d -m 0755 $(DESTDIR)$(PROFILEDIR)
	$(INSTALL) -m 0644 profiles/*.conf $(DESTDIR)$(PROFILEDIR)/
	$(INSTALL) -D -m 0644 60-scuf-controller.rules \
		$(DESTDIR)$(UDEVDIR)/60-scuf-controller.rules
	$(INSTALL) -D -m 0644 scuf-controller-modules-load.conf \
		$(DESTDIR)$(MODLOADDIR)/scuf-controller.conf
	$(INSTALL) -D -m 0644 scuf-controller.service \
		$(DESTDIR)$(UNITDIR)/scuf-controller.service
	$(INSTALL) -D -m 0644 scuf-controller.1 \
		$(DESTDIR)$(MANDIR)/man1/scuf-controller.1

uninstall:
	rm -f  $(DESTDIR)$(BINDIR)/scuf-controller
	rm -f  $(DESTDIR)$(UDEVDIR)/60-scuf-controller.rules
	rm -f  $(DESTDIR)$(MODLOADDIR)/scuf-controller.conf
	rm -f  $(DESTDIR)$(UNITDIR)/scuf-controller.service
	rm -f  $(DESTDIR)$(MANDIR)/man1/scuf-controller.1
	rm -rf $(DESTDIR)$(DATADIR)/scuf-controller
	@echo "Left in place: $(SYSCONFDIR)/scuf-controller.conf and $(CONFDIR)"

clean:
	@echo "Nothing to clean."
