'''
NodeJS-related BuildTargets.

Copyright (c) 2015 - 2017 Rob "N3X15" Nelson <nexisentertainment@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''
import os
from buildtools import os_utils
from buildtools.maestro.base_target import SingleBuildTarget


class _NPMLikeBuildTarget(SingleBuildTarget):
    def __init__(self, base_command, working_dir='.', opts=[], files=[], target=None, dependencies=[], exe_path=None):
        self.working_dir = working_dir
        self.opts = opts
        self.exe_path = exe_path
        if self.exe_path is None:
            self.exe_path = os_utils.which(base_command)
        super().__init__(target=target, files=files, dependencies=dependencies)

    def get_config(self):
        return {
            'working-dir': self.working_dir,
            'opts': self.opts,
            'exe-path': self.exe_path
        }

    def build(self):
        with os_utils.Chdir(self.working_dir):
            os_utils.cmd([self.exe_path] + self.opts, show_output=True, echo=True, critical=True)
        if not os.path.isfile(self.target):
            self.touch(self.target)


class YarnBuildTarget(_NPMLikeBuildTarget):
    BT_TYPE = 'Yarn'
    BT_LABEL = 'YARN'
    def __init__(self, working_dir='.', opts=[], modules_dir='node_modules', target=None, dependencies=[], yarn_path=None):
        if target is None:
            target = os.path.join(working_dir, modules_dir, '.yarn-integrity')
        super().__init__('yarn', working_dir=working_dir, opts=opts, target=target, exe_path=yarn_path, files=[os.path.join(working_dir, 'package.json')], dependencies=[])


class NPMBuildTarget(_NPMLikeBuildTarget):
    BT_TYPE = 'NPM'
    BT_LABEL = 'NPM'
    def __init__(self, working_dir='.', opts=[], modules_dir='node_modules', target=None, dependencies=[], npm_path=None):
        if target is None:
            target = os.path.join(working_dir, modules_dir, '.npm.target')
        super().__init__('npm', working_dir=working_dir, opts=opts, target=target, exe_path=npm_path, files=[os.path.join(working_dir, 'package.json')], dependencies=[])


class BowerBuildTarget(_NPMLikeBuildTarget):
    BT_TYPE = 'Bower'
    BT_LABEL = 'BOWER'
    def __init__(self, working_dir='.', opts=[], modules_dir='bower_components', target=None, dependencies=[], bower_path=None):
        if target is None:
            target = os.path.join(working_dir, modules_dir, '.bower.target')
        super().__init__('bower', working_dir=working_dir, opts=opts, target=target, exe_path=bower_path, files=[os.path.join(working_dir, 'bower.json')], dependencies=[])


class GruntBuildTarget(_NPMLikeBuildTarget):
    BT_TYPE = 'Grunt'
    BT_LABEL = 'GRUNT'
    def __init__(self, working_dir='.', opts=[], target=None, dependencies=[], grunt_pathc=None):
        if target is None:
            target = os.path.join(working_dir, 'tmp', '.grunt.target')
        super().__init__('grunt', working_dir=working_dir, opts=opts, target=target, exe_path=grunt_path, files=[os.path.join(working_dir, 'Gruntfile.js')], dependencies=[])
