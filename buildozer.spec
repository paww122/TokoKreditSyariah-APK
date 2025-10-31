[app]

# (str) Title of your application
title = Toko Kredit Syariah

# (str) Package name
package.name = tokokreditsyariah

# (str) Package domain (needed for android/ios packaging)
package.domain = com.tokokreditsyariah

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,gif,kv,atlas,txt,json,ttf,otf,wav,mp3,ogg,zip,html,css,js,xml

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*,images/*.png,data/*.json,fonts/*.ttf

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec,pyc,pyo,so

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests, bin, venv, .buildozer, __pycache__, .git, .github, .vscode, build, dist

# (list) List of exclusions using pattern matching
source.exclude_patterns = license,images/*/*.jpg,*.md,.gitignore

# (str) Application versioning (method 1)
version = 1.0.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements - synchronized with requirements.txt
requirements = python3,kivy==2.1.0,kivymd==1.1.1,cryptography==41.0.7,pbkdf2==1.3,pyserial==3.5,pybluez==0.23,google-api-python-client==2.108.0,google-auth-httplib2==0.1.1,google-auth-oauthlib==1.1.0,reportlab==4.0.7,plyer==2.1.0,python-dateutil==2.8.2,pillow==9.5.0,requests==2.31.0,pyjnius,android

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for android toolchain)
android.presplash_color = #FFFFFF

# (list) Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, BLUETOOTH, BLUETOOTH_ADMIN

# (int) Target Android API, should be as high as possible.
android.api = 33

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity