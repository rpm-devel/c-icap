%global modn c_icap
%global name c-icap
%global ver  0.6.5
%global vermaj 0.6

%if 0%{?suse_version}
%global shadow_pkg shadow
%else
%global shadow_pkg shadow-utils
%endif

Summary         : An implementation of an ICAP server
Name            : %{name}
Version         : %{ver}
Release         : 1%{?dist}%{?pext}
License         : LGPL-2.0-or-later
URL             : https://c-icap.sourceforge.net/
ExclusiveArch   : x86_64 aarch64
Source0         : https://downloads.sourceforge.net/project/%{name}/%{name}/%{vermaj}.x/%{modn}-%{ver}.tar.gz
Source1         : etc---logrotate.d---c-icap
Source2         : etc---sysconfig---c-icap.sysconfig
Source3         : etc---tmpfiles.d---c-icap.conf
Source4         : usr---lib---systemd---system---c-icap.service
Requires        : %{name}-libs = %{version}-%{release}
Requires(pre)   : %{shadow_pkg}
BuildRequires   : db4-devel gdbm-devel openldap-devel perl-devel tar zlib-devel bzip2-devel pcre-devel
BuildRequires   : systemd-rpm-macros
%{?systemd_requires}
Vendor          : Tsantilas Christos <chtsanti@users.sourceforge.net>

%description
C-icap is an implementation of an ICAP server. It can be used with HTTP proxies
that support the ICAP protocol to implement content adaptation and filtering
services. Most of the commercial HTTP proxies must support the ICAP protocol,
the open source Squid 3.x proxy server supports it too.

%package devel
Summary         : Development tools for %{name}
Requires        : %{name}-libs = %{version}-%{release}
Requires        : zlib-devel

%description devel
The c-icap-devel package contains the static libraries and header files for
developing software using c-icap.

%package ldap
Summary         : The LDAP module for %{name}
Requires        : %{name} = %{version}-%{release}

%description ldap
The c-icap-ldap package contains the LDAP module for c-icap.

%package libs
Summary         : Libraries used by %{name}

%description libs
The c-icap-libs package contains all runtime libraries used by c-icap and the
utilities.

%package perl
Summary         : The Perl handler for %{name}
Requires        : %{name} = %{version}-%{release}

%description perl
The c-icap-perl package contains the Perl handler for c-icap.

%package bin
Summary         : Related programs for %{name}
Requires        : %{name}-libs = %{version}-%{release}

%description bin
The c-icap-bin package contains several commandline tools for c-icap.

%prep
%setup -q -n %{modn}-%{ver}

%build
LIBS="-lpthread"; export LIBS
%configure \
  LDFLAGS="-L/usr/lib64/libdb4" \
  CFLAGS="${RPM_OPT_FLAGS} -fno-strict-aliasing -I/usr/include/libdb4" \
  --sysconfdir=%{_sysconfdir}/%{name}            \
  --enable-shared                                \
  --enable-static                                \
  --enable-large-files                           \
  --enable-lib-compat                            \
  --with-perl                                    \
  --with-zlib                                    \
  --with-bdb                                     \
  --with-ldap
  #--enable-ipv6 # net.ipv6.bindv6only not supported

%make_build

%install
%{__mkdir_p} %{buildroot}%{_sbindir}
%{__mkdir_p} %{buildroot}%{_datadir}/%{modn}/{contrib,templates}
%{__mkdir_p} %{buildroot}%{_localstatedir}/log/%{name}

%make_install

%{__mv}      -f      %{buildroot}%{_bindir}/%{name} %{buildroot}%{_sbindir}

%{__mkdir_p}                      %{buildroot}%{_sysconfdir}/logrotate.d
%{__install} -m 0644 %{SOURCE1}   %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__mkdir_p}                      %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -m 0644 %{SOURCE2}   %{buildroot}%{_sysconfdir}/sysconfig/%{name}
%{__mkdir_p}                      %{buildroot}%{_sysconfdir}/tmpfiles.d
%{__install} -m 0644 %{SOURCE3}   %{buildroot}%{_sysconfdir}/tmpfiles.d/%{name}.conf
%{__mkdir_p}                      %{buildroot}/usr/lib/systemd/system
%{__install} -m 0644 %{SOURCE4}   %{buildroot}/usr/lib/systemd/system/%{name}.service

