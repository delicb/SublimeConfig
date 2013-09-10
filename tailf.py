import os
import io
import stat
import time
import threading
import sublime
import sublime_plugin


# Set of IDs of view that are being monitored.
TAILF_VIEWS = set()


class TailF(sublime_plugin.TextCommand):
    '''
    Start monitoring file in `tail -f` line style.
    '''

    def __init__(self, *args, **kwargs):
        super(TailF, self).__init__(*args, **kwargs)
        self.prev_file_size = -1
        self.prev_mod_time = -1

    def run(self, edit):
        self.view.set_read_only(True)
        t = threading.Thread(target=self.thread_handler)
        TAILF_VIEWS.add(self.view.id())
        t.start()

    def thread_handler(self):
        while True:
            if self.view.id() in TAILF_VIEWS:
                if self.view.file_name() is None:
                    sublime.error_message('File not save on disk')
                    return
                else:
                    file_stat = os.stat(self.view.file_name())
                    new_size = file_stat[stat.ST_SIZE]
                    new_mod_time = file_stat[stat.ST_MTIME]
                if (new_mod_time > self.prev_mod_time or
                        new_size != self.prev_file_size):
                    self.view.run_command('update_file')
                    self.view.run_command('move_to',
                                          args={'to': 'eof', 'extend': False})
                    self.prev_file_size = new_size
                    self.prev_mod_time = new_mod_time
                time.sleep(self.view.settings().get('tailf_pull_rate'))
            else:
                return


class StopTailF(sublime_plugin.TextCommand):
    '''
    Stop monitoring file command.
    '''
    def run(self, edit):
        TAILF_VIEWS.remove(self.view.id())
        # restore view to previous state
        self.view.set_read_only(False)
        self.view.set_scratch(False)

    def description(self):
        return 'Stops monitoring file on disk'


class UpdateFile(sublime_plugin.TextCommand):
    '''
    Reloads content of the file and replaces view content with it.
    '''
    def run(self, edit):
        read_only = self.view.is_read_only()
        self.view.set_read_only(False)
        with io.open(self.view.file_name(), 'r', encoding='utf-8-sig') as f:
            content = f.read()
            whole_file = sublime.Region(0, self.view.size())
            self.view.replace(edit, whole_file, content)
        self.view.set_read_only(read_only)
        # don't ask user if he want's to save changes to disk
        self.view.set_scratch(True)


class TailFEventListener(sublime_plugin.EventListener):
    '''
    Listener that removes files from monitored files once file is
    about to be closed.
    '''
    def on_pre_close(self, view):
        if view.id() in TAILF_VIEWS:
            TAILF_VIEWS.remove(view.id())
