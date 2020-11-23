import pytest
import os
import sys
import runAM
import json

# insert project directory to $PATH for imports to work
test_file = os.path.realpath(__file__)
test_dir = os.path.dirname(test_file)
project_dir = os.path.dirname(test_dir)
sys.path.append(project_dir)

def test_000_can_assert_true():
    # before any test verify if PyTest is working and can assert True
    assert True

def test_010_addServerTicket():
    # add server ticket into server_tickets table
    inserted_docID_list = list()
    # add profile tickets first, as they are recovered to run self.generatePortConfigData()
    profileStore = runAM.ProfileTicketStore(database_name='test_store', directory=os.path.join(project_dir, 'temp'))
    profileStore.drop_table('profile_tickets')
    ticket_filename = os.path.join(test_dir, "data/profile_tickets/fallback.yml")
    ticket_data = runAM.read.yaml_file(ticket_filename)
    profileStore.addProfileTicket(ticket_data)
    # add server tickets
    serverStore = runAM.ServerTicketStore(database_name='test_store', directory=os.path.join(project_dir, 'temp'))
    serverStore.drop_table('server_tickets')
    ticket_filename_list = ['test_server1.yml', 'test_server2.yml', 'test_server4.yml']
    for ticket_filename in ticket_filename_list:
        fullpath = os.path.join(test_dir, f"data/server_tickets/{ticket_filename}")
        ticket_data = runAM.read.yaml_file(fullpath)
        docIDs_just_inserted = serverStore.addServerTicket(ticket_data)
        for docID in docIDs_just_inserted:
            inserted_docID_list.append(docID)
    assert inserted_docID_list == ['1', '2', '3']

def test_015_addServerTicket_failed(capsys):
    # confirm that ticket with a duplicate switch_name/switch_port combination can not be added
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        inserted_docID_list = list()
        serverStore = runAM.ServerTicketStore(database_name='test_store', directory=os.path.join(project_dir, 'temp'))
        # add server ticket into server_tickets table
        ticket_filename_list = ['test_server3.yml']
        for ticket_filename in ticket_filename_list:
            fullpath = os.path.join(test_dir, f"data/server_tickets/{ticket_filename}")
            ticket_data = runAM.read.yaml_file(fullpath)
            docIDs_just_inserted = serverStore.addServerTicket(ticket_data)
            for docID in docIDs_just_inserted:
                inserted_docID_list.append(docID)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 'ERROR: Can not add test_server3. Port Ethernet1/1 on LEAF1B is already in use.'

def test_020_queryServerTicket():
    # find a server with specific ID in the server_tickets table
    serverStore = runAM.ServerTicketStore(database_name='test_store', directory=os.path.join(project_dir, 'temp'))
    server_list = serverStore.queryServerTicket(server_id='test_server1')
    assert server_list == [{
        "1": {
            "server_id": "test_server1",
            "notes": [
                "add ticket number",
                "or any other notes here"
            ],
            "connections": [
                {
                    "switch_name": "LEAF1A",
                    "switch_port": "Ethernet1/1",
                    "port_channel": {
                        "profiles": [
                            [
                                "fallback",
                                "port_channel"
                            ]
                        ],
                        "mode": "active"
                    },
                    "switchport": {
                        "mode": "trunk",
                        "vlan": "1, 5-55"
                    }
                },
                {
                    "switch_name": "LEAF1B",
                    "switch_port": "Ethernet1/1",
                    "port_channel": {
                        "profiles": [
                            [
                                "fallback",
                                "port_channel"
                            ]
                        ],
                        "mode": "active"
                    },
                    "switchport": {
                        "mode": "trunk",
                        "vlan": "1, 5-55"
                    }
                }
            ]
        }
    }]

def test_030_deleteServerTicket():
    # delete a server with specific ID in from server_tickets table
    serverStore = runAM.ServerTicketStore(database_name='test_store', directory=os.path.join(project_dir, 'temp'))
    deleted_docs = serverStore.deleteServerTicket(server_id='test_server1')
    assert deleted_docs == ['1']
