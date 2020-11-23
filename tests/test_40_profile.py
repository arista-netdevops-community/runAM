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

def test_010_addProfileTicket():
    # add profile ticket into profile_tickets table
    ticket_filename = os.path.join(test_dir, "data/profile_tickets/fallback.yml")
    ticket_data = runAM.read.yaml_file(ticket_filename)
    profileStore = runAM.ProfileTicketStore(database_name='test_store', directory=os.path.join(project_dir, 'temp'))
    profileStore.drop_table('profile_tickets')
    inserted_docID_list = profileStore.addProfileTicket(ticket_data)
    assert inserted_docID_list == ['1']

def test_020_queryProfileTicket():
    # find a ticket in profile_tickets table
    profileStore = runAM.ProfileTicketStore(database_name='test_store', directory=os.path.join(project_dir, 'temp'))
    ticket_list = profileStore.queryProfileTicket(tags='fallback, port_channel')
    assert ticket_list == [
        {
            "1": {
                "tags": [
                    "fallback",
                    "port_channel",
                    "any description"
                ],
                "fallback": {
                    "mode": "individual",
                    "timeout": 50
                }
            }
        }
    ]

def test_030_deleteProfileTicket():
    # delete a ticket in profile_tickets table
    profileStore = runAM.ProfileTicketStore(database_name='test_store', directory=os.path.join(project_dir, 'temp'))
    deleted_docs = profileStore.deleteProfileTicket(tags='fallback, port_channel')
    assert deleted_docs == ['1']
