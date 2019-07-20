#!/usr/bin/env python

import os
import threading
import logging
import math


def search_jira_threaded(query, jira_connection):
    full_query_results = []
    threads = []
    max_query_threads = int(os.environ.get('MAX_QUERY_THREADS', 8))

    num_threads_needed = calculate_num_threads_from_total_results(query, jira_connection)

    max_threads = min(num_threads_needed, max_query_threads)

    logging.debug('max_threads = {}'.format(max_threads))

    gunicorn_threads = int(os.environ.get('GUNICORN_THREADS', 5))

    num_started_threads = 0

    while num_started_threads <= num_threads_needed:
        while threading.active_count() <= max_threads + gunicorn_threads:
            logging.debug('threading.active_count() = {}'.format(threading.active_count()))
            start_at = 100 * num_started_threads
            max_results = 100 * (num_started_threads + 1)
            t = threading.Thread(target=threaded_search_job, args=(query, jira_connection, start_at, max_results, full_query_results))
            threads.append(t)
            t.start()
            num_started_threads += 1

    for thread in threads:
        if thread.is_alive():
            logging.debug('{} still alive'.format(thread.getName()))
            thread.join()
            logging.debug('{} joined {}'.format(thread.getName(), threading.currentThread().getName()))
    logging.debug('Returning full_query_results')
    return full_query_results


def calculate_num_threads_from_total_results(query, jira_connection):
    total_check_query = jira_connection.search_issues(query, fields='total')
    total_results = total_check_query.total
    num_threads_needed = math.ceil(total_results / 100)

    logging.debug('total = {}'.format(total_results))
    logging.debug('num_threads_needed = {}'.format(num_threads_needed))
    return num_threads_needed


def threaded_search_job(query, jira_connection, start_at, max_results, full_query_results):
    logging.debug('Starting')
    threaded_search_job_query_results = jira_connection.search_issues(query,
                                                                      fields='assignee,summary,status,issuetype,priority,project,issuelinks,subtasks,customfield_10007,customfield_10006,parent',
                                                                      startAt=start_at,
                                                                      maxResults=max_results)
    full_query_results.extend(threaded_search_job_query_results)
    logging.debug('Done')
