# Import built-in libraries
from collections import defaultdict
from copy import deepcopy

from RetrievalModels import RetrievalModels


class Query:
    """
    Class which exposes APIs to query an inverted index using various modes and scoring models
    """
    def __init__(self, config, inverted_index, retrieval_model='dirichlet', mode='doc', count=10):
        """
        class config: Instance of the configuration of the active inverted index
        class inverted_index: The inverted index to use for querying
        str retrieval_model: Scoring model to be used for querying
        str mode: Type of querying algorithm to use
        int count: Number of documents to retrieve
        """
        self.config = config
        self.inverted_index = inverted_index
        self.retrieval_model = retrieval_model
        self.mode = mode
        self.count = count
    
    def get_documents(self, query_string):
        """
        Returns a sorted list of documents from the index given a query
        str query_string: A query of arbitrary number of terms
        """
        if self.mode == 'term':
            return self.term_at_a_time_retrieval(query_string)
        elif self.mode == 'doc':
            return self.document_at_a_time_retrieval(query_string)
        elif self.mode == 'conj_term':
            return self.conjunctive_term_at_a_time_retrieval(query_string)
        elif self.mode == 'conj_doc':
            return self.conjunctive_document_at_a_time_retrieval(query_string)
    
    def term_at_a_time_retrieval(self, query_string):
        """
        Returns documents using the term-at-a-time retrieval algorithm
        Look at all the documents containing a query term and update each document's score
        Do this for each query term
        str query_string: A query of arbitrary number of terms
        """
        print('Term at a time')
        scores = defaultdict(int)
        query_terms = query_string.split()
        scoring_model = RetrievalModels(query_terms, self.inverted_index, self.retrieval_model)
        # Get the unique terms in the query
        unique_query_terms = set(query_terms)
        results = []

        # This is how the book implements
        # inverted_lists = {}
        # for query_term in unique_query_terms:
        #     inverted_lists[query_term] = self.inverted_index.get_inverted_list(query_term)
        # for query_term, inverted_list in inverted_lists.items():
        #     postings = inverted_list.get_postings()
        #     for posting in postings:
        #         doc_id = posting.get_doc_id()
        #         scores[doc_id] += scoring_model.get_score(query_term, posting)
        
        # This is probably a more efficient implementation
        for query_term in unique_query_terms:
            inverted_list = self.inverted_index.get_inverted_list(query_term)
            postings = inverted_list.get_postings()
            for posting in postings:
                doc_id = posting.get_doc_id()
                dtf = posting.get_dtf()
                scores[doc_id] += scoring_model.get_score(query_term, posting)
        
        scores_list = scores.items()
        # https://stackoverflow.com/a/613218/6492944 - Sorting a list of tuples by second element in descending order
        # https://stackoverflow.com/questions/54300715/python-3-list-sorting-with-a-tie-breaker
        # When sorting two docs with same scores, they are sorted by document ID to maintain consistency
        sorted_scores_list = sorted(scores_list, key=lambda x: (x[1], x[0]), reverse=True)
        
        # Return the meta info of the top self.count number of documents
        for score in sorted_scores_list[:self.count]:
            doc_id = score[0]
            doc_meta = deepcopy(self.inverted_index.get_doc_meta(doc_id))
            doc_meta['score'] = score[1]
            results.append(doc_meta)
        return results

    def document_at_a_time_retrieval(self, query_string):
        """
        Returns documents using the document-at-a-time retrieval algorithm
        Look at every document in the collection
        Check if it is present in the inverted list of a query term
        Update each document's score
        str query_string: A query of arbitrary number of terms
        """
        print('Doc at a time')
        scores = defaultdict(int)
        query_terms = query_string.split()
        scoring_model = RetrievalModels(query_terms, self.inverted_index, self.retrieval_model)
        # Get the unique terms in the query
        unique_query_terms = set(query_terms)
        results = []

        # This is how the book implements
        # inverted_lists = {}
        # for query_term in unique_query_terms:
        #     inverted_lists[query_term] = self.inverted_index.get_inverted_list(query_term)
        # for doc_id in range(1, self.inverted_index.get_total_docs() + 1):
        #     score = 0
            # for query_term, inverted_list in inverted_lists.items():
            #     postings = inverted_list.get_postings()
            #     for posting in postings:
            #         if posting.get_doc_id() == doc_id:
            #             score += scoring_model.get_score(query_term, posting)
            # scores[doc_id] = score

        # This is probably a more efficient implementation
        for query_term in unique_query_terms:
            inverted_list = self.inverted_index.get_inverted_list(query_term)
            for doc_id in range(1, self.inverted_index.get_total_docs() + 1):
                postings = inverted_list.get_postings()
                for posting in postings:
                    if posting.get_doc_id() == doc_id:
                        scores[doc_id] += scoring_model.get_score(query_term, posting)
        
        scores_list = scores.items()
        # https://stackoverflow.com/a/613218/6492944 - Sorting a list of tuples by second element in descending order
        # https://stackoverflow.com/questions/54300715/python-3-list-sorting-with-a-tie-breaker
        # When sorting two docs with same scores, they are sorted by document ID to maintain consistency
        sorted_scores_list = sorted(scores_list, key=lambda x: (x[1], x[0]), reverse=True)
        
        # Return the meta info of the top self.count number of documents
        for score in sorted_scores_list[:self.count]:
            doc_id = score[0]
            doc_meta = deepcopy(self.inverted_index.get_doc_meta(doc_id))
            doc_meta['score'] = score[1]
            results.append(doc_meta)
        return results
    
    def conjunctive_term_at_a_time_retrieval(self, query_string):
        """
        Returns documents using the conjunctive-term-at-a-time retrieval algorithm
        str query_string: A query of arbitrary number of terms
        """
        pass

    def conjunctive_document_at_a_time_retrieval(self, query_string):
        """
        Returns documents using the conjunctive-document-at-a-time retrieval algorithm
        str query_string: A query of arbitrary number of terms
        """
        pass
