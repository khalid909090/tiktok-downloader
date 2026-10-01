import os
import threading
import subprocess

import yt_dlp

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder


# ==================================================
# ANDROID / PYJNIUS
# ==================================================

try:
    from jnius import autoclass
    PYJNIUS_AVAILABLE = True
except ImportError:
    PYJNIUS_AVAILABLE = False


# ==================================================
# SAVE LOCATION
# ==================================================

SAVE_FOLDER = "/storage/emulated/0/Download/Gun"

os.makedirs(SAVE_FOLDER, exist_ok=True)


# ==================================================
# LOGGER
# ==================================================

class MyLogger:

    def debug(self, msg):
        print("[DEBUG]", msg)

    def info(self, msg):
        print("[INFO]", msg)

    def warning(self, msg):
        print("[WARNING]", msg)

    def error(self, msg):
        print("[ERROR]", msg)


# ==================================================
# USER INTERFACE
# ==================================================

KV = """

#:import dp kivy.metrics.dp

BoxLayout:

    orientation: "vertical"

    padding: dp(18)
    spacing: dp(14)

    canvas.before:

        Color:
            rgba: 0.035, 0.035, 0.045, 1

        Rectangle:
            pos: self.pos
            size: self.size


    # ==================================================
    # TITLE
    # ==================================================

    Label:

        text: "TikTok Downloader"

        font_size: "29sp"

        bold: True

        color: 1, 1, 1, 1

        size_hint_y: None

        height: dp(65)


    # ==================================================
    # URL
    # ==================================================

    TextInput:

        id: url

        hint_text: "Paste TikTok video URL"

        font_size: "17sp"

        multiline: False

        padding: dp(12)

        size_hint_y: None

        height: dp(55)


    # ==================================================
    # DOWNLOAD
    # ==================================================

    Button:

        id: download_button

        text: "DOWNLOAD VIDEO"

        font_size: "19sp"

        bold: True

        size_hint_y: None

        height: dp(58)

        on_release: app.start_download()


    # ==================================================
    # PROGRESS
    # ==================================================

    ProgressBar:

        id: progress

        max: 100

        value: 0

        size_hint_y: None

        height: dp(12)


    # ==================================================
    # PERCENT
    # ==================================================

    Label:

        id: percent

        text: "0%"

        font_size: "22sp"

        color: 1, 1, 1, 1

        size_hint_y: None

        height: dp(40)


    # ==================================================
    # STATUS
    # ==================================================

    Label:

        id: status

        text: "Ready"

        font_size: "17sp"

        color: 0.8, 0.8, 0.8, 1

        text_size: self.width, None

        halign: "center"


    # ==================================================
    # ERROR
    # ==================================================

    Label:

        id: error

        text: ""

        font_size: "13sp"

        color: 1, 0.35, 0.35, 1

        text_size: self.width, None

        halign: "center"


    Widget:


    # ==================================================
    # OPEN FOLDER
    # ==================================================

    Button:

        text: "OPEN DOWNLOAD FOLDER"

        font_size: "17sp"

        size_hint_y: None

        height: dp(55)

        on_release: app.open_folder()


    # ==================================================
    # CLEAR
    # ==================================================

    Button:

        text: "CLEAR"

        font_size: "17sp"

        size_hint_y: None

        height: dp(50)

        on_release: app.clear_url()

"""


# ==================================================
# APPLICATION
# ==================================================

