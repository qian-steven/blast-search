from Bio import SeqIO 
from BioSQL import BioSeqDatabase 
from BioSQL import BioSeq
import os
import mysql.connector
from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML
from Bio.Blast import Record

# help(NCBIWWW.qblast)

server = BioSeqDatabase.open_database(user = 'root', password = '10022aA#', driver = 'mysql.connector', db = 'bioinformatics-final')
del server['saltcress']
'''
db = server['arabidopsis_2']
seq_record = db.lookup(accession='BK010421')
print(db.values)
# print(seq_record.seq
print(db.items)
print(seq_record.id, seq_record.description[:200] + "...")
print("Sequence length %i," % len(seq_record.seq))
# print(seq_record.seq)
namespace_list = server.adaptor.execute_and_fetch_col0("select name from biodatabase")
for i in namespace_list:
    print(i)
''' 
'''
result_handle = open("eutrema_sal_blast.xml")
blast_records = NCBIXML.parse(result_handle)
for blast_record in blast_records:
    for alignment in blast_record.alignments:
        for hsp in alignment.hsps:
            print(hsp.query)
'''

# test_name = input("input name: ")

# server.adaptor.execute("INSERT INTO blast_run (blast_run_name) VALUES ('%s')" %(test_name))
# server.adaptor.execute("DELETE from biodatabase where biodatabase_id = 16")
    
# run_id = server.adaptor.last_id("blast_run")
# print (run_id)

# connection = mysql.connector.connect(host='localhost', user='root', password='10022aA#', database='test-project')
# server = connection.cursor()

# server.execute("INSERT INTO blast_run (run_name) VALUES ('test2')")
# server.close()
#connection.close()


server.commit()
server.close()

# print(BioSeq.Seq)

# print(NCBIWWW.qblast("blastn", "nt", '219004'))

# result_handle = open('RZ1WB70M013-Alignment.xml')
# blast_record = NCBIXML.read(result_handle)

'''
E_VALUE_THRESH = 0.04

for alignment in blast_record.alignments:
    for hsp in alignment.hsps:
        if hsp.expect < E_VALUE_THRESH:
            print("****Alignment****")
            print("sequence:", alignment.title)
            print("length:", alignment.length)
            print("e value:", hsp.expect)
            print(hsp.query[0:75] + "...")
            print(hsp.match[0:75] + "...")
            print(hsp.sbjct[0:75] + "...")

            
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
'''