%{__install} -m 0755 contrib/*.pl %{buildroot}%{_datadir}/%{modn}/contrib

%{__rm}      -f                   %{buildroot}%{_libdir}/lib*.so.{?,??}

%pre
if ! getent group  %{name} >/dev/null 2>&1; then
  /usr/sbin/groupadd -r %{name}
fi
if ! getent passwd %{name} >/dev/null 2>&1; then
  /usr/sbin/useradd  -r -g %{name}   \
    -d %{_localstatedir}/run/%{name} \
    -c "C-ICAP Service user" -M      \
    -s /sbin/nologin %{name}
fi
exit 0 # Always pass

%post
%systemd_post c-icap.service

%preun
%systemd_preun c-icap.service

%postun
%systemd_postun_with_restart c-icap.service

%ldconfig_scriptlets libs

%files
%license COPYING
%doc AUTHORS INSTALL README TODO
%attr(750,root,%{name}) %dir %{_sysconfdir}/%{name}
%attr(640,root,%{name}) %config(noreplace) %{_sysconfdir}/%{name}/*.conf
%attr(640,root,%{name}) %config(noreplace) %{_sysconfdir}/%{name}/*.magic
%attr(640,root,%{name}) %{_sysconfdir}/%{name}/*.default
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%config(noreplace) %{_sysconfdir}/tmpfiles.d/%{name}.conf
/usr/lib/systemd/system/%{name}.service
%dir %{_libdir}/%{modn}
%{_libdir}/%{modn}/bdb_tables.so
%{_libdir}/%{modn}/dnsbl_tables.so
%{_libdir}/%{modn}/shared_cache.so
%{_libdir}/%{modn}/srv_echo.so
%{_libdir}/%{modn}/srv_ex206.so
%{_libdir}/%{modn}/sys_logger.so
%{_sbindir}/%{name}
%{_datadir}/%{modn}
%{_mandir}/man8/%{name}.8*
%attr(750,%{name},%{name}) %dir %{_localstatedir}/log/%{name}
%attr(750,%{name},%{name}) %dir %{_localstatedir}/run/%{name}

%files devel
%{_bindir}/%{name}-*config
%{_includedir}/%{modn}
%{_libdir}/libicapapi.*a
%{_libdir}/libicapapi.so
%{_libdir}/%{modn}/bdb_tables.*a
%{_libdir}/%{modn}/dnsbl_tables.*a
%{_libdir}/%{modn}/ldap_module.*a
%{_libdir}/%{modn}/perl_handler.*a
%{_libdir}/%{modn}/shared_cache.*a
%{_libdir}/%{modn}/srv_echo.*a
%{_libdir}/%{modn}/srv_ex206.*a
%{_libdir}/%{modn}/sys_logger.*a
%{_mandir}/man8/%{name}-*config.8*

%files ldap
%{_libdir}/%{modn}/ldap_module.so

%files libs
%license COPYING
%{_libdir}/libicapapi.so.*

%files perl
%{_libdir}/%{modn}/perl_handler.so

%files bin
%{_bindir}/%{name}-client
%{_bindir}/%{name}-mkbdb
%{_bindir}/%{name}-stretch
%{_mandir}/man8/%{name}-client.8*
%{_mandir}/man8/%{name}-mkbdb.8*
%{_mandir}/man8/%{name}-stretch.8*

%changelog
* Sat Jul 05 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 0.6.5-1
- Multi-distro pass: guard Requires(pre) shadow-utils vs shadow for openSUSE/SLES via %%shadow_pkg

* Thu Jul 03 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 0.6.5-1
- Version: 0.6.4 → 0.6.5 (latest)
- Source0: fix URL http→https, fix path 0.2.x → %{vermaj}.x (0.6.x); verified 302→200
- URL: http→https
- SPDX: LGPLv2+ → LGPL-2.0-or-later; ExclusiveArch; shadow-utils; systemd macros; %%make_build/%%make_install; %%license; %%ldconfig_scriptlets libs

* Fri May 22 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 0.6.4-1
- Fix spec violations: %global for constants, use %{buildroot}

* Fri Apr 24 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 0.6.4-1
- Update to 0.6.4
- Modernize spec for AlmaLinux 10; remove Buildroot, Group, %clean, %defattr

* Thu Mar 16 2017 Marcin Skarbek <rpm@skarbek.name> - 0.4.4-1
- Update to 0.4.4

* Mon Jan 07 2013 Oliver Seeburger <oliver.seeburger@sundermeier-werkzeugbau.de> - 0.2.5-1
- Update to 0.2.5

* Mon Dec 31 2012 Oliver Seeburger <oliver.seeburger@sundermeier-werkzeugbau.de> - 0.2.4-1
- Update to 0.2.4

* Fri Nov 16 2012 Oliver Seeburger <oliver.seeburger@sundermeier-werkzeugbau.de> - 0.2.3-1
- Update to 0.2.3

* Tue Sep 25 2012 Oliver Seeburger <oliver.seeburger@sundermeier-werkzeugbau.de> - 0.2.2-1
- Update to 0.2.2

* Wed Jul 04 2012 Oliver Seeburger <oliver.seeburger@sundermeier-werkzeugbau.de> - 0.2.1-1
- Update to 0.2.1

* Mon Jun 04 2012 Oliver Seeburger <oliver.seeburger@sundermeier-werkzeugbau.de> - 0.1.7-2
- Initial build for Fedora 17
