# Copyright Concurrent Technologies Corporation 2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import atexit
import glob
import json
import logging
import os
import time
from datetime import datetime as DT
from locale import gettext as _
from sys import stderr
from typing import Sequence

from fapolicy_analyzer.ui.actions import (
    NotificationType,
    add_notification,
    apply_changesets,
    clear_changesets,
    restore_system_checkpoint,
)
from fapolicy_analyzer.ui.changeset_wrapper import Changeset
from fapolicy_analyzer.ui.store import dispatch, get_system_feature
from fapolicy_analyzer.util.format import f


class SessionManager:
    """
    A singleton wrapper class for maintaining user sessions
    """

    def __init__(self):
        self.__bAutosaveEnabled = False
        self.__tmpFileBasename = "/tmp/FaCurrentSession.tmp"
        self.__listAutosavedFilenames = []
        self.__iTmpFileCount = 2
        self.__changesets: Sequence[Changeset] = []

        get_system_feature().subscribe(on_next=self.on_next_system)

        # Register cleanup callback function
        atexit.register(self.cleanup)

    def __cleanup_autosave_sessions(self):
        """Deletes all current autosaved session files. These files were
        created during the current editing session, and are deleted after a deploy,
        or a session file open/restore operation."""
        logging.info("SessionManager::__cleanup_autosave_sessions()")
        logging.debug(self.__listAutosavedFilenames)
        for names in self.__listAutosavedFilenames:
            os.remove(names)
        self.__listAutosavedFilenames.clear()

    def __force_cleanup_autosave_sessions(self):
        """Brute force collection and deletion of all detected autosave files"""
        logging.debug("SessionManager::__force_cleanup_autosave_sessions()")
        strSearchPattern = self.__tmpFileBasename + "_*.json"
        logging.debug("Search Pattern: {}".format(strSearchPattern))
        listTmpFiles = glob.glob(strSearchPattern)
        logging.debug("Glob search results: {}".format(listTmpFiles))
        if listTmpFiles:
            for tmpF in listTmpFiles:
                # Add the tmp file to the deletion list if it's not currently in the list
                if os.path.isfile(tmpF) and tmpF not in self.__listAutosavedFilenames:
                    logging.debug(
                        "Adding Session file to deletion list: " "{}".format(tmpF)
                    )
                    self.__listAutosavedFilenames.append(tmpF)
            self.__cleanup_autosave_sessions()

    def cleanup(self):
        """SessionManager singleton / global object clean-up
        effectively the SessionManager's destructor."""
        logging.info("SessionManager::cleanup()")
        self.__force_cleanup_autosave_sessions()

    def on_next_system(self, system):
        if not system:
            return

        changesets = system.get("changesets").changesets

        # if changesets have changes request an auto save
        if self.__changesets != changesets:
            self.__changesets = changesets
            self.autosave_edit_session(self.__changesets)

    # ####################### Accessors Functions ####################
    def set_autosave_enable(self, bEnable):
        logging.info("SessionManager::set_autosave_enable: {}".format(bEnable))
        self.__bAutosaveEnabled = bEnable

    def set_autosave_filename(self, strFileBasename):
        logging.info(
            "SessionManager::set_autosave_filename: {}".format(strFileBasename)
        )
        self.__tmpFileBasename = strFileBasename

    def set_autosave_filecount(self, iFilecount):
        logging.info("SessionManager::set_autosave_filecount: {}".format(iFilecount))
        self.__iTmpFileCount = iFilecount

    # ######################## Edit Session Mgmt ############################
    def save_edit_session(self, data: Sequence[Changeset], strJsonFile: str):

        # Convert changeset list to list of dicts containing path/action pairs
        dictPA = [c.serialize() for c in data]
        logging.debug("Path/Action Dict: {}".format(dictPA))

        # Save the pending changeset queue to the specified json file
        logging.info("SessionManager::save_edit_session({})".format(strJsonFile))
        with open(strJsonFile, "w") as fp:
            json.dump(dictPA, fp, sort_keys=True, indent=4)

    def open_edit_session(self, strJsonFile: str) -> bool:
        logging.info(
            "Entered SessionManager::open_edit_session({})".format(strJsonFile)
        )
        with open(strJsonFile, "r") as fp:
            try:
                data = json.load(fp) or []
            except Exception as ex:
                logging.exception("json.load() failure: {}".format(ex))
                dispatch(
                    add_notification(
                        f(_("Failed to load edit session from file {strJsonFile}")),
                        NotificationType.ERROR,
                    )
                )
                return False

        logging.debug("Loaded dict = ", data)
        changesets = [Changeset.deserialize(d) for d in data]
        logging.debug("SessionManager::open_edit_session():{}".format(changesets))

        if changesets:
            # Deleting current edit session history prior to replacing it.
            dispatch(restore_system_checkpoint())
            dispatch(clear_changesets())
            dispatch(apply_changesets(*changesets))
        return True

    def detect_previous_session(self):
        """Searches for preexisting tmp files; Returns bool"""
        logging.info("SessionManager searching for previous session")
        strSearchPattern = self.__tmpFileBasename + "_*.json"
        logging.debug("Search Pattern: {}".format(strSearchPattern))
        listTmpFiles = glob.glob(strSearchPattern)
        listTmpFiles.sort()
        logging.debug("Glob search results: {}".format(listTmpFiles))
        if listTmpFiles:
            for tmpF in listTmpFiles:
                if os.path.isfile(tmpF):
                    logging.debug("Session file detected: {}".format(tmpF))
                    return True
        return False

    def restore_previous_session(self):
        """Restore latest prior session"""
        logging.info("SessionManager::restore_previous_session()")

        # Determine file to load, in newest to oldest order
        strSearchPattern = self.__tmpFileBasename + "_*.json"
        logging.debug("Search Pattern: {}".format(strSearchPattern))
        listTmpFiles = glob.glob(strSearchPattern)
        listTmpFiles.sort()
        listTmpFiles.reverse()
        logging.debug(listTmpFiles)

        # iterate through the time ordered files; stop on first successful load
        bReturn = False
        for tmpF in listTmpFiles:
            try:
                self.open_edit_session(tmpF)
                self.__cleanup_autosave_sessions()
                bReturn = True
                break

            except Exception:
                logging.warning("FAIL: Restoring {} load failure".format(tmpF))
                continue

        # All autosaved files failed on loading
        self.__cleanup_autosave_sessions()
        return bReturn

    def autosave_edit_session(self, data: Sequence[Changeset]):
        """Constructs a new tmp session filename w/timestamp, populates it with
        the current session state, saves it, and deletes the oldest tmp session file"""
        logging.info("SessionManager::autosave_edit_session()")

        # Bypass if autosave is not enabled
        if not self.__bAutosaveEnabled:
            logging.debug(" Session autosave is disabled/bypassed")
            return

        timestamp = DT.fromtimestamp(time.time()).strftime("%Y%m%d_%H%M%S_%f")
        strFilename = self.__tmpFileBasename + "_" + timestamp + ".json"
        logging.debug("  Writing to: {}".format(strFilename))
        try:
            self.save_edit_session(data, strFilename)
            self.__listAutosavedFilenames.append(strFilename)
            logging.debug(self.__listAutosavedFilenames)

            # Delete oldest tmp file
            if (
                self.__listAutosavedFilenames
                and len(self.__listAutosavedFilenames) > self.__iTmpFileCount
            ):
                self.__listAutosavedFilenames.sort()
                strOldestFile = self.__listAutosavedFilenames[0]
                logging.debug("Deleting: {}".format(strOldestFile))
                os.remove(strOldestFile)
                del self.__listAutosavedFilenames[0]
                logging.debug(self.__listAutosavedFilenames)

        except IOError as error:
            print(
                "Warning: __autosave_edit_session() failed: {}".format(error),
                file=stderr,
            )
            print("Continuing...", file=stderr)


sessionManager = SessionManager()
