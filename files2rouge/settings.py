import os
import json

PATHS = ['ROUGE_path', 'ROUGE_data']
PARAMS = PATHS + []

def _default_path():
  _dir, _filename = os.path.split(__file__)
  return os.path.join(_dir, 'settings.json')


class Settings:

  def __init__(self, path=None):
    self.path = _default_path() if path is None else path

  def _load(self):
    with open(self.path, 'r') as f:
        data = json.load(f)
    self.set_data(data)

  def _generate(self, data):
    self.set_data(data)
    with open(self.path, 'w') as f:
      json.dump(data, f, indent=2)

  def set_data(self, data):
    """Check & set data to `data`
    """
    for param in PARAMS:
      if param not in data:
        raise ValueError('Missing parameter %d in data' % param)

    for path_key in PATHS:
      path = data[path_key]
      if not os.path.exists(path):
        raise ValueError("Path does not exist %s" % path)
    self.data = data
