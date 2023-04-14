import os.path
import os
import re
import subprocess
import urllib.request
import ssl
import urllib.error
import time


lb=bool()
proxy=''
proxy_type = ''
os_upgrade_urls = ['http://apt.thousandeyes.com', 'http://changelogs.ubuntu.com', 'http://archive.canonical.com', 'https://changelogs.ubuntu.com', 'https://apt.thousandeyes.com']
reg_url='https://registry.agt.thousandeyes.com'
sc1_url='https://sc1.thousandeyes.com'
c1_url='https://c1.thousandeyes.com'
data_url='https://data1.agt.thousandeyes.com'
all_urls=[reg_url, sc1_url, c1_url, data_url]
yum_path = '/etc/yum.repos.d/thousandeyes.repo'
apt_path = '/etc/apt/sources.list.d/thousandeyes.list'
os_info=[]
yum_config_rh8=['[thousandeyes]', 'name=ThousandEyes', 'baseurl=https://yum.thousandeyes.com/RHEL/8/x86_64/', 'gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-thousandeyes', 'gpgcheck=1']
yum_config_rh7=['[thousandeyes]', 'name=ThousandEyes', 'baseurl=https://yum.thousandeyes.com/RHEL/7/x86_64/', 'gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-thousandeyes', 'gpgcheck=1']
apt_config_file="deb https://apt.thousandeyes.com focal main"
os_release_path = '/etc/os-release'
yum_gpg_key=""""-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v1.4.11 (GNU/Linux)

mQENBFApO8oBCACxHESumhIcqUTvpIA+q9yIWQQL2nE1twF1T92xIJ9kgOF/5ali
iEqtNm0Vm2lpZy/LBcTG/UJY5rsKZVVWaepzXsNABeqzEE8t1CMGJ3hqtaZu59nd
VglzwuNuNL+qTjtgX3taPQrO9SQNwMq7lpQeTgBKAM8PjjKMdjezHl2rdtEdG2Km
VtN9qYDmb4ysCwq+ifCwOsZ4AM97r1M1+KwjNIa9EqA86qBixp2WqxaZ0ba4S3TG
wxwEa9Zcm+OXYKcU3TBug+S1OMp14E3PlfSCuS1T7xvbV0KgQRSOsMgPYQLcvw8u
r/uyONvdrx2+/oKrnd/ePZu2ha83msqOR+3vABEBAAG0KVRob3VzYW5kRXllcyA8
YnVpbGR1c2VyQHRob3VzYW5kZXllcy5jb20+iQE4BBMBAgAiBQJQKTvKAhsDBgsJ
CAcDAgYVCAIJCgsEFgIDAQIeAQIXgAAKCRDJmhX1vnGJAKdFB/44WXjZvtirSNzn
Z9vDdxk/zXiWCyR/19znf+piIYCbRBqtoVGRxsxMS0FFHZZ4W6SlieklWJX3WShh
/17EaxC596Aegp4MuwTTQ3hMdEtyB1hDd1e1XQUQULaW/0+4u+dD9n6pHYnKF4Zx
DOQhJ5uXgKTaGZ5Z01JG92R9FxQJMre4j2N4F+EYd6pR9Cr2eBk5CVdnvw8njSak
PhmtmIjhf9faCsWf+mJGQuYggSKk8DJcobIjT3TqLoUlRYwhre1cnB/0mGTph/P1
xFCSpCMGU51jwpyUy1t2bHYeSVAba4PNqOOlITwRfDkKQxB9frI8ycGyx2S+eKFD
Qty56ztU
=p3tN
-----END PGP PUBLIC KEY BLOCK-----"""

#Opens file for reading and check for regex NAME and VERSION which are added to os_version list
def read_os_version(file, *args):
    with open(file) as f:
        for line in f:
            if re.search('NAME', line) and line.startswith('NAME'):
                line = line[6:-2]
                os_info.append(line.strip())
            elif re.search('VERSION_ID', line) and line.startswith('VERSION_ID'):
                line=line[12:-2]
                os_info.append(line.strip())
        f.close()

def check_repo(os_name):
    # Use a breakpoint in the code line below to debug your script.
    if os_name == 'Red Hat Enterprise Linux':
        yum_conf=os.path.isfile(yum_path)
        os_version=os_info[1]
        if not yum_conf:
            print("***File {} doesn't exist. Creating repo file...***".format(yum_path))
            if os_version.startswith('7'):
                print("***Detected OS version {}***".format(os_version))
                with open(yum_path, "w") as yum_conf_write:
                    for yum_item in yum_config_rh7:
                        yum_conf_write.write(yum_item)
                        yum_conf_write.write("\n")
                    if proxy_use=='y':
                        yum_conf_write.write('proxy="{}://{}"'.format(proxy_type, proxy))
                        yum_conf_write.write("\n")
                        yum_auth = input('***Would you like to configure authentication for proxy?(y/n)***\n')
                        if yum_auth =='y':
                            proxy_user = input('***Add proxy username.***\n')
                            yum_conf_write.write('proxy_username="{}"'.format(proxy_user))
                            yum_conf_write.write("\n")
                            proxy_passwd = input('***Add proxy password.***\n')
                            yum_conf_write.write('proxy_username="{}"'.format(proxy_passwd))
                            yum_conf_write.write("\n")
                yum_conf_write.close()
            elif os_version.startswith('8'):
                print("***Detected OS version {}***".format(os_version))
                with open(yum_path, "w") as yum_conf_write:
                    for yum_item in yum_config_rh8:
                        yum_conf_write.write(yum_item)
                        yum_conf_write.write("\n")
                    if proxy_use == 'y':
                        yum_conf_write.write('proxy="{}://{}"'.format(proxy_type, proxy))
                        yum_conf_write.write("\n")
                yum_conf_write.close()
        else:
            print("***File {} exist. Skipping creating repo file.***".format(yum_path))
            with open(yum_path, 'r') as read_proxy:
                for line in read_proxy:
                    if re.search('proxy=', line):
                        print(line)
                    if re.search('proxy_user', line):
                        print(line)
                    if re.search('proxy_auth', line):
                        print(line)

    elif os_name == 'Ubuntu':
        apt_conf=os.path.isfile(apt_path)
        if not apt_conf:
            print("File {} doesn't exist. Creating repo file.".format(apt_path))
            with open(apt_path, "w") as apt_conf_write:
                apt_conf_write.write(apt_config_file)
        else:
            print("***File {} exist. Skipping creating repo file.***".format(apt_path))
    else:
        print('OS version is not RHAT or Ubuntu!')


