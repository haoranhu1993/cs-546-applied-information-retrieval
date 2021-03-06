# Import built-in libraries
import argparse
import json
import os

# Import src files
from Indexer import Indexer
from Query import Query
from DiceCoefficient import DiceCoefficient
from utils import *


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_file_name', default='shakespeare-scenes.json',
                        help='Set the name of the data file to load the data from')
    parser.add_argument('--compressed', default=1,
                        help='Set to 0 to not store compressed index')
    parser.add_argument('--in_memory', default=0,
                        help='Set to 1 if you want to store the whole index in memory')
    parser.add_argument('--retrieval_model', default='raw_counts',
                        help='Set the type of retrieval model for queries')
    parser.add_argument('--data_dir', default='data',
                        help='Set the name of the data directory')
    parser.add_argument('--index_dir', default='index',
                        help='Set the name of the index directory')
    parser.add_argument('--compressed_dir', default='compressed',
                        help='Set the name of the compressed index directory under index_dir')
    parser.add_argument('--uncompressed_dir', default='uncompressed',
                        help='Set the name of the uncompressed index directory under index_dir')
    parser.add_argument('--config_file_name', default='config',
                        help='Set the name of the config file')
    parser.add_argument('--inverted_lists_file_name', default='inverted_lists',
                        help='Set the name of the inverted lists file')
    parser.add_argument('--lookup_table_file_name', default='lookup_table',
                        help='Set the name of the lookup table file')
    parser.add_argument('--docs_meta_file_name', default='docs_meta',
                        help='Set the name of the documents meta info file')
    parser.add_argument('--collection_stats_file_name', default='collection_stats',
                        help='Set the name of the colelction stats file')
    parser.add_argument('--document_vectors_file_name', default='document_vectors',
                        help='Set the name of the documents vectors file')
    args = parser.parse_args()

    # Create an indexer
    indexer = Indexer(args)

    if not indexer.config.compressed:
        print('Using uncompressed index')
        # Get the inverted index
        inverted_index_1 = indexer.get_inverted_index(False)

        # Get the vocabulary
        vocab = inverted_index_1.get_vocabulary()

        print('Running a few quick tests.....')

        # Test a query
        query = Query(indexer.config, inverted_index_1)
        results = query.get_documents('setting the scene')
        print('Query Results for {}: '.format('setting the scene'), results)

        # Test dice coefficient
        dice = DiceCoefficient(indexer.config, inverted_index_1)
        dice_coeffs = dice.calculate_dice_coefficients(vocab[150], count=10)
        print('Top 10 Dice Coefficients for {}: '.format(
            vocab[150]), dice_coeffs)

    if indexer.config.compressed:
        print('Using compressed index')
        # Get the inverted index
        inverted_index_2 = indexer.get_inverted_index(True)

        # Get the vocabulary
        vocab = inverted_index_2.get_vocabulary()

        print('Running a few quick tests.....')

        # Test a query
        query = Query(indexer.config, inverted_index_2)
        results = query.get_documents('setting the scene')
        print('Query Results for {}: '.format('setting the scene'), results)

        # Test dice coefficient
        dice = DiceCoefficient(indexer.config, inverted_index_2)
        dice_coeffs = dice.calculate_dice_coefficients(vocab[150], count=10)
        print('Top 10 Dice Coefficients for {}: '.format(
            vocab[150]), dice_coeffs)


if __name__ == '__main__':
    main()
