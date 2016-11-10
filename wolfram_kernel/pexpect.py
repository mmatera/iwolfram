from metakernel.pexpect import spawnu, EOF, TIMEOUT, ExceptionPexpect



class myspawn(spawnu):
    def __init__(self, kernel, *args,**kwargs):
        self.kernel = kernel
        self.super(myspawn,self).__init__(args,kwargs)


    def read_nonblocking(self, size=1, timeout=-1):
        if self.closed:
            raise ValueError('I/O operation on closed file.')

        if timeout == -1:
            timeout = self.timeout

        if not pty:
            return self._winread(size, timeout)

        # Note that some systems such as Solaris do not give an EOF when
        # the child dies. In fact, you can still try to read
        # from the child_fd -- it will block forever or until TIMEOUT.
        # For this case, I test isalive() before doing any reading.
        # If isalive() is false, then I pretend that this is the same as EOF.
        if not self.isalive():
            # timeout of 0 means "poll"
            r, w, e = self.__select([self.child_fd], [], [], 0)
            if not r:
                self.flag_eof = True
                raise EOF('End Of File (EOF). Braindead platform.')
        elif self.__irix_hack:
            # Irix takes a long time before it realizes a child was terminated.
            # FIXME So does this mean Irix systems are forced to always have
            # FIXME a 2 second delay when calling read_nonblocking? That sucks.
            r, w, e = self.__select([self.child_fd], [], [], 2)
            if not r and not self.isalive():
                self.flag_eof = True
                raise EOF('End Of File (EOF). Slow platform.')

        r, w, e = self.__select([self.child_fd], [], [], timeout)

        if not r:
            if not self.isalive():
                # Some platforms, such as Irix, will claim that their
                # processes are alive; timeout on the select; and
                # then finally admit that they are not alive.
                self.flag_eof = True
                raise EOF('End of File (EOF). Very slow platform.')
            else:
                raise TIMEOUT('Timeout exceeded.')

        if self.child_fd in r:
            try:
                s = os.read(self.child_fd, size)
            except OSError as err:
                if err.args[0] == errno.EIO:
                    # Linux-style EOF
                    self.flag_eof = True
                    raise EOF('End Of File (EOF). Exception style platform.')
                raise
            if s == b'':
                # BSD-style EOF
                self.flag_eof = True
                raise EOF('End Of File (EOF). Empty string style platform.')

            s = self._coerce_read_string(s)
            self._log(s, 'read')
            return s

        raise ExceptionPexpect('Reached an unexpected state.')  # pragma: no cover
