# Import built-in libraries
import os
import argparse
import time
import json

# Import src files
from Indexer import Indexer
from Query import Query
from DiceCoefficient import DiceCoefficient
from utils import *


def run_experiments(compressed=0, uncompressed=0):
    indexer = Indexer(argparse.Namespace(
        **{'index_dir': 'index', 'config_file_name': 'config'}))
    config = indexer.config

    inverted_index_uncompressed = None
    inverted_index_compressed = None

    if uncompressed:
        print('Using uncompressed index')
        # Get the uncompressed inverted index
        inverted_index_uncompressed = indexer.get_inverted_index(False)
        # Get the vocabulary
        vocab_uncompressed = inverted_index_uncompressed.get_vocabulary()

    if compressed:
        print('Using compressed index')
        # Get the compressed inverted index
        inverted_index_compressed = indexer.get_inverted_index(True)
        # Get the vocabulary
        vocab_compressed = inverted_index_compressed.get_vocabulary()

    if inverted_index_uncompressed and inverted_index_compressed:
        run_comparison_test(inverted_index_uncompressed,
                            inverted_index_compressed)

    if inverted_index_uncompressed:
        index = inverted_index_uncompressed
    elif inverted_index_compressed:
        index = inverted_index_compressed

    print('Generating 7 word queries..........')
    run_query_generator(index, 100, 7)

    print('Generating stats for 7 word queries..........')
    run_query_stats_generator(index)

    print('Generating 7 two word phrase queries..........')
    run_dice_generator(config, index)

    print('Running timing experiment for uncompressed index..........')
    run_timing_experiment(config, inverted_index_uncompressed)

    print('Running timing experiment for compressed index..........')
    run_timing_experiment(config, inverted_index_compressed)

    print('Generating dataset stats..........')
    run_stats_generator(index)

    print('Running retrieval model tasks')
    run_retrieval_models_tasks(config, index, indexer, top_k=10, judge_queries=[3])

    print('Finished evaluation!')


def run_comparison_test(inverted_index_uncompressed, inverted_index_compressed):
    print(compare_indices(inverted_index_uncompressed, inverted_index_compressed))


def run_query_generator(index, number_of_queries, terms_per_query):
    queries = generate_random_queries(
        index, number_of_queries, terms_per_query)
    dump_strings_to_disk(queries, '../evaluation/queries_7_terms.txt')
    print('7 term queries generated!')


def run_query_stats_generator(index):
    queries_stats = []
    # Read 7 term queries from disk
    with open('../evaluation/queries_7_terms.txt', 'r') as f:
        queries = f.read().split('\n')
        for query in queries:
            terms = query.split()
            line = []
            for term in terms:
                ctf = index.get_ctf(term)
                df = index.get_df(term)
                line.append(term)
                line.append(str(ctf))
                line.append(str(df))
            query_stats = ' '.join(line)
            queries_stats.append(query_stats)
    dump_strings_to_disk(
        queries_stats, '../evaluation/queries_7_terms_stats.txt')
    print('7 term queries with stats generated!')


def run_dice_generator(config, index):
    dice = DiceCoefficient(config, index)
    queries = None

    # Read 7 term queries from disk
    with open('../evaluation/queries_7_terms.txt', 'r') as f:
        queries = f.read().split('\n')

    # Generate 100 queries with dice pairs of each of the 7 words - returns 14 word queries
    dice_terms_strings, dice_paired_queries = add_dice_terms_to_random_queries(
        queries, dice)
    dump_strings_to_disk(dice_terms_strings,
                         '../evaluation/max_dice_7_terms.txt')
    print('Max dice for each term in query file generated!')

    dump_strings_to_disk(dice_paired_queries,
                         '../evaluation/queries_14_terms.txt')
    print('14 term queries generated!')


