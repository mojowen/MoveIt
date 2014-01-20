import commands

class Local:

    base_dir = None

    def cd(self,dir):
        self.base_dir = dir

    def c(self,command):
        if self.base_dir is not None:
            command = 'cd '+self.base_dir+';'+command

        return commands.getstatusoutput(command)[1]
