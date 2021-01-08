'''
flameTimewarpML
Flame 2020 and higher
written by Andrii Toloshnyy
andriy.toloshnyy@gmail.com
'''

import os
import sys
import time
import threading
import atexit
from pprint import pprint
from pprint import pformat

menu_group_name = 'Timewarp ML'
DEBUG = True

__version__ = 'v0.0.1'

class flameAppFramework(object):
    # flameAppFramework class takes care of preferences

    class prefs_dict(dict):
        # subclass of a dict() in order to directly link it 
        # to main framework prefs dictionaries
        # when accessed directly it will operate on a dictionary under a 'name'
        # key in master dictionary.
        # master = {}
        # p = prefs(master, 'app_name')
        # p['key'] = 'value'
        # master - {'app_name': {'key', 'value'}}
            
        def __init__(self, master, name, **kwargs):
            self.name = name
            self.master = master
            if not self.master.get(self.name):
                self.master[self.name] = {}
            self.master[self.name].__init__()

        def __getitem__(self, k):
            return self.master[self.name].__getitem__(k)
        
        def __setitem__(self, k, v):
            return self.master[self.name].__setitem__(k, v)

        def __delitem__(self, k):
            return self.master[self.name].__delitem__(k)
        
        def get(self, k, default=None):
            return self.master[self.name].get(k, default)
        
        def setdefault(self, k, default=None):
            return self.master[self.name].setdefault(k, default)

        def pop(self, k, v=object()):
            if v is object():
                return self.master[self.name].pop(k)
            return self.master[self.name].pop(k, v)
        
        def update(self, mapping=(), **kwargs):
            self.master[self.name].update(mapping, **kwargs)
        
        def __contains__(self, k):
            return self.master[self.name].__contains__(k)

        def copy(self): # don't delegate w/ super - dict.copy() -> dict :(
            return type(self)(self)
        
        def keys(self):
            return self.master[self.name].keys()

        @classmethod
        def fromkeys(cls, keys, v=None):
            return self.master[self.name].fromkeys(keys, v)
        
        def __repr__(self):
            return '{0}({1})'.format(type(self).__name__, self.master[self.name].__repr__())

        def master_keys(self):
            return self.master.keys()

    def __init__(self):
        self.name = self.__class__.__name__
        self.bundle_name = 'flameTimewarpML'

        # self.prefs scope is limited to flame project and user
        self.prefs = {}
        self.prefs_user = {}
        self.prefs_global = {}
        self.debug = DEBUG
        
        try:
            import flame
            self.flame = flame
            self.flame_project_name = self.flame.project.current_project.name
            self.flame_user_name = flame.users.current_user.name
        except:
            self.flame = None
            self.flame_project_name = None
            self.flame_user_name = None
        
        import socket
        self.hostname = socket.gethostname()
        
        if sys.platform == 'darwin':
            self.prefs_folder = os.path.join(
                os.path.expanduser('~'),
                 'Library',
                 'Caches',
                 self.bundle_name)
        elif sys.platform.startswith('linux'):
            self.prefs_folder = os.path.join(
                os.path.expanduser('~'),
                '.config',
                self.bundle_name)

        self.prefs_folder = os.path.join(
            self.prefs_folder,
            self.hostname,
        )

        self.log('[%s] waking up' % self.__class__.__name__)
        self.load_prefs()

        # preferences defaults

        if not self.prefs_global.get('bundle_location'):
            self.bundle_location = os.path.join(
                os.path.expanduser('~'),
                 self.bundle_name)
        else:
            self.bundle_location = self.prefs_global.get('bundle_location')

        #    self.prefs_global['menu_auto_refresh'] = {
        #        'media_panel': True,
        #        'batch': True,
        #        'main_menu': True
        #    }
        
        self.apps = []

        # unpack bundle sequence
        self.unpacking_thread = threading.Thread(target=self.unpack_bundle, args=())
        self.unpacking_thread.daemon = True
        self.unpacking_thread.start()

    def log(self, message):
        if self.debug:
            print ('[DEBUG %s] %s' % (self.bundle_name, message))

    def load_prefs(self):
        import pickle
        
        prefix = self.prefs_folder + os.path.sep + self.bundle_name
        prefs_file_path = prefix + '.' + self.flame_user_name + '.' + self.flame_project_name + '.prefs'
        prefs_user_file_path = prefix + '.' + self.flame_user_name  + '.prefs'
        prefs_global_file_path = prefix + '.prefs'

        try:
            prefs_file = open(prefs_file_path, 'r')
            self.prefs = pickle.load(prefs_file)
            prefs_file.close()
            self.log('preferences loaded from %s' % prefs_file_path)
            self.log('preferences contents:\n' + pformat(self.prefs))
        except:
            self.log('unable to load preferences from %s' % prefs_file_path)

        try:
            prefs_file = open(prefs_user_file_path, 'r')
            self.prefs_user = pickle.load(prefs_file)
            prefs_file.close()
            self.log('preferences loaded from %s' % prefs_user_file_path)
            self.log('preferences contents:\n' + pformat(self.prefs_user))
        except:
            self.log('unable to load preferences from %s' % prefs_user_file_path)

        try:
            prefs_file = open(prefs_global_file_path, 'r')
            self.prefs_global = pickle.load(prefs_file)
            prefs_file.close()
            self.log('preferences loaded from %s' % prefs_global_file_path)
            self.log('preferences contents:\n' + pformat(self.prefs_global))

        except:
            self.log('unable to load preferences from %s' % prefs_global_file_path)

        return True

    def save_prefs(self):
        import pickle

        if not os.path.isdir(self.prefs_folder):
            try:
                os.makedirs(self.prefs_folder)
            except:
                self.log('unable to create folder %s' % prefs_folder)
                return False

        prefix = self.prefs_folder + os.path.sep + self.bundle_name
        prefs_file_path = prefix + '.' + self.flame_user_name + '.' + self.flame_project_name + '.prefs'
        prefs_user_file_path = prefix + '.' + self.flame_user_name  + '.prefs'
        prefs_global_file_path = prefix + '.prefs'

        try:
            prefs_file = open(prefs_file_path, 'w')
            pickle.dump(self.prefs, prefs_file)
            prefs_file.close()
            self.log('preferences saved to %s' % prefs_file_path)
            self.log('preferences contents:\n' + pformat(self.prefs))
        except:
            self.log('unable to save preferences to %s' % prefs_file_path)

        try:
            prefs_file = open(prefs_user_file_path, 'w')
            pickle.dump(self.prefs_user, prefs_file)
            prefs_file.close()
            self.log('preferences saved to %s' % prefs_user_file_path)
            self.log('preferences contents:\n' + pformat(self.prefs_user))
        except:
            self.log('unable to save preferences to %s' % prefs_user_file_path)

        try:
            prefs_file = open(prefs_global_file_path, 'w')
            pickle.dump(self.prefs_global, prefs_file)
            prefs_file.close()
            self.log('preferences saved to %s' % prefs_global_file_path)
            self.log('preferences contents:\n' + pformat(self.prefs_global))
        except:
            self.log('unable to save preferences to %s' % prefs_global_file_path)
            
        return True

    def unpack_bundle(self):
        from PySide2 import QtWidgets
        import traceback

        start = time.time()
        script_file_name, ext = os.path.splitext(os.path.abspath(__file__))
        script_file_name += '.py'
        self.log('script file: %s' % script_file_name)
        bundle_path = os.path.join(self.bundle_location, 'bundle')            
        script = None

        try:
            with open(script_file_name, 'r') as scriptfile:
                script = scriptfile.read()
                scriptfile.close()
        except Exception as e:
            import flame
            msg = 'flameTimewrarpML: %s' % e
            dmsg = pformat(traceback.format_exc())
            
            def show_error_mbox():
                mbox = QtWidgets.QMessageBox()
                mbox.setWindowTitle('flameTimewrarpML')
                mbox.setText(msg)
                mbox.setDetailedText(dmsg)
                mbox.setStyleSheet('QLabel{min-width: 800px;}')
                mbox.exec_()
        
            flame.schedule_idle_event(show_error_mbox)
            return False
        
        if not script:
            return False
            
        bundle_id = str(hash(script))
        self.log('bindle_id: %s lenght %s' % (bundle_id, len(script)))

        if (os.path.isdir(bundle_path) and os.path.isfile(os.path.join(bundle_path, 'bundle_id'))):
            self.log('checking existing bundle id %s' % os.path.join(bundle_path, 'bundle_id'))
            with open(os.path.join(bundle_path, 'bundle_id'), 'r') as bundle_id_file:
                if bundle_id_file.read() == bundle_id:
                    self.log('env bundle already exists with id matching current version, no need to unpack again')
                    bundle_id_file.close()
                    return True
                else:
                    self.log('existing env bundle id does not match current one, replacing...')

        if os.path.isdir(bundle_path):
            try:
                cmd = 'rm -rf ' + os.path.abspath(bundle_path)
                self.log('cleaning up old bundle folder')
                self.log('executing: %s' % cmd)
                os.system(cmd)
            except Exception as e:
                import flame
                msg = 'flameTimewrarpML: %s' % e
                dmsg = pformat(traceback.format_exc())
                
                def show_error_mbox():
                    mbox = QtWidgets.QMessageBox()
                    mbox.setWindowTitle('flameTimewrarpML')
                    mbox.setText(msg)
                    mbox.setDetailedText(dmsg)
                    mbox.setStyleSheet('QLabel{min-width: 800px;}')
                    mbox.exec_()
            
                flame.schedule_idle_event(show_error_mbox)
                return False

        try:
            self.log('creating new bundle folder: %s' % bundle_path)
            os.makedirs(bundle_path)
        except Exception as e:
            import flame
            msg = 'flameTimewrarpML: %s' % e
            dmsg = pformat(traceback.format_exc())
            
            def show_error_mbox():
                mbox = QtWidgets.QMessageBox()
                mbox.setWindowTitle('flameTimewrarpML')
                mbox.setText(msg)
                mbox.setDetailedText(dmsg)
                mbox.setStyleSheet('QLabel{min-width: 800px;}')
                mbox.exec_()
        
            flame.schedule_idle_event(show_error_mbox)
            return False

        start_position = script.rfind('# bundle payload starts here') + 33
        payload = script[start_position:-4]
        payload_dest = os.path.join(self.bundle_location, 'bundle.tar.bz2')
        
        try:
            import base64
            self.log('unpacking payload: %s' % payload_dest)
            with open(payload_dest, 'wb') as payload_file:
                payload_file.write(base64.b64decode(payload))
                payload_file.close()
            cmd = 'tar xjf ' + payload_dest + ' -C ' + self.bundle_location + '/'
            self.log('executing: %s' % cmd)
            os.system(cmd)
            self.log('cleaning up %s' % payload_dest)
            os.remove(payload_dest)
        except Exception as e:
            import flame
            msg = 'flameTimewrarpML: %s' % e
            dmsg = pformat(traceback.format_exc())
            
            def show_error_mbox():
                mbox = QtWidgets.QMessageBox()
                mbox.setWindowTitle('flameTimewrarpML')
                mbox.setText(msg)
                mbox.setDetailedText(dmsg)
                mbox.setStyleSheet('QLabel{min-width: 800px;}')
                mbox.exec_()
        
            flame.schedule_idle_event(show_error_mbox)
            return False

        try:
            with open(os.path.join(bundle_path, 'bundle_id'), 'w+') as bundle_id_file:
                bundle_id_file.write(bundle_id)
        except Exception as e:
            import flame
            msg = 'flameTimewrarpML: %s' % e
            dmsg = pformat(traceback.format_exc())
            
            def show_error_mbox():
                mbox = QtWidgets.QMessageBox()
                mbox.setWindowTitle('flameTimewrarpML')
                mbox.setText(msg)
                mbox.setDetailedText(dmsg)
                mbox.setStyleSheet('QLabel{min-width: 800px;}')
                mbox.exec_()
    
            flame.schedule_idle_event(show_error_mbox)
            return False

        delta = time.time() - start
        self.log('bundle extracted to %s' % bundle_path)
        self.log('extracting bundle took %s sec' % str(delta))

        env_bundle_file = os.path.join(os.path.dirname(__file__), 'flameTimewarpMLenv.tar.bz2')
        if os.path.isfile(env_bundle_file):
            self.unpack_env(env_bundle_file)
            os.remove(env_bundle_file)

        return True
            
    def unpack_env(self, env_bundle_file):
        from PySide2 import QtWidgets
        import traceback

        start = time.time()
        if not os.path.isfile(env_bundle_file):
            import flame
            msg = 'flameTimewrarpML: Can not find env bundle %s' % env_bundle_file
            dmsg = 'Please put flameTimewrarpMLenv.bundle next to the actual python script\n'
            dmsg += 'It contains prebuild python and cuda environment needed to run ML Timewarp'
            
            def show_error_mbox():
                mbox = QtWidgets.QMessageBox()
                mbox.setWindowTitle('flameTimewrarpML')
                mbox.setText(msg)
                mbox.setDetailedText(dmsg)
                mbox.setStyleSheet('QLabel{min-width: 800px;}')
                mbox.exec_()
            
            flame.schedule_idle_event(show_error_mbox)
            return False

        try:
            self.log('extracting new env bundle...')
            cmd = self.bundle_location + '/bundle/bin/pbzip2 -dc ' + env_bundle_file + ' | tar xf - -C ' + self.bundle_location
            self.log('executing: %s' % cmd)
            os.system(cmd)
            delta = time.time() - start
            self.log('env bundle extracted to %s' % self.bundle_location + 'miniconda3')
            self.log('extracting env bundle took %s sec' % str(delta))
        except Exception as e:
            import flame
            msg = 'flameTimewrarpML: %s' % e
            dmsg = pformat(traceback.format_exc())
            
            def show_error_mbox():
                mbox = QtWidgets.QMessageBox()
                mbox.setWindowTitle('flameTimewrarpML')
                mbox.setText(msg)
                mbox.setDetailedText(dmsg)
                mbox.setStyleSheet('QLabel{min-width: 800px;}')
                mbox.exec_()
        
            flame.schedule_idle_event(show_error_mbox)
            return False
        