def run_timing_experiment(config, inverted_index):
    query_index = Query(config, inverted_index)

    # Read 7 term queries from disk
    with open('../evaluation/queries_7_terms.txt', 'r') as f:
        queries = f.read().split('\n')
        print('Experiment on 7 word queries.....')
        start_time = time.time()
        for i in range(100):
            for query in queries:
                query_index.get_documents(query)
        end_time = time.time()
        print('Time Taken: ', (end_time - start_time) / 100, 'seconds')

    # Read 14 term queries from disk
    with open('../evaluation/queries_14_terms.txt', 'r') as f:
        queries = f.read().split('\n')
        print('Experiment on 14 word queries.....')
        start_time = time.time()
        for query in queries:
            query_index.get_documents(query)
        end_time = time.time()
        print('Time Taken: ', end_time - start_time, 'seconds')


def run_stats_generator(index):
    longest_play, shortest_play, longest_scene, shortest_scene, average_scene_length = get_data_stats(
        index)
    print('Longest Play: Play ID =',
          longest_play[0], '| Play Length =', longest_play[1])
    print('Shortest Play: Play ID =',
          shortest_play[0], '| Play Length =', shortest_play[1])
    print('Longest Scene: Scene ID =',
          longest_scene[0], '| Scene Number =', longest_scene[1], '| Scene Length =', longest_scene[2])
    print('Shortest Scene: Scene ID =',
          shortest_scene[0], '| Scene Number =', shortest_scene[1], '| Scene Length =', shortest_scene[2])
    print('Average Scene Length: ', average_scene_length)


def run_retrieval_models_tasks(config, inverted_index, indexer, top_k=10, judge_queries=[3]):
    queries = None

    final_judgments_file_name = '../evaluation/' + 'judgments.txt'
    open(final_judgments_file_name, 'w').close()

    # Read the retrieval model queries from disk
    with open('../evaluation/queries_retrieval_model.txt', 'r') as f:
        queries = f.read().split('\n')

    with open('../evaluation/trecrun_configs.json', 'r') as f:
        trecrun_configs = json.load(f)
        oit_identifier = trecrun_configs['oitIdentifier']
        trecrun_output_format = trecrun_configs['outputFormat']
        tasks = trecrun_configs['tasks']
        for task in tasks:
            retrieval_model = task['retrievalModelName']
            retrieval_model_method = task['retrievalModelMethod']
            retrieval_model_args = task['params']
            params = '-'.join(str(arg) for arg in list(retrieval_model_args.values()))
            if params:
                params = '-' + params
            query_index = Query(config,
                                inverted_index,
                                mode='doc',
                                retrieval_model=retrieval_model,
                                count=inverted_index.get_total_docs(),
                                **retrieval_model_args)
            query_results = []
            for i, query in enumerate(queries):
                query_result = {
                    'query': query,
                    'topic_number': i + 1,
                    'run_tag': oit_identifier + '-' + retrieval_model_method + params,
                    'docs': query_index.get_documents(query)
                }
                query_results.append(query_result)
            
            trecrun_file_name = '../evaluation/' + retrieval_model_method + trecrun_output_format
            generate_trecrun_file(trecrun_file_name, query_results)

            scenes = get_scenes(indexer.load_data())
            trecrun_judgments_file_name = '../evaluation/' + retrieval_model_method + '_judgments.txt'
            generate_trecrun_judgments_file(trecrun_judgments_file_name, query_results, scenes, top_k, judge_queries)

            generate_final_judgments_file(final_judgments_file_name, query_results, top_k, judge_queries)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--compressed', default=0,
                        help='Set to 1 to run experiments with compressed index')
    parser.add_argument('--uncompressed', default=0,
                        help='Set to 1 to run experiments with uncompressed index')
    parser.add_argument('--index_dir', default='index',
                        help='Set the name of the index directory')
    args = parser.parse_args()

    compressed = int(args.compressed)
    uncompressed = int(args.uncompressed)

    if not compressed and not uncompressed:
        compressed = 1
        uncompressed = 1

    # Create the evaluation directory if it doesn't exist
    if not os.path.exists('../evaluation'):
        os.mkdir('../evaluation')

    run_experiments(compressed=compressed, uncompressed=uncompressed)