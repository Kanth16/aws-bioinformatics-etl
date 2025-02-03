use NeurologicalDiseases;

Drop table if exists Omim;

CREATE TABLE Omim (
    Omim_ID BIGINT,
    BioGrid_id Bigint,
    Phenotype VARCHAR(255),
    Mutation VARCHAR(255),
    SNPs VARCHAR(255) ,
    Load_Key BIGINT,
    Omim_Key Varchar(255) PRIMARY KEY,
    preferred_title Varchar(255),
    Disease_Name VARCHAR(255),
    FOREIGN KEY (Biogrid_id) REFERENCES UniProt(Biogrid_id)
);