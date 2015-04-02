import os, yaml, glob, jinja2

from buildtools.bt_logging import log
import fnmatch
    
def replace_var(input, varname, replacement):
    return input.replace('%%' + varname + '%%', replacement)

def replace_vars(input, var_replacements):
    for key, val in var_replacements.items():
        input = replace_var(input, key, val)
    return input

def dict_merge(a, b, path=None):
    "merges b into a"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                dict_merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                # Old behavior: scream
                # raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
                # New behavior: Overwrite A with B.
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a

class Config(object):
    def __init__(self, filename, default={}, template_dir='.', variables={}):
        self.environment = jinja2.Environment(loader=jinja2.loaders.FileSystemLoader(template_dir))
        if filename is None:
            self.cfg=default
        else:
            self.Load(filename, merge=False, defaults=default, variables=variables)
                
    def Load(self, filename, merge=False, defaults=None, variables={}):
        with log.info("Loading %s...",filename):
            if not os.path.isfile(filename):
                if defaults is None:
                    log.error('Failed to load %s.', filename)
                    return False
                else:
                    log.warn('File not found, loading defaults.')
                    with open(filename, 'w') as f:
                        yaml.dump(defaults, f, default_flow_style=False)

            template = self.environment.get_template(filename)
            rendered = template.render(variables)
            
            newcfg = yaml.load(rendered)
            if merge:
                self.cfg = dict_merge(self.cfg, newcfg)
            else:
                self.cfg = newcfg
        return True
    
    def LoadFromFolder(self, path, pattern='*.yml', variables={}):
        'For conf.d/ stuff.'
        for root, dirs, files in os.walk(path):
            for file in files:
                filename = os.path.join(root,file)
                if fnmatch.fnmatch(filename, pattern):
                    self.Load(filename, merge=True, variables=variables)
        #for filename in glob.glob(os.path.join(path,pattern)):
        #    self.Load(filename, merge=True)
        
    def __getitem__(self, key):
        return self.cfg.__getitem__(key)
    
    def __setitem__(self, key, value):
        return self.cfg.__setitem__(key)
    
    def get(self, key, default=None):
        parts = key.split('.')
        try:
            value = self.cfg[parts[0]]
            if len(parts) == 1:
                return value
            for part in parts[1:]:
                value = value[part]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key, value):
        parts = key.split('.')
        try:
            if len(parts) == 1:
                self.cfg[parts[0]] = value
            L = self.cfg[parts[0]]
            for part in parts[1:-1]:
                L = L[part]
            L[parts[-1]] = value
        except (KeyError, TypeError):
            return

class Properties(object):
    def __init__(self):
        self.properties = {}
        
    def Load(self, filename, default=None, expand_vars={}):
        with log.info("Loading %s...", filename):
            if not os.path.isfile(filename):
                if default is None:
                    log.critical('File not found, exiting!')
                    log.info('To load defaults, specify default=<dict> to Properties.Load().')
                    sys.exit(1)
                else:
                    log.warn('File not found, loading defaults.')
                    with open(filename, 'w') as f:
                        self.dumpTo(default, f)
                        
            with open(filename, 'r') as f:
                for line in f:
                    if line.strip() == '': continue
                    # Ignore comments.
                    if line.strip().startswith('#'): continue
                    
                    key, value = line.strip().split('=', 1)
                    if key in self.properties:
                        log.warn('Key "%s" already exists, overwriting!', key)
                    value = replace_vars(value, expand_vars)
                    self.properties[key] = value
                    
            if default is None: return
            for k, v in default.items():
                if k not in self.properties:
                    self.properties[k] = v
                    log.info('Added default property %s = %s', k, v)
                
    def Save(self, filename):
        with log.info("Saving %s...", filename):
            with open(filename, 'w') as f:
                Properties.dumpTo(self.properties, f)
            
    @classmethod
    def dumpTo(cls, properties, f):
        for k, v in sorted(properties.items()):
            f.write("{}={}\n".format(k, v))
        
    def __getitem__(self, key):
        return self.properties.__getitem__(key)
    
    def __setitem__(self, key, value):
        return self.properties.__setitem__(key)
