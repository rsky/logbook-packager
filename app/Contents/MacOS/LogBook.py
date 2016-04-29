#!/usr/bin/python
# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import os
import subprocess

# アプリケーションバンドル情報
BUNDLE_IDENTIFIER = 'logbook_bundle_identifier_placeholder'
BUNDLE_NAME = 'logbook_bundle_name_placeholder'
ICON_NAME = 'logbook_icon_name_placeholder'

# アプリケーションバンドル内パス
MY_PATH = os.path.abspath(__file__)
CONTENTS_DIR = os.path.dirname(os.path.dirname(MY_PATH))
LOGBOOK_JAR_PATH = os.path.join(CONTENTS_DIR, 'Java', 'logbook-kai.jar')
RESOURCES_DIR = os.path.join(CONTENTS_DIR, 'Resources')
ICON_PATH = os.path.join(RESOURCES_DIR, ICON_NAME)

# ホームディレクトリ以下のパス
LIBRARY_DIR = os.path.join(os.environ['HOME'], 'Library')
APPLICATION_SUPPORT_DIR = os.path.join(LIBRARY_DIR, 'Application Support')
LOGBOOK_SUPPORT_DIR = os.path.join(APPLICATION_SUPPORT_DIR, BUNDLE_NAME)

# 起動ディレクトリ以下に作るサブディレクトリ
SUB_DIRECTORIES = (
     'battlelog',
     'config',
     'plugins',
     'resources',
     'sounds/alert',
     'sounds/mission',
     'sounds/ndock',
)

# パーミッション
UMASK = 0o022
DIRECTORY_PERM = 0o755

# umask設定
os.umask(UMASK)

# 各種ディレクトリ作成
if not os.path.exists(LOGBOOK_SUPPORT_DIR):
    os.makedirs(LOGBOOK_SUPPORT_DIR, DIRECTORY_PERM)

os.chdir(LOGBOOK_SUPPORT_DIR)
for subdir in SUB_DIRECTORIES:
    if not os.path.exists(subdir):
        os.makedirs(subdir, DIRECTORY_PERM)

# アイコンを指定して起動
subprocess.call((
    'java',
    '-Xdock:icon={0}'.format(ICON_PATH),
    '-jar', LOGBOOK_JAR_PATH,
))
