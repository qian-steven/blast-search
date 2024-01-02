from Bio import SeqIO 
from BioSQL import BioSeqDatabase 
from BioSQL import BioSeq
import os
import mysql.connector
from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML

def get_database_schema():
    
    #attempt to connect to database
    while True:
        try: 
            database_schema = input("Enter your database schema: ")
            server = BioSeqDatabase.open_database(user = 'root', password = '10022aA#', driver = 'mysql.connector', db = database_schema) 
            return server
        except Exception as e:
            print(e)
            print("Please try again.")

def get_dataset_name(server):
    
    # input namespace that serves as a primary key on the biodatabase table
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

def load_sequence_data(server):
    
    db = get_dataset_name(server)
    file_format = get_file_format()
    file_name = get_file_name()

    try:
        count = db.load(SeqIO.parse(file_name, file_format), True)
    except Exception as e:
        print(f"An exception occurred: {e}")
        print("Exiting sequence load")
        return  

    server.commit() 
    server.close()

    print("Successfully loaded ", count, "records")

def view_sequence_data(server):
    while True:
        print("\nMenu:")
        print("1. View namespaces")
        print("2. View sequence records in a namespace")
        print("3. View sequence record info")
        print("4. View raw sequence from a sequence record")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            # list all namespaces by name and output the total number of sequence records
            namespace_list = server.adaptor.execute_and_fetch_col0("select name from biodatabase")
            for i in namespace_list:
                db = server[i]
                print(i, "- %i total sequence records" % len(db))

        elif choice == '2':

            try:
                namespace = input("Enter a namespace: ")
                db = server[namespace]
            except Exception as e:
                print(f"An exception occurred: {e}")
                print("Exiting sequence load")
                return  
            
            namespace_id = server.adaptor.execute_and_fetch_col0("select biodatabase_id from biodatabase where name = '%s'" %(namespace))[0]

            seq_acc_list = server.adaptor.execute_and_fetch_col0("select accession from bioentry where biodatabase_id = '%s'" %namespace_id)

            for i in seq_acc_list:
                print(i)

            # seq_record = db.lookup(accession='BK010421')
            # print(seq_record.id, seq_record.description[:200] + "...")

        elif choice == '3':
         
            try:
                namespace = input("Enter a namespace: ")
                db = server[namespace]

            except Exception as e:
                print(f"An exception occurred: {e}")
                print("Exiting sequence load")
                return  
            
            while True:
                print("Choose a lookup method:")
                print("1. GI number")
                print("2. Accession number")
                key_value = input("Enter the corresponding number (1 or 2): ")
            
                if key_value in ['1', '2']:
                    key_value = {'1': 'gi', '2': 'accession'}[key_value]
                    break
                else:
                    print("Invalid choice. Please enter 1 or 2.")

            seq_list = []            

            while True:
                user_input = input("Enter your lookup values one at a time (type 'done' or hit ENTER to finish): ")

                if not user_input:
                    break

                if user_input.lower() == 'done':
                    break

                seq_list.append(user_input)

            if key_value == 'gi':
                for identifier in seq_list:
                    seq_record = db.lookup(gi=identifier)
                    print("\n" + seq_record.id, seq_record.description[:100] + "...")
                    print("Sequence length %i" % len(seq_record.seq))

            if key_value == 'accession':
                for identifier in seq_list:
                    seq_record = db.lookup(accession=identifier)
                    print("\n" + seq_record.id, seq_record.description[:100] + "...")
                    print("Sequence length %i" % len(seq_record.seq)) 

        elif choice == '4':
            
            try:
                namespace = input("Enter a namespace: ")
                db = server[namespace]

            except Exception as e:
                print(f"An exception occurred: {e}")
                print("Exiting sequence load")
                return   
                      
            while True:

                print("Choose a lookup method:")
                print("1. GI number")
                print("2. Accession number")

                key_value = input("Enter the corresponding number (1 or 2): ")
            
                if key_value in ['1', '2']:
                    key_value = {'1': 'gi', '2': 'accession'}[key_value]
                    break
                else:
                    print("Invalid choice. Please enter 1 or 2.")            

            seq_input = input("Enter your lookup value: ")

            if key_value == 'gi':
                seq_record = db.lookup(gi=seq_input)

            if key_value == 'accession':
                seq_record = db.lookup(accession=seq_input)

            print(seq_record.id, seq_record.description[:100] + "...")
            print(seq_record.seq)

        elif choice == '5':
            print("Exiting the program. Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

def load_BLAST_data(server):
    
    blast_file_name = input("Enter your XML file name: ")
    blast_run_name = input("Give this BLAST run a name: ")

    result_handle = open(blast_file_name)
    blast_records = NCBIXML.parse(result_handle)

    server.adaptor.execute("INSERT INTO blast_run (blast_run_name) VALUES ('%s')" %(blast_run_name))
    run_id = server.adaptor.last_id("blast_run")
    blast_record_count = 0

    for blast_record in blast_records:
        
        blast_record_count += 1
        server.adaptor.execute("INSERT INTO blast_record (blast_record_description, blast_run_id) VALUES ('%s', '%s')" %(blast_record.query, run_id))
        blast_record_id = server.adaptor.last_id("blast_record")

        for alignment in blast_record.alignments:

            server.adaptor.execute("INSERT INTO alignment (alignment_title, alignment_length, blast_record_id) VALUES ('%s', '%s', %i)" %(alignment.title,alignment.length,blast_record_id))
            alignment_id = server.adaptor.last_id("alignment")

            for hsp in alignment.hsps:
                server.adaptor.execute("INSERT INTO hsp (hsp_e_value, hsp_query, hsp_match, hsp_subject, hsp_score, alignment_id) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" %(hsp.expect, hsp.query, hsp.match, hsp.sbjct, hsp.score, alignment_id))
    
    server.commit()
    print("Successfully uploaded ", blast_record_count, " BLAST records")

def analyze_BLAST_data(server):

    while True:
        print("\n Select an action:")
        print("1. View HSPs from a BLAST Record")
        print("2. Search a BLAST Run by Alignment Length and E-Value")
        print("3. Exit Program")
        choice = input("Enter the corresponding number (1, 2, or 3): ")

        if choice == '1':

            print("Select a BLAST run: ")
            blast_run_list = server.adaptor.execute_and_fetch_col0("select blast_run_id from blast_run")
            for blast_run_id in blast_run_list:
                blast_run_name = server.adaptor.execute_and_fetch_col0("select blast_run_name from blast_run where blast_run_id = '%s'" %(blast_run_id))[0]
                print("%s - %s" %(blast_run_id, blast_run_name))
            
            blast_run_choice = input("Enter the corresponding BLAST run ID: ")

            print("Select a BLAST record: ")
            blast_record_list = server.adaptor.execute_and_fetch_col0("select blast_record_id from blast_record where blast_run_id = '%s'" %(blast_run_choice))

            for blast_record_id in blast_record_list:
                blast_record_description = server.adaptor.execute_and_fetch_col0("select blast_record_description from blast_record where blast_record_id = '%s'" %(blast_record_id))[0]
                print("%s - %s ..." %(blast_record_id, blast_record_description[:100]))
            
            blast_record_choice = input("Enter the corresponding BLAST record ID: ")

            print("\nPrinting HSPs from BLAST record (limited to top 25 alignments): ")

            alignment_list = server.adaptor.execute_and_fetch_col0("select alignment_id from alignment where blast_record_id = '%s' limit 25" %(blast_record_choice))

            for alignment_id in alignment_list:

                alignment_title = server.adaptor.execute_and_fetch_col0("select alignment_title from alignment where alignment_id = '%s'" %(alignment_id))[0]
                alignment_length = server.adaptor.execute_and_fetch_col0("select alignment_length from alignment where alignment_id = '%s'" %(alignment_id))[0]
                hsp_list = server.adaptor.execute_and_fetch_col0("select hsp_id from hsp where alignment_id = '%s'" %(alignment_id))

                for hsp_id in hsp_list:
                    
                    hsp_e_value = server.adaptor.execute_and_fetch_col0("select hsp_e_value from hsp where hsp_id = '%s'" %(hsp_id))[0]
                    hsp_query = server.adaptor.execute_and_fetch_col0("select hsp_query from hsp where hsp_id = '%s'" %(hsp_id))[0]
                    hsp_match = server.adaptor.execute_and_fetch_col0("select hsp_match from hsp where hsp_id = '%s'" %(hsp_id))[0]
                    hsp_subject = server.adaptor.execute_and_fetch_col0("select hsp_subject from hsp where hsp_id = '%s'" %(hsp_id))[0]
                    hsp_score = server.adaptor.execute_and_fetch_col0("select hsp_score from hsp where hsp_id = '%s'" %(hsp_id))[0]
                    print("\nAlignment: " + alignment_title)
                    print("Alignment Length: %s" %(alignment_length))
                    print("E Value: %s" %(hsp_e_value))
                    print("Score: %s" %(hsp_score))
                    print(hsp_query[0:125] + "...")
                    print(hsp_match[0:125] + "...")
                    print(hsp_subject[0:125] + "...")

        elif choice == '2':
            print("Select a BLAST run: ")
            blast_run_list = server.adaptor.execute_and_fetch_col0("select blast_run_id from blast_run")
            for blast_run_id in blast_run_list:
                blast_run_name = server.adaptor.execute_and_fetch_col0("select blast_run_name from blast_run where blast_run_id = '%s'" %(blast_run_id))[0]
                print("%s - %s" %(blast_run_id, blast_run_name))
            
            blast_run_choice = input("Enter the corresponding BLAST run ID: ")

            alignment_length_input = input("Select an alignment length threshold: ")
            alignment_length_threshold = int(alignment_length_input)

            e_value_input = input("Select an E-Value threshold: ")
            e_value_threshold = float(e_value_input)

            blast_record_list = server.adaptor.execute_and_fetch_col0("select blast_record_id from blast_record where blast_run_id = '%s'" %(blast_run_choice))

            for blast_record_id in blast_record_list:

                alignment_list = server.adaptor.execute_and_fetch_col0("select alignment_id from alignment where blast_record_id = '%s'" %(blast_record_id))
                for alignment_id in alignment_list:
                    
                    alignment_length = server.adaptor.execute_and_fetch_col0("select alignment_length from alignment where alignment_id = '%s'" %(alignment_id))[0]
                    if alignment_length <= alignment_length_threshold:
                        
                        hsp_list = server.adaptor.execute_and_fetch_col0("select hsp_id from hsp where alignment_id = '%s'" %(alignment_id))

                        for hsp_id in hsp_list:
                            hsp_e_value = server.adaptor.execute_and_fetch_col0("select hsp_e_value from hsp where hsp_id = '%s'" %(hsp_id))[0]

                            if hsp_e_value <= e_value_threshold:
                                alignment_title = server.adaptor.execute_and_fetch_col0("select alignment_title from alignment where alignment_id = '%s'" %(alignment_id))[0]                       
                                hsp_score = server.adaptor.execute_and_fetch_col0("select hsp_score from hsp where hsp_id = '%s'" %(hsp_id))[0]

                                print("\nAlignment: " + alignment_title)
                                print("Alignment Length: %s" %(alignment_length))
                                print("E Value: %s" %(hsp_e_value))
                                print("Score: %s" %(hsp_score))         

        elif choice == '3':
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 3.")

def BLAST_search(server):
    # obtain the string to search on qBLAST
    search_term = input("Enter a qBLAST lookup term (e.g. accession number, GI number, raw text): ")

    if not search_term: 
        return

    # run qBLAST SEARCH
    result_handle = NCBIWWW.qblast("blastn", "nt", search_term)

    while True:
        print("qBLAST search complete. Would you like to import your results?")       
        print("1. Yes")
        print("2. No")
        choice = input("Enter the corresponding number (1 or 2): ")

        if choice == '1':

            blast_run_name = input("Give this BLAST run a name: ")
            blast_records = NCBIXML.parse(result_handle)

            server.adaptor.execute("INSERT INTO blast_run (blast_run_name) VALUES ('%s')" %(blast_run_name))
            run_id = server.adaptor.last_id("blast_run")
            blast_record_count = 0

            # Loop through and upload BLAST results

            for blast_record in blast_records:
                
                blast_record_count += 1
                server.adaptor.execute("INSERT INTO blast_record (blast_record_description, blast_run_id) VALUES ('%s', '%s')" %(blast_record.query, run_id))
                blast_record_id = server.adaptor.last_id("blast_record")

                for alignment in blast_record.alignments:

                    server.adaptor.execute("INSERT INTO alignment (alignment_title, alignment_length, blast_record_id) VALUES ('%s', '%s', %i)" %(alignment.title,alignment.length,blast_record_id))
                    alignment_id = server.adaptor.last_id("alignment")

                    for hsp in alignment.hsps:
                        server.adaptor.execute("INSERT INTO hsp (hsp_e_value, hsp_query, hsp_match, hsp_subject, hsp_score, alignment_id) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" %(hsp.expect, hsp.query, hsp.match, hsp.sbjct, hsp.score, alignment_id))
            
            server.commit()
            print("Successfully uploaded ", blast_record_count, " BLAST records")
            return

        if choice == '2':
            print("Quitting...")
            break

        else:
            print("Invalid choice. Please enter 1 or 2.")

def main():

    server = get_database_schema()

    while True:
        print("\nMenu:")
        print("1. Load sequence data")
        print("2. View sequence data")
        print("3. Load BLAST data")
        print("4. Analyze BLAST data")
        print("5. Run a qBLAST search")
        print("6. Exit the program")

        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            load_sequence_data(server)
        elif choice == "2":
            view_sequence_data(server)
        elif choice == "3":
            load_BLAST_data(server)
        elif choice == "4":
            analyze_BLAST_data(server)
        elif choice == "5":
            BLAST_search(server)
        elif choice == "6":
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")

if __name__ == "__main__":
    main()
