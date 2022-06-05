import os, sys
import cmd

from meoclient import *
from services import *

class MeoCloudRepl(cmd.Cmd):

    rcwd = '/'
    intro = "Welcome to meo cloud repl!\n" + \
    "Enter Press Tab to see commands\n"+ \
    "help <cmd> or ?<cmd> for description\n" + \
    "^D or exit to quit"
    prompt = f'meocloud [{rcwd}]> '
    meo = get_meo_client()
    cwd = os.getcwd()

    def _rcwd_to_rpath(self,path):
        rpath = f"{self.rcwd}/{path}"
        if rpath.startswith('/') and self.rcwd == '/': rpath = rpath[1:]
        if rpath.endswith('/'): rpath = rpath[:-1]
        print(f"rpath:{rpath}")
        return rpath


    #### DEFINITION OF COMMANDS ####

    def do_lls(self,args):
        os.system('ls -la')

    def help_rls(self):
        self.help_mls()

    def help_lls(self):
        print("List the local file contents")

    def help_pwd(self):
        self.help_lcd()
    
    def do_pwd(self,args):
        self.do_lcd(args)


    def do_mls(self,args):
        files = None
        r = self.meo.get_list(self._rcwd_to_rpath(args))
        if r.status_code != 200:
            print(f"Something got wrong: status {r.status_code}")
            return

        files = r.json()

        for item in files['contents']:
            items_row = [str(item['bytes']),item['modified'],item['name']]
            if 'mime_type' in item.keys():
                items_row.append(item['mime_type'])
            else: items_row.append('')
            item_line = "{0[0]:<9}{0[1]:30.25}{0[3]:28}{0[2]}".format(items_row)
            print(item_line)

    def do_rls(self,args):
        self.do_mls(args)

    def help_mls(self):
        print("Lists the remote files")

    def do_lcd(self,args):
        if len(args) == 0:
            print(self.cwd)
            return
        print(f"chdir to {args}")
        os.chdir(args)
        self.cwd = os.getcwd()

    def help_lcd(self):
        print("Changes the current directory")

    def do_rcd(self,args):
        if len(args) == 0:
            print(self.rcwd)
            return
        self.rcwd = self._rcwd_to_rpath(args)

    def help_rcd(self):
        print("Changes the current directory on the remote side")

    def do_rup(self,args):
        self.rcwd =  self.rcwd[0:self.rcwd.rfind('/')+1]

    def help_rup(self):
        print("Goes one level up in the dirtree")

    def do_lup(self,args):
        os.chdir(os.path.pardir)
        self.cwd = os.getcwd()
        print(f"chdir to {self.cwd}")

    def help_lup(self):
        print("Change the local directory up one level")

    def do_get(self,args):
        r = self.meo.get_file(self._rcwd_to_rpath(args))
        print(f"Saving to {args}")
        with open(args,'wb') as downloaded_file:
            downloaded_file.write(r.content)
            downloaded_file.close()

    def help_get(self):
        print("Downloads a file")

    def do_put(self,args):
        r = self.meo.upload_data(self._rcwd_to_rpath(args), open(args, 'rb').read())
        if r.status_code != 200:
            print(f"Something unexpected occurred: {r.status_code}")
            return
        json_pprint(r.json())

    def help_put(self):
        print("Uploads a file")

    def complete_put(self, text, line, begidx, endidx):
        return [f for f in os.listdir(self.cwd) if f.startswith(text)]

    def _complete_remote(self,text,line,begidx, endidx):
        files = None
        r = self.meo.get_list(self.rcwd)
        files = r.json()['contents']
        return [f for f in map(lambda f:f['name'][1:],files) if f.startswith(text)]

    def complete_get(self,text,line,begidx, endidx):
        return self._complete_remote(text,line,begidx, endidx)

    def do_cat(self,args):
        with open(args,'r') as f:
            print(f.read(1024))
            f.close()

    def help_cat(self):
        print("Shows the first 1024 bytes of a local file")

    def do_del(self,args):
        r = self.meo.delete_file(self._rcwd_to_rpath(args))
        json_pprint(r.json())

    def complete_del(self,text,line,begidx, endidx):
        return self._complete_remote(text,line,begidx, endidx)


    def help_del(self):
        print("Deletes a remote file")

    def do_exit(self,args):
        return True

    do_EOF = do_exit

    def help_exit(self):
        print("Exits the REPL!")

    def do_mkdir(self,args):
        newpathdir = args
        print(f"Creating {newpathdir}")
        r = self.meo.mkdir(newpathdir)
        json_pprint(r.json())

    def help_mkdir(self):
        print("Creates a new directory")

    def do_properties(self,args):
        r = self.meo.properties(self._rcwd_to_rpath(args))
        json_pprint(r.json())

    def help_properties(self):
        print("Shows the file properties")

    def complete_properties(self,text,line,begidx, endidx):
        return self._complete_remote(text,line,begidx, endidx)


    def do_rcat(self,args):
        r = self.meo.get_file(self._rcwd_to_rpath(args))
        print(r.text[:256])

    def help_rcat(self):
        print("Dumps the first 1024 bytes of a file")

    def complete_rcat(self,text,line,begidx, endidx):
        return self._complete_remote(text,line,begidx, endidx)


    def do_rdwnld(self,args):
        import time
        r = self.meo.schedule_download_remote(args)
        job_id = r.json()['job']
        print(job_id)
        r = self.meo.pending_remote_download_status(job_id)
        print(r.json())
        time.sleep(10)
        r = self.meo.pending_remote_download_status(job_id)
        print(r.json())

    def do_rdwnldq(self,job_id):
        r = self.meo.pending_remote_download_status(job_id)
        print(r.json())

## END OF COMMANDS DEFINITION ##

    def postloop(self) -> None:
        print('Goodbye!')
        super().postloop()

    def postcmd(self,stop,line):
        self.prompt = f'meocloud [{self.rcwd}]> '
        return super().postcmd(stop,line)


def main():
    MeoCloudRepl().cmdloop()

if __name__ == '__main__':
    main()
