from utils.differs import HtmlDiffer


def get_command_table(before_xml, after_xml, show_command):
    """
    Returns an HTML table of the differences between a specific command on all devices

    :param before_xml:
    :param after_xml:
    :param show_command:
    :return:
    """
    xpath_query = "//command[@cmd='{}']/text()".format(show_command)
    before_command_lines = list()
    after_command_lines = list()
    for device in before_xml.xpath(xpath_query):
        print device.split('\n')
        before_command_lines = before_command_lines + device.split('\n')
    for device in after_xml.xpath(xpath_query):
        after_command_lines = after_command_lines + device.split('\n')
    diff = HtmlDiffer(wrapcolumn=120)
    table = diff.make_table(before_command_lines, after_command_lines)
    return table


def get_device_table(before_xml, after_xml, show_device):
    """
    Generates an HTML table of the differences between all commands on a specific device
    :param before_xml:
    :param after_xml:
    :param show_device:
    :return:
    """
    xpath_query = "//device[@host='{}']/command/text()".format(show_device)
    before_command_lines = list()
    after_command_lines = list()
    for command in before_xml.xpath(xpath_query):
        before_command_lines = before_command_lines + command.split('\n')
    for command in after_xml.xpath(xpath_query):
        after_command_lines = after_command_lines + command.split('\n')
    diff = HtmlDiffer(wrapcolumn=120)
    table = diff.make_table(before_command_lines, after_command_lines)
    return table
