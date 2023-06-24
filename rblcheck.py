#!/usr/bin/python3
import argparse, socket, subprocess

def reverse_ip(ip_address):
    return ".".join(ip_address.split(".")[::-1])

def get_resolver_ip():
    with open('/etc/resolv.conf', 'r') as resolv_file:
        for line in resolv_file:
            if line.startswith('nameserver'):
                resolver_ip = line.split()[1]
                return resolver_ip

def main():
    parser = argparse.ArgumentParser(description='Check if an IP address is listed on an RBL.')
    parser.add_argument('ip_address', metavar='IP', type=str, nargs='?',
                        help='IP address to check')
    parser.add_argument('rbl', metavar='RBL', type=str, nargs='?',
                        choices=['bl.spamcop.net', 'zen.spamhaus.org'],
                        help='RBL to check')
    parser.add_argument('resolver', metavar='RESOLVER', type=str, nargs='?',
                        help='DNS resolver to use')
    args = parser.parse_args()

    if not args.ip_address:
        ip_address = input("Please enter IP address to check: ")
    else:
        ip_address = args.ip_address

    rip = reverse_ip(ip_address)

    if not args.rbl:
        rbl_options = {'1': 'bl.spamcop.net', '2': 'zen.spamhaus.org', '3': 'custom'}
        for key, value in rbl_options.items():
            print(key,":", value)
        option = input('Please select RBL: ')
        if(option=='3'):
            rbl=input('Please enter custom rbl address: ')
        else:        
            rbl = rbl_options.get(option)
        if not rbl:
            print('Invalid option selected.')
            return
    else:
        rbl = args.rbl

    if not args.resolver:
        resolver = get_resolver_ip()
        resolver_options = {'1': '8.8.8.8', '2': '4.2.2.4', '3': '1.1.1.1', '4': 'custom'}
        for key, value in resolver_options.items():
            print(key,":", value)
        option = input(f'Please select resolver (Default = System resolver: {resolver}): ')
        if(option=='4'):
            resolver=input('Please input the custom resolver IP: ')
        else:
            if option:
                resolver = resolver_options.get(option)
        if not resolver:
            print('System resolver selected.')
    else:
        resolver = args.resolver

    cmd = f"dig @{resolver} -t a +short {rip}.{rbl}"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0 and len(result.stdout) > 0:
        print(f"\033[31mIP address {ip_address} is listed on {rbl} based on resolver {resolver}\033[0m")
    else:
        print(f"\033[32mIP {ip_address} is not listed on {rbl} based on resolver {resolver}\033[0m")

if __name__ == '__main__':
    main()