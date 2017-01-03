# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import os
import plistlib
import re
import shutil
import subprocess
from argparse import ArgumentParser
from codecs import BOM_UTF16_LE
from zipfile import ZipFile


# 各種ファイル・ディレクトリ名
EXECUTABLE_NAME = 'LogBook.py'
ICON_FILE_NAME = 'LogBook.icns'
ICON_SET_NAME = 'LogBook.iconset'
JAR_NAME = 'logbook-kai.jar'

# バンドル情報
DEFAULT_APP_NAME = 'LogBook.app'
DEFAULT_BUNDLE_IDENTIFIER = 'com.github.sanaehirotaka.logbook-kai'
DEFAULT_BUNDLE_NAME = 'LogBook'
DISPLAY_NAME = 'LogBook'
LOCALIZED_BUNDLE_NAMES = {
    'en': 'LogBook',
    'ja': '航海日誌',
}

# パーミッション
UMASK = 0o022
DIRECTORY_PERM = 0o755
EXECUTABLE_PERM = 0o755


class LogBookAppBuilder(object):
    def __init__(self, app_name, bundle_identifier, bundle_name, destination):
        self.bundle_identifier = bundle_identifier
        self.bundle_name = bundle_name
        self.app_dir = os.path.join(destination, app_name)
        self.contents_dir = os.path.join(self.app_dir, 'Contents')
        self.java_dir = os.path.join(self.contents_dir, 'Java')
        self.resources_dir = os.path.join(self.contents_dir, 'Resources')
        self.iconset_dir = os.path.join(destination, ICON_SET_NAME)
        self.extract_dir = os.path.join(destination, 'logbook-kai')

    def prepare(self):
        """
        作業ディレクトリを初期化する
        """
        for directory in (self.app_dir, self.iconset_dir, self.extract_dir):
            if os.path.exists(directory):
                shutil.rmtree(directory)

    def copy_app(self, source):
        """
        アプリケーションバンドルのひな形をコピーし、
        起動スクリプトに情報を書き込む
        """
        shutil.copytree(source, self.app_dir)
        subprocess.call((
            'find',
            self.app_dir,
            '-name', '.DS_Store',
            '-delete',
        ))
        for directory in (self.java_dir, self.resources_dir):
            if not os.path.exists(directory):
                os.makedirs(directory, DIRECTORY_PERM)

        logbook_py = os.path.join(self.contents_dir, 'MacOS', EXECUTABLE_NAME)
        content = open(logbook_py, 'rb').read().decode('utf-8')
        replacements = (
            ('logbook_bundle_identifier_placeholder', self.bundle_identifier),
            ('logbook_bundle_name_placeholder', self.bundle_name),
            ('logbook_icon_name_placeholder', ICON_FILE_NAME),
        )
        for old_str, new_str in replacements:
            content = content.replace(old_str, new_str)
        open(logbook_py, 'wb').write(content.encode('utf-8'))
        os.chmod(logbook_py, EXECUTABLE_PERM)

    def make_plist(self, version=None):
        """
        アプリケーションバンドルのInfo.plistを生成する
        """
        info = {
            'CFBundleDisplayName': DISPLAY_NAME,
            'CFBundleExecutable': EXECUTABLE_NAME,
            'CFBundleIconFile': ICON_FILE_NAME,
            'CFBundleIdentifier': self.bundle_identifier,
            'CFBundleInfoDictionaryVersion': '6.0',
            'CFBundleLocalizations': list(LOCALIZED_BUNDLE_NAMES.keys()),
            'CFBundleName': self.bundle_name,
            'CFBundlePackageType': 'APPL',
            'CFBundleShortVersionString': '1',
            'CFBundleSignature': '???',
            'CFBundleVersion': '1',
            'LSHasLocalizedDisplayName': True,
        }
        if version:
            info['CFBundleShortVersionString'] = version
        path = os.path.join(self.contents_dir, 'Info.plist')
        plistlib.writePlist(info, path)

    def make_icon(self, source):
        """
        オリジナル画像を各種アイコンサイズにリサイズし、
        アプリケーションバンドル内に.icnsファイルを生成する
        """
        destination = os.path.join(self.resources_dir, ICON_FILE_NAME)
        _, extension = os.path.splitext(source)
        if extension == '.icns':
            shutil.copyfile(source, destination)
            return

        if not os.path.exists(self.iconset_dir):
            os.makedirs(self.iconset_dir, DIRECTORY_PERM)

        for x in (16, 32, 128, 256, 512):
            self.resize_icon(source, x, False)
            self.resize_icon(source, x, True)

        subprocess.call((
            'iconutil',
            '-c', 'icns',
            '-o', destination,
            self.iconset_dir,
        ))

    def resize_icon(self, source, size, retina=False):
        """
        アイコン画像をリサイズする
        """
        if retina:
            resolution = str(size * 2)
            suffix = '@2x'
        else:
            resolution = str(size)
            suffix = ''

        filename = 'icon_{0}x{0}{1}.png'.format(size, suffix)
        subprocess.call((
            'sips',
            '-z', resolution, resolution,
            source,
            '--out', os.path.join(self.iconset_dir, filename),
        ))

    def localize(self):
        """
        アプリケーション名のローカライゼーションファイルを生成する
        """
        for lang, name in LOCALIZED_BUNDLE_NAMES.items():
            lproj = os.path.join(self.resources_dir, '{0}.lproj'.format(lang))
            if not os.path.exists(lproj):
                os.makedirs(lproj, DIRECTORY_PERM)

            with open(os.path.join(lproj, 'InfoPlist.strings'), 'wb') as f:
                f.write(BOM_UTF16_LE)
                f.write((
                    'CFBundleName = "{name}";\n'
                    'CFBundleDisplayName = "{name}";\n'
                ).format(name=name).encode('utf-16le'))

    def make_zip(self, version):
        """
        アプリケーションバンドルののzipアーカイブを作成する
        """
        destination = os.path.dirname(self.app_dir)
        filename = 'LogBook-OSX-{}.zip'.format(version)
        zip_path = os.path.join(destination, filename)

        if os.path.exists(zip_path):
            os.unlink(zip_path)

        with ZipFile(zip_path, 'w') as zip:
            for dirpath, dirnames, filenames in os.walk(self.app_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    arc_name = os.path.relpath(filepath, destination)
                    zip.write(filepath, arc_name)
                for dirname in dirnames:
                    filepath = os.path.join(dirpath, dirname)
                    arc_name = os.path.relpath(filepath, destination) + os.path.sep
                    zip.write(filepath, arc_name)

    def extract_zip(self, source):
        """
        Zipアーカイブの内容をアプリケーションバンドル内に展開する
        """
        ZipFile(source, 'r').extractall(self.extract_dir)
        self.copy_jar(os.path.join(self.extract_dir, JAR_NAME))

    def copy_jar(self, source):
        """
        jarをアプリケーションバンドル内にコピーする
        """
        destination = os.path.join(self.java_dir, JAR_NAME)
        shutil.copyfile(source, destination)


def getargs():
    parser = ArgumentParser(description="LogBook application bundler")
    parser.add_argument('archive', metavar='FILE', nargs=1,
                        help='logbook-kaiのzipまたはjar')
    parser.add_argument('-T', '--template', metavar='TMPL_DIR',
                        default='app',
                        help='アプリケーションのひな形')
    parser.add_argument('-D', '--destination', metavar='DEST_DIR',
                        default='build',
                        help='出力先ディレクトリ')
    parser.add_argument('-A', '--app-name', metavar='NAME',
                        default=DEFAULT_APP_NAME, help='アプリケーション名')
    parser.add_argument('-N', '--bundle-name', metavar='NAME',
                        default=DEFAULT_BUNDLE_NAME, help='バンドル名')
    parser.add_argument('-B', '--bundle-identifier', metavar='IDENTIFIER',
                        default=DEFAULT_BUNDLE_IDENTIFIER, help='バンドルID')
    parser.add_argument('-I', '--icon', metavar='ICON', help='アイコン画像')
    parser.add_argument('-V', '--version', metavar='VERSION', help='バージョン番号')
    return parser.parse_args()


def main():
    os.umask(UMASK)
    args = getargs()

    source = args.archive[0]
    version = args.version
    if version is None:
        basename = os.path.basename(source)
        m = re.match(r'logbook-kai[\-_]([0-9.]+)[\-.](?:jar|zip)', basename)
        if m:
            version = m.group(1)

    app_name = args.app_name
    if not app_name.endswith('.app'):
        app_name += '.app'

    builder = LogBookAppBuilder(app_name=app_name,
                                bundle_name=args.bundle_name,
                                bundle_identifier=args.bundle_identifier,
                                destination=args.destination)
    builder.prepare()
    builder.copy_app(args.template)
    _, extension = os.path.splitext(source)
    if extension == '.jar':
        builder.copy_jar(source)
    else:
        builder.extract_zip(source)
    if args.icon:
        builder.make_icon(args.icon)
    builder.make_plist(version)
    builder.localize()
    builder.make_zip(version)


if __name__ == '__main__':
    main()
