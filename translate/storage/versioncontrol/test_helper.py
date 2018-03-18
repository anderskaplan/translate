# -*- coding: utf-8 -*-

import os
import shutil
import stat


def remove_readonly(func, path, _):
    """Clear the readonly bit and reattempt the removal"""
    os.chmod(path, stat.S_IWRITE)
    func(path)


class HelperTest(object):

    def remove_dirs(self, path):
        if os.path.exists(path):
            shutil.rmtree(path, onerror=remove_readonly)

    def get_test_path(self, method):
        return os.path.realpath("%s_%s" % (self.__class__.__name__, method.__name__))

    def setup_method(self, method):
        """Allocates a unique self.filename for the method, making sure it doesn't exist"""
        self.path = self.get_test_path(method)
        self.co_path = os.path.join(self.path, "checkout")
        self.remove_dirs(self.path)
        os.makedirs(self.path)
        self.setup_repo_and_checkout()

    def setup_repo_and_checkout(self):
        """Implementations should override this to create a repository and a
        clone/checkout.

        The repository should be in 'repo'.
        The checkout/clone should be in 'checkout'.
        """
        pass

    def teardown_method(self, method):
        """Makes sure that if self.filename was created by the method, it is cleaned up"""
        self.remove_dirs(self.path)

    def create_files(self, files_dict):
        """Creates file(s) named after the keys, with contents from the values
        of the dictionary."""
        for name, content in files_dict.items():
            assert not os.path.isabs(name)
            dirs = os.path.dirname(name)
            if dirs:
                os.path.makedirs(os.path.join(self.co_path, dirs))
            with open(os.path.join(self.co_path, dirs, name), 'wb') as fh:
                fh.write(content)
