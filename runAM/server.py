import runAM
import sys

class ServerTicketStore(runAM.generate.PortConfigGenerator):
    
    def addSingleServerTicket(self, ticket_data):
        """Add single ticket to server_tickets table.

        Args:
            ticket_data (dict): Server ticket data to add.
                                Verification:
                                - server_id must be unique
                                - switch_name/switch_port combination must not be in use

        Returns:
            str: The inserted document ID.
        """
        server_id = ticket_data['server_id']
        # check if server is already present
        for _, doc in self.table('server_tickets').items():
            if doc['server_id'] == server_id:
                sys.exit(f'ERROR: server {server_id} is already provisioned.')
        # check if port-leaf combination is already in use
        # TODO: Verify breakout vs parent port conflicts. For example: Ethernet1 and Ethernet1/1
        for ticket_connection in ticket_data['connections']:
            ticket_switch_name = ticket_connection['switch_name']
            ticket_switch_port = ticket_connection['switch_port']
            for _, doc in self.table('server_tickets').items():
                for existing_connection in doc['connections']:
                    if (ticket_switch_name == existing_connection['switch_name']) and (ticket_switch_port == existing_connection['switch_port']):
                        sys.exit(f'ERROR: Can not add {server_id}. Port {ticket_switch_port} on {ticket_switch_name} is already in use.')
        # if no verification failed, insert the ticket
        inserted_doc_id = self.insert_doc(ticket_data, table_name='server_tickets')
        return inserted_doc_id

    def addServerTicket(self, in_data):
        """Insert single or multiple server tikets into the server_tickets table.

        Args:
            in_data (dict or list): One or multiple tickets to insert.

        Returns:
            list: List of inserted document IDs.
        """
        doc_number_list = list()
        # for example, multi-doc yaml
        if isinstance(in_data, list):
            for ticket in in_data:
                doc_number = self.addSingleServerTicket(ticket)
                if not doc_number:
                    sys.exit('ERROR: Failed to insert the ticket into the datababse.')
                else:
                    doc_number_list.append(doc_number)
        # for example, single-doc yaml
        elif isinstance(in_data, dict):
            doc_number = self.addSingleServerTicket(in_data)
            if not doc_number:
                sys.exit('ERROR: Failed to insert the ticket into the datababse.')
            else:
                doc_number_list.append(doc_number)
        else:
            sys.exit('ERROR: Input data must be a dictionary or a list.')
        self.generatePortConfigData()  # generate low level port config data after inserting a new server
        self.write()
        return doc_number_list

    def queryServerTicket(self, server_id):
        """Find server ticket in server_tickets table, that is matching server_id.

        Args:
            server_id (str): Server ID to find in server_tickets table.

        Returns:
            list: List of matching servers in the format [{doc_id: doc}, ...]
        """
        server_match_list = list()
        for doc_id, doc in self.table('server_tickets').items():
            if doc['server_id'] == server_id:
                server_match_list.append({doc_id: doc})
        return server_match_list

    def deleteServerTicket(self, server_id):
        """Delete server ticket in server_tickets table, that is matching server_id.

        Args:
            server_id (str): Server ID to delete from server_tickets table.

        Returns:
            list: List of deleted document IDs.
        """
        deleted_doc_list = list()
        for doc_id, doc in self.table('server_tickets').copy().items():  # iterate over table copy to avoid changing dict in the process
            if doc['server_id'] == server_id:
                self.delete_doc(table_name='server_tickets', doc_id=doc_id)
                deleted_doc_list.append(doc_id)
        self.generatePortConfigData()  # generate low level port config data after inserting a new server
        self.write()
        return deleted_doc_list
