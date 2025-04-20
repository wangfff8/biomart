#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import sys
import json
import argparse
import secrets
import string

from pprint import pprint

import pandas as pd
import biomart
from biomart import BiomartServer
from biomart import BiomartDatabase
from biomart import BiomartDataset


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

my_attributes = [
    'ensembl_gene_id', 'ensembl_transcript_id', 'ensembl_peptide_id', 
    'external_gene_name', 'description', 'entrezgene_id', 'go_id', 
    'gene_biotype', 'chromosome_name', 'start_position', 'end_position',
    'transcript_length', 'strand'
]
my_colnames = [
    'Gene stable ID', 'Transcript stable ID',  'Protein stable ID', 'Gene name', 'Gene description',
    'NCBI gene (formerly Entrezgene) ID', 'GO term accession', 'Gene type', 'Chromosome/scaffold name',
    'Gene start (bp)', 'Gene end (bp)','Transcript length (including UTRs and CDS)', 'Strand'
]

def parse_args():
    parser = argparse.ArgumentParser(
        description="Download gene information, GO annotations, etc., from theEnsembl BioMart database."
    )
    parser.add_argument("--list", action="store_true", help="List available datasets")
    parser.add_argument("--level", choices=["gene_description", "transcript_description", "go_id", "entrez_gene_id"], help="the info level", metavar='')
    parser.add_argument("--species_type", choices=["animal", "plant", "fungi"], help="the species type", metavar='')
    parser.add_argument("--dataset", help="the ensemble species dataset", metavar='')
    parser.add_argument("--outfile", help="the output file", metavar='')
    args = parser.parse_args()
    return args


def load_datasets_from_json(json_file):
    with open(json_file) as j:
        ensembl_datasets_dict = json.load(j)
    return ensembl_datasets_dict


def list_datasets(ensembl_datasets_dict):
    pprint(ensembl_datasets_dict)
    sys.exit(0)


def get_query_attributes(level):
    options = {
        'gene_description': ['ensembl_gene_id', 'external_gene_name', 'description'],
        'transcript_description': ['ensembl_transcript_id', 'ensembl_gene_id', 'external_gene_name', 'description'],
        'entrez_gene_id': ['ensembl_gene_id', 'entrezgene_id'],
        'go_id': ['ensembl_gene_id', 'go_id']
    }

    if level not in options:
        raise ValueError(f"Parameter:level supports values is {list(options.keys())!r}")

    return options[level]


def get_column_name(query_attrs):
    query_column_name = [my_colnames[my_attributes.index(attr)] for attr in query_attrs]
    return query_column_name


def get_virtual_schema(species_type):
    virtualSchemaNames = {
        'animal': 'default',
        'plant': 'plants_mart',
        'fungi': 'fungi_mart'
    }
    return virtualSchemaNames[species_type]


def generate_random_string(length=32):
    # alphabet = string.ascii_lowercase + string.digits
    alphabet = '0123456789abcdef'  # 只包含 0-9, a-f
    return ''.join(secrets.choice(alphabet) for i in range(length))


def get_url(species_type):
    urls = {
        'animal': 'http://ensembl.org/biomart/martservice',
        # 'animal': f'http://ensembl.org/biomart/martview/{generate_random_string()}',
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


def main():
    args = parse_args()

    if args.list:
        ensembl_datasets_file = os.path.join(SCRIPT_DIR, "doc", "biomart_genes_datasets.json")
        ensembl_datasets_dict = load_datasets_from_json(ensembl_datasets_file)
        list_datasets(ensembl_datasets_dict)
        sys.exit(0)

    species_list = ['animal', 'plant', 'fungi']
    if args.species_type not in species_list:
        raise ValueError(f"Parameter:species_type supports values is {species_list}")

    url = get_url(args.species_type)
    # my_proxy = {'https_proxy': 'http://172.29.48.1:31181'}
    # biomart_server = BiomartServer(url = url, verbose = True, **my_proxy) 
    biomart_server = BiomartServer(url = url)
    database_name = get_database_name(args.species_type)
    ensembl_database = BiomartDatabase(server=biomart_server, name=database_name)
    virtual_schema = get_virtual_schema(args.species_type)
    ensembl_database.virtual_schema = virtual_schema
    ensembl_dataset = BiomartDataset(url, database=ensembl_database, name=args.dataset)

    # Check query attributes
    query_attributes = get_query_attributes(args.level)
    available_attrs = [attr for attr in query_attributes 
                      if attr in ensembl_dataset.attributes]
    
    # Get data from BioMart
    response_text = ensembl_dataset.search(params={"attributes": available_attrs})
    
    # Create DataFrame and handle missing columns
    df = pd.DataFrame(
        [row.split('\t') for row in response_text.strip().split("\n")],
        columns=available_attrs
    )
    
    # Add missing columns with NA values
    missing_attrs = set(query_attributes) - set(available_attrs)
    df = df.assign(**{attr: pd.NA for attr in missing_attrs})
    
    # Map column names and reorder
    col_mapping = dict(zip(my_attributes, my_colnames))
    out_df = df[query_attributes].rename(columns=col_mapping)
    
    # Clean data and save
    out_df.fillna('-').to_csv(args.outfile, sep='\t', index=False)


if __name__ == "__main__":
    main()