class flameMenuApp(object):
    def __init__(self, framework):
        self.name = self.__class__.__name__
        self.framework = framework
        self.menu_group_name = menu_group_name
        self.debug = DEBUG
        self.dynamic_menu_data = {}

        # flame module is only avaliable when a 
        # flame project is loaded and initialized
        self.flame = None
        try:
            import flame
            self.flame = flame
        except:
            self.flame = None
        
        self.prefs = self.framework.prefs_dict(self.framework.prefs, self.name)
        self.prefs_user = self.framework.prefs_dict(self.framework.prefs_user, self.name)
        self.prefs_global = self.framework.prefs_dict(self.framework.prefs_global, self.name)

        from PySide2 import QtWidgets
        self.mbox = QtWidgets.QMessageBox()

    @property
    def flame_extension_map(self):
        return {
            'Alias': 'als',
            'Cineon': 'cin',
            'Dpx': 'dpx',
            'Jpeg': 'jpg',
            'Maya': 'iff',
            'OpenEXR': 'exr',
            'Pict': 'pict',
            'Pixar': 'picio',
            'Sgi': 'sgi',
            'SoftImage': 'pic',
            'Targa': 'tga',
            'Tiff': 'tif',
            'Wavefront': 'rla',
            'QuickTime': 'mov',
            'MXF': 'mxf',
            'SonyMXF': 'mxf'
        }
        
    def __getattr__(self, name):
        def method(*args, **kwargs):
            print ('calling %s' % name)
        return method

    def log(self, message):
        self.framework.log('[' + self.name + '] ' + message)

    def rescan(self, *args, **kwargs):
        if not self.flame:
            try:
                import flame
                self.flame = flame
            except:
                self.flame = None

        if self.flame:
            self.flame.execute_shortcut('Rescan Python Hooks')
            self.log('Rescan Python Hooks')

    def get_export_preset_fields(self, preset):
        
        self.log('Flame export preset parser')

        # parses Flame Export preset and returns a dict of a parsed values
        # of False on error.
        # Example:
        # {'type': 'image',
        #  'fileType': 'OpenEXR',
        #  'fileExt': 'exr',
        #  'framePadding': 8
        #  'startFrame': 1001
        #  'useTimecode': 0
        # }
        
        from xml.dom import minidom

        preset_fields = {}

        # Flame type to file extension map

        flame_extension_map = {
            'Alias': 'als',
            'Cineon': 'cin',
            'Dpx': 'dpx',
            'Jpeg': 'jpg',
            'Maya': 'iff',
            'OpenEXR': 'exr',
            'Pict': 'pict',
            'Pixar': 'picio',
            'Sgi': 'sgi',
            'SoftImage': 'pic',
            'Targa': 'tga',
            'Tiff': 'tif',
            'Wavefront': 'rla',
            'QuickTime': 'mov',
            'MXF': 'mxf',
            'SonyMXF': 'mxf'
        }

        preset_path = ''

        if os.path.isfile(preset.get('PresetFile', '')):
            preset_path = preset.get('PresetFile')
        else:
            path_prefix = self.flame.PyExporter.get_presets_dir(
                self.flame.PyExporter.PresetVisibility.values.get(preset.get('PresetVisibility', 2)),
                self.flame.PyExporter.PresetType.values.get(preset.get('PresetType', 0))
            )
            preset_file = preset.get('PresetFile')
            if preset_file.startswith(os.path.sep):
                preset_file = preset_file[1:]
            preset_path = os.path.join(path_prefix, preset_file)

        self.log('parsing Flame export preset: %s' % preset_path)
        
        preset_xml_doc = None
        try:
            preset_xml_doc = minidom.parse(preset_path)
        except Exception as e:
            message = 'flameMenuSG: Unable parse xml export preset file:\n%s' % e
            self.mbox.setText(message)
            self.mbox.exec_()
            return False

        preset_fields['path'] = preset_path

        preset_type = preset_xml_doc.getElementsByTagName('type')
        if len(preset_type) > 0:
            preset_fields['type'] = preset_type[0].firstChild.data

        video = preset_xml_doc.getElementsByTagName('video')
        if len(video) < 1:
            message = 'flameMenuSG: XML parser error:\nUnable to find xml video tag in:\n%s' % preset_path
            self.mbox.setText(message)
            self.mbox.exec_()
            return False
        
        filetype = video[0].getElementsByTagName('fileType')
        if len(filetype) < 1:
            message = 'flameMenuSG: XML parser error:\nUnable to find video::fileType tag in:\n%s' % preset_path
            self.mbox.setText(message)
            self.mbox.exec_()
            return False

        preset_fields['fileType'] = filetype[0].firstChild.data
        if preset_fields.get('fileType', '') not in flame_extension_map:
            message = 'flameMenuSG:\nUnable to find extension corresponding to fileType:\n%s' % preset_fields.get('fileType', '')
            self.mbox.setText(message)
            self.mbox.exec_()
            return False
        
        preset_fields['fileExt'] = flame_extension_map.get(preset_fields.get('fileType'))

        name = preset_xml_doc.getElementsByTagName('name')
        if len(name) > 0:
            framePadding = name[0].getElementsByTagName('framePadding')
            startFrame = name[0].getElementsByTagName('startFrame')
            useTimecode = name[0].getElementsByTagName('useTimecode')
            if len(framePadding) > 0:
                preset_fields['framePadding'] = int(framePadding[0].firstChild.data)
            if len(startFrame) > 0:
                preset_fields['startFrame'] = int(startFrame[0].firstChild.data)
            if len(useTimecode) > 0:
                preset_fields['useTimecode'] = useTimecode[0].firstChild.data

        return preset_fields


