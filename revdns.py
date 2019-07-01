import subprocess
import sys

# This program is invoked like so (example):
# python revdns.py 146.112.62.105
# It needs to be deployed together with bash script get_cert_cn.sh
#
# It is intended to make a reverse check on a ip number (tested only wih ipv4)
# We use the host command to attempt a reverse dns check and moreover we try to pull CN info from a https certificate on the endpoint
# That way we can more often than not find the actual domain/organization of a IP even in cases when it is "hidden" by a content delivery network (amazonws, akamai, etc...)
# Use cases: traffic control and traffic analysis (like in a log server or in automated routines for blocking or alerting).

host_timeout = "4" # timeout in seconds for the host command
ssl_timeout= "6" # timeout in seconds for the openssl command

ipv4 = sys.argv[1];


# Invoking and parsing host is tested with host command version 9.10.3-P4-Ubuntu
#
# The output of the host command shall have the following format in order for parsing to work:
#
# X.X.X.X.in-addr.arpa domain name pointer www.acme.topdomain.
# X.X.X.X.in-addr.arpa domain name pointer acme.topdomain.
#
# (yes there may be more than one row, more than one name in the response)

host_name=""
try:
    host_output = subprocess.check_output(["host","-W "+host_timeout,ipv4])
    raw_host_array=host_output.split("name pointer ")
    raw_host_lenght = len(raw_host_array)
    for i in range(1,raw_host_lenght): # in fist item (0th) there is never a host name
        if i>1:
            host_name += " "
        host_name += ((raw_host_array[i]).split(".\n"))[0] # if there are more than one they  are separated by punctuation and newline
except:
    host_name="host-not-resolved"
print(host_name)


# Invoking and parsing openssl to pull cert info
# See the bash script for what version of openssl it is verified with

cert_cn=""
try:
    ssl_output = subprocess.check_output(["./get_cert_cn.sh",ipv4,ssl_timeout]);
    cert_cn = ""
    if "CN=" in ssl_output:
        cert_cn = (ssl_output.split("CN=")[1]).rstrip()
        if "/" in cert_cn:
            cert_cn = cert_cn.split("/")[0].strip()  # the separator for additional trailing fields in the cert info is "/"
except:
    cert_cn = "cert-cn-not-resolved"

print(cert_cn)

# Alternatively to using openssl we could implement this by pulling cert info with curl:
# curl --insecure --head -v https://
# more suggestions: https://serverfault.com/questions/661978/displaying-a-remote-ssl-certificate-details-using-cli-tools
# curl --insecure -v https://www.google.com 2>&1 | awk 'BEGIN { cert=0 } /^\* SSL connection/ { cert=1 } /^\*/ { if (cert) print }'
#

