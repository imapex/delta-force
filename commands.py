from netmiko import ConnectHandler


def disable_paging(channel):
    """
    set terminal len 0 on ssh session and clear recv buffer
    :param channel: paramiko.channel.Channel
    :return: None
    """
    channel.send("terminal length 0\n")
    # Clear the buffer
    channel.recv(1000)


def run_commands(host_list, user, pw, commands, device_type="cisco_nxos"):
    """
    Executes a list of commands on a switch
    :param host_list: list of IP/hostnames
    :param user: username to login to the switch
    :param pw:  password to login to the switch
    :param commands: list of commands to execute on each device
    :param device_type: netmiko device type
    :return:
    """
    output = "<snapshot>\n"
    for host in host_list:
        print repr(host)
        device = {"device_type": device_type,
                  "ip": host.rstrip(),
                  "username": user,
                  "password": pw,
                  }

        session = ConnectHandler(**device)
        output += '<device host="{}">\n'.format(host)
        output += "\n"

        for command in commands:
            output += '<command cmd="{}">\n'.format(command)
            output += session.send_command(command)
            output += "\n</command>\n"
        output += "\n</device>\n"
    output += "\n</snapshot>\n"
    return output
