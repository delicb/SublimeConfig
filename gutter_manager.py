from collections import defaultdict
from heapq import heappush, heappop
import sublime
import sublime_plugin

FLAGS = sublime.DRAW_EMPTY | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
ICONS = defaultdict(list)


class GutterManagerMixin(object):
    icons = defaultdict(list)

    def __init__(self, *args, **kwargs):
        super(GutterManagerMixin, self).__init__(*args, **kwargs)
        self.priorities = self.view.settings().get('gutter_priority', {})

    def add(self, key, icon, line, scope='', flags=FLAGS):
        priority = self.priorities.get(key, 10)
        line_reg = self.view.line(self.view.text_point(line, 0))
        heappush(self.icons[line], (priority, (key, [line_reg], scope, icon, flags)))
        print(self.icons)

    def remove(self, key, line=None):
        if line is not None:
            self.icons[line] = list(filter(lambda x: x[1][0] != key, self.icons[line]))
            return

        for line in self.icons.keys():
            self.icons[line] = list(filter(lambda x: x[1][0] != key, self.icons[line]))

    def clear(self):
        for line, rest in self.icons.items():
            self.view.erase_regions(rest[-1][1][0])

    def populate(self):
        for line, rest in self.icons.items():
            print(rest[-1][1])
            self.view.add_regions(*rest[-1][1])

    def refresh(self):
        self.clear()
        self.populate()


class AddGutterIcon(GutterManagerMixin, sublime_plugin.TextCommand):
    def __init__(self, *args, **kwargs):
        super(AddGutterIcon, self).__init__(*args, **kwargs)

    def run(self, edit, key, icon, line, scope='', flags=FLAGS):
        self.add(key, icon, line, scope, flags)
        self.refresh()
        # line_reg = self.view.line(self.view.text_point(line, 0))
        # self.icons[line] = (key, [line_reg], scope, icon, flags)
        # self.refresh()
        # self.view.add_regions(key, [line_reg], 'myScope', icon, flags)


class RemoveGutterIcon(GutterManagerMixin, sublime_plugin.TextCommand):
    def __init__(self, *args, **kwargs):
        super(RemoveGutterIcon, self).__init__(*args, **kwargs)

    def run(self, edit, key, line=None):
        self.clear()
        self.remove(key, line)
        # del self.icons[line]
        # print(self.icons)
        self.populate()


class GutterManager(sublime_plugin.TextCommand):
    def run(self, edit, key, lines, icon='', flags=0):
        if not hasattr(lines, '__iter__'):
            lines = [lines]
        region = self.region_for_lines(lines)
        ICONS[key].append(region)
        self.view.add_regions(key, [region], 'myScope', icon, flags)

    def region_for_lines(self, lines):
        reg = None
        for line in lines:
            this_reg = self.view.lines(sublime.Region(0, self.view.size()))[line-1]
            if reg is None:
                reg = this_reg
            else:
                reg = reg.cover(this_reg)
        return reg


class GutterClear(sublime_plugin.TextCommand):
    def run(self, edit, key):
        for reg in ICONS[key]:
            self.view.add_regions(key, [reg])
