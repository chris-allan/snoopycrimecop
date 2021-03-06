#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (C) 2012 Glencoe Software, Inc. All Rights Reserved.
# Use is subject to license terms supplied in LICENSE.txt
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import os
import shutil
import unittest

from scc import *

class TestDeploy(unittest.TestCase):

    def setUp(self):
        self.folder = os.path.abspath("deploy_test")
        self.live_folder = self.folder + ".live"
        self.tmp_folder = self.folder + ".tmp"
        
        # Initialize old folder
        os.mkdir(self.folder)
        self.oldfilename = "a"
        self.oldfile = os.path.join(self.folder, self.oldfilename)
        self.oldtargetfile = os.path.join(self.live_folder, self.oldfilename)
        open(self.oldfile, "w")
        self.olddirname = "d"
        self.olddir = os.path.join(self.folder, self.olddirname)
        self.oldtargetdir = os.path.join(self.live_folder, self.olddirname)
        os.mkdir(self.olddir)
        
        # Create tmp folder for content replacement
        os.mkdir(self.tmp_folder)
        self.newfilename = "b"
        self.newfile = os.path.join(self.tmp_folder, self.newfilename)
        self.newtargetfile = os.path.join(self.live_folder, self.newfilename)
        open(self.newfile, "w")

    def createBrokenSymlink(self, folder):
        self.brokenlinkname = "brokensymlink"
        self.brokenlink = os.path.join(folder, self.brokenlinkname)
        self.badsource = os.path.join(folder, "nonexistingsource")
        self.targetlink = os.path.join(self.folder, self.brokenlinkname)
        os.symlink(self.badsource, self.brokenlink)
        self.assertTrue(os.path.lexists(self.brokenlink))
        self.assertFalse(os.path.exists(self.brokenlink))

    def tearDown(self):
        for path in [self.folder, self.live_folder, self.tmp_folder]:
            if os.path.exists(path):
                if os.path.islink(path) or os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path)

    def testDeployInitInvalidFolder(self):
        self.assertRaises(Stop,  main, ["deploy", "--init", "invalid_folder"])

    def testDeployInitExistingLiveFolder(self):
        os.mkdir(self.live_folder)
        self.assertRaises(Stop,  main, ["deploy", "--init", self.folder])

    def testDeployInit(self):
        main(["deploy", "--init", self.folder])
        self.assertTrue(os.path.isdir(self.live_folder))
        self.assertTrue(os.path.islink(self.folder))
        self.assertTrue(os.path.isfile(self.oldtargetfile))
        self.assertTrue(os.path.isdir(self.oldtargetdir))

    def testDeployInitBrokenSymlink(self):
        self.createBrokenSymlink(self.folder)
        self.testDeployInit()
        self.assertFalse(os.path.lexists(self.targetlink))
        self.assertFalse(os.path.exists(self.targetlink))

    def testDeployNoInit(self):
        self.assertRaises(Stop,  main, ["deploy", self.folder])

    def testDeployWrongInit(self):
        os.mkdir(self.live_folder)
        self.assertRaises(Stop,  main, ["deploy", self.folder])

    def testDeployInvalidFolder(self):
        self.testDeployInit()
        self.assertRaises(Stop,  main, ["deploy", "invalid_folder"])

    def testDeployMissingTmpFolder(self):
        self.testDeployInit()
        shutil.rmtree(self.tmp_folder)
        self.assertRaises(Stop,  main, ["deploy", self.folder])

    def testDeploy(self):
        self.testDeployInit()
        main(["deploy", self.folder])
        self.assertFalse(os.path.exists(self.tmp_folder))
        self.assertFalse(os.path.exists(self.oldtargetfile))
        self.assertFalse(os.path.exists(self.oldtargetdir))
        self.assertTrue(os.path.isfile(self.newtargetfile))

    def testDeployBrokenSymlink(self):
        self.createBrokenSymlink(self.tmp_folder)
        self.testDeploy()
        self.assertFalse(os.path.lexists(self.targetlink))
        self.assertFalse(os.path.exists(self.targetlink))

if __name__ == '__main__':
    unittest.main()
