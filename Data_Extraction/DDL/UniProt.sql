use NeurologicalDiseases;

Drop table if exists UniProt;

CREATE TABLE UniProt (
    Primary_Accession_ID VARCHAR(255),
    UniProt_ID VARCHAR(255),
    Recommended_Name VARCHAR(255),
    Alternative_Names VARCHAR(255),
    Gene_Names VARCHAR(255),
    Organism VARCHAR(255),
    Biogrid_id BIGINT,
    Omim_ID BIGINT UNIQUE,
    UniProt_Key BIGINT PRIMARY KEY,
    Load_Key BIGINT UNIQUE,
    Disease_Name VARCHAR(255)
);
