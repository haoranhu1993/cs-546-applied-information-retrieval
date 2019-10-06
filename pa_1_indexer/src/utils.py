import random


def generate_random_terms_from_vocab(vocab, number_of_terms):
    terms = random.sample(vocab, number_of_terms)
    return terms

def generate_random_queries(vocab, number_of_queries, terms_per_query):
    queries = []
    for i in range(number_of_queries):
        terms = generate_random_terms_from_vocab(vocab, terms_per_query)
        query = ' '.join(terms)
        queries.append(query)
    return queries

def create_dice_paired_query(query, dice):
    terms = query.split()
    dice_terms = []
    dice_paired_terms = []
    for term in terms:
        dice_term, dice_coeff = dice.calculate_dice_coefficients(term, count=1)[0]
        dice_terms.append(dice_term)
        dice_paired_terms.append(term)
        dice_paired_terms.append(dice_term)
    dice_paired_query = ' '.join(dice_paired_terms)
    return (dice_terms, dice_paired_query)

def add_dice_terms_to_random_queries(queries, dice):
    dice_paired_queries = []
    for query in queries:
        dice_terms, dice_paired_query = create_dice_paired_query(query, dice)
        dice_paired_queries.append(dice_paired_query)
    return dice_paired_queries

def dump_queries_to_disk(queries, file):
    with open(file, 'w') as f:
        for query in queries:
            f.write(query)
            f.write('\n')

def compare_indices(index_1, index_2):
    vocab_1 = index_1.get_vocabulary()
    vocab_2 = index_2.get_vocabulary()
    assert len(vocab_1) == len(vocab_2), 'Vocabularies of the indices do not have equal number of terms'

    for i, term in enumerate(vocab_1):
        assert term == vocab_2[i], 'Vocabularies of the indices do not have terms in the same order'
        
        ctf_1 = index_1.get_ctf(term)
        ctf_2 = index_2.get_ctf(term)
        assert ctf_1 == ctf_2, 'Collection Term Frequencies do not match, term: {}, Index 1 has CTF: {} and Index 2 has CTF: {}'.format(term, ctf_1, ctf_2)

        df_1 = index_1.get_df(term)
        df_2 = index_2.get_df(term)
        assert df_1 == df_2, 'Document Frequencies do not match, term: {}, Index 1 has DF: {} and Index 2 has DF: {}'.format(term, df_1, df_2)

import struct


def vbyte_encode(num_list):
    list_buffer = bytearray()
    size_in_bytes = 0
    for num in num_list:
        while num >= 128:
            list_buffer += struct.pack('<B', num & 0x7f)
            size_in_bytes += struct.calcsize('<B')
            num >>= 7
        list_buffer += struct.pack('<B', num | 0x80)
        size_in_bytes += struct.calcsize('<B')
    return (list_buffer, size_in_bytes)


def vbyte_decode(list_buffer):
    num_list = []
    i = 0
    while i < len(list_buffer):
        pointer = 0
        byte = list_buffer[i]
        num = byte & 0x7f
        while byte & 0x80 == 0:
            i += 1
            pointer += 1
            byte = list_buffer[i]
            new_byte = byte & 0x7f
            num |= new_byte << (7 * pointer)
        num_list.append(num)
        i += 1
    return num_list

def delta_encode(positions):
    delta_encoded_positions = []
    previous_position = 0
    for position in positions:
        diff = position - previous_position
        delta_encoded_positions.append(diff)
        previous_position = position
    return delta_encoded_positions

def delta_decode(delta_encoded_positions):
    positions = []
    previous_position = 0
    for delta_encoded_position in delta_encoded_positions:
        position = delta_encoded_position + previous_position
        positions.append(position)
        previous_position = position
    return positions