# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from nose.tools import assert_equal, assert_items_equal

from gcdt.tenkai_core import _build_bundle_key

from gcdt_testtools.helpers import temp_folder  # fixtures!


def test_build_bundle_key():
    application_name = 'sample_name'
    expected = '%s/bundle.tar.gz' % application_name
    assert_equal(_build_bundle_key(application_name), expected)
