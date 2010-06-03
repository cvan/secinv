#!/usr/bin/env python26

import datetime
import os
import sys

def diff_list(l_old, l_new):
    """
    Creates a new dict representing a diff between two lists.
    """

    set_new, set_past = set(l_new), set(l_old)
    intersect = set_new.intersection(set_past)

    added = list(set_new - intersect)
    deleted = list(set_past - intersect)

    # Added and deleted items.
    diff = {'added': added, 'deleted': deleted}

    return diff


# BASE_PATH is the absolute path of '..' relative to this script location.
BASE_PATH = reduce(lambda l, r: l + os.path.sep + r,
    os.path.dirname(os.path.realpath(__file__)).split(os.path.sep)[:-1])

# Append settings directory.
sys.path.append(os.path.join(BASE_PATH, 'secinv'))

from django.core.management import execute_manager
try:
    import settings
except:
    print "Could not import settings"
    sys.exit(1)

# To suppress MySQLdb and haystack warnings.
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from django.core.management import setup_environ
setup_environ(settings)


from apps.machines.models import *

ip_dict = {'sit0': {'i_mac': '00:00:00:00', 'i_mask': '', 'i_ip': ''}, 'lo': {'i_mac': '00:00:00:00:00:06', 'i_mask': '255.0.0.0', 'i_ip': '127.0.0.1'}, 'eth0': {'i_mac': '01:50:56:a5:11:39', 'i_mask': '255.255.255.0', 'i_ip': '10.2.72.89'}}
ip_dict = {'sit0': {'i_mac': '00:00:00:00', 'i_mask': '', 'i_ip': ''}, 'eth0': {'i_mac': '01:50:56:a5:11:39', 'i_mask': '255.255.255.0', 'i_ip': '10.2.72.89'}}

system_dict = {'kernel_rel': '2.8.18-194.3.1.el5', 'hostname': 'cm-sectest02', 'nfs': 0, 'rh_rel': '5.5 (Tikanga)'}

services_dict = {'rpc.statd': '869', 'sshd': '22', 'sendmail': '25', 'nrpe': '5666', 'portmap': '111', 'mysqld': '3366', 'snmpd': '199'}
services_dict = {'httpd': '80', 'sshd': '22', 'sendmail': '25', 'nrpe': '5666', 'portmap': '111', 'mysqld': '3306', 'snmpd': '199', 'openvpn': '1194'}