def check_gpg_key():
    print('GPG START')
    if os_info[0] == 'Red Hat Enterprise Linux':
        yum_gpg_path = '/etc/pki/rpm-gpg/RPM-GPG-KEY-thousandeyes'
        yum_gpg_file = os.path.isfile(yum_gpg_path)
        rpm_list_cmd=("rpm", "-q", "gpg-pubkey", "--qf", "'%{NAME}-%{VERSION}-%{RELEASE}\t%{SUMMARY}\n'")
        rpm_key_list = subprocess.run(rpm_list_cmd, stdout=subprocess.PIPE)
        yum_key_in_rpm = re.search('ThousandEyes',str(rpm_key_list))
        if not yum_gpg_file or not yum_key_in_rpm:
            print("***File {} doesn't exist.")
            create_yum_repo = input("***Would you like to download and import gpg key to rpm?(y/n)***\n").lower()
            if create_yum_repo == 'y':
                print("***File {} doesn't exist. Creating key file and importing...***".format(yum_gpg_path))
                with open(yum_gpg_path, 'w') as yum_gpg_write:
                    yum_gpg_write.write(yum_gpg_key)
                    yum_import_cmd = ("sudo", "rpm", "--import", "/etc/pki/rpm-gpg/RPM-GPG-KEY-thousandeyes")
                    subprocess.run(yum_import_cmd, stdout=subprocess.PIPE )
                    print("***GPG IMPORT LOGS***")
                    print("***RPM import requires sudo permissions.***")
                    print("***While GPG key is set to 1 and GPG path is added to repo config, this should work.***")
                    print("***Run following commands to import and validate yum key!***")
                    print("sudo rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-thousandeyes")
                    print("rpm -q gpg-pubkey --qf '%{NAME}-%{VERSION}-%{RELEASE}\t%{SUMMARY}\n'")
            else:
                print('***GPG key file was NOT found or added to RPM.***')

    elif os_info[0] == 'Ubuntu':
        list_apt_keys=subprocess.run(["apt-key", "list"], stdout=subprocess.PIPE)
        if re.search('ThousandEyes', str(list_apt_keys.stdout)):
            print('***Found key in apt-key list. Skipping adding file. Do additional check manually.***')

        else:
            print("***Key is not in apt-key list. Creating key file and importing...***")
            create_apt_repo=input("***Would you like to download and import gpg key to apt?(y/n)***\n").lower()
            if create_apt_repo=='y':
                subprocess.run(["curl", "https://apt.thousandeyes.com/thousandeyes-apt-key.pub", "--output", "apt_key.pub"])
                time.sleep(3)
                subprocess.run(["apt-key", "add", "apt_key.pub"])
            else:
                print('***GPG key  was NOT found or added to APT.***')
    else:
        print('***Skipping check, unsupported OS.***')


def test_connectivity(url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    if proxy:
        try:
            req=urllib.request.Request(url)
            req.set_proxy(proxy,'http')
            url_response = urllib.request.urlopen(req, context=ctx)
            return url_response.getcode()
        except urllib.error.HTTPError as err:
            return err.code
    else:
        try:
            url_response=urllib.request.urlopen(url, context=ctx)
            return url_response.getcode()
        except urllib.error.HTTPError as err:
            return err.code
if __name__ == '__main__':
    while not lb:
        proxy_use = input('***Would you like to use proxy?***\n').lower()
        if proxy_use == 'y':
            proxy = input('***Add proxy hostname:port if you use proxy, example (my.proxy.url:80).***\n').lower()
            proxy_type = input('***Would you like to add HTTP or HTTPS proxy?(http/https)***\n').lower()
            lb=True
        elif proxy_use=='n':
            lb=True
        else:
            continue
    read_os_version(os_release_path)
    check_repo(os_info[0])
    check_gpg_key()
    for item in all_urls:
        te_response = test_connectivity(item)
        print('response:', te_response)
        if te_response == 404 or te_response == 401:
            print('***Connectivity to {} is OK!***'.format(item))
            print('***HTTP Response code:', te_response, '***')
        else:
            print('Connectivity to {} has FAILED!'.format(item))
            print('***HTTP Response code:', te_response, '***')

    for upgrade_item in os_upgrade_urls:
        apt_response = test_connectivity(upgrade_item)
        if apt_response == 301 or apt_response == 200:
            print('***Connectivity to {} is OK!***'.format(upgrade_item))
            print('***HTTP Response code:', apt_response, '***')
        else:
            print('Connectivity to {} has FAILED!'.format(upgrade_item))
            print('***HTTP Response code:', apt_response, '***')


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
