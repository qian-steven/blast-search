from Bio import SeqIO 
from BioSQL import BioSeqDatabase 
import os
import mysql.connector

def get_database_schema():
    while True:
        try: 
            database_schema = input("Enter a database schema: ")
            server = BioSeqDatabase.open_database(user = 'root', password = '10022aA#', driver = 'mysql.connector', db = database_schema) 
            return server
        except Exception as e:
            print(e)
            print("Please try again.")

def get_dataset_name(server):
    while True:
        try:
            dataset_name = input("Give this upload a namespace: ")
            db = server.new_database(dataset_name)
            return db
        except Exception as e:
            print(e)

def get_file_format():
    while True:
        print("Choose the file format:")
        print("1. Fasta")
        print("2. Genbank")
        print("3. Plain Text")
        choice = input("Enter the corresponding number (1, 2, or 3): ")

        if choice in ['1', '2', '3']:
            return {'1': 'fasta', '2': 'genbank', '3': 'plain text'}[choice]
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def get_file_name():
    return input("Enter the file name: ")

def main():
    
    server = get_database_schema()
    db = get_dataset_name(server)
    file_format = get_file_format()
    file_name = get_file_name()

    # print("\nInputs:")
    # print(f"Database Schema: {database_schema}")
    # print(f"Dataset Name: {dataset_name}")
    # print(f"File Format: {file_format}")
    # print(f"File Name: {file_name}")

    count = db.load(SeqIO.parse(file_name, file_format), True) 
    print("Successfully loaded ", count, "records")

    server.commit() 
    server.close()

if __name__ == "__main__":
    main()