rpms_dict = {'serialized': "S'Deeployment_Guide-en-US-5.2-11.noarch.rpm\\nGConf2-2.14.0-9.el5.x86_64.rpm\\nMAKEDEV-3.23-1.2.x86_64.rpm\\nNetworkManager-0.7.0-10.el5.i386.rpm\\nNetworkManager-0.7.0-10.el5.x86_64.rpm\\nNetworkManager-glib-0.7.0-10.el5.i386.rpm\\nNetworkManager-glib-0.7.0-10.el5.x86_64.rpm\\nORBit2-2.14.3-5.el5.x86_64.rpm\\nSysVinit-2.86-15.el5.x86_64.rpm\\nacl-2.2.39-6.el5.x86_64.rpm\\nacpid-1.0.4-9.el5_4.2.x86_64.rpm\\namtu-1.0.6-1.el5.x86_64.rpm\\nanacron-2.3-45.el5.x86_64.rpm\\napr-1.2.7-11.el5_3.1.x86_64.rpm\\napr-util-1.2.7-11.el5.x86_64.rpm\\naspell-0.60.3-7.1.i386.rpm\\naspell-0.60.3-7.1.x86_64.rpm\\naspell-en-6.0-2.1.x86_64.rpm\\nat-3.1.8-84.el5.x86_64.rpm\\natk-1.12.2-1.fc6.x86_64.rpm\\nattr-2.4.32-1.1.x86_64.rpm\\naudit-1.7.17-3.el5.x86_64.rpm\\naudit-libs-1.7.17-3.el5.i386.rpm\\naudit-libs-1.7.17-3.el5.x86_64.rpm\\naudit-libs-python-1.7.17-3.el5.x86_64.rpm\\naugeas-libs-0.6.0-2.el5.x86_64.rpm\\nauthconfig-5.3.21-6.el5.x86_64.rpm\\nautofs-5.0.1-0.rc2.143.el5.x86_64.rpm\\navahi-0.6.16-7.el5.x86_64.rpm\\navahi-compat-libdns_sd-0.6.16-7.el5.x86_64.rpm\\nbasesystem-8.0-5.1.1.noarch.rpm\\nbash-3.2-24.el5.x86_64.rpm\\nbc-1.06-21.x86_64.rpm\\nbind-libs-9.3.6-4.P1.el5_4.2.x86_64.rpm\\nbind-utils-9.3.6-4.P1.el5_4.2.x86_64.rpm\\nbinutils-2.17.50.0.6-14.el5.x86_64.rpm\\nbitstream-vera-fonts-1.10-7.noarch.rpm\\nbluez-gnome-0.5-5.fc6.x86_64.rpm\\nbluez-libs-3.7-1.1.x86_64.rpm\\nbluez-utils-3.7-2.2.x86_64.rpm\\nbzip2-1.0.3-4.el5_2.x86_64.rpm\\nbzip2-libs-1.0.3-4.el5_2.x86_64.rpm\\ncairo-1.2.4-5.el5.x86_64.rpm\\nccid-1.3.8-1.el5.x86_64.rpm\\ncheckpolicy-1.33.1-6.el5.x86_64.rpm\\nchkconfig-1.3.30.2-2.el5.x86_64.rpm\\nconman-0.1.9.2-8.el5.x86_64.rpm\\ncoolkey-1.1.0-14.el5.i386.rpm\\ncoolkey-1.1.0-14.el5.x86_64.rpm\\ncoreutils-5.97-23.el5_4.2.x86_64.rpm\\ncpio-2.6-23.el5_4.1.x86_64.rpm\\ncpp-4.1.2-48.el5.x86_64.rpm\\ncpuspeed-1.2.1-9.el5.x86_64.rpm\\ncracklib-2.8.9-3.3.i386.rpm\\ncracklib-2.8.9-3.3.x86_64.rpm\\ncracklib-dicts-2.8.9-3.3.x86_64.rpm\\ncrash-4.1.2-4.el5.x86_64.rpm\\ncrontabs-1.10-8.noarch.rpm\\ncryptsetup-luks-1.0.3-5.el5.i386.rpm\\ncryptsetup-luks-1.0.3-5.el5.x86_64.rpm\\ncups-1.3.7-18.el5.x86_64.rpm\\ncups-libs-1.3.7-18.el5.x86_64.rpm\\ncurl-7.15.5-9.el5.x86_64.rpm\\ncyrus-sasl-2.1.22-5.el5_4.3.x86_64.rpm\\ncyrus-sasl-lib-2.1.22-5.el5_4.3.i386.rpm\\ncyrus-sasl-lib-2.1.22-5.el5_4.3.x86_64.rpm\\ncyrus-sasl-plain-2.1.22-5.el5_4.3.i386.rpm\\ncyrus-sasl-plain-2.1.22-5.el5_4.3.x86_64.rpm\\ndb4-4.3.29-10.el5.i386.rpm\\ndb4-4.3.29-10.el5.x86_64.rpm\\ndbus-1.1.2-14.el5.x86_64.rpm\\ndbus-glib-0.73-8.el5.i386.rpm\\ndbus-glib-0.73-8.el5.x86_64.rpm\\ndbus-libs-1.1.2-14.el5.i386.rpm\\ndbus-libs-1.1.2-14.el5.x86_64.rpm\\ndbus-python-0.70-9.el5_4.x86_64.rpm\\ndesktop-file-utils-0.10-7.x86_64.rpm\\ndevice-mapper-1.02.39-1.el5.i386.rpm\\ndevice-mapper-1.02.39-1.el5.x86_64.rpm\\ndevice-mapper-event-1.02.39-1.el5.x86_64.rpm\\ndevice-mapper-multipath-0.4.7-34.el5_5.1.x86_64.rpm\\ndhclient-3.0.5-23.el5.x86_64.rpm\\ndhcpv6-client-1.0.10-18.el5.x86_64.rpm\\ndiffutils-2.8.1-15.2.3.el5.x86_64.rpm\\ndmidecode-2.10-3.el5.x86_64.rpm\\ndmraid-1.0.0.rc13-63.el5.x86_64.rpm\\ndmraid-events-1.0.0.rc13-63.el5.x86_64.rpm\\ndnsmasq-2.51-1.el5.rf.x86_64.rpm\\ndos2unix-3.1-27.2.el5.x86_64.rpm\\ndosfstools-2.11-9.el5.x86_64.rpm\\ndump-0.4b41-4.el5.x86_64.rpm\\ne2fsprogs-1.39-23.el5.x86_64.rpm\\ne2fsprogs-libs-1.39-23.el5.i386.rpm\\ne2fsprogs-libs-1.39-23.el5.x86_64.rpm\\ned-0.2-39.el5_2.x86_64.rpm\\neject-2.1.5-4.2.el5.x86_64.rpm\\nelfutils-libelf-0.137-3.el5.x86_64.rpm\\nethtool-6-4.el5.x86_64.rpm\\nexpat-1.95.8-8.3.el5_4.2.i386.rpm\\nexpat-1.95.8-8.3.el5_4.2.x86_64.rpm\\nfacter-1.5.7-1.rhel5.x86_64.rpm\\nfbset-2.1-22.x86_64.rpm\\nfile-4.17-15.el5_3.1.x86_64.rpm\\nfilesystem-2.4.0-3.el5.x86_64.rpm\\nfindutils-4.2.27-6.el5.x86_64.rpm\\nfinger-0.17-32.2.1.1.x86_64.rpm\\nfipscheck-1.2.0-1.el5.x86_64.rpm\\nfipscheck-lib-1.2.0-1.el5.x86_64.rpm\\nfirstboot-tui-1.4.27.8-1.el5.x86_64.rpm\\nfontconfig-2.4.1-7.el5.x86_64.rpm\\nfping-2.4-1.b2.2.el5.rf.x86_64.rpm\\nfreetype-2.2.1-21.el5_3.x86_64.rpm\\nftp-0.17-35.el5.x86_64.rpm\\ngamin-0.1.7-8.el5.x86_64.rpm\\ngamin-python-0.1.7-8.el5.x86_64.rpm\\ngawk-3.1.5-14.el5.x86_64.rpm\\ngcc-4.1.2-48.el5.x86_64.rpm\\ngdbm-1.8.0-26.2.1.x86_64.rpm\\ngettext-0.14.6-4.el5.x86_64.rpm\\ngit-1.7.1-1.x86_64.rpm\\nglib2-2.12.3-4.el5_3.1.i386.rpm\\nglib2-2.12.3-4.el5_3.1.x86_64.rpm\\nglibc-2.5-49.i686.rpm\\nglibc-2.5-49.x86_64.rpm\\nglibc-common-2.5-49.x86_64.rpm\\nglibc-devel-2.5-49.x86_64.rpm\\nglibc-headers-2.5-49.x86_64.rpm\\ngnupg-1.4.5-14.x86_64.rpm\\ngnutls-1.4.1-3.el5_4.8.x86_64.rpm\\ngpg-pubkey-37017186-45761324.(none).rpm\\ngpg-pubkey-6b8d79e6-3f49313d.(none).rpm\\ngpm-1.20.1-74.1.i386.rpm\\ngpm-1.20.1-74.1.x86_64.rpm\\ngrep-2.5.1-55.el5.x86_64.rpm\\ngroff-1.18.1.1-11.1.x86_64.rpm\\ngrub-0.97-13.5.x86_64.rpm\\ngtk2-2.10.4-20.el5.x86_64.rpm\\ngzip-1.3.5-11.el5_4.1.x86_64.rpm\\nhal-0.5.8.1-59.el5.i386.rpm\\nhal-0.5.8.1-59.el5.x86_64.rpm\\nhdparm-6.6-2.x86_64.rpm\\nhesiod-3.1.0-8.x86_64.rpm\\nhicolor-icon-theme-0.9-2.1.noarch.rpm\\nhmaccalc-0.9.6-3.el5.x86_64.rpm\\nhtmlview-4.0.0-2.el5.noarch.rpm\\nhttpd-2.2.3-43.el5.x86_64.rpm\\nhwdata-0.213.18-1.el5.1.noarch.rpm\\nifd-egate-0.05-15.x86_64.rpm\\ninfo-4.8-14.el5.x86_64.rpm\\ninitscripts-8.45.30-2.el5.x86_64.rpm\\niproute-2.6.18-11.el5.x86_64.rpm\\nipsec-tools-0.6.5-13.el5_3.1.x86_64.rpm\\niptables-1.3.5-5.3.el5_4.1.x86_64.rpm\\niptables-ipv6-1.3.5-5.3.el5_4.1.x86_64.rpm\\niptstate-1.4-2.el5.x86_64.rpm\\niputils-20020927-46.el5.x86_64.rpm\\nirda-utils-0.9.17-2.fc6.x86_64.rpm\\nirqbalance-0.55-15.el5.x86_64.rpm\\njwhois-3.2.3-8.el5.x86_64.rpm\\nkbd-1.12-21.el5.x86_64.rpm\\nkernel-2.6.18-194.3.1.el5.x86_64.rpm\\nkernel-2.6.18-194.el5.x86_64.rpm\\nkernel-devel-2.6.18-194.3.1.el5.x86_64.rpm\\nkernel-devel-2.6.18-194.el5.x86_64.rpm\\nkernel-headers-2.6.18-194.3.1.el5.x86_64.rpm\\nkeyutils-libs-1.2-1.el5.i386.rpm\\nkeyutils-libs-1.2-1.el5.x86_64.rpm\\nkpartx-0.4.7-34.el5_5.1.x86_64.rpm\\nkrb5-libs-1.6.1-36.el5_5.2.i386.rpm\\nkrb5-libs-1.6.1-36.el5_5.2.x86_64.rpm\\nkrb5-workstation-1.6.1-36.el5_5.2.x86_64.rpm\\nksh-20100202-1.el5.x86_64.rpm\\nkudzu-1.2.57.1.24-1.x86_64.rpm\\nless-436-2.el5.x86_64.rpm\\nlftp-4.0.7-1.el5.rf.x86_64.rpm\\nlibICE-1.0.1-2.1.i386.rpm\\nlibICE-1.0.1-2.1.x86_64.rpm\\nlibIDL-0.8.7-1.fc6.x86_64.rpm\\nlibSM-1.0.1-3.1.i386.rpm\\nlibSM-1.0.1-3.1.x86_64.rpm\\nlibX11-1.0.3-11.el5.i386.rpm\\nlibX11-1.0.3-11.el5.x86_64.rpm\\nlibXau-1.0.1-3.1.i386.rpm\\nlibXau-1.0.1-3.1.x86_64.rpm\\nlibXcursor-1.1.7-1.1.x86_64.rpm\\nlibXdmcp-1.0.1-2.1.i386.rpm\\nlibXdmcp-1.0.1-2.1.x86_64.rpm\\nlibXext-1.0.1-2.1.i386.rpm\\nlibXext-1.0.1-2.1.x86_64.rpm\\nlibXfixes-4.0.1-2.1.x86_64.rpm\\nlibXft-2.1.10-1.1.x86_64.rpm\\nlibXi-1.0.1-4.el5_4.i386.rpm\\nlibXi-1.0.1-4.el5_4.x86_64.rpm\\nlibXinerama-1.0.1-2.1.x86_64.rpm\\nlibXrandr-1.1.1-3.3.x86_64.rpm\\nlibXrender-0.9.1-3.1.x86_64.rpm\\nlibXres-1.0.1-3.1.x86_64.rpm\\nlibXt-1.0.2-3.2.el5.i386.rpm\\nlibXt-1.0.2-3.2.el5.x86_64.rpm\\nlibXxf86vm-1.0.1-3.1.i386.rpm\\nlibXxf86vm-1.0.1-3.1.x86_64.rpm\\nlibacl-2.2.39-6.el5.x86_64.rpm\\nlibaio-0.3.106-5.i386.rpm\\nlibaio-0.3.106-5.x86_64.rpm\\nlibattr-2.4.32-1.1.x86_64.rpm\\nlibcap-1.10-26.i386.rpm\\nlibcap-1.10-26.x86_64.rpm\\nlibdaemon-0.10-5.el5.i386.rpm\\nlibdaemon-0.10-5.el5.x86_64.rpm\\nlibdrm-2.0.2-1.1.i386.rpm\\nlibdrm-2.0.2-1.1.x86_64.rpm\\nlibevent-1.4.13-1.x86_64.rpm\\nlibgcc-4.1.2-48.el5.i386.rpm\\nlibgcc-4.1.2-48.el5.x86_64.rpm\\nlibgcrypt-1.4.4-5.el5.i386.rpm\\nlibgcrypt-1.4.4-5.el5.x86_64.rpm\\nlibgomp-4.4.0-6.el5.x86_64.rpm\\nlibgpg-error-1.4-2.i386.rpm\\nlibgpg-error-1.4-2.x86_64.rpm\\nlibgssapi-0.10-2.x86_64.rpm\\nlibhugetlbfs-1.3-7.el5.i386.rpm\\nlibhugetlbfs-1.3-7.el5.x86_64.rpm\\nlibidn-0.6.5-1.1.x86_64.rpm\\nlibjpeg-6b-37.x86_64.rpm\\nlibnotify-0.4.2-6.el5.x86_64.rpm\\nlibpcap-0.9.4-15.el5.x86_64.rpm\\nlibpng-1.2.10-7.1.el5_3.2.x86_64.rpm\\nlibselinux-1.33.4-5.5.el5.i386.rpm\\nlibselinux-1.33.4-5.5.el5.x86_64.rpm\\nlibselinux-python-1.33.4-5.5.el5.x86_64.rpm\\nlibselinux-utils-1.33.4-5.5.el5.x86_64.rpm\\nlibsemanage-1.9.1-4.4.el5.x86_64.rpm\\nlibsepol-1.15.2-3.el5.i386.rpm\\nlibsepol-1.15.2-3.el5.x86_64.rpm\\nlibstdc++-4.1.2-48.el5.i386.rpm\\nlibstdc++-4.1.2-48.el5.x86_64.rpm\\nlibsysfs-2.0.0-6.x86_64.rpm\\nlibtermcap-2.0.8-46.1.i386.rpm\\nlibtermcap-2.0.8-46.1.x86_64.rpm\\nlibtiff-3.8.2-7.el5_3.4.x86_64.rpm\\nlibusb-0.1.12-5.1.i386.rpm\\nlibusb-0.1.12-5.1.x86_64.rpm\\nlibuser-0.54.7-2.1.el5_4.1.x86_64.rpm\\nlibutempter-1.1.4-4.el5.i386.rpm\\nlibutempter-1.1.4-4.el5.x86_64.rpm\\nlibvolume_id-095-14.21.el5.i386.rpm\\nlibvolume_id-095-14.21.el5.x86_64.rpm\\nlibwnck-2.16.0-4.fc6.x86_64.rpm\\nlibxml2-2.6.26-2.1.2.8.x86_64.rpm\\nlibxml2-python-2.6.26-2.1.2.8.x86_64.rpm\\nlm_sensors-2.10.7-9.el5.x86_64.rpm\\nlogrotate-3.7.4-9.x86_64.rpm\\nlsof-4.78-3.x86_64.rpm\\nlvm2-2.02.56-8.el5_5.1.x86_64.rpm\\nlzo2-2.02-3.el5.rf.x86_64.rpm\\nm2crypto-0.16-6.el5.6.x86_64.rpm\\nm4-1.4.5-3.el5.1.x86_64.rpm\\nmailcap-2.1.23-1.fc6.noarch.rpm\\nmailx-8.1.1-44.2.2.x86_64.rpm\\nmake-3.81-3.el5.x86_64.rpm\\nman-1.6d-1.1.x86_64.rpm\\nman-pages-2.39-15.el5.noarch.rpm\\nmcelog-0.9pre-1.29.el5.x86_64.rpm\\nmcstrans-0.2.11-3.el5.x86_64.rpm\\nmdadm-2.6.9-3.el5.x86_64.rpm\\nmesa-libGL-6.5.1-7.8.el5.i386.rpm\\nmesa-libGL-6.5.1-7.8.el5.x86_64.rpm\\nmgetty-1.1.33-9.fc6.x86_64.rpm\\nmicrocode_ctl-1.17-1.50.el5.x86_64.rpm\\nmingetty-1.07-5.2.2.x86_64.rpm\\nmkbootdisk-1.5.3-2.1.x86_64.rpm\\nmkinitrd-5.1.19.6-61.el5_5.1.i386.rpm\\nmkinitrd-5.1.19.6-61.el5_5.1.x86_64.rpm\\nmktemp-1.5-23.2.2.x86_64.rpm\\nmlocate-0.15-1.el5.2.x86_64.rpm\\nmodule-init-tools-3.3-0.pre3.1.60.el5.x86_64.rpm\\nmozldap-6.0.5-1.el5.x86_64.rpm\\nmtools-3.9.10-2.fc6.x86_64.rpm\\nmtr-0.75-1.el5.rf.x86_64.rpm\\nmysql-5.0.77-4.el5_4.2.i386.rpm\\nmysql-5.0.77-4.el5_4.2.x86_64.rpm\\nmysql-server-5.0.77-4.el5_4.2.x86_64.rpm\\nnagios-nrpe-2.12-1.el5.rf.x86_64.rpm\\nnagios-plugins-1.4.14-1.el5.rf.x86_64.rpm\\nnano-1.3.12-1.1.x86_64.rpm\\nnash-5.1.19.6-61.el5_5.1.x86_64.rpm\\nnc-1.84-10.fc6.x86_64.rpm\\nncurses-5.5-24.20060715.i386.rpm\\nncurses-5.5-24.20060715.x86_64.rpm\\nnet-snmp-5.3.2.2-9.el5_5.1.x86_64.rpm\\nnet-snmp-libs-5.3.2.2-9.el5_5.1.x86_64.rpm\\nnet-tools-1.60-81.el5.x86_64.rpm\\nnewt-0.52.2-15.el5.x86_64.rpm\\nnfs-utils-1.0.9-44.el5.x86_64.rpm\\nnfs-utils-lib-1.0.8-7.6.el5.x86_64.rpm\\nnmap-5.00-1.el5.rf.x86_64.rpm\\nnotification-daemon-0.3.5-9.el5.x86_64.rpm\\nnscd-2.5-49.x86_64.rpm\\nnspr-4.8.4-1.el5_4.i386.rpm\\nnspr-4.8.4-1.el5_4.x86_64.rpm\\nnss-3.12.6-1.el5_4.i386.rpm\\nnss-3.12.6-1.el5_4.x86_64.rpm\\nnss-tools-3.12.6-1.el5_4.x86_64.rpm\\nnss_db-2.2-35.4.el5_5.i386.rpm\\nnss_db-2.2-35.4.el5_5.x86_64.rpm\\nnss_ldap-253-25.el5.i386.rpm\\nnss_ldap-253-25.el5.x86_64.rpm\\nntp-4.2.2p1-9.el5_4.1.x86_64.rpm\\nntsysv-1.3.30.2-2.el5.x86_64.rpm\\nnumactl-0.9.8-11.el5.i386.rpm\\nnumactl-0.9.8-11.el5.x86_64.rpm\\nopenldap-2.3.43-12.el5.i386.rpm\\nopenldap-2.3.43-12.el5.x86_64.rpm\\nopenldap-clients-2.3.43-12.el5.x86_64.rpm\\nopenssh-4.3p2-41.el5.x86_64.rpm\\nopenssh-clients-4.3p2-41.el5.x86_64.rpm\\nopenssh-server-4.3p2-41.el5.x86_64.rpm\\nopenssl-0.9.8e-12.el5_4.6.i686.rpm\\nopenssl-0.9.8e-12.el5_4.6.x86_64.rpm\\nopenvpn-2.0.9-1.el5.rf.x86_64.rpm\\npam-0.99.6.2-6.el5_4.1.i386.rpm\\npam-0.99.6.2-6.el5_4.1.x86_64.rpm\\npam_ccreds-3-5.i386.rpm\\npam_ccreds-3-5.x86_64.rpm\\npam_krb5-2.2.14-15.i386.rpm\\npam_krb5-2.2.14-15.x86_64.rpm\\npam_passwdqc-1.0.2-1.2.2.i386.rpm\\npam_passwdqc-1.0.2-1.2.2.x86_64.rpm\\npam_pkcs11-0.5.3-23.i386.rpm\\npam_pkcs11-0.5.3-23.x86_64.rpm\\npam_smb-1.1.7-7.2.1.i386.rpm\\npam_smb-1.1.7-7.2.1.x86_64.rpm\\npango-1.14.9-8.el5.x86_64.rpm\\npaps-0.6.6-19.el5.x86_64.rpm\\nparted-1.8.1-27.el5.i386.rpm\\nparted-1.8.1-27.el5.x86_64.rpm\\npasswd-0.73-1.x86_64.rpm\\npatch-2.5.4-29.2.3.el5.x86_64.rpm\\npax-3.4-2.el5.x86_64.rpm\\npciutils-2.2.3-8.el5.x86_64.rpm\\npcmciautils-014-5.x86_64.rpm\\npcre-6.6-2.el5_1.7.x86_64.rpm\\npcsc-lite-1.4.4-1.el5.x86_64.rpm\\npcsc-lite-libs-1.4.4-1.el5.x86_64.rpm\\nperl-5.8.8-27.el5.x86_64.rpm\\nperl-Crypt-DES-2.05-3.2.el5.rf.x86_64.rpm\\nperl-Crypt-PasswdMD5-1.3-1.2.el5.rf.noarch.rpm\\nperl-DBD-mysql-4.014-1.el5.rf.x86_64.rpm\\nperl-DBI-1.609-1.el5.rf.x86_64.rpm\\nperl-Digest-HMAC-1.01-15.noarch.rpm\\nperl-Digest-SHA1-2.12-2.el5.rf.x86_64.rpm\\nperl-Git-1.7.1-1.x86_64.rpm\\nperl-Net-Daemon-0.43-1.el5.rf.noarch.rpm\\nperl-Net-SNMP-5.2.0-1.2.el5.rf.noarch.rpm\\nperl-PlRPC-0.2020-1.el5.rf.noarch.rpm\\nperl-Socket6-0.23-1.el5.rf.x86_64.rpm\\nperl-String-CRC32-1.4-2.fc6.x86_64.rpm\\npinfo-0.6.9-1.fc6.x86_64.rpm\\npkinit-nss-0.7.6-1.el5.x86_64.rpm\\npm-utils-0.99.3-10.el5.x86_64.rpm\\npolicycoreutils-1.33.12-14.8.el5.x86_64.rpm\\npoppler-0.5.4-4.4.el5_4.11.x86_64.rpm\\npoppler-utils-0.5.4-4.4.el5_4.11.x86_64.rpm\\npopt-1.10.2.3-18.el5.x86_64.rpm\\nportmap-4.0-65.2.2.1.x86_64.rpm\\npostgresql-libs-8.1.21-1.el5_5.1.x86_64.rpm\\nppp-2.4.4-2.el5.x86_64.rpm\\nprelink-0.4.0-2.el5.x86_64.rpm\\nprocmail-3.22-17.1.x86_64.rpm\\nprocps-3.2.7-16.el5.x86_64.rpm\\npsacct-6.3.2-44.el5.x86_64.rpm\\npsmisc-22.2-7.x86_64.rpm\\npuppet-0.25.4-1.rhel5.x86_64.rpm\\npyOpenSSL-0.6-1.p24.7.2.2.x86_64.rpm\\npygobject2-2.12.1-5.el5.x86_64.rpm\\npython-2.4.3-27.el5.x86_64.rpm\\npython-dmidecode-3.10.8-4.el5.x86_64.rpm\\npython-elementtree-1.2.6-5.x86_64.rpm\\npython-iniparse-0.2.3-4.el5.noarch.rpm\\npython-sqlite-1.1.7-1.2.1.x86_64.rpm\\npython-urlgrabber-3.1.0-5.el5.noarch.rpm\\npython26-2.6.2-geekymedia1.1.rhel5.x86_64.rpm\\npython26-devel-2.6.2-geekymedia1.1.rhel5.x86_64.rpm\\npython26-libs-2.6.2-geekymedia1.1.rhel5.x86_64.rpm\\npython26-setuptools-0.6c7-1.rhel5.noarch.rpm\\npython26-test-2.6.2-geekymedia1.1.rhel5.x86_64.rpm\\npython26-tools-2.6.2-geekymedia1.1.rhel5.x86_64.rpm\\nquota-3.13-1.2.5.el5.x86_64.rpm\\nrdate-1.4-8.el5.x86_64.rpm\\nrdist-6.1.5-44.x86_64.rpm\\nreadahead-1.3-8.el5.x86_64.rpm\\nreadline-5.1-3.el5.i386.rpm\\nreadline-5.1-3.el5.x86_64.rpm\\nredhat-logos-4.9.16-1.noarch.rpm\\nredhat-lsb-3.1-12.3.EL.i386.rpm\\nredhat-lsb-3.1-12.3.EL.x86_64.rpm\\nredhat-menus-6.7.8-3.el5.noarch.rpm\\nredhat-release-5Server-5.5.0.2.x86_64.rpm\\nredhat-release-notes-5Server-31.x86_64.rpm\\nrhel-instnum-1.0.9-1.el5.noarch.rpm\\nrhn-check-0.4.20-33.el5_5.1.noarch.rpm\\nrhn-client-tools-0.4.20-33.el5_5.1.noarch.rpm\\nrhn-setup-0.4.20-33.el5_5.1.noarch.rpm\\nrhnlib-2.5.22-3.el5.noarch.rpm\\nrhnsd-4.7.0-5.el5.x86_64.rpm\\nrhpl-0.194.1-1.x86_64.rpm\\nrmt-0.4b41-4.el5.x86_64.rpm\\nrng-utils-2.0-1.14.1.fc6.x86_64.rpm\\nrootfiles-8.1-1.1.1.noarch.rpm\\nrp-pppoe-3.5-32.1.x86_64.rpm\\nrpm-4.4.2.3-18.el5.x86_64.rpm\\nrpm-libs-4.4.2.3-18.el5.x86_64.rpm\\nrpm-python-4.4.2.3-18.el5.x86_64.rpm\\nrsh-0.17-40.el5.x86_64.rpm\\nrsync-3.0.7-1.el5.rf.x86_64.rpm\\nruby-1.8.5-5.el5_4.8.x86_64.rpm\\nruby-augeas-0.3.0-1.el5.x86_64.rpm\\nruby-irb-1.8.5-5.el5_4.8.x86_64.rpm\\nruby-libs-1.8.5-5.el5_4.8.x86_64.rpm\\nruby-rdoc-1.8.5-5.el5_4.8.x86_64.rpm\\nscreen-4.0.3-1.el5_4.1.x86_64.rpm\\nsed-4.1.5-5.fc6.x86_64.rpm\\nselinux-policy-2.4.6-279.el5.noarch.rpm\\nselinux-policy-targeted-2.4.6-279.el5.noarch.rpm\\nsendmail-8.13.8-8.el5.x86_64.rpm\\nsetarch-2.0-1.1.x86_64.rpm\\nsetools-3.0-3.el5.x86_64.rpm\\nsetserial-2.17-19.2.2.x86_64.rpm\\nsetup-2.5.58-7.el5.noarch.rpm\\nsetuptool-1.19.2-1.x86_64.rpm\\nsgpio-1.2.0_10-2.el5.x86_64.rpm\\nshadow-utils-4.0.17-15.el5.x86_64.rpm\\nslang-2.0.6-4.el5.x86_64.rpm\\nsmartmontools-5.38-2.el5.x86_64.rpm\\nsos-1.7-9.49.el5.noarch.rpm\\nspecspo-13-1.el5.noarch.rpm\\nsqlite-3.3.6-5.x86_64.rpm\\nstartup-notification-0.8-4.1.x86_64.rpm\\nstrace-4.5.18-5.el5_4.4.x86_64.rpm\\nstunnel-4.15-2.el5.1.x86_64.rpm\\nsudo-1.7.2p1-6.el5_5.x86_64.rpm\\nsvrcore-4.0.4-3.el5.i386.rpm\\nsvrcore-4.0.4-3.el5.x86_64.rpm\\nsymlinks-1.2-24.2.2.x86_64.rpm\\nsysfsutils-2.0.0-6.x86_64.rpm\\nsysklogd-1.4.1-46.el5.x86_64.rpm\\nsyslinux-3.86-1.el5.rf.x86_64.rpm\\nsysstat-7.0.2-3.el5.x86_64.rpm\\nsystem-config-network-tui-1.3.99.18-1.el5.noarch.rpm\\nsystem-config-securitylevel-tui-1.6.29.1-5.el5.x86_64.rpm\\ntalk-0.17-29.2.2.x86_64.rpm\\ntar-1.15.1-30.el5.x86_64.rpm\\ntcl-8.4.13-4.el5.x86_64.rpm\\ntcp_wrappers-7.6-40.7.el5.i386.rpm\\ntcp_wrappers-7.6-40.7.el5.x86_64.rpm\\ntcpdump-3.9.4-15.el5.x86_64.rpm\\ntcsh-6.14-17.el5.x86_64.rpm\\ntelnet-0.17-39.el5.x86_64.rpm\\ntermcap-5.5-1.20060701.1.noarch.rpm\\ntime-1.7-27.2.2.x86_64.rpm\\ntix-8.4.0-11.fc6.x86_64.rpm\\ntk-8.4.13-5.el5_1.1.x86_64.rpm\\ntkinter26-2.6.2-geekymedia1.1.rhel5.x86_64.rpm\\ntmpwatch-2.9.7-1.1.el5.2.x86_64.rpm\\ntraceroute-2.0.1-5.el5.x86_64.rpm\\ntree-1.5.0-4.x86_64.rpm\\ntzdata-2010i-1.el5.x86_64.rpm\\nudev-095-14.21.el5.x86_64.rpm\\nudftools-1.0.0b3-3.el5.rf.x86_64.rpm\\nunix2dos-2.2-26.2.3.el5.x86_64.rpm\\nunzip-5.52-3.el5.x86_64.rpm\\nusbutils-0.71-2.1.x86_64.rpm\\nusermode-1.88-3.el5.2.x86_64.rpm\\nutil-linux-2.13-0.52.el5_4.1.x86_64.rpm\\nvconfig-1.9-3.x86_64.rpm\\nvim-common-7.0.109-6.el5.x86_64.rpm\\nvim-enhanced-7.0.109-6.el5.x86_64.rpm\\nvim-minimal-7.0.109-6.el5.x86_64.rpm\\nvixie-cron-4.1-77.el5_4.1.x86_64.rpm\\nvmware-update-manager-ga-1.0.0-84689.i386.rpm\\nwget-1.11.4-2.el5_4.1.x86_64.rpm\\nwhich-2.16-7.x86_64.rpm\\nwireless-tools-28-2.el5.i386.rpm\\nwireless-tools-28-2.el5.x86_64.rpm\\nwords-3.0-9.1.noarch.rpm\\nwpa_supplicant-0.5.10-9.el5.x86_64.rpm\\nxorg-x11-filesystem-7.1-2.fc6.noarch.rpm\\nyp-tools-2.9-1.el5.x86_64.rpm\\nypbind-1.19-12.el5.x86_64.rpm\\nyum-3.2.22-26.el5.noarch.rpm\\nyum-metadata-parser-1.1.2-3.el5.x86_64.rpm\\nyum-rhn-plugin-0.5.4-15.el5.noarch.rpm\\nyum-security-1.1.16-13.el5.noarch.rpm\\nyum-updatesd-0.9-2.el5.noarch.rpm\\nyum-utils-1.1.16-13.el5.noarch.rpm\\nzip-2.31-2.el5.x86_64.rpm\\nzlib-1.2.3-3.i386.rpm\\nzlib-1.2.3-3.x86_64.rpm'\np0\n.", 
'sha1': '18510f996b191d0b4f76830245bc5d77edb87ff2',
'unserialized': 'quartz-1.0.2.rpm\nDeeployment_Guide-en-US-5.2-11.noarch.rpm\nGConf2-2.14.0-9.el5.x86_64.rpm\nMAKEDEV-3.23-1.2.x86_64.rpm\nNetworkManager-0.7.0-10.el5.i386.rpm\nNetworkManager-0.7.0-10.el5.x86_64.rpm\nNetworkManager-glib-0.7.0-10.el5.i386.rpm\nNetworkManager-glib-0.7.0-10.el5.x86_64.rpm\nORBit2-2.14.3-5.el5.x86_64.rpm\nSysVinit-2.86-15.el5.x86_64.rpm\nacl-2.2.39-6.el5.x86_64.rpm\nacpid-1.0.4-9.el5_4.2.x86_64.rpm\namtu-1.0.6-1.el5.x86_64.rpm\nanacron-2.3-45.el5.x86_64.rpm\napr-1.2.7-11.el5_3.1.x86_64.rpm\napr-util-1.2.7-11.el5.x86_64.rpm\naspell-0.60.3-7.1.i386.rpm\naspell-0.60.3-7.1.x86_64.rpm\naspell-en-6.0-2.1.x86_64.rpm\nat-3.1.8-84.el5.x86_64.rpm\natk-1.12.2-1.fc6.x86_64.rpm\nattr-2.4.32-1.1.x86_64.rpm\naudit-1.7.17-3.el5.x86_64.rpm\naudit-libs-1.7.17-3.el5.i386.rpm\naudit-libs-1.7.17-3.el5.x86_64.rpm\naudit-libs-python-1.7.17-3.el5.x86_64.rpm\naugeas-libs-0.6.0-2.el5.x86_64.rpm\nauthconfig-5.3.21-6.el5.x86_64.rpm\nautofs-5.0.1-0.rc2.143.el5.x86_64.rpm\navahi-0.6.16-7.el5.x86_64.rpm\navahi-compat-libdns_sd-0.6.16-7.el5.x86_64.rpm\nbasesystem-8.0-5.1.1.noarch.rpm\nbash-3.2-24.el5.x86_64.rpm\nbc-1.06-21.x86_64.rpm\nbind-libs-9.3.6-4.P1.el5_4.2.x86_64.rpm\nbind-utils-9.3.6-4.P1.el5_4.2.x86_64.rpm\nbinutils-2.17.50.0.6-14.el5.x86_64.rpm\nbitstream-vera-fonts-1.10-7.noarch.rpm\nbluez-gnome-0.5-5.fc6.x86_64.rpm\nbluez-libs-3.7-1.1.x86_64.rpm\nbluez-utils-3.7-2.2.x86_64.rpm\nbzip2-1.0.3-4.el5_2.x86_64.rpm\nbzip2-libs-1.0.3-4.el5_2.x86_64.rpm\ncairo-1.2.4-5.el5.x86_64.rpm\nccid-1.3.8-1.el5.x86_64.rpm\ncheckpolicy-1.33.1-6.el5.x86_64.rpm\nchkconfig-1.3.30.2-2.el5.x86_64.rpm\nconman-0.1.9.2-8.el5.x86_64.rpm\ncoolkey-1.1.0-14.el5.i386.rpm\ncoolkey-1.1.0-14.el5.x86_64.rpm\ncoreutils-5.97-23.el5_4.2.x86_64.rpm\ncpio-2.6-23.el5_4.1.x86_64.rpm\ncpp-4.1.2-48.el5.x86_64.rpm\ncpuspeed-1.2.1-9.el5.x86_64.rpm\ncracklib-2.8.9-3.3.i386.rpm\ncracklib-2.8.9-3.3.x86_64.rpm\ncracklib-dicts-2.8.9-3.3.x86_64.rpm\ncrash-4.1.2-4.el5.x86_64.rpm\ncrontabs-1.10-8.noarch.rpm\ncryptsetup-luks-1.0.3-5.el5.i386.rpm\ncryptsetup-luks-1.0.3-5.el5.x86_64.rpm\ncups-1.3.7-18.el5.x86_64.rpm\ncups-libs-1.3.7-18.el5.x86_64.rpm\ncurl-7.15.5-9.el5.x86_64.rpm\ncyrus-sasl-2.1.22-5.el5_4.3.x86_64.rpm\ncyrus-sasl-lib-2.1.22-5.el5_4.3.i386.rpm\ncyrus-sasl-lib-2.1.22-5.el5_4.3.x86_64.rpm\ncyrus-sasl-plain-2.1.22-5.el5_4.3.i386.rpm\ncyrus-sasl-plain-2.1.22-5.el5_4.3.x86_64.rpm\ndb4-4.3.29-10.el5.i386.rpm\ndb4-4.3.29-10.el5.x86_64.rpm\ndbus-1.1.2-14.el5.x86_64.rpm\ndbus-glib-0.73-8.el5.i386.rpm\ndbus-glib-0.73-8.el5.x86_64.rpm\ndbus-libs-1.1.2-14.el5.i386.rpm\ndbus-libs-1.1.2-14.el5.x86_64.rpm\ndbus-python-0.70-9.el5_4.x86_64.rpm\ndesktop-file-utils-0.10-7.x86_64.rpm\ndevice-mapper-1.02.39-1.el5.i386.rpm\ndevice-mapper-1.02.39-1.el5.x86_64.rpm\ndevice-mapper-event-1.02.39-1.el5.x86_64.rpm\ndevice-mapper-multipath-0.4.7-34.el5_5.1.x86_64.rpm\ndhclient-3.0.5-23.el5.x86_64.rpm\ndhcpv6-client-1.0.10-18.el5.x86_64.rpm\ndiffutils-2.8.1-15.2.3.el5.x86_64.rpm\ndmidecode-2.10-3.el5.x86_64.rpm\ndmraid-1.0.0.rc13-63.el5.x86_64.rpm\ndmraid-events-1.0.0.rc13-63.el5.x86_64.rpm\ndnsmasq-2.51-1.el5.rf.x86_64.rpm\ndos2unix-3.1-27.2.el5.x86_64.rpm\ndosfstools-2.11-9.el5.x86_64.rpm\ndump-0.4b41-4.el5.x86_64.rpm\ne2fsprogs-1.39-23.el5.x86_64.rpm\ne2fsprogs-libs-1.39-23.el5.i386.rpm\ne2fsprogs-libs-1.39-23.el5.x86_64.rpm\ned-0.2-39.el5_2.x86_64.rpm\neject-2.1.5-4.2.el5.x86_64.rpm\nelfutils-libelf-0.137-3.el5.x86_64.rpm\nethtool-6-4.el5.x86_64.rpm\nexpat-1.95.8-8.3.el5_4.2.i386.rpm\nexpat-1.95.8-8.3.el5_4.2.x86_64.rpm\nfacter-1.5.7-1.rhel5.x86_64.rpm\nfbset-2.1-22.x86_64.rpm\nfile-4.17-15.el5_3.1.x86_64.rpm\nfilesystem-2.4.0-3.el5.x86_64.rpm\nfindutils-4.2.27-6.el5.x86_64.rpm\nfinger-0.17-32.2.1.1.x86_64.rpm\nfipscheck-1.2.0-1.el5.x86_64.rpm\nfipscheck-lib-1.2.0-1.el5.x86_64.rpm\nfirstboot-tui-1.4.27.8-1.el5.x86_64.rpm\nfontconfig-2.4.1-7.el5.x86_64.rpm\nfping-2.4-1.b2.2.el5.rf.x86_64.rpm\nfreetype-2.2.1-21.el5_3.x86_64.rpm\nftp-0.17-35.el5.x86_64.rpm\ngamin-0.1.7-8.el5.x86_64.rpm\ngamin-python-0.1.7-8.el5.x86_64.rpm\ngawk-3.1.5-14.el5.x86_64.rpm\ngcc-4.1.2-48.el5.x86_64.rpm\ngdbm-1.8.0-26.2.1.x86_64.rpm\ngettext-0.14.6-4.el5.x86_64.rpm\ngit-1.7.1-1.x86_64.rpm\nglib2-2.12.3-4.el5_3.1.i386.rpm\nglib2-2.12.3-4.el5_3.1.x86_64.rpm\nglibc-2.5-49.i686.rpm\nglibc-2.5-49.x86_64.rpm\nglibc-common-2.5-49.x86_64.rpm\nglibc-devel-2.5-49.x86_64.rpm\nglibc-headers-2.5-49.x86_64.rpm\ngnupg-1.4.5-14.x86_64.rpm\ngnutls-1.4.1-3.el5_4.8.x86_64.rpm\ngpg-pubkey-37017186-45761324.(none).rpm\ngpg-pubkey-6b8d79e6-3f49313d.(none).rpm\ngpm-1.20.1-74.1.i386.rpm\ngpm-1.20.1-74.1.x86_64.rpm\ngrep-2.5.1-55.el5.x86_64.rpm\ngroff-1.18.1.1-11.1.x86_64.rpm\ngrub-0.97-13.5.x86_64.rpm\ngtk2-2.10.4-20.el5.x86_64.rpm\ngzip-1.3.5-11.el5_4.1.x86_64.rpm\nhal-0.5.8.1-59.el5.i386.rpm\nhal-0.5.8.1-59.el5.x86_64.rpm\nhdparm-6.6-2.x86_64.rpm\nhesiod-3.1.0-8.x86_64.rpm\nhicolor-icon-theme-0.9-2.1.noarch.rpm\nhmaccalc-0.9.6-3.el5.x86_64.rpm\nhtmlview-4.0.0-2.el5.noarch.rpm\nhttpd-2.2.3-43.el5.x86_64.rpm\nhwdata-0.213.18-1.el5.1.noarch.rpm\nifd-egate-0.05-15.x86_64.rpm\ninfo-4.8-14.el5.x86_64.rpm\ninitscripts-8.45.30-2.el5.x86_64.rpm\niproute-2.6.18-11.el5.x86_64.rpm\nipsec-tools-0.6.5-13.el5_3.1.x86_64.rpm\niptables-1.3.5-5.3.el5_4.1.x86_64.rpm\niptables-ipv6-1.3.5-5.3.el5_4.1.x86_64.rpm\niptstate-1.4-2.el5.x86_64.rpm\niputils-20020927-46.el5.x86_64.rpm\nirda-utils-0.9.17-2.fc6.x86_64.rpm\nirqbalance-0.55-15.el5.x86_64.rpm\njwhois-3.2.3-8.el5.x86_64.rpm\nkbd-1.12-21.el5.x86_64.rpm\nkernel-2.6.18-194.3.1.el5.x86_64.rpm\nkernel-2.6.18-194.el5.x86_64.rpm\nkernel-devel-2.6.18-194.3.1.el5.x86_64.rpm\nkernel-devel-2.6.18-194.el5.x86_64.rpm\nkernel-headers-2.6.18-194.3.1.el5.x86_64.rpm\nkeyutils-libs-1.2-1.el5.i386.rpm\nkeyutils-libs-1.2-1.el5.x86_64.rpm\nkpartx-0.4.7-34.el5_5.1.x86_64.rpm\nkrb5-libs-1.6.1-36.el5_5.2.i386.rpm\nkrb5-libs-1.6.1-36.el5_5.2.x86_64.rpm\nkrb5-workstation-1.6.1-36.el5_5.2.x86_64.rpm\nksh-20100202-1.el5.x86_64.rpm\nkudzu-1.2.57.1.24-1.x86_64.rpm\nless-436-2.el5.x86_64.rpm\nlftp-4.0.7-1.el5.rf.x86_64.rpm\nlibICE-1.0.1-2.1.i386.rpm\nlibICE-1.0.1-2.1.x86_64.rpm\nlibIDL-0.8.7-1.fc6.x86_64.rpm\nlibSM-1.0.1-3.1.i386.rpm\nlibSM-1.0.1-3.1.x86_64.rpm\nlibX11-1.0.3-11.el5.i386.rpm\nlibX11-1.0.3-11.el5.x86_64.rpm\nlibXau-1.0.1-3.1.i386.rpm\nlibXau-1.0.1-3.1.x86_64.rpm\nlibXcursor-1.1.7-1.1.x86_64.rpm\nlibXdmcp-1.0.1-2.1.i386.rpm\nlibXdmcp-1.0.1-2.1.x86_64.rpm\nlibXext-1.0.1-2.1.i386.rpm\nlibXext-1.0.1-2.1.x86_64.rpm\nlibXfixes-4.0.1-2.1.x86_64.rpm\nlibXft-2.1.10-1.1.x86_64.rpm\nlibXi-1.0.1-4.el5_4.i386.rpm\nlibXi-1.0.1-4.el5_4.x86_64.rpm\nlibXinerama-1.0.1-2.1.x86_64.rpm\nlibXrandr-1.1.1-3.3.x86_64.rpm\nlibXrender-0.9.1-3.1.x86_64.rpm\nlibXres-1.0.1-3.1.x86_64.rpm\nlibXt-1.0.2-3.2.el5.i386.rpm\nlibXt-1.0.2-3.2.el5.x86_64.rpm\nlibXxf86vm-1.0.1-3.1.i386.rpm\nlibXxf86vm-1.0.1-3.1.x86_64.rpm\nlibacl-2.2.39-6.el5.x86_64.rpm\nlibaio-0.3.106-5.i386.rpm\nlibaio-0.3.106-5.x86_64.rpm\nlibattr-2.4.32-1.1.x86_64.rpm\nlibcap-1.10-26.i386.rpm\nlibcap-1.10-26.x86_64.rpm\nlibdaemon-0.10-5.el5.i386.rpm\nlibdaemon-0.10-5.el5.x86_64.rpm\nlibdrm-2.0.2-1.1.i386.rpm\nlibdrm-2.0.2-1.1.x86_64.rpm\nlibevent-1.4.13-1.x86_64.rpm\nlibgcc-4.1.2-48.el5.i386.rpm\nlibgcc-4.1.2-48.el5.x86_64.rpm\nlibgcrypt-1.4.4-5.el5.i386.rpm\nlibgcrypt-1.4.4-5.el5.x86_64.rpm\nlibgomp-4.4.0-6.el5.x86_64.rpm\nlibgpg-error-1.4-2.i386.rpm\nlibgpg-error-1.4-2.x86_64.rpm\nlibgssapi-0.10-2.x86_64.rpm\nlibhugetlbfs-1.3-7.el5.i386.rpm\nlibhugetlbfs-1.3-7.el5.x86_64.rpm\nlibidn-0.6.5-1.1.x86_64.rpm\nlibjpeg-6b-37.x86_64.rpm\nlibnotify-0.4.2-6.el5.x86_64.rpm\nlibpcap-0.9.4-15.el5.x86_64.rpm\nlibpng-1.2.10-7.1.el5_3.2.x86_64.rpm\nlibselinux-1.33.4-5.5.el5.i386.rpm\nlibselinux-1.33.4-5.5.el5.x86_64.rpm\nlibselinux-python-1.33.4-5.5.el5.x86_64.rpm\nlibselinux-utils-1.33.4-5.5.el5.x86_64.rpm\nlibsemanage-1.9.1-4.4.el5.x86_64.rpm\nlibsepol-1.15.2-3.el5.i386.rpm\nlibsepol-1.15.2-3.el5.x86_64.rpm\nlibstdc++-4.1.2-48.el5.i386.rpm\nlibstdc++-4.1.2-48.el5.x86_64.rpm\nlibsysfs-2.0.0-6.x86_64.rpm\nlibtermcap-2.0.8-46.1.i386.rpm\nlibtermcap-2.0.8-46.1.x86_64.rpm\nlibtiff-3.8.2-7.el5_3.4.x86_64.rpm\nlibusb-0.1.12-5.1.i386.rpm\nlibusb-0.1.12-5.1.x86_64.rpm\nlibuser-0.54.7-2.1.el5_4.1.x86_64.rpm\nlibutempter-1.1.4-4.el5.i386.rpm\nlibutempter-1.1.4-4.el5.x86_64.rpm\nlibvolume_id-095-14.21.el5.i386.rpm\nlibvolume_id-095-14.21.el5.x86_64.rpm\nlibwnck-2.16.0-4.fc6.x86_64.rpm\nlibxml2-2.6.26-2.1.2.8.x86_64.rpm\nlibxml2-python-2.6.26-2.1.2.8.x86_64.rpm\nlm_sensors-2.10.7-9.el5.x86_64.rpm\nlogrotate-3.7.4-9.x86_64.rpm\nlsof-4.78-3.x86_64.rpm\nlvm2-2.02.56-8.el5_5.1.x86_64.rpm\nlzo2-2.02-3.el5.rf.x86_64.rpm\nm2crypto-0.16-6.el5.6.x86_64.rpm\nm4-1.4.5-3.el5.1.x86_64.rpm\nmailcap-2.1.23-1.fc6.noarch.rpm\nmailx-8.1.1-44.2.2.x86_64.rpm\nmake-3.81-3.el5.x86_64.rpm\nman-1.6d-1.1.x86_64.rpm\nman-pages-2.39-15.el5.noarch.rpm\nmcelog-0.9pre-1.29.el5.x86_64.rpm\nmcstrans-0.2.11-3.el5.x86_64.rpm\nmdadm-2.6.9-3.el5.x86_64.rpm\nmesa-libGL-6.5.1-7.8.el5.i386.rpm\nmesa-libGL-6.5.1-7.8.el5.x86_64.rpm\nmgetty-1.1.33-9.fc6.x86_64.rpm\nmicrocode_ctl-1.17-1.50.el5.x86_64.rpm\nmingetty-1.07-5.2.2.x86_64.rpm\nmkbootdisk-1.5.3-2.1.x86_64.rpm\nmkinitrd-5.1.19.6-61.el5_5.1.i386.rpm\nmkinitrd-5.1.19.6-61.el5_5.1.x86_64.rpm\nmktemp-1.5-23.2.2.x86_64.rpm\nmlocate-0.15-1.el5.2.x86_64.rpm\nmodule-init-tools-3.3-0.pre3.1.60.el5.x86_64.rpm\nmozldap-6.0.5-1.el5.x86_64.rpm\nmtools-3.9.10-2.fc6.x86_64.rpm\nmtr-0.75-1.el5.rf.x86_64.rpm\nmysql-5.0.77-4.el5_4.2.i386.rpm\nmysql-5.0.77-4.el5_4.2.x86_64.rpm\nmysql-server-5.0.77-4.el5_4.2.x86_64.rpm\nnagios-nrpe-2.12-1.el5.rf.x86_64.rpm\nnagios-plugins-1.4.14-1.el5.rf.x86_64.rpm\nnano-1.3.12-1.1.x86_64.rpm\nnash-5.1.19.6-61.el5_5.1.x86_64.rpm\nnc-1.84-10.fc6.x86_64.rpm\nncurses-5.5-24.20060715.i386.rpm\nncurses-5.5-24.20060715.x86_64.rpm\nnet-snmp-5.3.2.2-9.el5_5.1.x86_64.rpm\nnet-snmp-libs-5.3.2.2-9.el5_5.1.x86_64.rpm\nnet-tools-1.60-81.el5.x86_64.rpm\nnewt-0.52.2-15.el5.x86_64.rpm\nnfs-utils-1.0.9-44.el5.x86_64.rpm\nnfs-utils-lib-1.0.8-7.6.el5.x86_64.rpm\nnmap-5.00-1.el5.rf.x86_64.rpm\nnotification-daemon-0.3.5-9.el5.x86_64.rpm\nnscd-2.5-49.x86_64.rpm\nnspr-4.8.4-1.el5_4.i386.rpm\nnspr-4.8.4-1.el5_4.x86_64.rpm\nnss-3.12.6-1.el5_4.i386.rpm\nnss-3.12.6-1.el5_4.x86_64.rpm\nnss-tools-3.12.6-1.el5_4.x86_64.rpm\nnss_db-2.2-35.4.el5_5.i386.rpm\nnss_db-2.2-35.4.el5_5.x86_64.rpm\nnss_ldap-253-25.el5.i386.rpm\nnss_ldap-253-25.el5.x86_64.rpm\nntp-4.2.2p1-9.el5_4.1.x86_64.rpm\nntsysv-1.3.30.2-2.el5.x86_64.rpm\nnumactl-0.9.8-11.el5.i386.rpm\nnumactl-0.9.8-11.el5.x86_64.rpm\nopenldap-2.3.43-12.el5.i386.rpm\nopenldap-2.3.43-12.el5.x86_64.rpm\nopenldap-clients-2.3.43-12.el5.x86_64.rpm\nopenssh-4.3p2-41.el5.x86_64.rpm\nopenssh-clients-4.3p2-41.el5.x86_64.rpm\nopenssh-server-4.3p2-41.el5.x86_64.rpm\nopenssl-0.9.8e-12.el5_4.6.i686.rpm\nopenssl-0.9.8e-12.el5_4.6.x86_64.rpm\nopenvpn-2.0.9-1.el5.rf.x86_64.rpm\npam-0.99.6.2-6.el5_4.1.i386.rpm\npam-0.99.6.2-6.el5_4.1.x86_64.rpm\npam_ccreds-3-5.i386.rpm\npam_ccreds-3-5.x86_64.rpm\npam_krb5-2.2.14-15.i386.rpm\npam_krb5-2.2.14-15.x86_64.rpm\npam_passwdqc-1.0.2-1.2.2.i386.rpm\npam_passwdqc-1.0.2-1.2.2.x86_64.rpm\npam_pkcs11-0.5.3-23.i386.rpm\npam_pkcs11-0.5.3-23.x86_64.rpm\npam_smb-1.1.7-7.2.1.i386.rpm\npam_smb-1.1.7-7.2.1.x86_64.rpm\npango-1.14.9-8.el5.x86_64.rpm\npaps-0.6.6-19.el5.x86_64.rpm\nparted-1.8.1-27.el5.i386.rpm\nparted-1.8.1-27.el5.x86_64.rpm\npasswd-0.73-1.x86_64.rpm\npatch-2.5.4-29.2.3.el5.x86_64.rpm\npax-3.4-2.el5.x86_64.rpm\npciutils-2.2.3-8.el5.x86_64.rpm\npcmciautils-014-5.x86_64.rpm\npcre-6.6-2.el5_1.7.x86_64.rpm\npcsc-lite-1.4.4-1.el5.x86_64.rpm\npcsc-lite-libs-1.4.4-1.el5.x86_64.rpm\nperl-5.8.8-27.el5.x86_64.rpm\nperl-Crypt-DES-2.05-3.2.el5.rf.x86_64.rpm\nperl-Crypt-PasswdMD5-1.3-1.2.el5.rf.noarch.rpm\nperl-DBD-mysql-4.014-1.el5.rf.x86_64.rpm\nperl-DBI-1.609-1.el5.rf.x86_64.rpm\nperl-Digest-HMAC-1.01-15.noarch.rpm\nperl-Digest-SHA1-2.12-2.el5.rf.x86_64.rpm\nperl-Git-1.7.1-1.x86_64.rpm\nperl-Net-Daemon-0.43-1.el5.rf.noarch.rpm\nperl-Net-SNMP-5.2.0-1.2.el5.rf.noarch.rpm\nperl-PlRPC-0.2020-1.el5.rf.noarch.rpm\nperl-Socket6-0.23-1.el5.rf.x86_64.rpm\nperl-String-CRC32-1.4-2.fc6.x86_64.rpm\npinfo-0.6.9-1.fc6.x86_64.rpm\npkinit-nss-0.7.6-1.el5.x86_64.rpm\npm-utils-0.99.3-10.el5.x86_64.rpm\npolicycoreutils-1.33.12-14.8.el5.x86_64.rpm\npoppler-0.5.4-4.4.el5_4.11.x86_64.rpm\npoppler-utils-0.5.4-4.4.el5_4.11.x86_64.rpm\npopt-1.10.2.3-18.el5.x86_64.rpm\nportmap-4.0-65.2.2.1.x86_64.rpm\npostgresql-libs-8.1.21-1.el5_5.1.x86_64.rpm\nppp-2.4.4-2.el5.x86_64.rpm\nprelink-0.4.0-2.el5.x86_64.rpm\nprocmail-3.22-17.1.x86_64.rpm\nprocps-3.2.7-16.el5.x86_64.rpm\npsacct-6.3.2-44.el5.x86_64.rpm\npsmisc-22.2-7.x86_64.rpm\npuppet-0.25.4-1.rhel5.x86_64.rpm\npyOpenSSL-0.6-1.p24.7.2.2.x86_64.rpm\npygobject2-2.12.1-5.el5.x86_64.rpm\npython-2.4.3-27.el5.x86_64.rpm\npython-dmidecode-3.10.8-4.el5.x86_64.rpm\npython-elementtree-1.2.6-5.x86_64.rpm\npython-iniparse-0.2.3-4.el5.noarch.rpm\npython-sqlite-1.1.7-1.2.1.x86_64.rpm\npython-urlgrabber-3.1.0-5.el5.noarch.rpm\npython26-2.6.2-geekymedia1.1.rhel5.x86_64.rpm\npython26-devel-2.6.2-geekymedia1.1.rhel5.x86_64.rpm\npython26-libs-2.6.2-geekymedia1.1.rhel5.x86_64.rpm\npython26-setuptools-0.6c7-1.rhel5.noarch.rpm\npython26-test-2.6.2-geekymedia1.1.rhel5.x86_64.rpm\npython26-tools-2.6.2-geekymedia1.1.rhel5.x86_64.rpm\nquota-3.13-1.2.5.el5.x86_64.rpm\nrdate-1.4-8.el5.x86_64.rpm\nrdist-6.1.5-44.x86_64.rpm\nreadahead-1.3-8.el5.x86_64.rpm\nreadline-5.1-3.el5.i386.rpm\nreadline-5.1-3.el5.x86_64.rpm\nredhat-logos-4.9.16-1.noarch.rpm\nredhat-lsb-3.1-12.3.EL.i386.rpm\nredhat-lsb-3.1-12.3.EL.x86_64.rpm\nredhat-menus-6.7.8-3.el5.noarch.rpm\nredhat-release-5Server-5.5.0.2.x86_64.rpm\nredhat-release-notes-5Server-31.x86_64.rpm\nrhel-instnum-1.0.9-1.el5.noarch.rpm\nrhn-check-0.4.20-33.el5_5.1.noarch.rpm\nrhn-client-tools-0.4.20-33.el5_5.1.noarch.rpm\nrhn-setup-0.4.20-33.el5_5.1.noarch.rpm\nrhnlib-2.5.22-3.el5.noarch.rpm\nrhnsd-4.7.0-5.el5.x86_64.rpm\nrhpl-0.194.1-1.x86_64.rpm\nrmt-0.4b41-4.el5.x86_64.rpm\nrng-utils-2.0-1.14.1.fc6.x86_64.rpm\nrootfiles-8.1-1.1.1.noarch.rpm\nrp-pppoe-3.5-32.1.x86_64.rpm\nrpm-4.4.2.3-18.el5.x86_64.rpm\nrpm-libs-4.4.2.3-18.el5.x86_64.rpm\nrpm-python-4.4.2.3-18.el5.x86_64.rpm\nrsh-0.17-40.el5.x86_64.rpm\nrsync-3.0.7-1.el5.rf.x86_64.rpm\nruby-1.8.5-5.el5_4.8.x86_64.rpm\nruby-augeas-0.3.0-1.el5.x86_64.rpm\nruby-irb-1.8.5-5.el5_4.8.x86_64.rpm\nruby-libs-1.8.5-5.el5_4.8.x86_64.rpm\nruby-rdoc-1.8.5-5.el5_4.8.x86_64.rpm\nscreen-4.0.3-1.el5_4.1.x86_64.rpm\nsed-4.1.5-5.fc6.x86_64.rpm\nselinux-policy-2.4.6-279.el5.noarch.rpm\nselinux-policy-targeted-2.4.6-279.el5.noarch.rpm\nsendmail-8.13.8-8.el5.x86_64.rpm\nsetarch-2.0-1.1.x86_64.rpm\nsetools-3.0-3.el5.x86_64.rpm\nsetserial-2.17-19.2.2.x86_64.rpm\nsetup-2.5.58-7.el5.noarch.rpm\nsetuptool-1.19.2-1.x86_64.rpm\nsgpio-1.2.0_10-2.el5.x86_64.rpm\nshadow-utils-4.0.17-15.el5.x86_64.rpm\nslang-2.0.6-4.el5.x86_64.rpm\nsmartmontools-5.38-2.el5.x86_64.rpm\nsos-1.7-9.49.el5.noarch.rpm\nspecspo-13-1.el5.noarch.rpm\nsqlite-3.3.6-5.x86_64.rpm\nstartup-notification-0.8-4.1.x86_64.rpm\nstrace-4.5.18-5.el5_4.4.x86_64.rpm\nstunnel-4.15-2.el5.1.x86_64.rpm\nsudo-1.7.2p1-6.el5_5.x86_64.rpm\nsvrcore-4.0.4-3.el5.i386.rpm\nsvrcore-4.0.4-3.el5.x86_64.rpm\nsymlinks-1.2-24.2.2.x86_64.rpm\nsysfsutils-2.0.0-6.x86_64.rpm\nsysklogd-1.4.1-46.el5.x86_64.rpm\nsyslinux-3.86-1.el5.rf.x86_64.rpm\nsysstat-7.0.2-3.el5.x86_64.rpm\nsystem-config-network-tui-1.3.99.18-1.el5.noarch.rpm\nsystem-config-securitylevel-tui-1.6.29.1-5.el5.x86_64.rpm\ntalk-0.17-29.2.2.x86_64.rpm\ntar-1.15.1-30.el5.x86_64.rpm\ntcl-8.4.13-4.el5.x86_64.rpm\ntcp_wrappers-7.6-40.7.el5.i386.rpm\ntcp_wrappers-7.6-40.7.el5.x86_64.rpm\ntcpdump-3.9.4-15.el5.x86_64.rpm\ntcsh-6.14-17.el5.x86_64.rpm\ntelnet-0.17-39.el5.x86_64.rpm\ntermcap-5.5-1.20060701.1.noarch.rpm\ntime-1.7-27.2.2.x86_64.rpm\ntix-8.4.0-11.fc6.x86_64.rpm\ntk-8.4.13-5.el5_1.1.x86_64.rpm\ntkinter26-2.6.2-geekymedia1.1.rhel5.x86_64.rpm\ntmpwatch-2.9.7-1.1.el5.2.x86_64.rpm\ntraceroute-2.0.1-5.el5.x86_64.rpm\ntree-1.5.0-4.x86_64.rpm\ntzdata-2010i-1.el5.x86_64.rpm\nudev-095-14.21.el5.x86_64.rpm\nudftools-1.0.0b3-3.el5.rf.x86_64.rpm\nunix2dos-2.2-26.2.3.el5.x86_64.rpm\nunzip-5.52-3.el5.x86_64.rpm\nusbutils-0.71-2.1.x86_64.rpm\nusermode-1.88-3.el5.2.x86_64.rpm\nutil-linux-2.13-0.52.el5_4.1.x86_64.rpm\nvconfig-1.9-3.x86_64.rpm\nvim-common-7.0.109-6.el5.x86_64.rpm\nvim-enhanced-7.0.109-6.el5.x86_64.rpm\nvim-minimal-7.0.109-6.el5.x86_64.rpm\nvixie-cron-4.1-77.el5_4.1.x86_64.rpm\nvmware-update-manager-ga-1.0.0-84689.i386.rpm\nwget-1.11.4-2.el5_4.1.x86_64.rpm\nwhich-2.16-7.x86_64.rpm\nwireless-tools-28-2.el5.i386.rpm\nwireless-tools-28-2.el5.x86_64.rpm\nwords-3.0-9.1.noarch.rpm\nwpa_supplicant-0.5.10-9.el5.x86_64.rpm\nxorg-x11-filesystem-7.1-2.fc6.noarch.rpm\nyp-tools-2.9-1.el5.x86_64.rpm\nypbind-1.19-12.el5.x86_64.rpm\nyum-3.2.22-26.el5.noarch.rpm\nyum-metadata-parser-1.1.2-3.el5.x86_64.rpm\nyum-rhn-plugin-0.5.4-15.el5.noarch.rpm\nyum-security-1.1.16-13.el5.noarch.rpm\nyum-updatesd-0.9-2.el5.noarch.rpm\nyum-utils-1.1.16-13.el5.noarch.rpm\nzip-2.31-2.el5.x86_64.rpm\nzlib-1.2.3-3.i386.rpm\nzlib-1.2.3-3.x86_64.rpm'}



