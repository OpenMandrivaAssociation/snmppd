Summary:	SNMP proxy daemon
Name:		snmppd
Version:	0.5.2
Release:	%mkrel 5
License:	GPL
Group:		System/Servers
URL:		http://bubble.nsys.by/
Source0:	http://bubble.nsys.by/projects/snmppd/%{name}-%{version}.tar.bz2
Source1:	%{name}.init
Source2:	http://bubble.nsys.by/projects/libsplit/libsplit-0.2.tar.bz2
Source3:	check_snmpp.conf.README
Source4:	check_snmpp.cfg
Patch1:		snmppd-0.5.1-pidfile_location_fix.diff
Patch2:		snmppd-0.5.1-config_file_location_fix.diff
Patch3:		snmppd-0.5.1-antibork_1.diff
Patch4:		snmppd-compile_fix.diff
BuildRequires:	autoconf2.5
BuildRequires:	automake1.7
BuildRequires:	net-snmp-devel
BuildRequires:	openssl-devel
Requires:	nagios
Requires:	nagios-plugins
Requires:	net-snmp-mibs
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
snmppd is an SNMP proxy daemon that is designed to work with Nagios. It loads
MIBs upon startup, listens on a TCP socket for SNMP GET requests, polls the
specified host, and returns the value to caller process. The caller process is
usually the Nagios plugin check_snmpp. 

%package -n	nagios-check_snmpp
Summary:	Snmpp plugin for nagios
Group:		Networking/Other
Requires:	nagios
Requires:	nagios-plugins
Requires:	net-snmp-utils
Requires:	%{name} = %{version}

%description -n	nagios-check_snmpp
check_snmpp plugin for nagios (replacement for check_snmp)

This plugin uses the 'snmpget' command included with the net-snmp-utils
package.

%prep

%setup -q -a2
%patch1 -p0
%patch2 -p0
%patch3 -p0
%patch4 -p0

cp %{SOURCE1} snmppd.init
cp %{SOURCE3} check_snmpp.conf.README
cp %{SOURCE4} check_snmpp.cfg

# lib64 fix
perl -pi -e "s|/lib\b|/%{_lib}|g" configure*
perl -pi -e "s|_LIBDIR_|%{_libdir}|g" *.cfg

%build
rm -f configure
libtoolize --force --copy; aclocal-1.7 -I config; autoheader; automake-1.7 --add-missing --copy --foreign; autoconf

pushd libsplit-0.2
%make C_FLAGS="%{optflags} -fPIC" libsplit.a
popd

#export PROG_CFLAGS="%{optflags} -I`pwd`/libsplit-0.2 -L`pwd`/libsplit-0.2"
export CFLAGS="%{optflags} -I`pwd`/libsplit-0.2 -L`pwd`/libsplit-0.2"
export SPLITTERLIBS="`pwd`/libsplit-0.2/libsplit.a"

%configure2_5x \
    --libdir=%{_libdir}/nagios/plugins \
    --libexecdir=%{_libdir}/nagios/plugins

make \
    CFLAGS="%{optflags} -I`pwd`/libsplit-0.2 -L`pwd`/libsplit-0.2" \
    SPLITTERLIBS="`pwd`/libsplit-0.2/libsplit.a"

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%makeinstall_std

install -d %{buildroot}%{_sysconfdir}/nagios/plugins.d
install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_localstatedir}/lib/snmppd
install -d %{buildroot}/var/run/snmppd

install -m0755 snmppd.init %{buildroot}%{_initrddir}/snmppd

install -m0644 check_snmpp.cfg %{buildroot}%{_sysconfdir}/nagios/plugins.d/

# clean up
rm -rf %{buildroot}%{_includedir}

%pre
%_pre_useradd snmppd %{_localstatedir}/lib/snmppd /bin/sh

%post
%_post_service snmppd

%preun
%_preun_service snmppd

%postun
%_postun_userdel snmppd

%post -n nagios-check_snmpp
/sbin/service nagios condrestart > /dev/null 2>/dev/null || :

%postun -n nagios-check_snmpp
/sbin/service nagios condrestart > /dev/null 2>/dev/null || :

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS ChangeLog README TODO
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/snmppd.conf
%attr(755,root,root) %{_initrddir}/snmppd
%{_sbindir}/snmppd
%attr(0755,snmppd,snmppd) %dir %{_localstatedir}/lib/snmppd
%attr(0755,snmppd,snmppd) %dir /var/run/snmppd

%files -n nagios-check_snmpp
%defattr(-,root,root)
%doc check_snmpp.conf.README
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/nagios/plugins.d/check_snmpp.cfg
%{_libdir}/nagios/plugins/check_snmpp
