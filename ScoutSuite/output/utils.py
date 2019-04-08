# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import sys

from ScoutSuite.core.console import print_error

from six.moves import input

from ScoutSuite import DEFAULT_RESULT_FILE, DEFAULT_HTMLREPORT_FILE, DEFAULT_EXCEPTIONS_FILE, DEFAULT_RULESET_FILE, \
    DEFAULT_ERRORS_FILE


def prompt_for_yes_no(question):
    """
    Ask a question and prompt for yes or no

    :param question:                    Question to ask; answer is yes/no
    :return:                            :boolean
    """

    while True:
        sys.stdout.write(question + ' (y/n)? ')
        choice = input().lower()
        if choice == 'yes' or choice == 'y':
            return True
        elif choice == 'no' or choice == 'n':
            return False
        else:
            print_error('\'%s\' is not a valid answer. Enter \'yes\'(y) or \'no\'(n).' % choice)


def prompt_for_overwrite(filename, force_write):
    """
    Confirm before overwriting existing files. Do not prompt if the file does not exist or force_write is set

    :param filename:                    Name of the file to be overwritten
    :param force_write:                 Do not ask for confirmation and automatically return True if set
    :return:                            :boolean
    """
    #
    if not os.path.exists(filename) or force_write:
        return True
    return prompt_for_yes_no('File \'{}\' already exists. Do you want to overwrite it'.format(filename))


def get_filename(file_type, profile, report_dir):
    """
    Returns the file name for a given file type
    
    :param file_type: can be one of the following:
            'RESULTS' - results JSON/JS file
            'EXCEPTIONS' - exceptions file
            'HTMLREPORT' - HTML report
            'RULESET' - ruleset file
            'ERRORS' - errors file
    """

    if file_type == 'RESULTS':
        filename = DEFAULT_RESULT_FILE
        first_line = 'scoutsuite_results ='
    elif file_type == 'EXCEPTIONS':
        filename = DEFAULT_EXCEPTIONS_FILE
        first_line = 'exceptions ='
    elif file_type == 'HTMLREPORT':
        filename = DEFAULT_HTMLREPORT_FILE
        first_line = None
    elif file_type == 'RULESET':
        filename = DEFAULT_RULESET_FILE
        first_line = 'scoutsuite_results ='
    elif file_type == 'ERRORS':
        filename = DEFAULT_ERRORS_FILE
        first_line = None
    else:
        print_error('Invalid file type provided: {}'.format(file_type))
        raise Exception

    # Append profile name if necessary
    if profile != 'default' and file_type != 'RULESET':
        name, extention = filename.split('.')
        filename = '%s-%s.%s' % (name, profile, extention)

    return (os.path.join(report_dir, filename), first_line)