class TikTokDownloader(App):


    # ==================================================
    # BUILD
    # ==================================================

    def build(self):

        self.title = "TikTok Downloader"

        self.mActivity = None

        if PYJNIUS_AVAILABLE:

            try:

                PythonActivity = autoclass(
                    "org.kivy.android.PythonActivity"
                )

                self.mActivity = PythonActivity.mActivity

            except Exception as e:

                print(
                    "Android Activity error:",
                    e
                )

        return Builder.load_string(KV)


    # ==================================================
    # START DOWNLOAD
    # ==================================================

    def start_download(self):

        url = self.root.ids.url.text.strip()

        self.root.ids.error.text = ""


        # Empty URL

        if not url:

            self.root.ids.status.text = (
                "Please paste a TikTok URL"
            )

            return


        # Check TikTok URL

        if "tiktok.com" not in url.lower():

            self.root.ids.status.text = (
                "Invalid TikTok URL"
            )

            return


        # Reset UI

        self.root.ids.progress.value = 0

        self.root.ids.percent.text = "0%"

        self.root.ids.status.text = (
            "Preparing download..."
        )

        self.root.ids.error.text = ""


        # Disable button

        self.root.ids.download_button.disabled = True


        # Background thread

        thread = threading.Thread(

            target=self.download_video,

            args=(url,),

            daemon=True

        )

        thread.start()


    # ==================================================
    # DOWNLOAD VIDEO
    # ==================================================

    def download_video(self, url):

        try:

            # Make sure folder exists

            os.makedirs(
                SAVE_FOLDER,
                exist_ok=True
            )


            options = {

                # ------------------------------------------
                # OUTPUT FILE
                # ------------------------------------------

                "outtmpl": os.path.join(
                    SAVE_FOLDER,
                    "%(title)s [%(id)s].%(ext)s"
                ),


                # ------------------------------------------
                # FORMAT
                # ------------------------------------------

                "format":
                    "bv*[ext=mp4]+ba[ext=m4a]/"
                    "b[ext=mp4]/"
                    "best",


                # ------------------------------------------
                # SINGLE VIDEO
                # ------------------------------------------

                "noplaylist": True,


                # ------------------------------------------
                # RETRIES
                # ------------------------------------------

                "retries": 5,

                "fragment_retries": 5,


                # ------------------------------------------
                # CONTINUE
                # ------------------------------------------

                "continuedl": True,


                # ------------------------------------------
                # QUIET
                # ------------------------------------------

                "quiet": True,

                "no_warnings": True,


                # ------------------------------------------
                # LOGGER
                # ------------------------------------------

                "logger": MyLogger(),


                # ------------------------------------------
                # PROGRESS
                # ------------------------------------------

                "progress_hooks": [
                    self.progress_hook
                ],

            }


            print(
                "================================"
            )

            print(
                "Starting yt-dlp"
            )

            print(
                "URL:",
                url
            )

            print(
                "SAVE:",
                SAVE_FOLDER
            )

            print(
                "================================"
            )


            # yt-dlp

            with yt_dlp.YoutubeDL(
                options
            ) as ydl:

                ydl.download([url])


            # Success

            Clock.schedule_once(
                lambda dt:
                self.download_finished()
            )


        except Exception as e:

            error = str(e)

            print(
                "================================"
            )

            print(
                "DOWNLOAD ERROR:"
            )

            print(error)

            print(
                "================================"
            )


            Clock.schedule_once(
                lambda dt:
                self.download_error(error)
            )


    # ==================================================
    # PROGRESS HOOK
    # ==================================================

    def progress_hook(self, data):

        try:

            status = data.get(
                "status"
            )


            # ------------------------------------------
            # DOWNLOADING
            # ------------------------------------------

            if status == "downloading":

                total = (
                    data.get("total_bytes")
                    or
                    data.get(
                        "total_bytes_estimate"
                    )
                )


                downloaded = data.get(
                    "downloaded_bytes",
                    0
                )


                if total:

                    percent = (
                        downloaded /
                        total
                    ) * 100


                    speed = data.get(
                        "speed"
                    )


                    eta = data.get(
                        "eta"
                    )


                    Clock.schedule_once(

                        lambda dt:
                        self.update_progress(
                            percent,
                            speed,
                            eta
                        )

                    )


            # ------------------------------------------
            # FINISHED
            # ------------------------------------------

            elif status == "finished":

                Clock.schedule_once(

                    lambda dt:
                    self.update_progress(
                        100,
                        None,
                        None
                    )

                )


        except Exception as e:

            print(
                "Progress error:",
                e
            )


    # ==================================================
    # UPDATE PROGRESS
    # ==================================================

    def update_progress(
        self,
        percent,
        speed=None,
        eta=None
    ):

        self.root.ids.progress.value = (
            percent
        )


        self.root.ids.percent.text = (
            f"{percent:.1f}%"
        )


        # Speed

        if speed:

            if speed >= 1024 * 1024:

                speed_text = (
                    f"{speed / 1024 / 1024:.2f} MB/s"
                )

            elif speed >= 1024:

                speed_text = (
                    f"{speed / 1024:.1f} KB/s"
                )

            else:

                speed_text = (
                    f"{speed:.0f} B/s"
                )


            if eta is not None:

                status = (
                    f"Downloading... "
                    f"{speed_text} | "
                    f"ETA: {eta}s"
                )

            else:

                status = (
                    f"Downloading... "
                    f"{speed_text}"
                )


            self.root.ids.status.text = (
                status
            )

        else:

            self.root.ids.status.text = (
                "Downloading..."
            )


    # ==================================================
    # SUCCESS
    # ==================================================

    def download_finished(self):

        self.root.ids.progress.value = 100

        self.root.ids.percent.text = "100%"

        self.root.ids.status.text = (
            "Download completed successfully!"
        )

        self.root.ids.error.text = ""

        self.root.ids.download_button.disabled = False


    # ==================================================
    # ERROR
    # ==================================================

    def download_error(
        self,
        error
    ):

        self.root.ids.status.text = (
            "Download failed!"
        )


        # Make error readable

        if len(error) > 800:

            error = error[-800:]


        self.root.ids.error.text = (
            "Error:\n" + error
        )


        self.root.ids.download_button.disabled = False


    # ==================================================
    # CLEAR
    # ==================================================

    def clear_url(self):

        self.root.ids.url.text = ""

        self.root.ids.progress.value = 0

        self.root.ids.percent.text = "0%"

        self.root.ids.status.text = "Ready"

        self.root.ids.error.text = ""

        self.root.ids.download_button.disabled = False


    # ==================================================
    # OPEN DOWNLOAD FOLDER
    # ==================================================

    def open_folder(self):

        try:

            # Make sure folder exists

            os.makedirs(
                SAVE_FOLDER,
                exist_ok=True
            )


            # ------------------------------------------
            # ANDROID / PYJNIUS
            # ------------------------------------------

            if PYJNIUS_AVAILABLE and self.mActivity:

                Intent = autoclass(
                    "android.content.Intent"
                )

                Uri = autoclass(
                    "android.net.Uri"
                )


                # --------------------------------------
                # First attempt:
                # Open Download folder
                # --------------------------------------

                intent = Intent(
                    Intent.ACTION_VIEW
                )


                intent.setDataAndType(
                    Uri.parse(
                        "content://com.android.externalstorage.documents/"
                        "document/primary%3ADownload"
                    ),
                    "vnd.android.document/directory"
                )


                intent.addFlags(
                    Intent.FLAG_ACTIVITY_NEW_TASK
                )


                try:

                    self.mActivity.startActivity(
                        intent
                    )

                    self.root.ids.status.text = (
                        "Opening Download folder..."
                    )

                    return

                except Exception as e:

                    print(
                        "Android folder intent failed:",
                        e
                    )


            # ------------------------------------------
            # Fallback: AM command
            # ------------------------------------------

            result = subprocess.run(

                [
                    "am",
                    "start",
                    "-a",
                    "android.intent.action.VIEW",
                    "-d",
                    "content://com.android.externalstorage.documents/root/primary"
                ],

                capture_output=True,

                text=True
            )


            print(
                "Folder command:",
                result.stdout
            )

            print(
                "Folder error:",
                result.stderr
            )


            self.root.ids.status.text = (
                "Opening file manager..."
            )


        except Exception as e:

            print(
                "Folder error:",
                e
            )

            self.root.ids.status.text = (
                "Cannot open file manager"
            )


    # ==================================================
    # RUN
    # ==================================================


if __name__ == "__main__":

    TikTokDownloader().run()