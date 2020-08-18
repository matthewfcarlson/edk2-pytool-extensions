# @file web_dependency.py
# This module implements ExternalDependency for files that are available for download online.
#
##
# Copyright (c) Microsoft Corporation
#
# SPDX-License-Identifier: BSD-2-Clause-Patent
##

import os
import logging
import shutil
import tarfile
import zipfile
import tempfile
import urllib.error
import urllib.request
import json
from edk2toolext.environment.extdeptypes.web_dependency import WebDependency


class GithubDependency(WebDependency):
    '''
    ext_dep fields:
    - sha256:  optional. hash of downloaded file to be checked against.
    - source:  the github user or organization that released this
    - name:    the repo to download
    - version: the tag to download from
    - match:   a string to search the asset name for (case-insensitive)
    '''

    TypeString = "github"
    Valid_Content_Types = {"application/gzip": 'tar', "application/x-zip-compressed": 'zip'}

    def __init__(self, descriptor):
        # skip the WebDependency constructor and just got to the one above it
        super(WebDependency, self).__init__(descriptor)
        self.sha256 = descriptor.get('sha256', None)
        self.match = descriptor.get('match', None)
        self.compression_type = 'zip'
        self.internal_path = ''
        self.download_is_directory = True

    def get_download_url(self):
        ''' requests the asset location from github's API '''
        api_url = f"https://api.github.com/repos/{self.source}/{self.name}/releases/tags/{self.version}"
        try:
            request = urllib.request.Request(api_url)
            # Yes- I am encoding the client ID and secret in plain text here. This allows us to get around the rate limiting
            request.add_header(
                "Authorization", "Basic NjZkNTRkY2VmOTlhOTkyMTU0NWM6NjViZTMzOGQyMmNhZThkMmU0Nzk2NGQ3ZDFkYjM5YjE4ZGU5N2RjYQ==")
            # Download the file and save it locally as the download_location_file
            with urllib.request.urlopen(api_url) as response:
                raw_data = response.read()
                data = json.loads(raw_data)
                if "assets" not in data:
                    raise ValueError("assets")
                data = data["assets"]
                if len(data) == 0:
                    raise ValueError("No assets found")
                # Loop through the assets return from the API
                for asset in data:
                    if "content_type" not in asset:
                        raise ValueError("content_type")
                    content_type = asset['content_type']
                    if content_type not in self.Valid_Content_Types:
                        continue
                    if self.match and self.match.lower() not in asset['name'].lower():
                        logging.debug(f"Skipping {asset['name']} since it doesn't match filter")
                        continue
                    self.compression_type = self.Valid_Content_Types[content_type]
                    if "browser_download_url" not in asset:
                        raise ValueError("browser_download_url")
                    return asset["browser_download_url"]
                raise ValueError(f'No assets found that match')
        except ValueError as e:
            logging.error(f"Invalid formatting for Github API when resolving ext_dep {self.name} at {self.source}")
            raise e
        except urllib.error.HTTPError as e:
            logging.error(f"Ran into an issue when resolving ext_dep {self.name} at {self.source}")
            raise e

    def __str__(self):
        """ return a string representation of this """
        return f"GithubDependecy: {self.source}@{self.version}"
