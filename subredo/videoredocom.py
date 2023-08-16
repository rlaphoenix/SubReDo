import logging
from pathlib import Path
from typing import Any

import comtypes
import comtypes.client


class VideoReDo:
    def __init__(self):
        comtypes.CoInitialize()

        self.is_pro = False
        self.is_v5 = False

        try:
            vrd_silent = comtypes.client.CreateObject("VideoReDoPro6.VideoReDoSilent")  # check for v6 pro first
            self.is_pro = True
        except:
            try:
                vrd_silent = comtypes.client.CreateObject("VideoReDo6.VideoReDoSilent")  # check for v6 next
            except:
                try:
                    vrd_silent = comtypes.client.CreateObject("VideoReDo5.VideoReDoSilent")  # check for v5 last
                    self.is_v5 = True
                except:
                    raise EnvironmentError(
                        "Unable to Interface with VideoReDo. Is it installed? "
                        "Only VideoReDo 5, 6, and 6 Pro is supported."
                    )

        self.vrd = vrd_silent.VRDInterface
        self.vrd_version = self.vrd.ProgramGetVersionNumber
        logging.info(self.vrd_version)

    def __del__(self):
        if not self.vrd:
            return

        self.vrd.ProgramExit()

        comtypes.CoUninitialize()

    def get_version(self) -> str:
        """Get VideoReDo Installation Version."""
        return self.vrd_version

    def get_is_pro(self) -> bool:
        """Get if VideoReDo Installation is a Pro edition."""
        return self.is_pro

    def get_profiles(self) -> dict[str, dict[str, Any]]:
        """Get a list of Profiles."""
        if not self.vrd:
            return {}

        profiles = {}

        try:
            for i in range(self.vrd.ProfilesGetCount):
                profile_name = self.vrd.ProfilesGetProfileName(i)
                if self.is_v5:
                    enabled = self.vrd.ProfilesGetProfileEnabled(i)
                elif self.vrd.ProfilesGetProfileIsAdScan(i):
                    enabled = False
                else:
                    enabled = self.vrd.ProfilesGetProfileIsEnabled(i)
                profiles[profile_name] = {
                    "enabled": enabled,
                    "extension": self.vrd.ProfilesGetProfileExtension(i)
                }
        except Exception as e:
            print(e)
            raise

        return profiles

    def get_status(self) -> dict[str, Any]:
        """Get Status of VideoReDo Operation."""
        if not self.vrd:
            return {}

        try:
            return {
                "state": {
                    1: "running",
                    2: "paused"
                }.get(self.vrd.OutputGetState, "none"),
                "percent": self.vrd.OutputGetPercentComplete,
                "text": self.vrd.OutputGetStatusText
            }
        except Exception as e:
            print(e)
            raise

    def pause_output(self):
        """Instruct VideoReDo to pause the output process."""
        if not self.vrd:
            return False

        if self.vrd.OutputGetState == 1:
            self.vrd.OutputPause(True)

    def resume_output(self):
        """Instruct VideoReDo to resume the output process."""
        if not self.vrd:
            return False

        if self.vrd.OutputGetState == 2:
            self.vrd.OutputPause(False)

    def abort_output(self) -> bool:
        """
        Instruct VideoReDo to stop the output process.

        Note that output occurs in a background thread, and you should not assume that
        the abort has completed when this call returns. Continue to monitor
        `IsOutputInProgress` until that returns false.

        Returns True if output was in progress prior to calling this function, otherwise
        False.
        """
        if not self.vrd:
            return False

        if self.vrd.OutputGetState != 0:
            return self.vrd.OutputAbort()

    def file_open(self, filename: Path) -> bool:
        """
        Open a VideoReDo project file or a video file.

        If an MPEG program or transport stream file is specified, then FileOpen will open
        the first video stream it finds and the first audio stream it finds for that
        video. To specify specific audio and video PIDs either use a project file or use
        the FileOpenBatchPIDS if running QuickStream Fix.

        Parameters:
            filename: Path to a VideoReDo project file or video file.

        Returns True if successful, otherwise False.
        """
        if not self.vrd:
            return False

        # TODO: What is Param 2? Was added in v5
        return self.vrd.FileOpen(str(filename.absolute()), False)

    def file_save_as(self, filename: Path, profile: str) -> bool:
        """
        Save your current project to the specified file.

        Parameters:
            filename: Path to a video file.
            profile: Output Profile to use when saving.

        Returns True if successful, otherwise False.
        """
        if not self.vrd:
            return False

        return self.vrd.FileSaveAs(str(filename.absolute()), profile)

    @property
    def output_get_percent_complete(self) -> float:
        return self.vrd.OutputGetPercentComplete
