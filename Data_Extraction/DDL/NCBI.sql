use NeurologicalDiseases;

Drop table if exists NCBI;

CREATE TABLE NCBI (
    Alleles VARCHAR(255),
    NCBI_ID VARCHAR(255),
    SNP_Position BIGINT,
    Gene_ID BIGINT,
    Chromosome_Number VARCHAR(255),
    Chromosome_Location VARCHAR(255),
    Load_Key BIGINT,
    NCBI_Key VARCHAR(255) PRIMARY KEY,
    SNPs Varchar(255),
    Disease_Name VARCHAR(255)
);