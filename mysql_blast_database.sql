-- Table: blast_run
CREATE TABLE blast_run (
    blast_run_id INT PRIMARY KEY auto_increment,
    blast_run_name VARCHAR(500)
);

-- Table: blast_record
CREATE TABLE blast_record (
    blast_record_id INT PRIMARY KEY auto_increment,
    blast_record_description LONGTEXT,
    blast_run_id INT,
    FOREIGN KEY (blast_run_id) REFERENCES blast_run(blast_run_id)
);

-- Table: alignment
CREATE TABLE alignment (
    alignment_id INT PRIMARY KEY auto_increment,
    alignment_title LONGTEXT,
    alignment_length INT,
    blast_record_id INT,
    FOREIGN KEY (blast_record_id) REFERENCES blast_record(blast_record_id)
);

-- Table: hsp
CREATE TABLE hsp (
    hsp_id INT PRIMARY KEY auto_increment,
    hsp_e_value FLOAT,
    hsp_query LONGTEXT,
    hsp_match LONGTEXT,
    hsp_subject LONGTEXT,
    hsp_query_coverage FLOAT,
    hsp_percentage_identity FLOAT,
    hsp_score INT,
    alignment_id INT,
    FOREIGN KEY (alignment_id) REFERENCES alignment(alignment_id)
);