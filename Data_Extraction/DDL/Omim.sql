use NeurologicalDiseases;

Drop table if exists Omim;

CREATE TABLE Omim (
    Omim_ID BIGINT,
    Phenotype VARCHAR(255),
    Mutation VARCHAR(255),
    SNPs VARCHAR(255) UNIQUE,
    Load_Key BIGINT UNIQUE,
    Omim_Key BIGINT PRIMARY KEY,
    FOREIGN KEY (Omim_ID) REFERENCES UniProt(Omim_ID)
);