class flameTimewrapML(flameMenuApp):
    def __init__(self, framework):
        flameMenuApp.__init__(self, framework)

    def build_menu(self):
        def scope_clip(selection):
            import flame
            for item in selection:
                if isinstance(item, (flame.PyClip)):
                    return True
            return False

        if not self.flame:
            return []
        
        menu = {'actions': []}
        menu['name'] = self.menu_group_name
        menu_item = {}
        menu_item['name'] = 'Create slowmotion with ML'
        menu_item['execute'] = self.slowmo
        menu_item['isEnabled'] = scope_clip
        menu['actions'].append(menu_item)

        return menu

    def slowmo(self, selection):
        pprint (selection)
        # slowmo_dialog()

    def slowmo_dialog(self, *args, **kwargs):
        from PySide2 import QtWidgets, QtCore

        self.asset_name = ''
        flameMenuNewBatch_prefs = self.framework.prefs.get('flameMenuNewBatch', {})
        self.asset_task_template =  flameMenuNewBatch_prefs.get('asset_task_template', {})

        window = QtWidgets.QDialog()
        window.setMinimumSize(280, 180)
        window.setWindowTitle('Create Asset in Shotgun')
        window.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        window.setStyleSheet('background-color: #313131')

        screen_res = QtWidgets.QDesktopWidget().screenGeometry()
        window.move((screen_res.width()/2)-150, (screen_res.height() / 2)-180)

        vbox = QtWidgets.QVBoxLayout()
        vbox.setAlignment(QtCore.Qt.AlignTop)

        # Asset Task Template label

        lbl_TaskTemplate = QtWidgets.QLabel('Task Template', window)
        lbl_TaskTemplate.setStyleSheet('QFrame {color: #989898; background-color: #373737}')
        lbl_TaskTemplate.setMinimumHeight(28)
        lbl_TaskTemplate.setMaximumHeight(28)
        lbl_TaskTemplate.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(lbl_TaskTemplate)

        # Shot Task Template Menu

        btn_AssetTaskTemplate = QtWidgets.QPushButton(window)
        flameMenuNewBatch_prefs = self.framework.prefs.get('flameMenuNewBatch', {})
        asset_task_template = flameMenuNewBatch_prefs.get('asset_task_template', {})
        code = asset_task_template.get('code', 'No code')
        btn_AssetTaskTemplate.setText(code)
        asset_task_templates = self.connector.sg.find('TaskTemplate', [['entity_type', 'is', 'Asset']], ['code'])
        asset_task_templates_by_id = {x.get('id'):x for x in asset_task_templates}
        asset_task_templates_by_code_id = {x.get('code') + '_' + str(x.get('id')):x for x in asset_task_templates}
        def selectAssetTaskTemplate(template_id):
            template = shot_task_templates_by_id.get(template_id, {})
            code = template.get('code', 'no_code')
            btn_AssetTaskTemplate.setText(code)
            self.asset_task_template = template
        btn_AssetTaskTemplate.setFocusPolicy(QtCore.Qt.NoFocus)
        btn_AssetTaskTemplate.setMinimumSize(258, 28)
        btn_AssetTaskTemplate.move(40, 102)
        btn_AssetTaskTemplate.setStyleSheet('QPushButton {color: #9a9a9a; background-color: #29323d; border-top: 1px inset #555555; border-bottom: 1px inset black}'
                                    'QPushButton:pressed {font:italic; color: #d9d9d9}'
                                    'QPushButton::menu-indicator {image: none;}')
        btn_AssetTaskTemplate_menu = QtWidgets.QMenu()
        for code_id in sorted(asset_task_templates_by_code_id.keys()):
            template = asset_task_templates_by_code_id.get(code_id, {})
            code = template.get('code', 'no_code')
            template_id = template.get('id')
            action = btn_AssetTaskTemplate_menu.addAction(code)
            action.triggered[()].connect(lambda template_id=template_id: selectAssetTaskTemplate(template_id))
        btn_AssetTaskTemplate.setMenu(btn_AssetTaskTemplate_menu)
        vbox.addWidget(btn_AssetTaskTemplate)

        # Shot Name Label

        lbl_AssettName = QtWidgets.QLabel('New Asset Name', window)
        lbl_AssettName.setStyleSheet('QFrame {color: #989898; background-color: #373737}')
        lbl_AssettName.setMinimumHeight(28)
        lbl_AssettName.setMaximumHeight(28)
        lbl_AssettName.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(lbl_AssettName)

        # Shot Name Text Field
        def txt_AssetName_textChanged():
            self.asset_name = txt_AssetName.text()
        txt_AssetName = QtWidgets.QLineEdit('', window)
        txt_AssetName.setFocusPolicy(QtCore.Qt.ClickFocus)
        txt_AssetName.setMinimumSize(280, 28)
        txt_AssetName.setStyleSheet('QLineEdit {color: #9a9a9a; background-color: #373e47; border-top: 1px inset #black; border-bottom: 1px inset #545454}')
        txt_AssetName.textChanged.connect(txt_AssetName_textChanged)
        vbox.addWidget(txt_AssetName)

        # Spacer Label

        lbl_Spacer = QtWidgets.QLabel('', window)
        lbl_Spacer.setStyleSheet('QFrame {color: #989898; background-color: #313131}')
        lbl_Spacer.setMinimumHeight(4)
        lbl_Spacer.setMaximumHeight(4)
        lbl_Spacer.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addWidget(lbl_Spacer)

        # Create and Cancel Buttons
        hbox_Create = QtWidgets.QHBoxLayout()

        select_btn = QtWidgets.QPushButton('Create', window)
        select_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        select_btn.setMinimumSize(128, 28)
        select_btn.setStyleSheet('QPushButton {color: #9a9a9a; background-color: #424142; border-top: 1px inset #555555; border-bottom: 1px inset black}'
                                'QPushButton:pressed {font:italic; color: #d9d9d9}')
        select_btn.clicked.connect(window.accept)

        cancel_btn = QtWidgets.QPushButton('Cancel', window)
        cancel_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        cancel_btn.setMinimumSize(128, 28)
        cancel_btn.setStyleSheet('QPushButton {color: #9a9a9a; background-color: #424142; border-top: 1px inset #555555; border-bottom: 1px inset black}'
                                'QPushButton:pressed {font:italic; color: #d9d9d9}')
        cancel_btn.clicked.connect(window.reject)

        hbox_Create.addWidget(cancel_btn)
        hbox_Create.addWidget(select_btn)

        vbox.addLayout(hbox_Create)

        window.setLayout(vbox)
        if window.exec_():
            if self.asset_name == '':
                return {}
            else:
                data = {'project': {'type': 'Project','id': self.connector.sg_linked_project_id},
                'code': self.asset_name,
                'task_template': self.asset_task_template}
                self.log('creating new asset...')
                new_asset = self.connector.sg.create('Asset', data)
                self.log('new asset:\n%s' % pformat(new_asset))
                self.log('updating async cache for cuttent_tasks')
                self.connector.cache_retrive_result('current_tasks', True)
                self.log('creating new batch')
                self.create_new_batch(new_asset)

                for app in self.framework.apps:
                    app.rescan()

                return new_asset
        else:
            return {}



