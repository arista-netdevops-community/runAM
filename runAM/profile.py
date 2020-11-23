import runAM
import sys

class ProfileTicketStore(runAM.db.JSONStore):

    def addSingleProfileTicket(self, ticket_data):
        """Add single ticket to profile_tickets table.

        Args:
            ticket_data (dict): Profile ticket data to add.
                                Verification:
                                - profile tags must be unique

        Returns:
            str: The inserted document ID.
        """
        inserted_doc_id = 0
        tag_list = ticket_data['tags']
        for _, doc in self.table('profile_tickets').items():
            if set(doc['tags']).issubset(tag_list):
                sys.exit(f'ERROR: A profile must have unique tags.')
        inserted_doc_id = self.insert_doc(ticket_data, table_name='profile_tickets')
        return inserted_doc_id

    def addProfileTicket(self, in_data):
        """Insert single or multiple profile tikets into the profile_tickets table.

        Args:
            in_data (dict or list): One or multiple tickets to insert.

        Returns:
            list: List of inserted document IDs.
        """
        doc_number_list = list()
        # for example, multi-doc yaml
        if isinstance(in_data, list):
            for ticket in in_data:
                doc_number = self.addSingleProfileTicket(ticket)
                if not doc_number:
                    sys.exit('ERROR: Failed to insert the ticket into the datababse.')
                else:
                    doc_number_list.append(doc_number)
        # for example, single-doc yaml
        elif isinstance(in_data, dict):
            doc_number = self.addSingleProfileTicket(in_data)
            if not doc_number:
                sys.exit('ERROR: Failed to insert the ticket into the datababse.')
            else:
                doc_number_list.append(doc_number)
        else:
            sys.exit('ERROR: Input data must be a dictionary or a list.')
        self.write()
        return doc_number_list

    def queryProfileTicket(self, tags):
        """Find profile tickets in profile_tickets table, that are matching specified tag list.

        Args:
            tags (str): List of tags to find matching profiles. Separated by ','.

        Returns:
            list: List of matching profiles in the format [{doc_id: doc}, ...]
        """
        tag_list = [tag.strip() for tag in tags.split(',')]
        profile_match_list = list()
        for doc_id, doc in self.table('profile_tickets').items():
            if set(tag_list).issubset(doc['tags']):
                profile_match_list.append({doc_id: doc})
        return profile_match_list

    def deleteProfileTicket(self, tags):
        """Delete profile tickets in profile_tickets table, that are matching specified tag list.

        Args:
            tags (str): List of tags to find matching profiles. Separated by ','.

        Returns:
            list: List of deleted document IDs.
        """
        tag_list = [tag.strip() for tag in tags.split(',')]
        deleted_doc_list = list()
        for doc_id, doc in self.table('profile_tickets').copy().items():  # iterate over table copy to avoid changing dict in the process
            if set(tag_list).issubset(doc['tags']):
                self.delete_doc(table_name='profile_tickets', doc_id=doc_id)
                deleted_doc_list.append(doc_id)
        self.write()
        return deleted_doc_list
