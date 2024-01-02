# import

from Bio import SeqIO 
from BioSQL import BioSeqDatabase 
import os
import mysql.connector

server = BioSeqDatabase.open_database(user = 'root', password = '10022aA#', driver = 'mysql.connector', db = 'bioinformatics_final') 

db = server.new_database("orchid") 
#count = db.load(SeqIO.parse("ls_orchid.fasta", "fasta"), True) 
#server.commit() 
#server.close()