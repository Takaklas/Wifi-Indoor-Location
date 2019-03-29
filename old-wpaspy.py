#!/usr/bin/python
#
# wpa_supplicant/hostapd control interface using Python
# Copyright (c) 2013, Jouni Malinen <j@w1.fi>
#
# This software may be distributed under the terms of the BSD license.
# See README for more details.

from __future__ import print_function

import os
import stat
import socket
import select
import sys

counter = 0

class Ctrl:
    def __init__(self, path, port=9877):
        global counter
        self.started = False
        self.attached = False
        self.path = path
        self.port = port

        try:
            mode = os.stat(path).st_mode
            if stat.S_ISSOCK(mode):
                self.udp = False
            else:
                self.udp = True
        except:
            self.udp = True

        if not self.udp:
            self.s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            self.dest = path
            self.local = "/tmp/wpa_ctrl_" + str(os.getpid()) + '-' + str(counter)
            counter += 1
            self.s.bind(self.local)
            try:
                self.s.connect(self.dest)
            except Exception as e:
                self.s.close()
                os.unlink(self.local)
                raise
        else:
            try:
                self.s = None
                ai_list = socket.getaddrinfo(path, port, socket.AF_INET,
                                             socket.SOCK_DGRAM)
                for af, socktype, proto, cn, sockaddr in ai_list:
                    self.sockaddr = sockaddr
                    break
                self.s = socket.socket(af, socktype)
                self.s.settimeout(5)
                self.s.sendto("GET_COOKIE", sockaddr)
                reply, server = self.s.recvfrom(4096)
                self.cookie = reply
                self.port = port
            except:
                print("connect exception ", path, str(port))
                if self.s != None:
                    self.s.close()
                raise
        self.started = True

    def __del__(self):
        self.close()

    def close(self):
        if self.attached:
            try:
                self.detach()
            except Exception as e:
                # Need to ignore this allow the socket to be closed
                self.attached = False
                pass
        if self.started:
            self.s.close()
            if not self.udp:
                os.unlink(self.local)
            self.started = False

    def request(self, cmd, timeout=10):
        if self.udp:
            self.s.sendto(self.cookie + cmd, self.sockaddr)
        else:
            if sys.version_info[0] > 2:
                self.s.send(cmd.encode())
            else:
                self.s.send(cmd)
        [r, w, e] = select.select([self.s], [], [], timeout)
        if r:
            if sys.version_info[0] > 2:
                return (self.s.recv(4096)).decode()
            else:  
                return self.s.recv(4096)
        raise Exception("Timeout on waiting response")

    def attach(self):
        if self.attached:
            return None
        res = self.request("ATTACH")
        if "OK" in res:
            self.attached = True
            return None
        raise Exception("ATTACH failed")

    def detach(self):
        if not self.attached:
            return None
        while self.pending():
            ev = self.recv()
        res = self.request("DETACH")
        if "FAIL" not in res:
            self.attached = False
            return None
        raise Exception("DETACH failed")

    def terminate(self):
        if self.attached:
            try:
                self.detach()
            except Exception as e:
                # Need to ignore this to allow the socket to be closed
                self.attached = False
        self.request("TERMINATE")
        self.close()

    def pending(self, timeout=0):
        [r, w, e] = select.select([self.s], [], [], timeout)
        if r:
            return True
        return False

    def recv(self):
        if sys.version_info[0] > 2:
            res = (self.s.recv(4096)).decode()
        else:  
            res = self.s.recv(4096)
        return res
