import logging
import time
import copy
import pdb
import xutils
# cannot perform relative import
from . import test_base
from .test_base import BaseTestCase, json_request_return_dict
from .test_base_note import delete_note_for_test, create_note_for_test, get_default_group_id

class TestMain(BaseTestCase):
    def test_add_note_to_tag(self):
        # add_note_to_tag
        delete_note_for_test(name="add_note_to_tag")
        
        note_id = create_note_for_test(type="md", name="add_note_to_tag")
        
        data = dict(tag_code="test", note_ids = str(note_id))
        result = json_request_return_dict("/note/tag/add_note_to_tag", method="POST", data=data)
        assert result.get_bool("success")
        