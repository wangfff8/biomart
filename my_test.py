#!/usr/bin/env python
#! -*- coding:utf-8 -*-
import biomart

#print(dir(biomart))
#['BiomartAttribute', 'BiomartAttributePage', 'BiomartDatabase', 'BiomartDataset', 'BiomartException', 'BiomartFilter', 'BiomartServer', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__', 'attribute', 'attribute_page', 'database', 'dataset', 'filter', 'lib', 'server']


from biomart import BiomartServer

# animal
#server = BiomartServer( "http://ensembl.org/biomart", verbose = True )

#print(server.databases)
#{'ENSEMBL_MART_ENSEMBL': Ensembl Genes 112, 'ENSEMBL_MART_MOUSE': Mouse strains 112, 'ENSEMBL_MART_SEQUENCE': Sequence, 'ENSEMBL_MART_ONTOLOGY': Ontology, 'ENSEMBL_MART_GENOMIC': Genomic features 112, 'ENSEMBL_MART_SNP': Ensembl Variation 112, 'ENSEMBL_MART_FUNCGEN': Ensembl Regulation 112}

#ensembl_genes = biomart.BiomartDatabase(server = server, name = "ENSEMBL_MART_ENSEMBL")
#print(ensembl_genes.show_datasets())


# plant
#plant_server = BiomartServer( "http://plants.ensembl.org/biomart", verbose = True )

#print(plant_server.databases)
#{'plants_mart': Ensembl Plants Genes 59, 'plants_variations': Ensembl Plants Variations 59, 'plants_sequences': Ensembl Plants Sequences 59, 'plants_genomic_features': Ensembl Plants Genomic Features 59, 'ontology': Ontology Mart 112}

#plant_genes = biomart.BiomartDatabase(server = plant_server, name = "plants_mart" )
#print(plant_genes.show_datasets())


# fungi
#fungi_server = BiomartServer( "http://fungi.ensembl.org/biomart", verbose = True )

#print(fungi_server.databases)
#{'fungi_mart': Ensembl Fungi Genes 59, 'fungi_variations': Ensembl Fungi Variations 59, 'fungi_sequences': Ensembl Fungi Sequences 59, 'ontology': Ontology Mart 112}

#fungi_genes = biomart.BiomartDatabase(server = fungi_server, name = "fungi_mart")
#print(fungi_genes.show_datasets())


import os
import json
import argparse


file_path = os.path.dirname(os.path.relpath(__file__))
ensembl_datasets_file = os.path.join(file_path, "doc", "biomart_genes_datasets.json")
#with open(ensembl_datasets_file) as j:
#    ensembl_datasets_dict = json.load(j)
##print(ensembl_datasets_dict)
#
#
my_attributes = ['ensembl_gene_id', 'ensembl_transcript_id', 'ensembl_peptide_id', 'external_gene_name','description',
                   'entrezgene_id', 'go_id', 'gene_biotype', 'chromosome_name', 'start_position', 'end_position', 
                   'transcript_length', 'strand']
my_colnames = ['Gene stable ID', 'Transcript stable ID',  'Protein stable ID', 'Gene name', 'Gene description',   
              'NCBI gene (formerly Entrezgene) ID', 'GO term accession', 'Gene type', 'Chromosome/scaffold name', 
              'Gene start (bp)', 'Gene end (bp)','Transcript length (including UTRs and CDS)', 'Strand']


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download gene information & GO annotation from Ensembl BioMart database"
    )
    parser.add_argument("--list", action="store_true", help="List available datasets for the given species type (--species_type)", metavar='')
    parser.add_argument("--level", choices=["gene_description", "transcript_description", "go_id", "entrez_gene_id"], help = "the info level", metavar='')
    parser.add_argument("--species_type", choices=["animal", "plants", "fungi"], help = "the species type", metavar='')
    parser.add_argument("--dataset", help = "the species ensemble dataset", metavar='')
    parser.add_argument("--outfile", help = "the output file", metavar='')
    args = parser.parse_args()
    return args


def get_attrs(level):
    options = {
        'gene_description': ['ensembl_gene_id', 'external_gene_name', 'description'],
        'transcript_description': ['ensembl_transcript_id', 'ensembl_gene_id', 'external_gene_name', 'description'],
        'entrez_gene_id': ['ensembl_gene_id', 'entrezgene_id'],
        'go_id': ['ensembl_gene_id', 'go_id']
    }

    if not level in options:
        raise ValueError(f"Parameter:level supports values is {list(options.keys()):!r}")

    return options[level]


def get_virtualSchema(species_type):
    virtualSchemaNames = {
        'animal': 'default',
        'plant': 'plants_mart',
        'fungi': 'fungi_mart'
    }

    return virtualSchemaNames[species_type]


import secrets
import string

def generate_random_string(length=32):
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))


def get_url(species_type):
    urls = {
        'animal': 'http://ensembl.org/biomart',
        'plant': 'http://www.plants.ensembl.org/biomart/martservice',
        'fungi': 'http://www.fungi.ensembl.org/biomart/martservice'
    }

    return urls[species_type]


def get_database_name(species_type):
    databases = {
        'animal': 'ENSEMBL_MART_ENSEMBL',
        'plant': 'plants_mart',
        'fungi': 'fungi_mart'
    }

    return databases[species_type]


from biomart import BiomartDataset


species_list = ['animal', 'plant', 'fungi']

species_type = "plant"
geneset_name = "osativa_eg_gene"


if species_type not in species_list:
    raise ValueError(f"Parameter:species_type supports values is {species_list}")


url = get_url(species_type)
print("url:", url)
biomart_server = BiomartServer(url = url) 
database_name = get_database_name(species_type)
ensembl_database = biomart.BiomartDatabase(server = biomart_server, name = database_name )
ensembl_database.virtual_schema = get_virtualSchema(species_type)
ensembl_dataset = BiomartDataset(url, database = ensembl_database, name = geneset_name)
ensembl_dataset.virtual_schema = get_virtualSchema(species_type)


params = {}
my_attributes_test = my_attributes[:1] + my_attributes[3:5]
attributes = {"attributes": my_attributes_test}
params.update(attributes)
#print(ensembl_dataset.show_attributes())
response_text = ensembl_dataset.search(params = params)


