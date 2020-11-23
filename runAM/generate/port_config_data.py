import jq
import json
import re
import sys
import glom
import runAM


class GlomDict(dict):

    def assign(self, glom_path, value):
        glom.assign(self, glom_path, value, missing=dict)


class PortConfigGenerator(runAM.db.JSONStore):

    def generatePortConfigData(self):
        """Generate low level data to parse port configuration templates.
        """
        # clean tables
        self.drop_table('server_tickets_expanded')  # this table contains server tickets with all profile data expanded
        self.drop_table('port_config_data')  # this table contains low level data required to parse port configuration templates
        # copy server_tickets table into server_tickets_expanded
        for doc_id, doc in self.table('server_tickets').items():
            self.insert_doc(doc, table_name='server_tickets_expanded')
        # find all profile tags combinations
        profile_list = self.jq(table_name='profile_tickets', query_expression='..|select(.tags?!=null)')
        # find (recursively) path to value in server_tickets_expanded table with profiles defined
        for path in self.jq_path(table_name='server_tickets_expanded', query_expression='..|select(.profiles?!=null)'):
            # get a value for the discovered path
            value_with_profile = self.get_val(path, table_name='server_tickets_expanded')
            for value_tags in value_with_profile['profiles']:
                profile_not_found = True  # if matching profile exists in profile_tickets table. If not raise and error.
                for profile in profile_list:
                    profile_tags = profile['tags']
                    if set(value_tags).issubset(set(profile_tags)):
                        profile_copy = profile.copy()  # to avoid modification of the original profile
                        del profile_copy['tags']  # delete tags from profile copy to avoid merging them with the ticket
                        # merge value with the profile data
                        value_with_profile = runAM.tools.merge_data_objects(value_with_profile, profile_copy)
                        profile_not_found = False
                if profile_not_found:
                    sys.exit(f'ERROR: Not able to find matching profile ticket for {value_tags} in profile_tickets table.')
            del value_with_profile['profiles']  # delete profiles as they are already expended
            self.update_path(path, value_with_profile, table_name='server_tickets_expanded')  # update table with the new value with merged profile data

        # build low level port configuration data
        # > check every server ticket
        for doc_id, server_ticket in self.table('server_tickets_expanded').items():
            server_ports_ticket = dict()

            # > if port-channel is configured and no group defined, generate LACP group number
            lacp_group_number = 0
            lacp_member_ports = list()
            for connection in server_ticket['connections']:
                if 'port_channel' in connection.keys():
                    # if group number is already defined manually in the ticket
                    if 'group_number' in connection['port_channel'].keys():
                        if not lacp_group_number:
                            lacp_group_number = connection['port_channel']['group_number']
                        elif lacp_group_number != connection['port_channel']['group_number']:
                            sys.exit(f'ERROR: statically defined LACP group numbers for {server_ticket["server_id"]} are not matching.')
                    else:
                        lacp_member_ports.append(connection['switch_port'])
            if lacp_member_ports:
                lacp_member_ports.sort()  # sort lacp members to find the lowest port
                lowest_lacp_member_port = lacp_member_ports[0]
                lowest_member_digits = ''.join(
                    re.findall(r'\d+', lowest_lacp_member_port)
                )
                if len(lowest_member_digits) == 1:
                    generated_group_number = int(f'100{lowest_member_digits}')
                elif len(lowest_member_digits) == 2:
                    generated_group_number = int(f'10{lowest_member_digits}')
                elif len(lowest_member_digits) == 3:
                    generated_group_number = int(f'1{lowest_member_digits}')
                else:
                    sys.exit('ERROR: Can not build port-channel name as memer interface name has more than 3 digits.')
                # check there is a conflict with a manually defined number defined for some connections by mistake
                if lacp_group_number:
                    if lacp_group_number != generated_group_number:
                        sys.exit(f'ERROR: LACP group number for {server_ticket["server_id"]} is defined manually, but not for all connections and not matching generated number.')
                lacp_group_number = generated_group_number  # if no error, use generated group number
            # build port-channel name
            port_channel_name = 'Port-Channel ' + str(lacp_group_number)

            # > check every server connection
            for connection in server_ticket['connections']:
                cd = GlomDict()  # cd - short for connection details

                # the switch name the node is connected to
                cd.assign('switch_name', connection['switch_name'])
                # define port description
                if 'description' in connection.keys():
                    description = connection['description']
                else:
                    description = server_ticket['server_id']  # default description is based on server ID
                cd.assign(f'interface.ethernet.{connection["switch_port"]}.description', description)
                # set interface speed
                if 'speed' in connection.keys():
                    speed = connection['speed']
                else:
                    speed = '25gfull'  # default interface speed is 25G
                cd.assign(f'interface.ethernet.{connection["switch_port"]}.speed', speed)
                # set FEC (forward error correction) for the interface if defined
                if 'fec' in connection.keys():
                    cd.assign(f'interface.ethernet.{connection["switch_port"]}.fec', connection['fec'])
                # set switchport configuration if defined
                if 'switchport' in connection.keys():
                    cd.assign(f'interface.ethernet.{connection["switch_port"]}.switchport', connection['switchport'])
                # build port-channel configuration
                if 'port_channel' in connection.keys():
                    cd.assign(f'interface.ethernet.{connection["switch_port"]}.channel.group', lacp_group_number)
                    cd.assign(f'interface.ethernet.{connection["switch_port"]}.channel.mode', connection['port_channel']['mode'])
                    cd.assign(f'interface.port_channel.{port_channel_name}.description', 'to_' + server_ticket["server_id"])
                    cd.assign(f'interface.port_channel.{port_channel_name}.mlag', lacp_group_number)
                    
                    if 'fallback' in connection['port_channel'].keys():
                        cd.assign(f'interface.port_channel.{port_channel_name}.fallback', connection['port_channel']['fallback'])

                    if 'lacp_rate' in connection['port_channel'].keys():
                        cd.assign(f'interface.ethernet.{connection["switch_port"]}.lacp.rate', connection['port_channel']['lacp_rate'])

                    if 'description' in connection['port_channel'].keys():
                        cd.assign(f'interface.port_channel.{port_channel_name}.description', connection['port_channel']['description'])

                    if 'switchport' in connection['port_channel'].keys():
                        cd.assign(f'interface.port_channel.{port_channel_name}.switchport', connection['port_channel']['switchport'])

                server_ports_ticket = runAM.tools.merge_data_objects(server_ports_ticket, cd)

            self.insert_doc(server_ports_ticket, table_name='port_config_data')
        