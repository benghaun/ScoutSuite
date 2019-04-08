from __future__ import print_function

import datetime
import os
import shutil
import zipfile

import dateutil.tz
from ScoutSuite.core.console import print_info, print_exception

from ScoutSuite import DEFAULT_RESULT_FILE, DEFAULT_HTMLREPORT_FILE, DEFAULT_EXCEPTIONS_FILE
from ScoutSuite import ERRORS_LIST
from ScoutSuite.output.js import JavaScriptReaderWriter
from ScoutSuite.output.utils import get_filename, prompt_4_overwrite


class HTMLReport(object):
    """
    Base HTML report
    """

    def __init__(self, profile, report_dir, timestamp=False, exceptions=None):
        exceptions = {} if exceptions is None else exceptions
        self.report_dir = report_dir
        self.profile = profile.replace('/', '_').replace('\\', '_')  # Issue 111
        self.current_time = datetime.datetime.now(dateutil.tz.tzlocal())
        if timestamp != False:
            self.timestamp = self.current_time.strftime("%Y-%m-%d_%Hh%M%z") if not timestamp else timestamp
            self.profile = '%s-%s' % (self.profile, self.timestamp)
        self.exceptions = exceptions
        self.scout_report_data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
        self.html_data_path = os.path.join(self.scout_report_data_path, 'html')
        self.jsrw = JavaScriptReaderWriter(self.profile, report_dir, timestamp)

    def get_content_from(self, templates_type):
        contents = ''
        template_dir = os.path.join(self.html_data_path, templates_type)
        template_files = [os.path.join(template_dir, f) for f in os.listdir(template_dir) if
                          os.path.isfile(os.path.join(template_dir, f))]
        for filename in template_files:
            try:
                with open('%s' % filename, 'rt') as f:
                    contents = contents + f.read()
            except Exception as e:
                print_exception('Error reading filename %s: %s' % (filename, e))
        return contents

    def prepare_html_report_dir(self):
        if not os.path.isdir(self.report_dir):
            os.makedirs(self.report_dir)
        run_results_dir = os.path.join(self.report_dir, 'scoutsuite-results')
        if not os.path.isdir(run_results_dir):
            os.makedirs(run_results_dir)
        # Copy static 3rd-party files
        archive = os.path.join(self.scout_report_data_path, 'includes.zip')
        zip_ref = zipfile.ZipFile(archive)
        zip_ref.extractall(self.report_dir)
        zip_ref.close()
        # Copy static files
        inc_scout_dir = os.path.join(self.report_dir, 'inc-scoutsuite')
        src_inc_scout_dir = os.path.join(self.scout_report_data_path, 'inc-scoutsuite')
        if os.path.isdir(inc_scout_dir):
            shutil.rmtree(inc_scout_dir)
        shutil.copytree(src_inc_scout_dir, inc_scout_dir)


class ScoutReport(HTMLReport):
    """
    Scout HTML report
    """

    def __init__(self, provider, profile=None, report_dir=None, timestamp=False, exceptions=None):
        exceptions = {} if exceptions is None else exceptions
        self.html_root = DEFAULT_HTMLREPORT_FILE
        self.provider = provider
        super(ScoutReport, self).__init__(profile, report_dir, timestamp, exceptions)

    def save(self, config, exceptions, force_write=False, debug=False):
        self.prepare_html_report_dir()
        self.jsrw.save_to_file(config, 'RESULTS', force_write, debug)
        self.jsrw.save_to_file(exceptions, 'EXCEPTIONS', force_write, debug)
        if ERRORS_LIST:
            self.jsrw.save_to_file(ERRORS_LIST, 'ERRORS', force_write, debug=True)
        return self.create_html_report(force_write)

    def create_html_report(self, force_write):
        contents = ''
        # Use all scripts under html/partials/
        contents += self.get_content_from('partials')
        contents += self.get_content_from('partials/%s' % self.provider)
        # Use all scripts under html/summaries/
        contents += self.get_content_from('summaries')
        contents += self.get_content_from('summaries/%s' % self.provider)
        new_file, first_line = get_filename('HTMLREPORT', self.profile, self.report_dir)
        print_info('Creating %s' % new_file)
        if prompt_4_overwrite(new_file, force_write):
            if os.path.exists(new_file):
                os.remove(new_file)
            with open(os.path.join(self.html_data_path, self.html_root)) as f:
                with open(new_file, 'wt') as nf:
                    for line in f:
                        newline = line
                        if self.profile != 'default':
                            newline = newline.replace(DEFAULT_RESULT_FILE,
                                                      DEFAULT_RESULT_FILE.replace('.js', '-%s.js' % self.profile))
                            newline = newline.replace(DEFAULT_EXCEPTIONS_FILE,
                                                      DEFAULT_EXCEPTIONS_FILE.replace('.js', '-%s.js' % self.profile))
                        newline = newline.replace('<!-- PLACEHOLDER -->', contents)
                        nf.write(newline)
        return new_file
