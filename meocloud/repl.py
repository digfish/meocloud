import argparse
import cmd
import os
import sys

from .meoclient import *
from .services import *
import tqdm



class MeoCloudRepl(cmd.Cmd):

    rcwd = '/'
    intro = "Welcome to meo cloud repl!\n" + \
    "Enter Press Tab to see commands\n"+ \
    "help <cmd> or ?<cmd> for description\n" + \
    "^D or exit to quit"
    prompt = f'meocloud [{rcwd}]> '
    meo = get_meo_client()
    cwd = os.getcwd()
    listdir_cache = dict()

    args_usage = \
    """ 
        rls <dir>       list remote dir <dir>
        mls <dir>       idem
        put <file>      save the file in remote dir
        get <file>      downloads the file locate in remote dir
        del <path>      deletes the remote path
        mkdir <dir>     creates the remote dir
        md <file>       metadata of remote file
    """        

    def preloop(self) -> None:
        self._refresh_listdir_cache()
        return super().preloop()

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

    def _refresh_listdir_cache(self):
        if self.rcwd.startswith('/'):
            cd = self.rcwd[1:]
        else:
            cd = self.rcwd

        r = self.meo.get_list(cd)
        if r.status_code != 200:
            print(f"Something got wrong: status {r.status_code}")
            return None
        files = r.json()
        self.listdir_cache[self.rcwd] = dict()
        for item in files['contents']:
            self.listdir_cache[self.rcwd][item['name']] = item
        return True


    def do_mls(self,args):
        files = None
        #r = self.meo.get_list(self._rcwd_to_rpath(args))
        if len(args.strip()) == 0:
            args = self.rcwd
        if args.startswith('/'):
            args = args[1:]
        print(f"Listing %s :"%self.rcwd)

        # prints the file list from cache
        for item in self.listdir_cache[self.rcwd].values():
            items_row = [str(item['bytes']),item['modified'],item['name']]
            if 'mime_type' in item.keys():
                items_row.append(item['mime_type'])
            elif 'is_dir' in item.keys() and item['is_dir'] == True:
                items_row.append('<DIR>')
            else: items_row.append('')
            item_line = "{0[0]:<9}{0[1]:30.25}{0[3]:28}{0[2]}".format(items_row)
            print(item_line)
        return


    def do_rls(self,args):
        self.do_mls(args)

    def help_mls(self):
        print("Lists the remote files")

    def do_lcd(self,args):
        if len(args) == 0:
            print(self.cwd)
            return
        os.chdir(args)
        self.cwd = os.getcwd()
        print(f"Local dir: {os.getcwd()}")

    def help_lcd(self):
        print("Changes the current local directory")

    def do_rcd(self,args):
        rcwd_before = self.rcwd
        if len(args) == 0:
            print(self.rcwd)
            return
        if args == '..': 
            self.do_rup(args)
            return
        if self.rcwd != '/' and args != '/':
            self.rcwd = self.rcwd + '/' + args
        elif self.rcwd == '/':
            if args != '/': self.rcwd = args
            else: self.rcwd = '/'
        
        result = self._refresh_listdir_cache()
        if result is None:
            self.rcwd = rcwd_before
        print(f"Remote dir: {self.rcwd}")

    def help_rcd(self):
        print("Changes the current directory on the remote side")

    def do_rup(self,args):
        last_slash = self.rcwd.rfind('/')
        if last_slash == -1:
            self.rcwd = '/'
        else:
            self.rcwd =  self.rcwd[0:last_slash]
        print(f"Remote dir: {self.rcwd}")
    
    def help_rup(self):
        print("Goes one level up in the dirtree")

    def do_lup(self,args):
        os.chdir(os.path.pardir)
        self.cwd = os.getcwd()
        print(f"Local dir: {os.getcwd()}")

    def help_lup(self):
        print("Change the local directory up one level")

    def do_get(self,args):
        r = self.meo.get_file(args)
        print(f"Saving to {self.cwd}/{args}")
        totalsize = int(r.headers.get('content-length', 0))
        chunk_size = int(totalsize / 10)  # 1 Kibibyte
        readsofar = 0
        with open(args,'wb') as downloaded_file:
            for data in r.iter_content(chunk_size):
                readsofar += chunk_size
                if readsofar > totalsize: readsofar = totalsize
                percent = int(readsofar / totalsize * 100.0)
                sys.stderr.write("\r{read}/{total} ({percent:3.0f}%)".format(read=readsofar,total=totalsize,
                                                                              percent=percent))     
                downloaded_file.write(data)
            downloaded_file.close()

    def help_get(self):
        print("Downloads a file")

    def do_put(self,args):
        if self.rcwd != '/':
            rpath = f"{self.rcwd}/{args}"
        else:
            rpath = args
        print(f"Uploading {rpath}")
        r = self.meo.upload_data(rpath,ChunkUploader (open(args, 'rb').read(),chunksize=1024*1024))
        if r.status_code != 200:
            print(f"Something unexpected occurred: {r.status_code}")
            return
        json_pprint(r.json())
        self._refresh_listdir_cache()

    def do_cput(self,args):
        rpath = args
        CHUNK_SIZE = 4*1024*1024
        print(f"Uploading {rpath}")
        filesize = os.path.getsize(rpath)
        f = open(rpath,'rb')
        r = self.meo._chunk_upload(f.read(CHUNK_SIZE))
        rj = r.json()
        upload_id = rj['upload_id']
        offset = int(rj['offset'])
        while (offset < filesize):
            r = self.meo._chunk_upload(f.read(CHUNK_SIZE),offset=offset,upload_id=upload_id)
            print(r.status_code)
            if r.status_code != 200 : break
            rj = r.json()
            upload_id = rj['upload_id']
            offset = int(rj['offset'])
            print(f"{upload_id}: {offset} <= {filesize}")
        f.close()
        print ("Upload finished!")
        r = self.meo._chunk_upload_commit(os.path.basename(rpath),upload_id)
        print(r)
        print(r.json())
        self._refresh_listdir_cache()

    def help_cput(self):
        print("Upload files in chunks, useful for big files (>150 MB)")

    def help_put(self):
        print("Uploads a file")

    def complete_put(self, text, line, begidx, endidx):
        return [f for f in os.listdir(self.cwd) if f.startswith(text)]

    def complete_lcd(self, text, line, begidx, endidx):
        return [f for f in os.listdir(self.cwd) if f.startswith(text) and os.path.isdir(f)]

    def complete_rcd(self, text, line, begidx, endidx):
        collect = []
        for direntry in self.listdir_cache[self.rcwd].keys():
            if self.listdir_cache[self.rcwd][direntry]['is_dir'] \
                and direntry.startswith(text): 
                    collect.append(direntry[1:])
        return collect


    def _complete_remote(self,text,line,begidx, endidx):
        files = None
        # args = self.rcwd
        # if args.startswith('/'):
        #     args = args[1:]
        # elif len(args)>1 : args = f"/{args}"
        # r = self.meo.get_list(args)
        # if r.status_code != 200:
        #     print("Something got wrong!")
        #     return
        # files = r.json()['contents']
        return [f for f in map(lambda f:f['name'][1:],self.listdir_cache[self.rcwd].values()) if f.startswith(text)]

    def complete_get(self,text,line,begidx, endidx):
        return self._complete_remote(text,line,begidx, endidx)

    def do_cat(self,args):
        CHUNK_SIZE = 256
        print(f"Showing the first {CHUNK_SIZE} of {args}:")
        with open(args,'r') as f:
            print(f.read(CHUNK_SIZE))
            f.close()

    def help_cat(self):
        print("Shows the first 1024 bytes of a local file")

    def do_del(self,args):
        print(f"Deleting {args}")
        r = self.meo.delete_file(args)
        self._refresh_listdir_cache()
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
        if self.rcwd != '/':
            newpathdir = f"{self.rcwd}/{args}"
        else:
            newpathdir = args
        print(f"Creating {newpathdir}")
        r = self.meo.mkdir(newpathdir)
        json_pprint(r.json())
        self._refresh_listdir_cache()

    def help_mkdir(self):
        print("Creates a new directory")

    def do_properties(self,args):
        print(f"Fetching metadata of {args}")
        r = self.meo.properties(args)
        json_pprint(r.json())

    def help_properties(self):
        print("Shows the file properties")

    def complete_properties(self,text,line,begidx, endidx):
        return self._complete_remote(text,line,begidx, endidx)


    def do_rcat(self,args):
        CHUNK_SIZE = 256
        print(f"Showing the first {CHUNK_SIZE} of {args}")
        r = self.meo.get_file(args)
        print(r.text[:CHUNK_SIZE])

    def help_rcat(self):
        print("Dumps the first 1024 bytes of a file")

    def complete_rcat(self,text,line,begidx, endidx):
        return self._complete_remote(text,line,begidx, endidx)

    def do_url(self,args):
        r = self.meo.get_media_url(args)
        rjurl = r.json()['url']
        print(rjurl)
    
    def help_url(self,args):
        print("Show the complete url to download directly a remote file")

    def complete_url(self,text,line,begidx, endidx):
        return self._complete_remote(text, line, begidx, endidx)

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
        self._refresh_listdir_cache()

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

