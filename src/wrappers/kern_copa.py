#!/usr/bin/env python


import arg_parser
import context
from helpers import kernel_ctl
import sys
from subprocess import call, check_output, check_call



def setup_kern_copa():
    cc_list = check_output('sysctl net.ipv4.tcp_allowed_congestion_control',
                           shell=True)
    cc_list = cc_list.split('=')[-1].split()
    
    if 'kern_copa' not in cc_list:
        # enable kern_copa kernel module
        sh_cmd = 'make --directory ~/kern-mod/'
        if call(sh_cmd, shell=True) != 0:
            sys.exit('Error: kern_copa build failed')

        sh_cmd = 'sudo insmod ~/kern-mod/kern_copa.ko'
        if call(sh_cmd, shell=True) != 0:
            sys.exit('Error: kern_copa insmod failed')

        # add kern_copa to kernel-allowed congestion control list
        kernel_ctl.enable_congestion_control('kern_copa')

    # check if qdisc is fq
    kernel_ctl.check_qdisc('fq')


def main():
    args = arg_parser.receiver_first()

    if args.option == 'deps':
        print 'iperf'
        return

    if args.option == 'setup_after_reboot':
        setup_kern_copa()
        return

    if args.option == 'receiver':
        cmd = ['iperf', '-Z', 'kern_copa', '-s', '-p', args.port]
        check_call(cmd)
        return

    if args.option == 'sender':
        cmd = ['iperf', '-Z', 'kern_copa', '-c', args.ip, '-p', args.port,
               '-t', '75']
        check_call(cmd)
        return


if __name__ == '__main__':
    main()