class ServerFunctions:
    def __init__(self, AUTH_KEY):
        self.machine_ip = '0.0.0.0'
        self.machine_id = 0
        self.auth_key = AUTH_KEY
        self.is_authenticated = False

        # Create logger.
        #self.logger = logging.getLogger("secinv")

    def authenticate(self, auth_key):
        '''
        Compare server's auth_key against client's auth_key.
        '''
        if self.auth_key != auth_key:
            print 'failed authentication'
            return False

        print 'ok authentication'
        self.is_authenticated = True
        return True

    def machine(self, ip_dict, system_dict, services_dict, rpms_dict):
        if not self.is_authenticated:
            return False

        # Get the machine IP address as the first ethernet interface.
        for interface in ip_dict.keys():
            if interface[0:3] == 'eth':
                self.machine_ip = ip_dict[interface]['i_ip']
                break

        ## Machine.
        try:
            m_obj = None

            m_objs = Machine.objects.filter(sys_ip=self.machine_ip).all()
            if m_objs:
                m_obj = m_objs[0]
            else:
                # Find machine by hostname if we cannot find by ip address.
                m_objs_by_h = Machine.objects.filter(
                    hostname=system_dict['hostname']).all()

                m_obj = m_objs_by_h[0]

            m_obj.date_scanned = datetime.datetime.now()
            m_diff = []

            if m_obj.sys_ip != self.machine_ip:
                m_obj.sys_ip = self.machine_ip
                m_diff.append('sys_ip')

            if m_obj.hostname != system_dict['hostname']:
                m_obj.hostname = system_dict['hostname']
                m_diff.append('hostname')

            if m_diff:
                m_obj.diff = ','.join(m_diff)
                m_obj.date_modified = datetime.datetime.now()

            m_obj.save()

            self.machine_obj = m_obj
            self.machine_id = self.machine_obj.id
        except IndexError:
            # Add machine if not in table.
            mach_dict = {'sys_ip': self.machine_ip,
                         'hostname': system_dict['hostname'],
                         'ext_ip': '',
                         'date_scanned': datetime.datetime.now()}
            m_new = Machine.objects.create(**mach_dict)
            self.machine_obj = m_new
            self.machine_id = m_new.id


        ## Interfaces.
        for interface in ip_dict.keys():
            if ip_dict[interface]['i_mac'] in ('00:00:00:00',
                                               '00:00:00:00:00:00'):
                ip_dict[interface]['i_mac'] = ''

            # If all fields are empty, then device is inactive -- so do not
            # insert a row.
            if ip_dict[interface]['i_ip'] == '' and \
               ip_dict[interface]['i_mac'] == '' and \
               ip_dict[interface]['i_mask'] == '':
                continue

            # If interface already exists in table, update accordingly.
            try:
                i_object = Interface.objects.filter(machine__id=self.machine_id,
                                                    i_name=interface).latest()

                i_diff = []
                if i_object.i_ip != ip_dict[interface]['i_ip']:
                    i_diff.append('i_ip')

                if i_object.i_mac != ip_dict[interface]['i_mac']:
                    i_diff.append('i_mac')

                if i_object.i_mask != ip_dict[interface]['i_mask']:
                    i_diff.append('i_mask')

                if i_diff:
                    i_dict = {'machine': self.machine_obj,
                              'i_name': interface,
                              'i_ip': ip_dict[interface]['i_ip'],
                              'i_mac': ip_dict[interface]['i_mac'],
                              'i_mask': ip_dict[interface]['i_mask']}
                    i_object = Interface.objects.create(**i_dict)

            except Interface.DoesNotExist:
                print 'interface does not exist'

                i_dict = {'machine': self.machine_obj,
                          'i_name': interface,
                          'i_ip': ip_dict[interface]['i_ip'],
                          'i_mac': ip_dict[interface]['i_mac'],
                          'i_mask': ip_dict[interface]['i_mask']}
                i_object = Interface.objects.create(**i_dict)

        # See if any interfaces have since been deactivated.

        # Get latest interfaces (select by distinct interface name).
        distinct_interfaces = Interface.objects.filter(
            machine__id=self.machine_id).values_list(
            'i_name', flat=True).distinct()
        print 'distinct_interfaces:', distinct_interfaces

        i_diff = diff_list(distinct_interfaces, ip_dict.keys())
        print 'i_diff:', i_diff

        # Update each interface as inactive.
        for i in i_diff['deleted']:
            i_latest = Interface.objects.filter(machine__id=self.machine_id,
                                                i_name=i, active=True).latest()

            i_inactive = Interface.objects.filter(machine__id=self.machine_id,
                                                  i_name=i, active=False).all()

            # Check if interface is already listed as inactive.
            if i_inactive.exists():
                continue

            i_dict = {'machine': self.machine_obj,
                      'i_name': i_latest.i_name,
                      'i_ip': i_latest.i_ip,
                      'i_mac': i_latest.i_mac,
                      'i_mask': i_latest.i_mask,
                      'active': False}
            i_object = Interface.objects.create(**i_dict)


        ## System.
        try:
            sys_object = System.objects.filter(
                machine__id=self.machine_id).latest()

            sys_diff = []

            if sys_object.kernel_rel != system_dict['kernel_rel']:
                sys_diff.append('kernel_rel')

            if sys_object.rh_rel != system_dict['rh_rel']:
                sys_diff.append('rh_rel')

            if sys_object.nfs != system_dict['nfs']:
                sys_diff.append('nfs')

            if sys_diff:
                sys_dict = {'machine': self.machine_obj,
                            'kernel_rel': system_dict['kernel_rel'],
                            'rh_rel': system_dict['rh_rel'],
                            'nfs': system_dict['nfs'],
                            'diff': ','.join(sys_diff)}
                sys_object = System.objects.create(**sys_dict)

        except System.DoesNotExist:
            print 'system does not exist'

            sys_dict = {'machine': self.machine_obj,
                        'kernel_rel': system_dict['kernel_rel'],
                        'rh_rel': system_dict['rh_rel'],
                        'nfs': system_dict['nfs']}
            sys_object = System.objects.create(**sys_dict)


        ## Services.
        procs = services_dict.keys()
        csv_procs = ','.join(procs)
        ports = services_dict.values()
        csv_ports = ','.join(ports)

        try:
            s_object = Services.objects.filter(
                machine__id=self.machine_id).latest()

            s_diff = []
            s_diff_ins_processes = []
            s_diff_del_processes = []
            s_diff_ins_ports = []
            s_diff_del_ports = []

            if s_object.processes != csv_procs:
                old = re.split(',', s_object.processes)
                new = procs

                s1 = set(old)
                s2 = set(new)
                print s1
                print s2

                new_procs = s2.difference(s1)
                del_procs = s1.difference(s2)
                print new_procs
                print del_procs

                s_diff_ins_processes = list(s2.difference(s1))
                s_diff_del_processes = list(s1.difference(s2))
                print s_diff_ins_processes
                print s_diff_del_processes

                s_diff.append('processes')

            if s_object.ports != csv_ports:
                old = re.split(',', s_object.ports)
                new = ports

                s1 = set(old)
                s2 = set(new)

                new_procs = s2.difference(s1)
                del_procs = s1.difference(s2)

                s_diff_ins_ports = list(s2.difference(s1))
                s_diff_del_ports = list(s1.difference(s2))

                s_diff.append('ports')

            if s_diff:
                s_dict = {'machine': self.machine_obj,
                          'processes': csv_procs,
                          'ports': csv_ports,
                          'diff': ','.join(s_diff)}
                s_object = Services.objects.create(**s_dict)

        except Services.DoesNotExist:
            print 'services does not exist'

            s_dict = {'machine': self.machine_obj,
                      'processes': csv_procs,
                      'ports': csv_ports}
            s_object = Services.objects.create(**s_dict)


        ## RPMs.
        try:
            r_object = RPMs.objects.filter(machine__id=self.machine_id).latest()

            r_diff = []
            if r_object.rpms != rpms_dict['unserialized']:
                r_diff.append('rpms')

            if r_diff:
                r_dict = {'machine': self.machine_obj,
                          'rpms': rpms_dict['unserialized']}
                r_object = RPMs.objects.create(**r_dict)

        except RPMs.DoesNotExist:
            print 'RPMs does not exist'

            r_dict = {'machine': self.machine_obj,
                      'rpms': rpms_dict['unserialized']}
            r_object = RPMs.objects.create(**r_dict)

        return True


sf = ServerFunctions('198574282968432567')
getattr(sf, 'authenticate')('198574282968432567')
getattr(sf, 'machine')(ip_dict, system_dict, services_dict, rpms_dict)


#machine_list = Machine.objects.all()
#print machine_list

#interface_list = Interface.objects.all()
#print interface_list

services_list = Services.objects.all()
print services_list

#rpms_list = RPMs.objects.all()
#print rpms_list

'''
distinct_interfaces = Interface.objects.filter(machine__id=1).values_list('i_name', flat=True).distinct()

latest_interfaces = []
for i in distinct_interfaces:
    latest_distinct = Interface.objects.filter(machine__id=1, i_name=i).latest()
    if latest_distinct:
        latest_interfaces.append(latest_distinct)
'''

