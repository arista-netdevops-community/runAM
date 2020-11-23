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

bookstore_json = {"store": {
    "book": [
        {
            "category": "reference",
            "author": "Nigel Rees",
            "title": "Sayings of the Century",
            "price": 8.95,
        },
        {
            "category": "fiction",
            "author": "Evelyn Waugh",
            "title": "Sword of Honour",
            "price": 12.99,
        },
        {
            "category": "fiction",
            "author": "Herman Melville",
            "title": "Moby Dick",
            "isbn": "0-553-21311-3",
            "price": 8.99,
            "tags": ["adventure", "fiction", "1851"]
        },
        {
            "category": "fiction",
            "author": "J. R. R. Tolkien",
            "title": "The Lord of the Rings",
            "isbn": "0-395-19395-8",
            "price": 22.99,
            "tags": ["fantasy", "fiction", "1954"]
        }
    ],
    "bicycle": [
        {
            "color": "red",
            "price": 19.95
        }
    ]
  }
}

def test_000_can_assert_true():
    # before any test verify if PyTest is working and can assert True
    assert True

def test_010_store_open_store_write():
    # init store and confirm that we have write access
    store = runAM.db.JSONStore(database_name='test_store', directory=os.path.join(project_dir, 'temp'))
    assert store.write()

def test_020_drop_table():
    # drop all tables in the document
    all_tables_clean = True
    store = runAM.db.JSONStore(database_name='test_store', directory=os.path.join(project_dir, 'temp'))
    for table_name in store.db.keys():
        table_content = store.drop_table(table_name)
        if table_content:  # if table is not empty, change the flag to false
            all_tables_clean = False
    store.write()
    assert all_tables_clean

def test_030_insert_documents():
    # insert documents into book and bicycle table
    store = runAM.db.JSONStore(database_name='test_store', directory=os.path.join(project_dir, 'temp'))
    book_doc_id_list = list()
    bicycle_doc_id_list = list()
    for book in bookstore_json['store']['book']:
        doc_id = store.insert_doc(data=book, table_name='book')
        book_doc_id_list.append(doc_id)
    for bicycle in bookstore_json['store']['bicycle']:
        doc_id = store.insert_doc(data=bicycle, doc_id='42', table_name='bicycle')
        bicycle_doc_id_list.append(doc_id)
    store.write()
    assert (
        book_doc_id_list == ['1', '2', '3', '4']
    ) and (
        bicycle_doc_id_list == ['42']
    )

def test_040_get_table():
    # get table content
    store = runAM.db.JSONStore(database_name='test_store', directory=os.path.join(project_dir, 'temp'))
    assert store.table('bicycle') == {"42": {"color": "red", "price": 19.95}}

def test_060_jq():
    # test basic jq query: find all books with tags
    store = runAM.db.JSONStore(database_name='test_store', directory=os.path.join(project_dir, 'temp'))
    value = store.jq(table_name='book', query_expression='..|select(.tags?!=null)')
    assert value == [
        {
            "category": "fiction",
            "author": "Herman Melville",
            "title": "Moby Dick",
            "isbn": "0-553-21311-3",
            "price": 8.99,
            "tags": ["adventure", "fiction", "1851"]
        },
        {
            "category": "fiction",
            "author": "J. R. R. Tolkien",
            "title": "The Lord of the Rings",
            "isbn": "0-395-19395-8",
            "price": 22.99,
            "tags": ["fantasy", "fiction", "1954"]
        }
    ]

def test_070_jq_path():
    # find the path to every value matched by jq
    store = runAM.db.JSONStore(database_name='test_store', directory=os.path.join(project_dir, 'temp'))
    path_list = store.jq_path(table_name='book', query_expression='..|select(.tags?!=null)')
    assert path_list == [['3'],['4']]

def  test_080_delete_doc():
    # delete a document from a table
    store = runAM.db.JSONStore(database_name='test_store', directory=os.path.join(project_dir, 'temp'))
    deleted_docs_list = store.delete_doc(table_name='bicycle', doc_id='42')
    store.write()
    assert deleted_docs_list == ['42']

def test_090_get_value():
    # find a value that corresponds to the path
    store = runAM.db.JSONStore(database_name='test_store', directory=os.path.join(project_dir, 'temp'))
    value = store.get_val(path_list=['4', 'tags', 0], table_name='book')
    assert value == 'fantasy'

def test_100_update_path():
    # update value in a table based on specified path
    store = runAM.db.JSONStore(database_name='test_store', directory=os.path.join(project_dir, 'temp'))
    updated_table = store.update_path(path=['4', 'tags', 2], data='year-1954', table_name='book')
    store.write()
    assert updated_table == {
        "1": {
            "category": "reference",
            "author": "Nigel Rees",
            "title": "Sayings of the Century",
            "price": 8.95
        },
        "2": {
            "category": "fiction",
            "author": "Evelyn Waugh",
            "title": "Sword of Honour",
            "price": 12.99
        },
        "3": {
            "category": "fiction",
            "author": "Herman Melville",
            "title": "Moby Dick",
            "isbn": "0-553-21311-3",
            "price": 8.99,
            "tags": [
                "adventure",
                "fiction",
                "1851"
            ]
        },
        "4": {
            "category": "fiction",
            "author": "J. R. R. Tolkien",
            "title": "The Lord of the Rings",
            "isbn": "0-395-19395-8",
            "price": 22.99,
            "tags": [
                "fantasy",
                "fiction",
                "year-1954"
            ]
        }
    }