class ChunkUploader(object):
    def __init__(self, data_to_upload, blocks=10, chunksize=0):
        self.data_to_upload = data_to_upload
        if chunksize !=  0 :
            self.chunksize = chunksize
        else:
            self.chunksize = int(len(data_to_upload) / blocks)
        self.totalsize = len(data_to_upload)
        self.readsofar = 0

    def __iter__(self):
            offset = 0
            while True:
                data = self.data_to_upload[offset:offset+self.chunksize]
                if not data:
                    sys.stderr.write("\n")
                    break
                self.readsofar += len(data)
                if self.readsofar >= self.totalsize: self.readsofar = self.totalsize
                percent = self.readsofar * 1e2 / self.totalsize
                sys.stderr.write("\r{read}/{total}  ({percent:3.0f}%)".format(read=self.readsofar,total=self.totalsize,
                                                                              percent=percent))
                offset += self.chunksize
                yield data

    def __len__(self):
        return self.totalsize



def main():
    description = 'manages your meocloud service'
    epilog = "With no arguments a REPL is launched \n " + \
     "The following commands are availabe as arguments:\n" + MeoCloudRepl.args_usage
    parser = argparse.ArgumentParser(description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command',help='command to execute')
    parser.add_argument('command_value',help='Value of the command',nargs='?')
    if len(sys.argv) == 1:
        MeoCloudRepl().cmdloop()
    else:
        args = parser.parse_args()
        command = args.command
        print(command)
        allowed_commands = ['mls','rls','put','del','mkdir','get','md','cput','url']
        repl = MeoCloudRepl()
        if  command not in allowed_commands:
            print(f"ERROR: '{command}' is not one of the valid commands:\n%s" % " ".join(allowed_commands) )
            print(repl.args_usage)
        if args.command_value is not None:
            command_value = args.command_value
        else: command_value = None
        repl._refresh_listdir_cache()
        if command in ['rls','mls']:
            if command_value is not None:
                repl.do_mls(command_value)
            else: repl.do_mls('/')
        elif command == 'md':
            repl.do_properties(command_value)
        elif command == 'get':
            repl.do_get(command_value)
        elif command == 'put':
            repl.do_put(command_value)
        elif command == 'del':
            repl.do_del(command_value)
        elif command == 'mkdir':
            repl.do_mkdir(command_value)
        elif command == 'cput':
            repl.do_cput(command_value)
  

if __name__ == '__main__':
    main()
