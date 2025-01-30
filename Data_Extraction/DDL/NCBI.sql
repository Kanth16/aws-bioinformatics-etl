use NeurologicalDiseases;

Drop table if exists NCBI;

CREATE TABLE NCBI (
    Alleles VARCHAR(255),
    Gene VARCHAR(255),
    Chromosome VARCHAR(255),
    Position BIGINT,
    Load_Key BIGINT UNIQUE,
    NCBI_Key BIGINT PRIMARY KEY,
    Omim_Key BIGINT,
    SNPs Varchar(255),
    FOREIGN KEY (SNPs) REFERENCES Omim(SNPs)
);