# --- FLAME STARTUP SEQUENCE ---
# Flame startup sequence is a bit complicated
# If the app installed in /opt/Autodesk/<user>/python
# project hooks are not called at startup. 
# One of the ways to work around it is to check 
# if we are able to import flame module straght away. 
# If it is the case - flame project is already loaded 
# and we can start our constructor. Otherwise we need 
# to wait for app_initialized hook to be called - that would 
# mean the project is finally loaded. 
# project_changed_dict hook seem to be a good place to wrap things up

# main objects:
# app_framework takes care of preferences and general stuff
# apps is a list of apps to load inside the main program

app_framework = None
apps = []

# Exception handler
def exeption_handler(exctype, value, tb):
    from PySide2 import QtWidgets
    import traceback
    msg = 'flameTimewrarpML: Python exception %s in %s' % (value, exctype)
    mbox = QtWidgets.QMessageBox()
    mbox.setWindowTitle('flameTimewrarpML')
    mbox.setText(msg)
    mbox.setDetailedText(pformat(traceback.format_exception(exctype, value, tb)))
    mbox.setStyleSheet('QLabel{min-width: 800px;}')
    mbox.exec_()
    sys.__excepthook__(exctype, value, tb)
sys.excepthook = exeption_handler

# register clean up logic to be called at Flame exit
def cleanup(apps, app_framework):    
    if apps:
        if DEBUG:
            print ('[DEBUG %s] unloading apps:\n%s' % ('flameMenuSG', pformat(apps)))
        while len(apps):
            app = apps.pop()
            if DEBUG:
                print ('[DEBUG %s] unloading: %s' % ('flameMenuSG', app.name))
            del app        
        del apps

    if app_framework:
        print ('PYTHON\t: %s cleaning up' % app_framework.bundle_name)
        app_framework.save_prefs()
        del app_framework

atexit.register(cleanup, apps, app_framework)

def load_apps(apps, app_framework):
    apps.append(flameTimewrapML(app_framework))
    app_framework.apps = apps
    if DEBUG:
        print ('[DEBUG %s] loaded:\n%s' % (app_framework.bundle_name, pformat(apps)))

def project_changed_dict(info):
    global app_framework
    global apps
    cleanup(apps, app_framework)

def app_initialized(project_name):
    global app_framework
    global apps
    if not app_framework:
        app_framework = flameAppFramework()
        print ('PYTHON\t: %s initializing' % app_framework.bundle_name)
        load_apps(apps, app_framework)

try:
    import flame
    app_initialized(flame.project.current_project.name)
except:
    pass

def get_media_panel_custom_ui_actions():

    menu = []
    selection = []

    try:
        import flame
        selection = flame.media_panel.selected_entries
    except:
        pass

    for app in apps:
        if app.__class__.__name__ == 'flameTimewrapML':
            app_menu = []
            app_menu = app.build_menu()
            if app_menu:
                menu.append(app_menu)
    return menu

# bundle payload starts here
'''
BUNDLE_PAYLOAD
'''