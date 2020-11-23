#!/usr/bin/env python3
import jq
import json
import sys
import os
from runAM.tools.change_nested_value import change_nested_value

class JSONStore:

    def __init__(self, database_name = 'db', directory='database'):
        self.db_filename = os.path.join(directory, f'{database_name}.json')

        # try to load the file if exists
        try:
            with open(self.db_filename, 'r') as db_file:
                self.db = json.load(db_file)
        except Exception as _:
            # if nothing was opened, init as empty dictionary
            self.db = dict()

    def write(self):
        """Save data to the file on exit.

        Returns:
            True: return True after execution for assert tests
        """
        with open(self.db_filename, 'w') as db_file:
            json.dump(self.db, db_file, indent=4)
        return True

    def drop_table(self, table_name='_default'):
        """Init existing or non-existing table in the database with an empty dictionary.

        Args:
            table_name (str, optional): Name of the table to init. Defaults to '_default'.

        Returns:
            dict: Empty table - {}. 
        """
        self.db.update({table_name: dict()})  # init table with empty dict
        return self.table(table_name)

    def insert_doc(self, data, doc_id='', table_name='_default'):
        """Insert a document into the database.

        Args:
            data (any): Data to insert as a document in the table.
            doc_id (str, optional): Document ID to set manually. If not specified, new doc ID will be generated automatically.
            table_name (str, optional): Table name to insert the document. Defaults to '_default'.

        Returns:
            str: New document ID.
        """
        existing_doc_ids = [int(id) for id in self.table(table_name).keys() if str(id).isdecimal()]
        if doc_id:  # if doc_id was defined manually
            new_doc_id = doc_id
            if int(new_doc_id) in existing_doc_ids:
                sys.exit(f'ERROR: docID {doc_id} is already present in the table {table_name}')
        else:
            try:
                new_doc_id = [id for id in range(min(existing_doc_ids), max(existing_doc_ids)+2) if id not in existing_doc_ids][0]  # take lowest missing docID or next after max
            except ValueError:  # ValueError: min() arg is an empty sequence
                new_doc_id = 1  # if table is empty
        self.table(table_name).update({
            str(new_doc_id): data
        })
        return str(new_doc_id)

    def table(self, table_name):
        """Return table content.

        Args:
            table_name (str): The name of the table to be returned.

        Returns:
            dict: The table content as doc_id: doc_value dictionary.
        """
        if table_name not in self.db.keys():
            self.db.update({table_name: dict()})  # add empty table if not present
        return self.db[table_name]

    def get_table_names(self):
        """Get the list of all table names in the database.

        Returns:
            list: List of table names.
        """
        return list(self.db.keys())

    def jq(self, table_name='_default', query_expression=''):
        """Find a value in a table using jq: https://stedolan.github.io/jq/

        Args:
            table_name (str, optional): The name of the table to query. Defaults to '_default'.
            query_expression (str, optional): jq query expression. Defaults to ''.

        Returns:
            list: List of matched values.
        """
        res = jq.compile(query_expression).input(self.table(table_name)).all()
        return res

    def jq_path(self, table_name='_default', query_expression='', return_glom_spec=False):
        """Find a path to a matched value in a table using jq: https://stedolan.github.io/jq/

        Args:
            table_name (str, optional): The name of the table to query. Defaults to '_default'.
            query_expression (str, optional): jq query expression. Defaults to ''.
            return_glom_spec (bool, optional): Return glom (https://glom.readthedocs.io/) spec tring instead of a list. Defaults to False.

        Returns:
            list: List of pathes to every matched value. Every path is a list of keys/indexes starting at table root.
        """
        res = jq.compile('path(%s)' % query_expression).input(self.table(table_name)).all()
        if return_glom_spec:
            path_list = list()
            for a_path in res:
                glom_spec = ''
                for k in a_path:
                    glom_spec += f'.{k}'
                path_list.append(glom_spec.lstrip('.'))
        else:
            path_list = res
        return path_list

    def get_val(self, path_list, table_name='_default'):
        """Get the value that corresponds to the path calculated by jq.

        Args:
            path_list (list): List of pathes to every value to be returned. 
            table_name (str, optional): The name of the table to where matched values must be located. Defaults to '_default'.

        Returns:
            list: List of values corresponding to to specified pathes.
        """
        data = self.table(table_name)
        for element in path_list:
            data = data[element]
        return data

    def delete_doc(self, table_name='_default', doc_id=''):
        """Delete a document with the specified doc_id from the table.

        Args:
            table_name (str, optional): The name of the table to delete the document from. Defaults to '_default'.
            doc_id (str, optional): The document id to be deleted. Defaults to ''.

        Returns:
            list: List of document IDs to be deleted.
        """
        deleted_docs = list()
        if doc_id:
            del self.table(table_name)[doc_id]
            deleted_docs.append(doc_id)
        return deleted_docs

    def update_path(self, path, data=dict(), table_name='_default'):
        """Update the value corresponding to the specified path.

        Args:
            path (list): list of keys/indexes starting at table root
            data (any, optional): The new value to be set. Defaults to dict().
            table_name (str, optional): The name of the table where the value must be changed. Defaults to '_default'.

        Returns:
            dict: Updated table content.
        """
        # update value in a table based on specified path
        self.table(table_name).update(
            change_nested_value(path, self.table(table_name), data)
        )
        return self.table(table_name)
