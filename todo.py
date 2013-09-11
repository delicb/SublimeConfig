import re
import sublime
import sublime_plugin


FLAGS = sublime.DRAW_EMPTY | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE
ICON = 'Packages/User/todo.png'
TODO_PATTERN = re.compile(r'^\s*# ?TODO:\s*(.*)$')


class TodoCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.handler()
        pass

    def handler(self):
        for line_range in self.view.lines(sublime.Region(0, self.view.size())):
            line = self.view.substr(line_range)
            match = TODO_PATTERN.match(line)
            if match:
                self.view.add_regions('todo', [line_range], 'todo', ICON, FLAGS)
                print(match.groups()[0])
            else:
                self.view.add_regions('todo', [line_range], 'todo', '', FLAGS)


class TodoModifiedListener(sublime_plugin.EventListener):
    def on_modified(self, view):
        view.run_command('todo')
