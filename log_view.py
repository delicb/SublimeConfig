import os
import io
import stat
import time
import threading
import sublime
import sublime_plugin


class DocumentViewer(sublime_plugin.TextCommand):
    def __init__(self, *args, **kwargs):
        super(DocumentViewer, self).__init__(*args, **kwargs)
        self.prev_file_size = -1

    def run(self, edit):
        self.view.set_read_only(True)
        t = threading.Thread(target=self.thread_handler)
        t.start()

    def thread_handler(self):
        while True:
            print('in while True')
            try:
                new_size = os.stat(self.view.file_name())[stat.ST_SIZE]
            except:
                print('failed to read file size: %s' % self.view.file_name())
                return
            if new_size > self.prev_file_size:
                self.view.run_command('update_file')
                self.view.show(self.view.size())
                self.prev_file_size = new_size
            time.sleep(0.5)


class UpdateFile(sublime_plugin.TextCommand):
    def run(self, edit):
        print('updating content of file')
        with io.open(self.view.file_name(), 'r', encoding='utf-8-sig') as f:
            content = f.read()
            self.view.replace(edit, sublime.Region(0, self.view.size()), content)

