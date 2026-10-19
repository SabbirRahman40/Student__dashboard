
[app]

title = Sabbir Smart Student Dashboard
package.name = studentdashboard
package.domain = com.sabbirrahman

source.dir = .
source.include_exts = py,json,png,jpg,jpeg,kv,atlas,ttf,otf
source.exclude_dirs = .git,.github,.buildozer,bin,__pycache__,venv,.venv

version = 1.0.0

requirements = python3,kivy

p4a.branch = develop
p4a.commit = d2ee8c5

orientation = portrait
fullscreen = 0

android.permissions =
android.api = 34
android.minapi = 21
android.ndk = 28c
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
android.copy_libs = 1
android.category = education

log_level = 2

[buildozer]

log_level = 2
build_dir = ./.buildozer
bin_dir = ./bin
