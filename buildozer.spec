[app]
title = CASSINELLI CLIENTES
package.name = cassinelliclientes
package.domain = org.cassinelli
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas
source.exclude_dirs = .git,__pycache__
version = 1.0.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 23
android.archs = arm64-v8a
android.ndk = 25b
android.accept_sdk_license = True

p4a.branch = v2024.01.21

[buildozer]
log_level = 2
warn_on_root = 1
