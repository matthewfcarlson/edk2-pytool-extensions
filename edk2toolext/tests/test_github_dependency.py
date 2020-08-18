# @file test_web_dependency.py
# Unit test suite for the GithubDependency class.
#
##
# Copyright (c) Microsoft Corporation
#
# SPDX-License-Identifier: BSD-2-Clause-Patent
##

import os
import unittest
import logging
import shutil
import tarfile
import zipfile
import tempfile
import json
import urllib.request
from edk2toolext.environment import environment_descriptor_files as EDF
from edk2toolext.environment.extdeptypes.github_dependency import GithubDependency

test_dir = None

bad_json_file = {
    "scope": "global",
    "type": "github",
    "name": "invalid",
    "source": "github",
    "version": "not_a_real_version",
}
bad_json_file2 = {
    "scope": "global",
    "type": "github",
    "name": "invalid",
    "source": "github/freno",
    "version": "not_a_real_version",
}
# JSON file that describes a single github release to download from the internet
github_nosha_extdep = {
    "scope": "global",
    "type": "github",
    "name": "freno",
    "source": "github",
    "version": "v1.0.5",
}
github_sha_extdep = {
    "scope": "global",
    "type": "github",
    "name": "freno",
    "source": "github",
    "version": "v1.0.5",
    "sha256": "faeccbfa7bca9bdc9740ac4a2cf64a5cba5b80b751cb037161c868f887b54d0a"
}
github_sha_match_extdep = {
    "scope": "global",
    "type": "github",
    "name": "freno",
    "source": "github",
    "version": "v1.0.5",
    "match": "linux_amd64",
    "sha256": "844dd305b9d4c28ed721850bb08a252676b6996cb850c529ffda53b280fe6400"
}


def prep_workspace():
    global test_dir
    # if test temp dir doesn't exist
    if test_dir is None or not os.path.isdir(test_dir):
        test_dir = tempfile.mkdtemp()
        logging.debug("temp dir is: %s" % test_dir)
    else:
        #shutil.rmtree(test_dir)
        test_dir = tempfile.mkdtemp()


def clean_workspace():
    global test_dir
    if test_dir is None:
        return

    if os.path.isdir(test_dir):
        #shutil.rmtree(test_dir)
        test_dir = None


class TestGithubDependency(unittest.TestCase):
    def setUp(self):
        prep_workspace()

    @classmethod
    def setUpClass(cls):
        logger = logging.getLogger('')
        logger.addHandler(logging.NullHandler())
        unittest.installHandler()

    @classmethod
    def tearDownClass(cls):
        clean_workspace()

    # throw in a bad url and test that it throws an exception.
    def test_fail_with_bad_url(self):
        ext_dep_file_path = os.path.join(test_dir, "bad_ext_dep.json")
        with open(ext_dep_file_path, "w+") as ext_dep_file:
            ext_dep_file.write(bad_json_file)

        ext_dep_descriptor = EDF.ExternDepDescriptor(ext_dep_file_path).descriptor_contents
        ext_dep = GithubDependency(ext_dep_descriptor)
        with self.assertRaises(urllib.error.HTTPError):
            ext_dep.fetch()
            self.fail("should have thrown an Exception")

    # try to download a single release from the internet
    def test_nosha_release(self):
        ext_dep_file_path = os.path.join(test_dir, "good_ext_dep.json")
        with open(ext_dep_file_path, "w+") as ext_dep_file:
            ext_dep_file.write(json.dumps(github_nosha_extdep))  # dump to a file

        ext_dep_descriptor = EDF.ExternDepDescriptor(ext_dep_file_path).descriptor_contents
        ext_dep = GithubDependency(ext_dep_descriptor)
        ext_dep.fetch()

        ext_dep_name = github_nosha_extdep['name'] + "_extdep"
        file_path = os.path.join(test_dir, ext_dep_name)
        print(file_path)
        if not os.path.isfile(file_path):
            self.fail("The downloaded file isn't there")

    # try to download a single file and test sha256 comparison
    def test_sha256_release(self):
        ext_dep_file_path = os.path.join(test_dir, "good_ext_dep.json")

        with open(ext_dep_file_path, "w+") as ext_dep_file:
            ext_dep_file.write(json.dumps(github_sha_extdep))  # dump to a file

        ext_dep_descriptor = EDF.ExternDepDescriptor(ext_dep_file_path).descriptor_contents
        ext_dep = GithubDependency(ext_dep_descriptor)
        ext_dep.fetch()

        ext_dep_name = github_sha_extdep['name'] + "_extdep"
        file_path = os.path.join(test_dir, ext_dep_name)
        print(file_path)
        if not os.path.isfile(file_path):
            self.fail("The downloaded file isn't there")
    
    # try to download a single file and test sha256 comparison
    def test_sha256_filtered_release(self):
        ext_dep_file_path = os.path.join(test_dir, "good_ext_dep.json")

        with open(ext_dep_file_path, "w+") as ext_dep_file:
            ext_dep_file.write(json.dumps(github_sha_match_extdep))  # dump to a file

        ext_dep_descriptor = EDF.ExternDepDescriptor(ext_dep_file_path).descriptor_contents
        ext_dep = GithubDependency(ext_dep_descriptor)
        ext_dep.fetch()

        ext_dep_name = github_sha_extdep['name'] + "_extdep"
        file_path = os.path.join(test_dir, ext_dep_name)
        print(file_path)
        if not os.path.isfile(file_path):
            self.fail("The downloaded file isn't there")


if __name__ == '__main__':
    unittest.main()
