# Defining the package namespace
%global ns_name ea
%global ns_dir /opt/cpanel

%global _scl_prefix %{ns_dir}
%global scl_name_base    %{ns_name}-php
%global scl_macro_base   %{ns_name}_php
%global scl_name_version 71
%global scl              %{scl_name_base}%{scl_name_version}
%scl_package %scl

# do not produce empty debuginfo package
%global debug_package %{nil}

Summary:       Package that installs PHP 7.1
Name:          %scl_name
Version:       7.1.17
Vendor:        cPanel, Inc.
# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4590 for more details
%define        release_prefix 1
Release:       %{release_prefix}%{?dist}.cpanel
Group:         Development/Languages
License:       GPLv2+

Source0:       macros-build
Source1:       README
Source2:       LICENSE
Source3:       whm_feature_addon

BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: scl-utils-build
BuildRequires: help2man
# Temporary work-around
BuildRequires: iso-codes

Requires:      %{?scl_prefix}php-common
Requires:      %{?scl_prefix}php-cli
Requires:      %{?scl_prefix}pear

%description
This is the main package for %scl Software Collection,
that install PHP 7.1 language.


%package runtime
Summary:   Package that handles %scl Software Collection.
Group:     Development/Languages
Requires:  scl-utils
Requires:  %scl

%description runtime
Package shipping essential scripts to work with %scl Software Collection.


%package build
Summary:   Package shipping basic build configuration
Group:     Development/Languages
Requires:  scl-utils-build

%description build
Package shipping essential configuration macros
to build %scl Software Collection.


%package scldevel
Summary:   Package shipping development files for %scl
Group:     Development/Languages

Provides:  ea-php-scldevel = %{version}
Conflicts: ea-php-scldevel > %{version}, ea-php-scldevel < %{version}

%description scldevel
Package shipping development files, especially usefull for development of
packages depending on %scl Software Collection.


%prep
%setup -c -T

cat <<EOF | tee enable
export PATH=%{_bindir}:%{_sbindir}\${PATH:+:\${PATH}}
export MANPATH=%{_mandir}:\${MANPATH}
EOF

# generate rpm macros file for depended collections
cat << EOF | tee scldev
%%scl_%{scl_macro_base}         %{scl}
%%scl_prefix_%{scl_macro_base}  %{scl_prefix}
EOF

# This section generates README file from a template and creates man page
# from that file, expanding RPM macros in the template file.
cat >README <<'EOF'
%{expand:%(cat %{SOURCE1})}
EOF

# copy the license file so %%files section sees it
cp %{SOURCE2} .


%build
# generate a helper script that will be used by help2man
cat >h2m_helper <<'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "%{scl_name} %{version} Software Collection" || cat README
EOF
chmod a+x h2m_helper

# generate the man page
help2man -N --section 7 ./h2m_helper -o %{scl_name}.7


%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -D -m 644 enable %{buildroot}%{_scl_scripts}/enable
install -D -m 644 scldev %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel
install -D -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/%{scl_name}.7
mkdir -p %{buildroot}/opt/cpanel/ea-php71/root/etc
mkdir -p %{buildroot}/opt/cpanel/ea-php71/root/usr/share/doc
mkdir -p %{buildroot}/opt/cpanel/ea-php71/root/usr/include
mkdir -p %{buildroot}/opt/cpanel/ea-php71/root/usr/share/man/man1
mkdir -p %{buildroot}/opt/cpanel/ea-php71/root/usr/bin
mkdir -p %{buildroot}/opt/cpanel/ea-php71/root/usr/var/cache
mkdir -p %{buildroot}/opt/cpanel/ea-php71/root/usr/var/tmp
mkdir -p %{buildroot}/opt/cpanel/ea-php71/root/usr/%{_lib}
mkdir -p %{buildroot}/usr/local/cpanel/whostmgr/addonfeatures
install %{SOURCE3} %{buildroot}/usr/local/cpanel/whostmgr/addonfeatures/%{name}

# Even if this package doesn't use it we need to do this because if another
# package does (e.g. pear licenses) it will be created and unowned by any RPM
%if 0%{?_licensedir:1}
mkdir %{buildroot}/%{_licensedir}
%endif

%scl_install

tmp_version=$(echo %{scl_name_version} | sed -re 's/([0-9])([0-9])/\1\.\2/')
sed -e 's/@SCL@/%{scl_macro_base}%{scl_name_version}/g' -e "s/@VERSION@/${tmp_version}/g" %{SOURCE0} \
  | tee -a %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-config

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files


%files runtime
%defattr(-,root,root)
%doc README LICENSE
%scl_files
%{_mandir}/man7/%{scl_name}.*
%dir /opt/cpanel/ea-php71/root/etc
%dir /opt/cpanel/ea-php71/root/usr
%dir /opt/cpanel/ea-php71/root/usr/share
%dir /opt/cpanel/ea-php71/root/usr/share/doc
%dir /opt/cpanel/ea-php71/root/usr/include
%dir /opt/cpanel/ea-php71/root/usr/share/man
%dir /opt/cpanel/ea-php71/root/usr/share/man/man1
%dir /opt/cpanel/ea-php71/root/usr/bin
%dir /opt/cpanel/ea-php71/root/usr/var
%dir /opt/cpanel/ea-php71/root/usr/var/cache
%dir /opt/cpanel/ea-php71/root/usr/var/tmp
%dir /opt/cpanel/ea-php71/root/usr/%{_lib}
%attr(644, root, root) /usr/local/cpanel/whostmgr/addonfeatures/%{name}
%if 0%{?_licensedir:1}
%dir %{_licensedir}
%endif

