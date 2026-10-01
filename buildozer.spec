[app]

title = TikTok Downloader
package.name = tiktokdownloader
package.domain = org.kimo

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt

version = 1.0

requirements = python3,kivy,yt-dlp,pyjnius

orientation = portrait

fullscreen = 0


[buildozer]

log_level = 2
warn_on_root = 1


[app:android]

android.api = 35
android.minapi = 23

android.permissions = INTERNET,READ_MEDIA_VIDEO,READ_MEDIA_IMAGES,WRITE_EXTERNAL_STORAGE

android.archs = arm64-v8a,armeabi-v7a

android.accept_sdk_license = True
