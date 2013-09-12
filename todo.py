import re
from collections import defaultdict
import sublime
import sublime_plugin


FLAGS = sublime.DRAW_EMPTY | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
PATTERNS = {
    re.compile(r'^\s*# ?TODO:\s*(.*)$'): 'todo',
    re.compile(r'^\s*# ?XXX:\s*(.*)$'): 'xxx',
}
# ICON = 'Packages/User/todo.png'
# TODO_PATTERN = re.compile(r'^\s*# ?TODO:\s*(.*)$')


class TodoCommand(sublime_plugin.TextCommand):
    def __init__(self, *args, **kwargs):
        super(TodoCommand, self).__init__(*args, **kwargs)
        self._icons = defaultdict(list)

    def run(self, edit):
        for line_range in self.view.lines(sublime.Region(0, self.view.size())):
            line = self.view.substr(line_range)
            # icon_set = False
            for pattern, icon in PATTERNS.items():
                match = pattern.match(line)
                if match:
                    self._icons[icon].append(line_range)
                else:
                    try:
                        self._icons[icon].remove(line_range)
                    except ValueError:
                        pass
        self.refresh()

    def refresh(self):
        # remove all icons
        for icon in self._icons.keys():
            print('removing %s' % icon)
            self.view.add_regions('todo-%s' % icon,
                                  [sublime.Region(0, self.view.size())],
                                  'todo', '', FLAGS)

        # add all icons again
        for icon, regions in self._icons.items():
            self.view.add_regions('todo-%s' % icon, regions, 'todo',
                                  'Packages/User/%s.png' % icon, FLAGS)


class TodoModifiedListener(sublime_plugin.EventListener):
    def on_modified(self, view):
        view.run_command('todo')