%files build
%defattr(-,root,root)
%{_root_sysconfdir}/rpm/macros.%{scl}-config


%files scldevel
%defattr(-,root,root)
%{_root_sysconfdir}/rpm/macros.%{scl_name_base}-scldevel


%changelog
* Thu Apr 26 2018 Cory McIntire <cory@cpanel.net> - 7.1.17-1
- Updated to version 7.1.17 via update_pkg.pl (EA-7422)

* Mon Apr 02 2018 Daniel Muey <dan@cpanel.net> - 7.1.16-1
- EA-7351: Update to v7.1.16, drop v7.1.15

* Thu Mar 01 2018 Daniel Muey <dan@cpanel.net> - 7.1.15-1
- EA-7264: Update to v7.1.15, drop v7.1.14

* Thu Feb 15 2018 Daniel Muey <dan@cpanel.net> - 7.1.14-2
- EA-5277: Add conflicts for ea-php##-scldevel packages

* Fri Feb 02 2018 Daniel Muey <dan@cpanel.net> - 7.1.14-1
- Updated to version 7.1.14 via update_pkg.pl (EA-7204)

* Wed Jan 17 2018 Daniel Muey <dan@cpanel.net> - 7.1.13-4
- EA-6958: Ensure ownership of _licensedir if it is set

* Tue Jan 09 2018 Dan Muey <dan@cpanel.net> - 7.1.13-3
- ZC-3247: Add support for the allowed-php list to WHM’s Feature Lists

* Tue Jan 09 2018 Rishwanth Yeddula <rish@cpanel.net> - 7.1.13-2
- ZC-3242: Ensure the runtime package requires the meta package

* Fri Jan 05 2018 Jacob Perkins <jacob.perkins@cpanel.net> - 7.1.13-1
- Updated to version 7.1.13 via update_pkg.pl (EA-7082)

* Sun Nov 26 2017 Cory McIntire <cory@cpanel.net> - 7.1.12-1
- Updated to version 7.1.12 via update_pkg.pl (ZC-3097)

* Fri Nov 03 2017 Dan Muey <dan@cpanel.net> - 7.1.11-2
- EA-3999: adjust files to get better cleanup on uninstall

* Fri Oct 27 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 7.1.11-1
- EA-6935: Updated to version 7.1.11

* Sun Oct 1 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 7.1.10-1
- Updated to version 7.1.10 via update_pkg.pl (EA-6849)

* Thu Aug 31 2017 Cory McIntire <cory@cpanel.net> - 7.1.9-1
- Updated to version 7.1.9 via update_pkg.pl (EA-6752)

* Sat Aug 05 2017 Cory McIntire <cory@cpanel.net> - 7.1.8-1
- Updated to version 7.1.8 via update_pkg.pl (EA-6588)

* Thu Jul 06 2017 Cory McIntire <cory@cpanel.net> - 7.1.7-1
- Updated to version 7.1.7 via update_pkg.pl (EA-6518)

* Thu Jun 08 2017 Cory McIntire <cory@cpanel.net> - 7.1.6-1
- EA-6372: New release for PHP 7.1.6

* Thu May 11 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 7.1.5-1
- EA-6270: New release for PHP 7.1.5

* Thu Apr 13 2017 Charan Angara <charan@cpanel.net> - 7.1.4-1
- EA-6150: New release for PHP 7.1.4

* Thu Mar 16 2017 Daniel Muey <dan@cpanel.net> - 7.1.3-1
- EA-6080: New release for PHP 7.1.3

* Fri Feb 17 2017 Jacob Perkins <jacob.perkins@cpanel.net> - 7.1.2-1
- EA-5999: New release for PHP 7.1.2

* Thu Jan 19 2017 Daniel Muey <dan@cpanel.net> - 7.1.1-1
* EA-5877: New release for PHP 7.1.1

* Fri Dec 9 2016 Jacob Perkins <jacob.perkins@cpanel.net> - 7.1.0-9
- New release for PHP 7.1.0

* Fri Nov 11 2016 Edwin Buck <e.buck@cpanel.net> - 7.1.0-8.RC6
- new release for release candidate 6.

* Fri Oct 15 2016 Edwin Buck <e.buck@cpanel.net> - 7.1.0-7.RC3
- new release for release candidate 3.

* Thu Sep 15 2016 Edwin Buck <e.buck@cpanel.net> - 7.1.0-5.RC2
- new release for release candidate 2.

* Fri Aug 19 2016 Jacob Perkins <jacob.perkins@cpanel.net> 7.1.0-4.beta3
- Updated PHP version to 7.1.0-1.beta3

* Wed Aug 10 2016 Edwin Buck <e.buck@cpanel.net> - 7.1.0-3.beta2
- new release for beta2.

* Mon Aug 08 2016 Edwin Buck <e.buck@cpanel.net> - 7.1.0-2.beta1
- add installation dependency on ea-php71-pear

* Mon Aug 01 2016 Edwin Buck <e.buck@cpanel.net> - 7.1.0-1.beta1
- new release for beta1.

* Wed Jul 13 2016 <jacob.perkins@cpanel.net> - 7.1.0-alpha3
- Initial packaging
