#!/usr/bin/python3

# Copyright 2025 Red Hat, Inc.
#
# NAME
#     vm-usb - VM Management USB Tool
#
# SYNOPSIS
#     vm-usb [-v|--verbose] [verb] [direct object]
#
# DESCRIPTION
#     This script is used to manage manifests and artifacts on the USB
#     device, and, by extension, can also manage the instructor's cache
#     and final foundation0 system.
#
# CHANGELOG
#   * Wed Jul 16 2025 Robert Locke <rlocke@redhat.com>
#   - clean up handling iso files for VMs
#   * Fri Jul 11 2025 Robert Locke <rlocke@redhat.com>
#   - better handle non manifest files in manifests directory
#   * Wed May 14 2025 Robert Locke <rlocke@redhat.com>
#   - clean up os.rmdir following unsuccessful umount
#   * Thu Apr 17 2025 Robert Locke <rlocke@redhat.com>
#   - clean up error handling on missing argument
#   * Thu Mar 27 2025 Robert Locke <rlocke@redhat.com>
#   - be slightly flexible on parted version - usbmkpart/usbmkboot still require 3.4+
#   * Wed Dec  4 2024 Robert Locke <rlocke@redhat.com>
#   - norock was a mistake
#   * Tue Dec  3 2024 Robert Locke <rlocke@redhat.com>
#   - add f0vmsmd5sum verb to extract md5sums into md5sum file
#   * Thu Oct  3 2024 Robert Locke <rlocke@redhat.com>
#   - at support request, adding norock to iso loop mounts
#   * Tue May 14 2024 Robert Locke <rlocke@redhat.com>
#   - move small partitions to front for gpt partitioning
#   * Thu Mar  7 2024 Robert Locke <rlocke@redhat.com>
#   - trap missing arguments
#   * Wed Oct 25 2023 Robert Locke <rlocke@redhat.com>
#   - add checking of publish date format in manifest validation
#   - clean up regex literals
#   * Tue Sep 27 2022 Robert Locke <rlocke@redhat.com>
#   - add logging to more commands (shift to _subprocess_call)
#   * Mon Sep 19 2022 Robert Locke <rlocke@redhat.com>
#   - stop 666 of log file, embed effective username in log file name
#   * Thu Sep 15 2022 Robert Locke <rlocke@redhat.com>
#   - add copyusbinstructor verb with no arguments
#   * Fri May 20 2022 Robert Locke <rlocke@redhat.com>
#   - announce when unmounting USB
#   * Mon Feb 14 2022 Robert Locke <rlocke@redhat.com>
#   - better error handling across verbs
#   * Mon Jan 31 2022 Robert Locke <rlocke@redhat.com>
#   - explore automatic paths to usbmk{boot,menu}
#   - deprecation warning for gpthybrid
#   * Mon Jul 19 2021 Robert Locke <rlocke@redhat.com>
#   - add rclone{get,put} verbs mirroring rsync{get,put}
#   * Tue Feb 23 2021 Robert Locke <rlocke@redhat.com>
#   - add some protections to usbmkboot (fail on blank msdos _usbpartitions)
#   - add support for msdos reporting ext* in _usbpartitions
#   * Fri Nov  6 2020 Robert Locke <rlocke@redhat.com>
#   - summarize error messages at end of output (verify*)
#   * Sun Sep 20 2020 Robert Locke <rlocke@redhat.com>
#   - SETUP-233 - correct artifact removal on usb "update"
#   * Mon Sep  1 2020 Robert Locke <rlocke@redhat.com>
#   - add usbverifynewer similar to verifynewer
#   * Fri May 15 2020 Robert Locke <rlocke@redhat.com>
#   - add support for -y|--yes to assume yes to all questions
#   * Fri Apr 24 2020 Robert Locke <rlocke@redhat.com>
#   - new verb verifynewer which scopes verify based on icmf date
#   * Tue Apr 21 2020 Robert Locke <rlocke@redhat.com>
#   - support numeric values in other icmf filename subparts
#   * Wed Apr  1 2020 Robert Locke <rlocke@redhat.com>
#   - disable sync mount option for USB (ten-fold performance improvement)
#   * Wed Mar  4 2020 Robert Locke <rlocke@redhat.com>
#   - add support for squashfs under content/iso
#   * Fri Nov 15 2019 Robert Locke <rlocke@redhat.com>
#   - add gptefi v. gpthybrid support
#   * Mon May 20 2019 Robert Locke <rlocke@redhat.com>
#   - add removeloop
#   * Fri Mar 29 2019 Robert Locke <rlocke@redhat.com>
#   - sketch usbmkmenu (replacement of course list menu)
#   * Wed Mar 13 2019 Robert Locke <rlocke@redhat.com>
#   - add usbmkpart
#   * Wed Feb 27 2019 Robert Locke <rlocke@redhat.com>
#   - remove needs to remove source type artifacts too
#   * Tue Dec  4 2018 Robert Locke <rlocke@redhat.com>
#   - convert to Python3
#   * Wed Aug 15 2018 Robert Locke <rlocke@redhat.com>
#   - avoid Fedora 28 default use of metadata_csum on ext4 filesystems
#   * Tue May 22 2018 Robert Locke <rlocke@redhat.com>
#   - correct initial deployment to ravclassroom
#   * Wed May  2 2018 Robert Locke <rlocke@redhat.com>
#   - use --inplace for rsync
#   * Mon Apr 30 2018 Robert Locke <rlocke@redhat.com>
#   - add copyrsync verb
#   * Mon Apr  2 2018 Robert Locke <rlocke@redhat.com>
#   - segregate deploy from activate to support quiesced
#   - better functionalize some verbs/activities
#   * Fri Jan 26 2018 Robert Locke <rlocke@redhat.com>
#   - address restrictive umask breaking USB
#   * Fri Nov 24 2017 Robert Locke <rlocke@redhat.com>
#   - fix usbadd and usbremove of type non-content
#   * Wed Sep 27 2017 Robert Locke <rlocke@redhat.com>
#   - begin work on f0disable and f0enable
#   - do not remove mountpoint when conflicting one exists (f0remove)
#   * Thu Sep  9 2017 Robert Locke <rlocke@redhat.com>
#   - f0remove summarize manual steps/failures at end
#   - stop unmounting USB if we did no USB activities
#   * Thu Apr 27 2017 Robert Locke <rlocke@redhat.com>
#   - usbupdate now properly recognizes newer versus older
#   * Thu Feb 23 2017 Robert Locke <rlocke@redhat.com>
#   - copy and copyusb will now replace existing manifest
#   * Tue Feb 14 2017 Robert Locke <rlocke@redhat.com>
#   - begin to address usb orphans
#   * Sun Dec  4 2016 Robert Locke <rlocke@redhat.com>
#   - usb{,size}{add,remove} now "skip" missing artifacts
#   - usbupdate treats RHCIfoundation like other manifests
#   * Tue Nov 29 2016 Robert Locke <rlocke@redhat.com>
#   - log should be 666
#   - do not exit if not running as root
#   - add rsync* verbs
#   * Mon Nov 14 2016 Robert Locke <rlocke@redhat.com>
#   - copy icmf then artifacts to make for easier cleanup
#   - add usbdiff verb
#   * Mon Apr  5 2016 Robert Locke <rlocke@redhat.com>
#   - usbmkboot now uses installed vesamenu.c32 (and support files)
#   - add validation to _read_manifest
#   * Tue Dec 15 2015 Robert Locke <rlocke@redhat.com>
#   - add --chmod to rsync to hopefully override permissions on f0
#   * Sun Nov 22 2015 Robert Locke <rlocke@redhat.com>
#   - add recursive removal of boot directory with usb{remove,add}
#   * Mon Nov 18 2015 Robert Locke <rlocke@redhat.com>
#   - add cacheusb and cachef0 verbs
#   - deprecate use of has_key
#   * Mon Oct 19 2015 Robert Locke <rlocke@redhat.com>
#   - compare hostname to usage
#   * Fri Sep 25 2015 Robert Locke <rlocke@redhat.com>
#   - change usbmkboot to chattr ldlinux.sys to turn off immutable
#   * Thu Aug 27 2015 Robert Locke <rlocke@redhat.com>
#   - change _chmod to detect recursion (should fix boot permissions)
#   - add source size and dest exists to _rsync logger.info
#   - change directory listing/sorting to be "natural"
#   * Fri Jul 24 2015 Robert Locke <rlocke@redhat.com>
#   - typo in _removeartifact was improperly uninstalling rpm
#   * Wed Mar  4 2015 Robert Locke <rlocke@redhat.com>
#   - add size, usbsizeadd, and usbsizeremove verbs
#   * Tue Feb  3 2015 Robert Locke <rlocke@redhat.com>
#   - change usbupdate (and usbadd) to only support ILT modality on USB
#   * Tue Jan 13 2015 Robert Locke <rlocke@redhat.com>
#   - add usbupdate
#   * Fri Jan  2 2015 Robert Locke <rlocke@redhat.com>
#   - add some f0 management options: f0list, f0remove
#   * Thu Dec 11 2014 Robert Locke <rlocke@redhat.com>
#   - protect from paths input as part of manifest filename
#   * Fri Oct 31 2014 Robert Locke <rlocke@redhat.com>
#   - tweak usbadd to replace RHCIfoundation-* or <name>-<technology>-*
#   - tweak sorting of courseusb finding manifest
#   - perform sync during usbumount
#   * Sun Sep 28 2014 Robert Locke <rlocke@redhat.com>
#   - disable ext4 64-bit that is not supported yet by extlinux
#   * Thu Sep 25 2014 Robert Locke <rlocke@redhat.com>
#   - add support for kpartx virtual stick
#   * Sun Sep 14 2014 Robert Locke <rlocke@redhat.com>
#   - add -v|--verbose - DEBUG to console, enable --progress on rsync
#   - add space report to usblist
#   - usbadd calculates disk space and aborts if insufficient
#   - usbremove reports space savings
#   * Thu Aug  7 2014 Robert Locke <rlocke@redhat.com>
#   - shift/save output to log file /tmp/vm-usb-<date>.log
#   * Thu Jul 24 2014 Robert Locke <rlocke@redhat.com>
#   - Add remove verb
#   - Add rmobsoletes verb
#   * Mon Jul  7 2014 Robert Locke <rlocke@redhat.com>
#   - add documentation stub for usbmkboot
#   * Thu Jul  3 2014 Robert Locke <rlocke@redhat.com>
#   - add usbverify verb to selectively verify manifests on USB
#   - add some blank lines to outputs of verify and validate
#   * Wed Jul  2 2014 Robert Locke <rlocke@redhat.com>
#   - establish stub of new verb f0validate
#   * Tue Jun 24 2014 Robert Locke <rlocke@redhat.com>
#   - correct usbvalidate check of boot files (opening of manifest)
#   * Fri Jun 20 2014 Robert Locke <rlocke@redhat.com>
#   - stop using /mnt/temp-dvd as a temporary mountpoint - move to /tmp
#   - clean up /tmp/tmpXXXXXX directories if we created them
#   * Thu Jun 19 2014 Robert Locke <rlocke@redhat.com>
#   - fix initial format failures
#   * Thu Jun 12 2014 Robert Locke <rlocke@redhat.com>
#   - add quickverify
#   * Tue May 27 2014 Robert Locke <rlocke@redhat.com>
#   - add summary result to verify and usbvalidate
#   * Sun May 25 2014 Robert Locke <rlocke@redhat.com>
#   - add some additional output and correct config file environment
#   * Mon May 20 2014 Robert Locke <rlocke@redhat.com>
#   - next release

"""vm-usb - VM Management USB Tool

USAGE
    vm-usb [-v|--verbose] [verb] [direct object]

Starting without a verb brings up the interactive console.
Verbose directs DEBUG output to console and enables progress on rsync.
"""

# To switch to Python2.7, change first line shbang and uncomment __future__
#from __future__ import print_function
import datetime
import time
import errno
import glob
import io
import logging
import os
import pwd
import re
import readline
import select
import shlex
import socket
import subprocess
import sys
import tempfile
try:
    import yaml
except ImportError:
    print("\033[91mERROR\033[0m: PyYAML (or python3-pyyaml) package is missing.", file=sys.stderr)
    sys.exit(1)
from sys import version_info
if version_info[0] == 3:
    import collections.abc
    collectionsAbc = collections.abc
elif version_info[0] == 2:
    import collections
    collectionsAbc = collections
    try:
        input = raw_input
    except NameError:
        pass
else:
    print("\033[91mERROR\033[0m: Unknown python version - input function not safe", file=sys.stderr)
    sys.exit(1)

# Hack to support Python 2.6 on RHEL 6
#if "check_output" not in dir( subprocess ): # duck punch it in!
#    def _f(*popenargs, **kwargs):
#        if 'stdout' in kwargs:
#            raise ValueError('stdout argument not allowed, it will be overridden.')
#        process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
#        output, unused_err = process.communicate()
#        retcode = process.poll()
#        if retcode:
#            cmd = kwargs.get("args")
#            if cmd is None:
#                cmd = popenargs[0]
#            raise subprocess.CalledProcessError(retcode, cmd)
#        return output
#    subprocess.check_output = _f

# Replace subprocess.call with this for logger redirection
def _subprocess_call(popenargs, logger, stdout_log_level=logging.DEBUG, stderr_log_level=logging.ERROR, **kwargs):
    """
    Variant of subprocess.call that accepts a logger instead of stdout/stderr,
    and logs stdout messages via logger.debug and stderr messages via
    logger.error.
    Courtesy of: https://gist.github.com/bgreenlee/1402841
    """
    child = subprocess.Popen(popenargs, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, **kwargs)
    log_level = {child.stdout: stdout_log_level,
                 child.stderr: stderr_log_level}
    def check_io():
        ready_to_read = select.select([child.stdout, child.stderr], [], [], 1000)[0]
        for io in ready_to_read:
            line = io.readline()
            if len(line) != 0:
                logger.log(log_level[io], line[:-1])
    # keep checking stdout/stderr until the child exits
    while child.poll() is None:
        check_io()
    check_io() # check again to catch anything after the process exits
    return child.wait()

# global options
# Label for USB device
rht_label = 'RHTINST'
# Mount point of USB
rht_usbmount = ''
# Partitioning of USB
rht_usbparts = {}
# Parent directory of foundation0
rht_kioskdir = '/content/'
# List of artifacts already checked
rht_already = set()
# Configuration
config = {}
# Verbosity
verbose = False
# Log file name
rht_logfile = '/tmp/vm-usb-' + pwd.getpwuid(os.geteuid()).pw_name + '-' + datetime.date.today().strftime('%Y%m%d') + '.log'
# Return code for non-interactive
rht_rc = 0
# Error message summary
error_summary = ''
# Whether to ignore prompt of yes/no
alwaysyes = False

class _ManifestValidationException(Exception):
   """There was a problem validating the manifest."""
   pass

def _configure_logging():
    """
    Initialize logger
    """
    if os.path.exists(rht_logfile) and not _w(rht_logfile):
        print("File \"" + rht_logfile + "\" not writeable", file=sys.stderr)
        sys.exit(2)
    logger = logging.getLogger('vm-usb')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(rht_logfile,mode="a")
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    if verbose:
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)-15s %(levelname)-8s %(message)s")
    fh.setFormatter(formatter)
    formatter = logging.Formatter("%(levelname)-8s %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

def _checkroot():
    """
    Verify that we are running with EUID of root
    """
    logger = logging.getLogger('vm-usb')
    if os.geteuid() == 0:
        logger.debug("Running with effective root privileges")
        #source = rht_logfile
        #try:
        #    retcode = subprocess.call("chmod 666 \"" + source + "\" &>/dev/null", shell=True)
        #    if retcode == 0:
        #        logger.debug(source + ": chmod OK")
        #    else:
        #        logger.error("chmod failed of " + source + ": retcode " + str(retcode))
        #except OSError as e:
        #    logger.error("chmod execution failed: " + str(e))
    else:
        logger.error("You should be root to run this utility (use sudo)")
        #sys.exit(1)

def _r(file):
   """Return true if the named file is readable."""
   return os.access(file, os.R_OK)

def _w(file):
   """Return true if the named file is writeable."""
   return os.access(file, os.W_OK)

def _bytes2human(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i+1)*10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n

def _cmd_exists(cmd):
   """Return true if the named cmd exists."""
   return subprocess.call("type " + cmd, shell=True,
       stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

def _only_upper(s):
   """Return only the upper case letters from string."""
   return [x for x in s if x.isupper()]

def _natsort(l):
   """Sort the given list in the way that humans expect."""
   convert = lambda text: int(text) if text.isdigit() else text
   alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
   return sorted(l, key=alphanum_key)

def _umount(target):
   """
   Function to unmount target
   """
   logger = logging.getLogger('vm-usb')
   logger.debug("Unmounting " + target)
   # Loop 5 times
   for i in range(5):
      logger.debug("Unmounting try #" + str(i + 1))
      try:
         retcode = _subprocess_call("umount \"" + target + "\"", logger, shell=True)
         if retcode == 0:
            logger.debug(target + ": Unmount OK")
            return
         else:
            logger.error("Unmount failed to " + target + ": retcode " + str(retcode))
      except OSError as e:
         logger.error("Unmount execution failed: " + str(e))
      lines = ''
      try:
         lines = subprocess.check_output(['grep', target, '/etc/mtab']).decode()
      except:
         logger.debug(target + ": no longer mounted")
         return
      if lines and i < 4:
         parts = lines.split(' ')
         logger.error("Are you still in the directory " + parts[1] + "?")
         logger.error("You have thirty seconds to get out")
         time.sleep(30)
         logger.info("Re-attempting unmount")

def _fstabit(destination, target):
   """
   Function to add mount entry to fstab and then mount it
   """
   logger = logging.getLogger('vm-usb')
   logger.info("Mounting " + destination + " to " + target)
   _createdir(target)
   if destination.endswith('.iso'):
      fstabline = destination + "   " + target + "   iso9660   loop,ro   0 0"
   else:
      fstabline = destination + "   " + target + "   auto   loop,ro   0 0"
   if not fstabline in open("/etc/fstab").read():
      # Only add line if not already there
      logger.debug("Adding line to fstab")
      with open("/etc/fstab", "a") as fstab:
         fstab.write(fstabline + "\n")
   try:
      retcode = _subprocess_call("mount -a", logger, shell=True)
      if retcode == 0:
         logger.debug(target + ": mount OK")
      else:
         logger.error("Mount failed to " + target + ": retcode " + str(retcode))
   except OSError as e:
      logger.error("Mount execution failed: " + str(e))

def _unfstabit(destination, target):
   """
   Function to unmount and remove mount entry in fstab
   """
   global error_summary
   logger = logging.getLogger('vm-usb')
   logger.info("Unmounting " + destination + " from " + target)
   # only unmount if currently mounted
   if os.path.ismount(target):
      try:
         retcode = _subprocess_call("umount " + destination, logger, shell=True)
         if retcode == 0:
            logger.debug(destination + ": umount OK")
         else:
            logger.error("Umount failed of " + destination + ": retcode " + str(retcode))
            error_summary = error_summary + "\nManually unmount " + destination
      except OSError as e:
         logger.error("Umount execution failed: " + str(e))
         error_summary = error_summary + "\nManually unmount " + destination
   else:
      logger.debug(target + ": mountpoint not currently mounted")
   # remove from fstab
   logger.debug("Removing " + destination + " " + target + " from /etc/fstab")
   if destination.endswith('.iso'):
      fstabline = destination + "   " + target + "   iso9660   loop,ro   0 0"
   else:
      fstabline = destination + "   " + target + "   auto   loop,ro   0 0"
   f = open("/etc/fstab","r")
   lines = f.readlines()
   f.close()
   f = open("/etc/fstab","w")
   for line in lines:
      if fstabline not in line:
         f.write(line)
   f.close()
   # check to make sure there is not a second one in fstab (conflicts)
   if destination.endswith('.iso'):
      fstabline = destination + "   " + target + "   iso9660   loop,ro   0 0"
   else:
      fstabline = destination + "   " + target + "   auto   loop,ro   0 0"
   if not fstabline in open("/etc/fstab").read():
      if os.path.isdir(target):
         try:
            os.rmdir(target)
            logger.debug(target + ": rmdir OK")
         except OSError as e:
            logger.error("Directory removal failed of " + target)
            logger.error("os.rmdir execution failed: " + str(e))
      else:
         logger.debug(target + ": mountpoint does not exist")
   else:
      try:
         retcode = _subprocess_call("mount -a", logger, shell=True)
         if retcode == 0:
            logger.debug(target + ": mount OK")
         else:
            logger.error("Mount failed to " + target + ": retcode " + str(retcode))
      except OSError as e:
         logger.error("Mount execution failed: " + str(e))

def _mountdvd(destination, target):
   """
   Function to mount DVD iso destination to target
   """
   logger = logging.getLogger('vm-usb')
   logger.debug("Mounting DVD " + destination + " to " + target)
   _createdir(target)
   try:
      retcode = _subprocess_call("mount -o loop,ro \"" + destination + "\" \"" + target + "\"", logger, shell=True)
      if retcode == 0:
         logger.debug(target + ": DVD mount OK")
      else:
         logger.error("Mount DVD failed to " + target + ": retcode " + str(retcode))
   except OSError as e:
      logger.error("Mount DVD execution failed: " + str(e))

def _usagematch(artifact):
   """Test whether artifact['usage'] matches system"""
   # Test to see if we should deploy based on hostname
   myhostname = socket.gethostname()
   if 'classroom' in artifact['usage']:
      return True
   elif 'foundation' in artifact['usage'] and 'foundation' in myhostname:
      return True
   else:
      return False

def _deploymanifest(manifestFile, location):
    """Copy manifest from location to foundation0."""
    global rht_usbmount
    manifestDirname = os.path.dirname(manifestFile)
    manifestFilename = os.path.basename(manifestFile)
    logger = logging.getLogger('vm-usb')
    rht_cachedir = config['repository']
    if location == "Cache":
        mfsource = os.path.join(rht_cachedir, manifestFilename)
    elif location == "USB":
        rht_usbmount = _usbmount()
        if not rht_usbmount:
            return
        mfsource = os.path.join(rht_usbmount, "manifests", manifestFilename)
    elif location == "Remote":
        mfsource = os.path.join("/tmp", manifestFilename)
    mfl = os.path.join(rht_kioskdir, "manifests")
    logger.info("Deploying from " + location + " Manifest: " + manifestFilename)
    try:
        data = _read_manifest(mfsource)
    except _ManifestValidationException as mfe:
        logger.error("Manifest " + mfsource + " is invalid.")
        logger.error(str(mfe))
        return False
    rht_course = data['curriculum']['name']
    rht_technology = data['curriculum']['technology']
    if manifestFilename.upper().startswith('RHCI'):
        activate = True
    else:
        activate = False
    if os.path.isdir(mfl):
        killmanifests = [manifest for manifest in _manifestsall(mfl) if manifest.startswith(rht_course)]
        keepmanifests = [manifest for manifest in _manifestsall(mfl) if not manifest.startswith(rht_course)]
        if killmanifests:
            if len(killmanifests) > 1:
                logger.error("Too many manifests to replace")
                for w in killmanifests:
                    logger.error("Want to replace " + w)
                logger.error("Use f0remove to eliminate manifests first")
                return False
            w = killmanifests[0]
            if w.endswith(".icmf"):
                activate = True
            try:
                data_w = _read_manifest(os.path.join(mfl, w))
            except _ManifestValidationException as mfe:
                logger.error("Manifest " + w + " is invalid.")
                logger.error(str(mfe))
                return False
            for a in data_w['curriculum']['artifacts']:
                if a['type'].startswith('content'):
                    a_others = []
                    # Skip those that are to be installed
                    for f in data['curriculum']['artifacts']:
                        if f['filename'] == a['filename']:
                            a_others.append(f)
                    if keepmanifests:
                        for x in keepmanifests:
                            try:
                                data_x = _read_manifest(os.path.join(mfl, x))
                            except:
                                logger.error("Manifest " + x + " is invalid.")
                                logger.error(str(mfe))
                                return False
                            # Skip those referenced in keepmanifests
                            for f in data_x['curriculum']['artifacts']:
                                if f['filename'] == a['filename']:
                                    a_others.append(f)
                    _removeartifact(a, a_others)
            logger.info("Deleting manifest " + w)
            _delete(os.path.join(mfl, w))
        else:
            activemanifests = _manifestsactive(mfl)
            if not activemanifests:
                activate = True
    else:
        activate = True
    # Copy the manifest file itself
    if activate:
        target = os.path.join(mfl, manifestFilename)
    else:
        target = os.path.join(mfl, manifestFilename + '_quiesced')
    _rsync(mfsource, target)
    # Copy the artifacts
    for artifact in data['curriculum']['artifacts']:
        if artifact['type'].startswith('content'):
            if location == "Cache":
                source = os.path.join(rht_cachedir, artifact['filename'])
            elif location == "USB":
                source = os.path.join(rht_usbmount, artifact['target directory'], artifact['filename'])
            elif location == "Remote":
                source = os.path.join(manifestDirname, artifact['filename'])
            destination = os.path.join(rht_kioskdir, artifact['target directory'], artifact['filename'])
            # Need to branch (iso, tar, else)
            _deployartifact(artifact, source, destination)
            if activate:
                manifests_compare = _manifests(mfl)
                manifests_compare = manifests_compare.remove(manifestFilename)
                a_others = _dupeartifact(artifact, manifests_compare, mfl)
                _activateartifact(artifact, a_others)
    logger.info("Appears to have copied manifest from " + location + " to f0.")

def _deployartifact(artifact, source, destination):
   """Branch deployment of artifact based on content type"""
   logger = logging.getLogger('vm-usb')
   if not _usagematch(artifact):
      logger.info(artifact['filename'] + ": skipped - wrong usage")
      return
   if 'iso' in artifact['content type']:
      # For iso, copy it, then mount if mountpoint provided
      _rsync(source, destination)
      target = destination
   elif 'rpm' in artifact['content type']:
      target = destination
      _rsync(source, destination)
   elif 'pdf' in artifact['content type']:
      # Set target to absolute final name if it exists
      if 'final name' in artifact:
         target = os.path.join(rht_kioskdir, artifact['final name'])
      else:
         target = destination
      _rsync(source, target)
   elif 'file' in artifact['content type']:
      # Set target to relative final name if it exists
      if 'final name' in artifact:
         target = os.path.join(rht_kioskdir, artifact['final name'])
      else:
         target = destination
      _rsync(source, target)
   elif 'boot' in artifact['content type']:
      target = destination
      _rsync(source, destination)
   else:
      logger.error(artifact['filename'] + ": skipped - bad content type")
   if 'hardlink names' in artifact:
      for linkname in artifact['hardlink names']:
         hardlink = os.path.join(rht_kioskdir, linkname)
         if os.path.exists(hardlink):
            logger.debug("Hard link already exists: " + linkname)
         else:
            _createdir(os.path.dirname(hardlink))
            logger.debug("Creating hard link: " + linkname)
            os.link(target, hardlink)

def _removeartifact(artifact, artifact_others):
   """Branch removal of artifact based on content type"""
   logger = logging.getLogger('vm-usb')
   if artifact_others:
      logger.info(artifact['filename'] + ": Exists in other")
   else:
      logger.info(artifact['filename'] + ": Unique artifact")
   if not _usagematch(artifact):
      logger.info(artifact['filename'] + ": skipped - wrong usage")
      return
   # Compare/eliminate hardlink names
   if 'hardlink names' in artifact:
      for linkname in artifact['hardlink names']:
         removeit = True
         hardlink = os.path.join(rht_kioskdir, linkname)
         if artifact_others:
            for a in artifact_others:
               if 'hardlink names' in a:
                  if linkname in a['hardlink names']:
                     removeit = False
         if removeit:
            if os.path.exists(hardlink):
               logger.debug(linkname + ": Hard link deleting")
               _delete(hardlink)
            else:
               logger.debug(linkname + ": Hard link missing")
         else:
            logger.debug(linkname + ": Hard link referenced")
   # For iso, unfstab if mountpoint provided, then delete
   if 'iso' in artifact['content type']:
      destination = os.path.join(rht_kioskdir, artifact['target directory'], artifact['filename'])
      if 'final name' in artifact:
         target = os.path.join(rht_kioskdir, artifact['final name'])
         unmountit = True
         if artifact_others:
            for a in artifact_others:
               if 'iso' in a['content type']:
                  if 'final name' in a:
                     if artifact['final name'] in a['final name']:
                        unmountit = False
         if unmountit:
            logger.debug(target + ": Mountpoint unfstab")
            _unfstabit(destination, target)
         else:
            logger.debug(target + ": Mountpoint referenced")
      else:
         logger.debug(artifact['filename'] + ": Mountpoint missing")
      removeit = True
      if artifact_others:
         for a in artifact_others:
            if artifact['target directory'] in a['target directory']:
               removeit = False
      if removeit:
         logger.debug(artifact['filename'] + ": ISO deleting")
         _delete(destination)
      else:
         logger.debug(artifact['filename'] + ": ISO referenced")
   # For rpm, uninstall, then delete
   elif 'rpm' in artifact['content type']:
      uninstallit = True
      if artifact_others:
         for a in artifact_others:
            if 'rpm' in a['content type']:
               uninstallit = False
      if uninstallit:
         logger.debug(artifact['filename'] + ": RPM uninstalling")
         _rpmuninstall(artifact['filename'])
      else:
         logger.debug(artifact['filename'] + ": RPM stays installed")
      removeit = True
      destination = os.path.join(rht_kioskdir, artifact['target directory'], artifact['filename'])
      if artifact_others:
         for a in artifact_others:
            if artifact['target directory'] in a['target directory']:
               removeit = False
      if removeit:
         logger.debug(artifact['filename'] + ": RPM deleting")
         _delete(destination)
      else:
         logger.debug(artifact['filename'] + ": RPM referenced")
   elif 'pdf' in artifact['content type']:
      # For pdf, remove
      removeit = True
      if 'final name' in artifact:
         target = os.path.join(rht_kioskdir, artifact['final name'])
         if artifact_others:
            for a in artifact_others:
               if 'final name' in a:
                  if artifact['final name'] in a['final name']:
                     removeit = False
      else:
         target = os.path.join(rht_kioskdir, artifact['target directory'], artifact['filename'])
         if artifact_others:
            for a in artifact_others:
               if artifact['target directory'] in a['target directory']:
                  removeit = False
      if removeit:
         logger.debug(target + ": PDF deleting")
         _delete(target)
      else:
         logger.debug(target + ": PDF referenced")
   elif 'file' in artifact['content type']:
      # For file, remove
      removeit = True
      if 'final name' in artifact:
         target = os.path.join(rht_kioskdir, artifact['final name'])
         if artifact_others:
            for a in artifact_others:
               if 'final name' in a:
                  if artifact['final name'] in a['final name']:
                     removeit = False
      else:
         target = os.path.join(rht_kioskdir, artifact['target directory'], artifact['filename'])
         if artifact_others:
            for a in artifact_others:
               if artifact['target directory'] in a['target directory']:
                  removeit = False
      if removeit:
         logger.debug(target + ": FILE deleting")
         _delete(target)
      else:
         logger.debug(target + ": FILE referenced")
   else:
      logger.error(artifact['filename'] + ": skipped - unable to remove " + artifact['content type'])

def _dupeartifact(artifact, manifests_other, manifests_location):
   """Check for artifact in manifests_other, return matches"""
   logger = logging.getLogger('vm-usb')
   x_others = []
   logger.debug("_dupeartifact artifact filen: " + artifact['filename'])
   if manifests_other:
      for w in manifests_other:
         try:
            data_w = _read_manifest(os.path.join(manifests_location, w))
         except _ManifestValidationException as mfe:
            logger.error("Manifest " + w + " is invalid.")
            logger.error(str(mfe))
            return False
         for f in data_w['curriculum']['artifacts']:
            if f['filename'] == artifact['filename']:
               x_others.append(f)
               logger.debug("_dupeartifact found in: " + w)
            else:
               logger.debug("_dupeartifact  NOT  in: " + w)
   else:
      logger.debug("_dupeartifact NOCHECK")
   return x_others

def _activateartifact(artifact, artifact_others):
   """Branch activate of artifact based on content type"""
   logger = logging.getLogger('vm-usb')
   if artifact_others:
      logger.debug(artifact['filename'] + ": Exists in other")
   else:
      logger.debug(artifact['filename'] + ": Unique artifact")
   if not _usagematch(artifact):
      logger.debug(artifact['filename'] + ": skipped - wrong usage")
      return
   destination = os.path.join(rht_kioskdir, artifact['target directory'], artifact['filename'])
   # For iso, fstab if mountpoint provided
   if 'iso' in artifact['content type']:
      if 'final name' in artifact:
         target = os.path.join(rht_kioskdir, artifact['final name'])
         mountit = True
         if artifact_others:
            for a in artifact_others:
               if 'iso' in a['content type']:
                  if 'final name' in a:
                     if artifact['final name'] in a['final name']:
                        mountit = False
         if mountit:
            logger.debug(target + ": Mountpoint fstab")
            _fstabit(destination, target)
         else:
            logger.debug(target + ": Mountpoint referenced")
      else:
         logger.debug(artifact['filename'] + ": Mountpoint missing")
   # For rpm, install
   elif 'rpm' in artifact['content type']:
      installit = True
      if artifact_others:
         for a in artifact_others:
            if 'rpm' in a['content type']:
               installit = False
      if installit:
         logger.debug(artifact['filename'] + ": RPM installing")
         _rpminstall(destination)
      else:
         logger.debug(artifact['filename'] + ": RPM already installed")
   else:
      logger.debug(artifact['filename'] + ": skipped " + artifact['content type'])

def _disableartifact(artifact, artifact_others):
   """Branch disable of artifact based on content type"""
   logger = logging.getLogger('vm-usb')
   if artifact_others:
      logger.debug(artifact['filename'] + ": Exists in other")
   else:
      logger.debug(artifact['filename'] + ": Unique artifact")
   if not _usagematch(artifact):
      logger.debug(artifact['filename'] + ": skipped - wrong usage")
      return
   # For iso, unfstab if mountpoint provided
   if 'iso' in artifact['content type']:
      if 'final name' in artifact:
         destination = os.path.join(rht_kioskdir, artifact['target directory'], artifact['filename'])
         target = os.path.join(rht_kioskdir, artifact['final name'])
         unmountit = True
         if artifact_others:
            for a in artifact_others:
               if 'iso' in a['content type']:
                  if 'final name' in a:
                     if artifact['final name'] in a['final name']:
                        unmountit = False
         if unmountit:
            logger.debug(target + ": Mountpoint unfstab")
            _unfstabit(destination, target)
         else:
            logger.debug(target + ": Mountpoint referenced")
      else:
         logger.debug(artifact['filename'] + ": Mountpoint missing")
   # For rpm, uninstall
   elif 'rpm' in artifact['content type']:
      uninstallit = True
      if artifact_others:
         for a in artifact_others:
            if 'rpm' in a['content type']:
               uninstallit = False
      if uninstallit:
         logger.debug(artifact['filename'] + ": RPM uninstalling")
         _rpmuninstall(artifact['filename'])
      else:
         logger.debug(artifact['filename'] + ": RPM stays installed")
   else:
      logger.debug(artifact['filename'] + ": skipped " + artifact['content type'])

def _checkartifact(filename, checksum, location):
   """
   Function to check an individual manifest artifact
   """
   # Check does an md5sum on artifact at location
   global rht_already
   failure = False
   if not os.path.isdir(location):
      return "\033[91mMISSING\033[0m"
   wannacheck = os.path.join(location, filename)
   if not os.path.isfile(wannacheck):
      return "\033[91mMISSING\033[0m"
   if checksum == "NOCHECK":
      return "\033[92mEXISTS \033[0m"
   elif checksum == "SIZE":
      return str(os.path.getsize(wannacheck))
   if wannacheck in rht_already:
      return "\033[92mALREADY\033[0m"
   else:
      rht_already.add(wannacheck)
   try:
      retcode = subprocess.call("echo \"" + checksum + "  " + wannacheck + "\" | md5sum -c - &>/dev/null", shell=True)
      if retcode < 0:
         return "\033[91mABORTED\033[0m"
      elif retcode > 0:
         return "\033[91mCORRUPT\033[0m"
      else:
         return "\033[92mGOODSUM\033[0m"
   except OSError as e:
      return "\033[91mEXEFAIL\033[0m"

def _chmod(source):
   """
   Uses chmod to make available source
   """
   global error_summary
   logger = logging.getLogger('vm-usb')
   opts = ""
   if os.path.isdir(source):
      opts = "--recursive"
   try:
      retcode = _subprocess_call("chmod " + opts + " a+rX \"" + source + "\"", logger, shell=True)
      if retcode == 0:
         logger.debug(source + ": chmod OK")
      else:
         logger.error("chmod failed of " + source + ": retcode " + str(retcode))
         error_summary = error_summary + "\nchmod failed of " + source
   except OSError as e:
      logger.error("chmod execution failed: " + str(e))

def _rsync(source, destination):
   """
   Uses rsync to copy from source to destination
   """
   global error_summary
   if verbose:
      progress="--progress "
   else:
      progress=""
   logger = logging.getLogger('vm-usb')
   if os.path.isfile(source):
      sourcesize = " (" + _bytes2human(os.path.getsize(source)) + ")"
   else:
      sourcesize = " (dir)"
   if os.path.exists(destination):
      destexists = " (exists)"
   else:
      destexists = ""
   logger.info("Copying " + source + sourcesize + " to " + destination + destexists)
   _createdir(os.path.dirname(destination))
   try:
      retcode = _subprocess_call("rsync -trv --inplace --chmod=ugo=rwX " + progress + "--copy-unsafe-links \"" + source + "\" \"" + destination + "\"", logger, shell=True)
      if retcode == 0:
         logger.debug(destination + ": copy OK")
         _chmod(destination)
      else:
         logger.error("Copy failed to " + destination + ": retcode " + str(retcode))
         error_summary = error_summary + "\nCopy failed of " + source
   except OSError as e:
      logger.error("rsync execution failed: " + str(e))

def _rclonesync(source, destination):
   """
   Uses rclone to copy from source to destination (one is remote)
   """
   global error_summary
   if verbose:
      progress="--progress "
   else:
      progress=""
   logger = logging.getLogger('vm-usb')
   if os.path.isfile(source):
      sourcesize = " (" + _bytes2human(os.path.getsize(source)) + ")"
   else:
      sourcesize = ""
   if os.path.exists(destination):
      destexists = " (exists)"
   else:
      destexists = ""
   logger.info("Copying " + source + sourcesize + " to " + destination + destexists)
   try:
      retcode = _subprocess_call("rclone " + progress + "--copy-links copy \"" + source + "\" \"" + destination + "\"", logger, shell=True)
      if retcode == 0:
         logger.debug(destination + ": copy OK")
      else:
         logger.error("Copy failed to " + destination + ": retcode " + str(retcode))
         error_summary = error_summary + "\nCopy failed of " + source
   except OSError as e:
      logger.error("rclone execution failed: " + str(e))

def _remotesync(source, destination):
   """
   Uses rsync to copy from source to destination (one is remote)
   """
   global error_summary
   if verbose:
      progress="--progress "
   else:
      progress=""
   logger = logging.getLogger('vm-usb')
   if os.path.isfile(source):
      sourcesize = " (" + _bytes2human(os.path.getsize(source)) + ")"
   else:
      sourcesize = ""
   if os.path.exists(destination):
      destexists = " (exists)"
   else:
      destexists = ""
   logger.info("Copying " + source + sourcesize + " to " + destination + destexists)
   try:
      retcode = _subprocess_call("rsync -trv --inplace --chmod=ugo=rwX " + progress + "--copy-unsafe-links \"" + source + "\" \"" + destination + "\"", logger, shell=True)
      if retcode == 0:
         logger.debug(destination + ": copy OK")
      else:
         logger.error("Copy failed to " + destination + ": retcode " + str(retcode))
         error_summary = error_summary + "\nCopy failed of " + source
   except OSError as e:
      logger.error("rsync execution failed: " + str(e))

#def _untar(source, target):
#   """
#   Function to extract source to target directory
#   """
#   logger = logging.getLogger('vm-usb')
#   logger.info("Extracting " + source + " to " + target)
#   _createdir(target)
#   try:
#      retcode = _subprocess_call("tar -xv -C \"" + target + "\" -f \"" + source + "\" 2>/dev/null", logger, shell=True)
#      if retcode == 0:
#         logger.debug(target + ": untar OK")
#         _chmod(target)
#      else:
#         logger.error("Extract failed to " + target + ": retcode " + str(retcode))
#   except OSError as e:
#      logger.error("untar execution failed: " + str(e))

#def _unxz(source, destination):
#   """
#   Function to uncompress source to destination
#   """
#   logger = logging.getLogger('vm-usb')
#   logger.info("Uncompressing " + source + " to " + destination)
#   _createdir(os.path.dirname(destination))
#   try:
#      retcode = _subprocess_call("xz --uncompress --verbose --keep --stdout \"" + source + "\" > \"" + destination + "\"", logger, shell=True)
#      if retcode == 0:
#         logger.debug(destination + ": unxz OK")
#         _chmod(destination)
#      else:
#         logger.error("Uncompress failed to " + destination + ": retcode " + str(retcode))
#   except OSError as e:
#      logger.error("unxz execution failed: " + str(e))

def _rpminstall(source):
   """
   Function to install source rpm
   """
   global error_summary
   logger = logging.getLogger('vm-usb')
   logger.info("Installing " + source)
   myrpm = os.path.basename(source)
   if myrpm.endswith('.rpm'):
      myrpm = myrpm[:-4]
   try:
      retcode = subprocess.call("yum list installed \"" + myrpm + "\" &>/dev/null", shell=True)
      if retcode == 0:
         logger.debug(source + ": already installed")
         return
   except OSError as e:
      logger.error("yum list execution failed: " + str(e))
   try:
      retcode = _subprocess_call("yum -y install \"" + source + "\"", logger, shell=True)
      if retcode == 0:
         logger.debug(source + ": install OK")
      else:
         logger.error("Install failed of " + source + ": retcode " + str(retcode))
         error_summary = error_summary + "\nManually install packge " + myrpm
   except OSError as e:
      logger.error("yum execution failed: " + str(e))

def _rpmuninstall(source):
   """
   Function to uninstall source rpm
   """
   global error_summary
   logger = logging.getLogger('vm-usb')
   logger.info("Uninstalling " + source)
   myrpm = os.path.basename(source)
   if myrpm.endswith('.rpm'):
      myrpm = myrpm[:-4]
   try:
      retcode = subprocess.call("yum list installed \"" + myrpm + "\" &>/dev/null", shell=True)
      if retcode == 0:
         logger.debug(source + ": currently installed")
         try:
            retcode = _subprocess_call("yum -y remove \"" + myrpm + "\"", logger, shell=True)
            if retcode == 0:
               logger.debug(source + ": uninstall OK")
            else:
               logger.error("Uninstall failed of " + myrpm + ": retcode " + str(retcode))
         except OSError as e:
            logger.error("yum execution failed: " + str(e))
            error_summary = error_summary + "\nManually remove packge " + myrpm
      else:
         logger.debug(source + ": already uninstalled")
   except OSError as e:
      logger.error("yum list execution failed: " + str(e))

def _delete(destination):
   """
   Function to delete destination
   """
   global error_summary
   logger = logging.getLogger('vm-usb')
   if os.path.exists(destination):
      logger.debug("Deleting " + destination)
      try:
         os.remove(destination)
      except OSError as e:
         logger.error("os.remove execution failed: " + str(e))
         error_summary = error_summary + "\nManually delete " + destination
         return
      if os.path.dirname(destination).endswith('manifests'):
         # Do not delete the manifests directory
         return
      if os.path.dirname(destination) in config['repository']:
         # Do not delete the cache directory
         return
      logger.debug("Deleting empty directories " + os.path.dirname(destination))
      try:
         os.removedirs(os.path.dirname(destination))
      except OSError as e:
         # Ignoring failures in deleting directories
         logger.debug("Directory not empty " + os.path.dirname(destination))
   else:
      logger.debug("NOT deleting " + destination + " - does not exist")

def _rename(source, destination):
   """
   Function to delete destination
   """
   global error_summary
   logger = logging.getLogger('vm-usb')
   logger.debug("Renaming " + source + " to " + destination)
   try:
      os.rename(source, destination)
   except OSError as e:
      logger.error("os.rename execution failed: " + str(e))
      error_summary = error_summary + "\nManually rename " + source + " to " + destination
      return

def _read_manifest(manifestFilename):
   """Get the object corresponding to the manifest's YAML."""
   currfile = os.path.basename(manifestFilename)
   if not currfile.lower().endswith((".icmf", ".icmf_quiesced")):
      raise _ManifestValidationException("Manifest does not end with .icmf or .icmf_quiesced")
   if not _r(manifestFilename):
      raise IOError("File \"" + manifestFilename + "\" not found")
   with open(manifestFilename) as infile:
      try:
         y=yaml.load(infile, Loader=yaml.SafeLoader)
      except yaml.parser.ParserError as e:
         raise _ManifestValidationException([str(e)])
   # Audit what values are being used and look for them
   if not 'curriculum' in y:
      raise _ManifestValidationException("Not a curriculum manifest")
   x=y['curriculum']
   currkeys=['name', 'technology', 'release', 'modality', 'generation', 'locale', 'description', 'publisher', 'publish date']
   for k in currkeys:
      if not k in x or not x[k]:
         raise _ManifestValidationException("Missing or blank curriculum:" + k)
   # Validate values in fields
   # Python 3.6 (RHEL 8) datetime forces naive dates/times and no colon in tz
   if sys.version_info >= (3,7):
      publishdate = str(x['publish date'])
      dateformat = '%Y-%m-%d %H:%M:%S%z'
      try:
         dateobject = datetime.datetime.strptime(publishdate, dateformat)
      except:
         raise _ManifestValidationException("Invalid publish date format " + dateformat + ": " + publishdate)
   else:
      publishdate = subprocess.check_output('grep -oP "publish date: \\K.*" ' + manifestFilename, shell=True).decode().replace("\n","")
      dateformat = '\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}[+-]\\d{2}:\\d{2}'
      if not re.fullmatch(dateformat, publishdate):
         raise _ManifestValidationException("Invalid publish date format " + dateformat + ": " + publishdate)
   # Parse filename into components
   currfileparsed = currfile[:-5].split("-")
   # Anything missing?
   # Do components match values inside manifest and both are non-empty?
   if not currfileparsed[0] == x['name']:
      raise _ManifestValidationException("Mismatched filename name: " + currfileparsed[0])
   if not currfileparsed[1] == x['technology']:
      raise _ManifestValidationException("Mismatched filename technology: " + currfileparsed[1])
   if not currfileparsed[2] == str(x['release']):
      raise _ManifestValidationException("Mismatched filename release: " + currfileparsed[2])
   currmodalities = currfileparsed[3].split('+')
   if not currmodalities == x['modality']:
      raise _ManifestValidationException("Mismatched filename modality: " + currfileparsed[3])
   if not currfileparsed[4] == str(x['generation']):
      raise _ManifestValidationException("Mismatched filename generation: " + currfileparsed[4])
   currlocalities = currfileparsed[5].split('.')[0].split('+')
   if not currlocalities == x['locale']:
      raise _ManifestValidationException("Mismatched filename locale: " + currfileparsed[5].split('.')[0])
   # Anything bad, print message, return False
   if not 'artifacts' in x:
      raise _ManifestValidationException("No artifacts in manifest")
   artkeys=['filename', 'checksum', 'type', 'usage']
   contkeys=['content type', 'target directory']
   typevals=['content', 'source', 'linux-exe', 'windows-exe']
   conttypevals=['iso', 'tar', 'rpm', 'file', 'pdf', 'boot']
   isokeys=['final name']
   for a in x['artifacts']:
      for k in artkeys:
         if not k in a or not a[k]:
            raise _ManifestValidationException("Missing or blank artifacts:" + k)
      if a['type'] not in typevals:
         raise _ManifestValidationException("Invalid artifact type " + a['filename'] +":" + a['type'])
      if a['type'].startswith('content'):
         for k in contkeys:
            if not k in a or not a[k]:
               raise _ManifestValidationException("Missing or blank artifacts: " + a['filename'] +"" + k)
         if a['content type'] not in conttypevals:
            raise _ManifestValidationException("Invalid artifact content type " + a['filename'] +":" + a['content type'])
         if a['content type'].startswith('iso'):
            for k in isokeys:
               if not k in a or not a[k]:
                  raise _ManifestValidationException("Missing or blank artifact iso field " + a['filename'] +":" + k)
   return y

def _verify(manifestFilename,where,sum):
   """Show details about resources for the named manifest, verifying it.

      where = 0 - cache; 1 - usb; 2 - f0; 3 - f0-quiesced
      sum = 0 - md5sum; 1 - existence; 2 - size
   """
   global error_summary
   logger = logging.getLogger('vm-usb')
   try:
      y=_read_manifest(manifestFilename)
   except _ManifestValidationException as mfe:
      logger.error("Manifest " + manifestFilename + " is invalid.")
      logger.error(str(mfe))
      error_summary = error_summary + '\nManifest ' + os.path.basename(manifestFilename) + ' is invalid.'
      error_summary = error_summary + '\n' + str(mfe)
      return False

   c=y['curriculum']
   print()
   print("Verifying manifest file", os.path.basename(manifestFilename))
   logger.debug("Verifying manifest file " + os.path.basename(manifestFilename))
   print("  Publish date:", c['publish date'])
   logger.debug("  Publish date: " + str(c['publish date']))
   if sum == 0:
      print("  type        md5sum  artifact-name")
   elif sum == 1:
      print("  type        exists  artifact-name")
   else:
      print("  type         size   artifact name")
   print("  ----------- ------- -----------------------------------------------")
   goodorbad=True
   totsize=0
   for a in c['artifacts']:
      if sum == 0:
         sumtocheck = a['checksum']
      elif sum == 1:
         sumtocheck = "NOCHECK"
      else:
         sumtocheck = "SIZE"
      if where == 0:
         validity = _checkartifact(a['filename'], sumtocheck, config['repository'])
      elif where == 1:
         if a['type'].startswith('content'):
            location = os.path.join(rht_usbmount, a['target directory'])
            validity = _checkartifact(a['filename'], sumtocheck, location)
         else:
            validity = "\033[92mNOCHECK\033[0m"
      elif where == 2 or where == 3:
         if a['type'].startswith('content') and _usagematch(a):
            location = os.path.join(rht_kioskdir, a['target directory'])
            if 'iso' in a['content type']:
               validity = _checkartifact(a['filename'], sumtocheck, location)
               if 'GOODSUM' in validity or 'EXISTS' in validity:
                  if where != 3 and 'final name' in a:
                     target = os.path.join(rht_kioskdir, a['final name'])
                     destination = os.path.join(location, a['filename'])
                     if destination.endswith('.iso'):
                        fstabline = destination + "   " + target + "   iso9660   loop,ro   0 0"
                     else:
                        fstabline = destination + "   " + target + "   auto   loop,ro   0 0"
                     if not fstabline in open("/etc/fstab").read():
                        validity = "\033[91mNOFSTAB\033[0m"
                     elif not os.path.ismount(target):
                        validity = "\033[91mNOMOUNT\033[0m"
                     else:
                        # Determine /dev name
                        lines = ''
                        devname = ''
                        try:
                           lines = subprocess.check_output(['grep', target, '/etc/mtab']).decode()
                        except:
                           validity = "\033[91mNOMOUNT\033[0m"
                        if lines:
                           for line in lines.split('\n'):
                              if line:
                                 parts = line.split(' ')
                                 #print target
                                 #print parts[1]
                                 #print line
                                 if parts[1] == target:
                                    devname = parts[0]
                                 #print devname
                        # losetup --list --noheadings -O BACK-FILE /dev/loop0
                        # (--noheadings not available in RHEL 7)
                        if devname:
                           try:
                              devlist = subprocess.check_output(['losetup', '--list', '-O', 'BACK-FILE', devname]).decode()
                              if not destination in devlist:
                                 validity = "\033[91mWRNGMNT\033[0m"
                           except:
                              validity = "\033[91mNOLOOPS\033[0m"
                        else:
                           validity = "\033[91mNOMOUNT\033[0m"
            elif 'rpm' in a['content type']:
               validity = _checkartifact(a['filename'], sumtocheck, location)
               if where != 3:
                  if 'GOODSUM' in validity or 'EXISTS' in validity:
                     rpmfile = a['filename'].rstrip('.rpm')
                     try:
                        retcode = subprocess.call("rpm -V " + rpmfile + " &>/dev/null", shell=True)
                        if retcode != 0:
                           validity = "\033[91mRPMFAIL\033[0m"
                     except OSError as e:
                        validity = "\033[91mRPMFAIL\033[0m"
            elif 'pdf' in a['content type'] or 'file' in a['content type']:
               if 'final name' in a:
                  target = os.path.join(rht_kioskdir, a['final name'])
                  location = os.path.dirname(target)
                  filename = os.path.basename(target)
               else:
                  filename = a['filename']
               if 'libvirt' in filename and 'classroom.xml' in filename:
                  validity = "\033[92mNOCHECK\033[0m"
               else:
                  validity = _checkartifact(filename, sumtocheck, location)
            elif 'boot' in a['content type']:
               validity = _checkartifact(a['filename'], sumtocheck, location)
            else:
               validity = "\033[92mNOCHECK\033[0m"
            if 'GOODSUM' in validity or 'EXISTS' in validity:
               if 'hardlink names' in a:
                  for linkname in a['hardlink names']:
                     hardlink = os.path.join(rht_kioskdir, linkname)
                     if not os.path.exists(hardlink):
                        validity = "\033[91mNOLINKS\033[0m"
         else:
            validity = "\033[92mNOCHECK\033[0m"
      if 'SIZE' in sumtocheck and validity.isdigit():
         totsize = totsize + int(validity)
         validity = _bytes2human(int(validity))
      print("  %-11s %7s %s" % (a['type'], validity, a['filename']))
      logger.debug("  %-11s %-7s %s" % (a['type'], ''.join(_only_upper(validity)), a['filename']))
      if 'GOODSUM' not in validity and 'NOCHECK' not in validity and 'EXISTS' not in validity and 'ALREADY' not in validity and 'SIZE' not in sumtocheck:
         goodorbad=False
         error_summary = error_summary + '\n  ' + a['type'] + '  ' + validity + '  ' + a['filename']
   print("=====================================================================")
   if 'SIZE' in sumtocheck:
      logger.info("Manifest total size " + _bytes2human(totsize))
   if goodorbad:
      logger.info("Manifest " + os.path.basename(manifestFilename) + " passed.")
   else:
      logger.warning("Manifest " + os.path.basename(manifestFilename) + " failed.")
      error_summary = error_summary + '\nManifest ' + os.path.basename(manifestFilename) + ' failed.'
   return goodorbad

def _createdir(target):
    """
    Verify the existence of target directory or create it
    """
    logger = logging.getLogger('vm-usb')
    logger.debug("Checking for directory " + target)
    if not os.path.isdir(target):
        try:
            os.makedirs(target)
            _chmod(target)
            logger.debug(target + ": created OK")
        except OSError as e:
            logger.error("Directory creation failed of " + target)
            logger.error("os.makedirs execution failed: " + str(e))

def _mountusb(destination):
    """Function to mount USB destination."""
    logger = logging.getLogger('vm-usb')
    target = tempfile.mkdtemp()
    logger.debug("Mounting " + destination + " to " + target)
    _createdir(target)
    try:
        #retcode = subprocess.call("mount -o sync \"" + destination + "\" \"" + target + "\" &>/dev/null", shell=True)
        retcode = _subprocess_call("mount \"" + destination + "\" \"" + target + "\"", logger, shell=True)
        if retcode == 0:
            logger.debug(destination + ": mount OK")
        else:
            logger.error("USB mount failed retcode: " + str(retcode))
            return
    except OSError as e:
        logger.error("mount execution failed: " + str(e))
        return
    mfdir = os.path.join(target, "manifests")
    _createdir(mfdir)
    mfdir = os.path.join(target, "instructor")
    _createdir(mfdir)
    return target

def _remountusb(destination):
    """Function to remount USB destination with needed option."""
    logger = logging.getLogger('vm-usb')
    logger.debug("USB Remounting " + destination)
    try:
        #retcode = subprocess.call("mount -o remount,sync \"" + destination + "\" &>/dev/null", shell=True)
        retcode = _subprocess_call("mount -o remount \"" + destination + "\"", logger, shell=True)
        if retcode == 0:
            logger.debug(destination + ": remount OK")
        else:
            logger.error("USB remount failed retcode: " + str(retcode))
            return
    except OSError as e:
        logger.error("mount execution failed: " + str(e))
        return

def _usbmount():
    """Returns the mountpoint of device labelled rht_label"""
    logger = logging.getLogger('vm-usb')
    devl = "/dev/disk/by-label/" + rht_label
    try:
        dev = os.path.normpath(os.path.join(os.path.dirname(devl), os.readlink(devl)))
    except:
        logger.error("USB device (RHTINST) not currently plugged in")
        return
    # If this is a "virtual disk", find its mapper name
    if "/dev/dm-" in dev:
        try:
            devloop = subprocess.check_output(['dmsetup', '-c', '--noheadings', '-o', 'name', 'info', dev]).decode()
        except:
            logger.error("Unable to trace device mapper of " + dev)
            return
        dev = "/dev/mapper/" + devloop.rstrip()
    try:
        line = subprocess.check_output(['grep', dev, '/etc/mtab']).decode()
        parts = line.split(' ')
        target = parts[1]
        mfdir = os.path.join(target, "manifests")
        _createdir(mfdir)
        mfdir = os.path.join(target, "instructor")
        _createdir(mfdir)
        #_remountusb(dev)
        return target
    except:
        target = _mountusb(dev)
    try:
        line = subprocess.check_output(['grep', dev, '/etc/mtab']).decode()
        parts = line.split(' ')
        return parts[1]
    except:
        logger.error("USB device (RHTINST) not currently mounted")

def _usbumount():
    """Function to umount of device labelled rht_label"""
    logger = logging.getLogger('vm-usb')
    devl = "/dev/disk/by-label/" + rht_label
    try:
        dev = os.path.normpath(os.path.join(os.path.dirname(devl), os.readlink(devl)))
    except:
        # print "Device not currently plugged in"
        return
    # If this is a "virtual disk", find its mapper name
    if "/dev/dm-" in dev:
        try:
            devloop = subprocess.check_output(['dmsetup', '-c', '--noheadings', '-o', 'name', 'info', dev]).decode()
        except:
            logger.error("Unable to trace device mapper of " + dev)
            return
        dev = "/dev/mapper/" + devloop.rstrip()
    try:
        line = subprocess.check_output(['grep', dev, '/etc/mtab']).decode()
        parts = line.split(' ')
    except:
        # print "Device not currently mounted"
        return
    try:
        line = subprocess.check_output(['grep', 'RHT_ENROLLMENT', '/proc/cmdline']).decode()
        # print "Not unmounting from Kickstart"
        return
    except:
        logger.info("Looking to unmount USB device " + dev)
    target = parts[1]
    logger.debug("Looking to sync data")
    try:
        line = subprocess.check_output(['sync']).decode()
    except:
        logger.debug("sync appears to have had a problem")
    _umount(dev)
    if os.path.isdir(target):
        try:
            os.rmdir(target)
            logger.debug(target + ": rmdir OK")
        except OSError as e:
            logger.error("Directory removal failed of " + target)
            logger.error("os.rmdir execution failed: " + str(e))

def _usbpartitions(destination=None):
    """Function to display partitions on passed device name or
       device mounted to rht_usbmount"""
    logger = logging.getLogger('vm-usb')
    global rht_usbparts
    global rht_usbmount
    # Do I need this to work before the device is usbformat'd?
    # Can we receive an "optional argument" of disk name?
    # If disk name passed, operate on that
    # If disk name not passed, "find" RHTINST and work backwards
    # "Find" RHTINST can use rht_usbmount or /dev/disk/by-label
    # Maybe return a dict?
    # Want to return "Whole disk name"
    # Want to return "partStyle": msdos, gptefi, gpthybrid
    # Want to return "RHTINST partname" (all)
    # Want to return "EFI System partname" (gptefi, gpthybrid)
    # Want to return "BIOS Boot partname" (gpthybrid)
    # Set flag depending on parted version
    try:
        # Test version
        partedversion = subprocess.check_output("parted -v | grep -o '[0-9]\\.[0-9]'", shell=True).decode().replace("\n","")
    except OSError as e:
        logger.error("parted version check failes: " + str(e))
        rht_rc = 6
        return
    partedfix = "-f"
    if float(partedversion) < 3.4:
        partedfix = ""
    # Initialize return variable rht_usbparts
    rht_usbparts = {'diskName': '', 'partStyle': '', 'partRHTINST': '', 'partESP': '', 'partBoot': ''}
    if destination == None:
        # Search for disk
        devl = "/dev/disk/by-label/" + rht_label
        try:
            devp = os.path.normpath(os.path.join(os.path.dirname(devl), os.readlink(devl)))
        except:
            # print "Device not currently plugged in nor specified"
            return
        dev = re.sub("\\d+$", "", devp)
        dev = re.sub("p$", "", dev)
        devn = devp.lstrip(dev)
    else:
        dev = destination
    logger.info("_usbpartitions Parent device is: " + dev)
    # FIXME Validate dev
    # Assign dev to return variable
    rht_usbparts['diskName'] = dev
    # Read in partition table type
    devdsk = os.path.basename(dev)
    devparts = [os.path.basename(x) for x in sorted(glob.glob("/sys/block/" + devdsk + "/" + devdsk + "*"))]
    #print(devparts)
    partGPT = False
    try:
        partTable = re.findall('Partition Table:.*', subprocess.check_output("LANG=en_US.UTF-8 parted -s " + partedfix + " " + dev + " print", shell=True).decode())
        if any('msdos' in s for s in partTable):
            rht_usbparts['partStyle'] = 'msdos'
        elif any('gpt' in s for s in partTable):
            partGPT = True
            rht_usbparts['partStyle'] = 'gptUnknown'
        else:
            # Unknown partition type
            rht_usbparts['partStyle'] = 'unrecognized'
            return
    except:
        logger.error("Device not readable: " + dev)
        rht_rc = 6
        return
    # Look for two/three gpt partition names - complain if not mine
    partList = subprocess.check_output("LANG=en_US.UTF-8 parted -s " + partedfix + " " + dev + " print | grep '^ [0-9].*'", shell=True).decode().splitlines()
    partFail = False
    if not partGPT:
        # Validate msdos - single partition, type ext2
        if not 'ext' in partList[0]:
            # Generate error - set failure flag
            partFail = True
        if len(partList) != 1:
            # Generate error - set failure flag
            partFail = True
        # if no fail, set rht_usbparts['partRHTINST']
        if not partFail:
            rht_usbparts['partRHTINST'] = devparts[0]
    else:
        # Clarify gpt style:
        #  gpthybrid - look for "phrases" in correct order - set gpthybrid
        #  gptefi - look for "phrases" in correct order - set gptefi
        #  gptoldefi - look for "phrases" in old order - set gptoldefi
        goodorbad = True
        if len(partList) == 3:
            if 'BIOS Boot Partition' not in partList[0]:
                logger.error("gpt partition 1 not created by usbmkpart")
                goodorbad = False
            if 'EFI System Partition' not in partList[1]:
                logger.error("gpt partition 2 not created by usbmkpart")
                goodorbad = False
            if 'Linux RHTINST' not in partList[2]:
                logger.error("gpt partition 3 not created by usbmkpart")
                goodorbad = False
            if goodorbad:
                rht_usbparts['partStyle'] = 'gpthybrid'
                rht_usbparts['partRHTINST'] = devparts[2]
                rht_usbparts['partESP'] = devparts[1]
                rht_usbparts['partBoot'] = devparts[0]
        elif len(partList) == 2:
            # gptefi tests
            if 'EFI System Partition' in partList[0] and 'Linux RHTINST' in partList[1]:
                rht_usbparts['partStyle'] = 'gptefi'
                rht_usbparts['partRHTINST'] = devparts[1]
                rht_usbparts['partESP'] = devparts[0]
                rht_usbparts['partBoot'] = ''
            # gptoldefi tests
            elif 'EFI System Partition' in partList[1] and 'Linux RHTINST' in partList[0]:
                rht_usbparts['partStyle'] = 'gptoldefi'
                rht_usbparts['partRHTINST'] = devparts[0]
                rht_usbparts['partESP'] = devparts[1]
                rht_usbparts['partBoot'] = ''
                logger.info("Warning: using old gpt partitioning")
            else:
                logger.error("gpt partitions 1 or 2 not created by usbmkpart")
                goodorbad = False
        if not goodorbad:
            partFail = True
    # FIXME doublecheck /dev/disk/by-label matches
    if partFail:
        logger.error("partitioning not matching usbmkpart")

def _usbspace():
    """Function to display space on device mounted to rht_usbmount"""
    logger = logging.getLogger('vm-usb')
    st = os.statvfs(rht_usbmount)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    return (total, used, free)

def _manifests(location):
    """List all the files in the repository ending in .icmf"""
    return [file for file in _natsort(os.listdir(location)) if
            file.lower().endswith('.icmf')]

def _manifestsactive(location):
    """List all the files in the repository ending in .icmf not RHCI"""
    return [file for file in _natsort(os.listdir(location)) if
            file.lower().endswith('.icmf') and
            not file.upper().startswith('RHCI')]

def _manifestsquiesced(location):
    """List all the files in the repository ending in .icmf_quiesced"""
    return [file for file in _natsort(os.listdir(location)) if
            file.lower().endswith('.icmf_quiesced')]

def _manifestsall(location):
    """List all the files in the repository ending in .icmf"""
    return [file for file in _natsort(os.listdir(location)) if
            file.lower().endswith('.icmf') or file.lower().endswith('.icmf_quiesced')]

def _artifacts(location):
    """List all the files in the repository not ending in .icmf"""
    return [file for file in _natsort(os.listdir(location)) if
            not file.lower().endswith('.icmf')]

def courseusb(course):
    """Copy course\'s manifest from USB to foundation0.

    Specify the course code of a manifest file found on the USB.
    """
    global rht_usbmount
    global rht_rc
    global error_summary
    error_summary = ''
    logger = logging.getLogger('vm-usb')
    rht_usbmount = _usbmount()
    if not rht_usbmount:
        return
    # Expand course to manifestfilename (first as typed, second as uppered)
    mfpart = course + "-*"
    candidates = [ f for f in _natsort(glob.glob(os.path.join(rht_usbmount, "manifests", mfpart))) if f.endswith('.icmf') ]
    if not candidates:
        mfpart = course.upper() + "-*"
        candidates = [ f for f in _natsort(glob.glob(os.path.join(rht_usbmount, "manifests", mfpart))) if f.endswith('.icmf') ]
    if not candidates:
        logger.error("Cannot find " + course + " manifest")
        rht_rc = 9
        return
    # Call copyusb(manifestfilename)
    copyusb(os.path.basename(candidates[-1]))
    # Output summary of errors that may need to be "corrected"
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("courseusb partially completed.")
    else:
        logger.info("courseusb completed.")

def copy(manifestFilename):
    """Copy manifest from cache to foundation0.

    Specify the manifest file found in the cache (use \"list\" to see
    what is available to copy from the cache).
    """
    global rht_rc
    global error_summary
    error_summary = ''
    logger = logging.getLogger('vm-usb')
    manifestFilename = os.path.basename(manifestFilename)
    _deploymanifest(manifestFilename, "Cache")
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("copy partially completed.")
    else:
        logger.info("copy completed.")

def copyusb(manifestUSBFilename):
    """Copy manifest from USB to foundation0.

    Specify the manifest file found on the USB (use \"usblist\" to see
    what is available to copy from the USB).
    """
    global rht_usbmount
    global rht_rc
    global error_summary
    error_summary = ''
    logger = logging.getLogger('vm-usb')
    manifestUSBFilename = os.path.basename(manifestUSBFilename)
    _deploymanifest(manifestUSBFilename, "USB")
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("copyusb partially completed.")
    else:
        logger.info("copyusb completed.")

def copyrsync(manifestRemoteFilename):
    """Copy manifest from rsync to foundation0.

    Specify the manifest file via rsync user@host:dir/manifest.
    """
    global rht_rc
    global error_summary
    error_summary = ''
    logger = logging.getLogger('vm-usb')
    manifestFilename = os.path.basename(manifestRemoteFilename)
    targetFilename = os.path.join("/tmp", manifestFilename)
    # Download to /tmp
    _rsync(manifestRemoteFilename, targetFilename)
    # Punt if file never arrived
    if os.path.isfile(targetFilename):
        _deploymanifest(manifestRemoteFilename, "Remote")
    else:
        logger.error("Manifest " + manifestRemoteFilename + " is unavailable.")
        rht_rc = 7
        return False
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("copyrsync partially completed.")
    else:
        logger.info("copyrsync completed.")

def copyusbinstructor():
    """Copy instructor/ from USB to foundation0.

    If it exists, copy the instructor/ directory tree found on the USB
    to the /home/kiosk/ directory on foundation0.
    """
    global rht_usbmount
    global rht_rc
    global error_summary
    error_summary = ''
    logger = logging.getLogger('vm-usb')
    rht_usbmount = _usbmount()
    if not rht_usbmount:
        return
    insdst = "/home/kiosk"
    if not os.path.isdir(insdst):
        # Missing kiosk home directory
        logger.error(insdst + " is missing from system - is this foundation0?")
        rht_rc = 3
        return
    inssrc = os.path.join(rht_usbmount, "instructor")
    if not os.path.isdir(inssrc):
        # Missing instructor directory
        logger.error(rht_usbmount + " does not have instructor directory")
        rht_rc = 3
        return
    logger.info("Deploying instructor/ from USB mounted at: " + rht_usbmount)
    _rsync(inssrc, insdst)
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("copyusbinstructor partially completed.")
    else:
        logger.info("copyusbinstructor completed.")

def rsyncput(manifestFilename, remoteTarget):
    """Copy manifest from cache to remote rsync user@host:dir.

    vm-usb> rsyncput icmffilename user@host:dir/

    Specify the manifest file found in the cache (use \"list\" to see
    what is available to copy from the cache).

    Requires remote host directory exists.
    """
    global rht_rc
    global error_summary
    error_summary = ''
    logger = logging.getLogger('vm-usb')
    manifestFilename = os.path.basename(manifestFilename)
    rht_cachedir = config['repository']
    mfsource = os.path.join(rht_cachedir, manifestFilename)
    logger.info("Uploading from Cache Manifest: " + manifestFilename)
    try:
        data = _read_manifest(mfsource)
    except _ManifestValidationException as mfe:
        logger.error("Manifest " + mfsource + " is invalid.")
        logger.error(str(mfe))
        rht_rc = 7
        return False
    # Copy the manifest file itself
    _remotesync(mfsource, remoteTarget)
    # Copy the artifacts
    for artifact in data['curriculum']['artifacts']:
        source = os.path.join(rht_cachedir, artifact['filename'])
        _remotesync(source, remoteTarget)
    logger.info("Appears to have copied manifest from cache to " + remoteTarget)
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("rsyncput partially completed.")
    else:
        logger.info("rsyncput completed.")

def rsyncget(remoteFilename, remoteSource):
    """Copy manifest from remote rsync user@host:dir to local cache.

    vm-usb> rsyncget icmffilename user@host:dir/

    Specify the manifest file found in the remote host (use appropriate
    tooling to obtain the name).
    """
    global rht_rc
    global error_summary
    error_summary = ''
    logger = logging.getLogger('vm-usb')
    rht_cachedir = config['repository']
    logger.info("Downloading from: " + remoteSource + "/" + remoteFilename)
    # Copy the manifest file itself
    source = remoteSource + "/" + remoteFilename
    _remotesync(source, rht_cachedir)
    mfsource = os.path.join(rht_cachedir, remoteFilename)
    try:
        data = _read_manifest(mfsource)
    except _ManifestValidationException as mfe:
        logger.error("Manifest " + mfsource + " is invalid.")
        logger.error(str(mfe))
        rht_rc = 7
        return False
    # Copy the artifacts
    for artifact in data['curriculum']['artifacts']:
        source = remoteSource + "/" + artifact['filename']
        _remotesync(source, rht_cachedir)
    logger.info("Appears to have copied manifest from " + remoteSource)
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("rsyncget partially completed.")
    else:
        logger.info("rsyncget completed.")

def rcloneput(manifestFilename, remoteTarget):
    """Copy manifest from cache to remote rclone target provider:bucket/dir.

    vm-usb> rcloneput icmffilename provider:bucket/dir/

    Specify the manifest file found in the cache (use \"list\" to see
    what is available to copy from the cache).

    Requires remote provider bucket exists.
    """
    global rht_rc
    global error_summary
    error_summary = ''
    logger = logging.getLogger('vm-usb')
    manifestFilename = os.path.basename(manifestFilename)
    rht_cachedir = config['repository']
    mfsource = os.path.join(rht_cachedir, manifestFilename)
    logger.info("Uploading from Cache Manifest: " + manifestFilename)
    try:
        data = _read_manifest(mfsource)
    except _ManifestValidationException as mfe:
        logger.error("Manifest " + mfsource + " is invalid.")
        logger.error(str(mfe))
        rht_rc = 7
        return False
    # Copy the manifest file itself
    _rclonesync(mfsource, remoteTarget)
    # Copy the artifacts
    for artifact in data['curriculum']['artifacts']:
        source = os.path.join(rht_cachedir, artifact['filename'])
        _rclonesync(source, remoteTarget)
    logger.info("Appears to have copied manifest from cache to " + remoteTarget)
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("rcloneput partially completed.")
    else:
        logger.info("rcloneput completed.")

def rcloneget(remoteFilename, remoteSource):
    """Copy manifest from remote rclone provider:bucket/dir to local cache.

    vm-usb> rcloneget icmffilename provider:bucket/dir

    Specify the manifest file found in the remote host (use appropriate
    tooling to obtain the name).
    """
    global rht_rc
    global error_summary
    error_summary = ''
    logger = logging.getLogger('vm-usb')
    rht_cachedir = config['repository']
    logger.info("Downloading from: " + remoteSource + "/" + remoteFilename)
    # Copy the manifest file itself
    source = remoteSource + "/" + remoteFilename
    _rclonesync(source, rht_cachedir)
    mfsource = os.path.join(rht_cachedir, remoteFilename)
    try:
        data = _read_manifest(mfsource)
    except _ManifestValidationException as mfe:
        logger.error("Manifest " + mfsource + " is invalid.")
        logger.error(str(mfe))
        rht_rc = 7
        return False
    # Copy the artifacts
    for artifact in data['curriculum']['artifacts']:
        source = remoteSource + "/" + artifact['filename']
        _rclonesync(source, rht_cachedir)
    logger.info("Appears to have copied manifest from " + remoteSource)
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("rcloneget partially completed.")
    else:
        logger.info("rcloneget completed.")

def cachef0(manifestF0icmfs):
    """Recreate cache on foundation0 from foundation0.

    Specify the manifest file found on foundation0 (use \"f0list\" to see
    what is available to copy from foundation0).
    """
    global rht_rc
    global error_summary
    error_summary = ''
    manifestF0icmfs = os.path.basename(manifestF0icmfs)
    logger = logging.getLogger('vm-usb')
    mfl = os.path.join(rht_kioskdir, "manifests")
    if not os.path.isdir(mfl):
        # Missing manifests directory
        logger.error(rht_kioskdir + " does not have manifests directory")
        rht_rc = 3
        return
    rht_cachedir = config['repository']
    mfsource = os.path.join(mfl, manifestF0icmfs)
    logger.info("Copying from f0: " + manifestF0icmfs)
    try:
        data = _read_manifest(mfsource)
    except _ManifestValidationException as mfe:
        logger.error("Manifest " + mfsource + " is invalid.")
        logger.error(str(mfe))
        rht_rc = 7
        return False
    # Copy the manifest file itself
    target = os.path.join(rht_cachedir, manifestF0icmfs)
    if target.endswith("_quiesced"):
        target = target[:-len("_quiesced")]
    _rsync(mfsource, target)
    # Copy the artifacts
    for artifact in data['curriculum']['artifacts']:
        if artifact['type'].startswith('content'):
            if 'final name' in artifact and not 'iso' in artifact['content type']:
                source = os.path.join(rht_kioskdir, artifact['final name'])
            else:
                source = os.path.join(rht_kioskdir, artifact['target directory'], artifact['filename'])
            destination = os.path.join(rht_cachedir, artifact['filename'])
            _rsync(source, destination)
    logger.info("Appears to have copied manifest from f0 to cache.")
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("cachef0 partially completed.")
    else:
        logger.info("cachef0 completed.")

def cacheusb(manifestUSBFilename):
    """Recreate cache on foundation0 from USB.

    Specify the manifest file found on the USB (use \"usblist\" to see
    what is available to copy from the USB).
    """
    global rht_usbmount
    global rht_rc
    global error_summary
    error_summary = ''
    manifestUSBFilename = os.path.basename(manifestUSBFilename)
    logger = logging.getLogger('vm-usb')
    rht_usbmount = _usbmount()
    if not rht_usbmount:
        return
    rht_cachedir = config['repository']
    mfsource = os.path.join(rht_usbmount, "manifests", manifestUSBFilename)
    logger.info("Copying from USB Manifest: " + manifestUSBFilename)
    try:
        data = _read_manifest(mfsource)
    except _ManifestValidationException as mfe:
        logger.error("Manifest " + mfsource + " is invalid.")
        logger.error(str(mfe))
        rht_rc = 7
        return False
    # Copy the manifest file itself
    target = os.path.join(rht_usbmount, "manifests", manifestUSBFilename)
    _rsync(mfsource, rht_cachedir)
    # Copy the artifacts
    for artifact in data['curriculum']['artifacts']:
        if artifact['type'].startswith('content'):
            source = os.path.join(rht_usbmount, artifact['target directory'], artifact['filename'])
            destination = os.path.join(rht_cachedir, artifact['filename'])
            _rsync(source, destination)
    logger.info("Appears to have copied manifest from f0 to cache.")
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("cacheusb partially completed.")
    else:
        logger.info("cacheusb completed.")

def f0remove(manifestF0icmfs):
    """Remove manifest from foundation0.

    Specify the manifest file found on foundation0 (use \"f0list\" to see
    what is available to remove from foundation0).
    """
    global rht_rc
    global error_summary
    error_summary = ''
    manifestF0icmfs = os.path.basename(manifestF0icmfs)
    logger = logging.getLogger('vm-usb')
    mfl = os.path.join(rht_kioskdir, "manifests")
    if not os.path.isdir(mfl):
        # Missing manifests directory
        logger.error(rht_kioskdir + " does not have manifests directory")
        rht_rc = 3
        return
    mfsource = os.path.join(mfl, manifestF0icmfs)
    manifests_other = [kiosk for kiosk in _manifestsall(mfl) if kiosk != manifestF0icmfs]
    logger.info("Removing from f0: " + manifestF0icmfs)
    logger.debug("Removing from f0: " + mfsource)
    try:
        data_x = _read_manifest(mfsource)
    except _ManifestValidationException as mfe:
        logger.error("Manifest " + mfsource + " is invalid.")
        logger.error(str(mfe))
        rht_rc = 7
        return False
    rht_course = data_x['curriculum']['name']
    # Loop through list of artifacts
    for a in data_x['curriculum']['artifacts']:
        if a['type'].startswith('content'):
            a_others = []
            if manifests_other:
                for w in manifests_other:
                    try:
                        data_w = _read_manifest(os.path.join(mfl, w))
                    except _ManifestValidationException as mfe:
                        logger.error("Manifest " + w + " is invalid.")
                        logger.error(str(mfe))
                        rht_rc = 7
                        return False
                    for f in data_w['curriculum']['artifacts']:
                        if f['filename'] == a['filename']:
                            a_others.append(f)
            _removeartifact(a, a_others)
    # Remove manifest files
    logger.info("Deleting manifest " + manifestF0icmfs)
    _delete(mfsource)
    # Output summary of manual steps that may need to be "corrected"
    if error_summary:
        error_summary = "List of manual tasks still to be done:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("f0remove partially completed.")
    else:
        logger.info("f0remove completed.")

#def f0disable(manifestF0Filename):
#    """Disable/Deactivate manifest on foundation0.
#
#    Specify the manifest file found on foundation0 (use \"f0list\" to see
#    what is available to disable from foundation0).
#    """
#    global error_summary
#    manifestF0Filename = os.path.basename(manifestF0Filename)
#    logger = logging.getLogger('vm-usb')
#    mfl = os.path.join(rht_kioskdir, "manifests")
#    if not os.path.isdir(mfl):
#        # Missing manifests directory
#        logger.error(rht_kioskdir + " does not have manifests directory")
#        return
#    mfsource = os.path.join(mfl, manifestF0Filename)
#    # This should only be testing enabled manifests
#    manifests_other = [kiosk for kiosk in os.listdir(mfl) if kiosk != manifestF0Filename]
#    error_summary = ''
#    logger.info("Disabling on f0: " + manifestF0Filename)
#    logger.debug("Disabling on f0: " + mfsource)
#    try:
#        data_x = _read_manifest(mfsource)
#    except _ManifestValidationException as mfe:
#        logger.error("Manifest " + mfsource + " is invalid.")
#        logger.error(str(mfe))
#        return False
#    rht_course = data_x['curriculum']['name']
#    # Loop through list of artifacts
#    for a in data_x['curriculum']['artifacts']:
#        if a['type'].startswith('content'):
#            a_others = []
#            if manifests_other:
#                for w in manifests_other:
#                    try:
#                        data_w = _read_manifest(os.path.join(mfl, w))
#                    except _ManifestValidationException as mfe:
#                        logger.error("Manifest " + w + " is invalid.")
#                        logger.error(str(mfe))
#                        return False
#                    for f in data_w['curriculum']['artifacts']:
#                        if f['filename'] == a['filename']:
#                            a_others.append(f)
#            _disableartifact(a, a_others)
#    # Rename manifest file
#    logger.info("Renaming manifest " + manifestF0Filename)
#    mfdest = mfsource + "_quiesced"
#    _rename(mfsource, mfdest)
#    # Output summary of manual steps that may need to be "corrected"
#    if error_summary:
#        error_summary = "List of manual tasks still to be done:" + error_summary
#        logger.error(error_summary)
#        logger.debug(error_summary)
#        logger.error("f0disable partially completed.")
#    else:
#        logger.info("f0disable completed.")

def f0activate(manifestF0quiesced):
    """Enable/Activate manifest on foundation0.

    Specify the quiesced manifest file found on foundation0 (use
    \"f0list\" to see what is available to enable from foundation0).
    By nature this will quiesce the current active course manifest.
    """
    global rht_rc
    global error_summary
    error_summary = ''
    manifestF0quiesced = os.path.basename(manifestF0quiesced)
    logger = logging.getLogger('vm-usb')
    mfl = os.path.join(rht_kioskdir, "manifests")
    if not os.path.isdir(mfl):
        # Missing manifests directory
        logger.error(rht_kioskdir + " does not have manifests directory")
        rht_rc = 3
        return
    # Validate that manifestF0quiesced is valid
    if not manifestF0quiesced in _manifestsquiesced(mfl):
        logger.error(manifestF0quiesced + " not a quiesced manifest")
        return
    manifestsF0active = _manifestsactive(mfl)
    manifests_other = _manifests(mfl)
    logger.info("Enabling on f0: " + manifestF0quiesced)
    if manifestsF0active:
        for manifestF0active in manifestsF0active:
            logger.info("Quiescing on f0: " + manifestF0active)
            if manifestF0active in manifests_other:
                manifests_other.remove(manifestF0active)
    for a in manifests_other:
        logger.info("Keeping: " + a)
    manifests_other.append(manifestF0quiesced)
    # Loop through manifestF0active, to quiesce....
    if manifestsF0active:
        for manifestF0active in manifestsF0active:
            logger.info("Quiescing on f0: " + manifestF0active)
            mfsource = os.path.join(mfl, manifestF0active)
            try:
                data_x = _read_manifest(mfsource)
            except _ManifestValidationException as mfe:
                logger.error("Manifest " + mfsource + " is invalid.")
                logger.error(str(mfe))
                rht_rc = 7
                return False
            # Loop through list of artifacts
            for a in data_x['curriculum']['artifacts']:
                if a['type'].startswith('content'):
                    # compare to manifests_other plus manifestF0quiesced
                    # if unique, disable
                    a_others = _dupeartifact(a, manifests_other, mfl)
                    _disableartifact(a, a_others)
            # Rename manifestF0active to _quiesced
            mfdest = mfsource + "_quiesced"
            _rename(mfsource, mfdest)
    # Loop through manifestF0quiesced
    # for each artifact, compare to manifests_other
    if manifestF0quiesced in manifests_other:
        manifests_other.remove(manifestF0quiesced)
    logger.info("Activating on f0: " + manifestF0quiesced)
    mfsource = os.path.join(mfl, manifestF0quiesced)
    try:
        data_x = _read_manifest(mfsource)
    except _ManifestValidationException as mfe:
        logger.error("Manifest " + mfsource + " is invalid.")
        logger.error(str(mfe))
        rht_rc = 7
        return False
    # Loop through list of artifacts
    for a in data_x['curriculum']['artifacts']:
        if a['type'].startswith('content'):
            # compare to manifests_other
            # if unique, enable
            a_others = _dupeartifact(a, manifests_other, mfl)
            _activateartifact(a, a_others)
    # Rename manifestF0active to no _quiesced
    logger.info("Renaming manifest " + manifestF0quiesced)
    mfdest = mfsource[:-len("_quiesced")]
    _rename(mfsource, mfdest)
    # Output summary of manual steps that may need to be "corrected"
    if error_summary:
        error_summary = "List of manual tasks still to be done:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("f0activate partially completed.")
    else:
        logger.info("f0activate completed.")

def usbsizeremove(manifestUSBFilename):
    """Display size test of remove manifest from USB.

    Specify the manifest file found on the USB (use \"usblist\" to see
    what is available to remove from the USB).
    """
    global rht_usbmount
    global rht_rc
    global error_summary
    error_summary = ''
    manifestUSBFilename = os.path.basename(manifestUSBFilename)
    logger = logging.getLogger('vm-usb')
    rht_usbmount = _usbmount()
    if not rht_usbmount:
        return
    mfl = os.path.join(rht_usbmount, "manifests")
    if not os.path.isdir(mfl):
        # Missing manifests directory
        logger.error(rht_usbmount + " does not have manifests directory")
        rht_rc = 4
        return
    mfsource = os.path.join(mfl, manifestUSBFilename)
    logger.info("Size test remove from USB: " + manifestUSBFilename)
    logger.debug("Size test remove from USB: " + mfsource)
    try:
        data_x = _read_manifest(mfsource)
    except _ManifestValidationException as mfe:
        logger.error("Manifest " + mfsource + " is invalid.")
        logger.error(str(mfe))
        rht_rc = 7
        return False
    rht_course = data_x['curriculum']['name']
    # Define list of files and sizes in manifest
    mfsize = dict()
    for f in data_x['curriculum']['artifacts']:
        if f['type'].startswith('content'):
            thefile = os.path.join(rht_usbmount, f['target directory'], f['filename'])
            if os.path.isfile(thefile):
                mfsize[thefile] = os.path.getsize(thefile)
            else:
                logger.error("Manifest " + manifestUSBFilename + " corrupt on USB")
                logger.error("Artifact " + f['filename'] + " missing on USB")
                logger.error("USB is corrupt, you should probably start over.")
    mfsize[mfsource] = os.path.getsize(mfsource)
    mfsize_totorig = sum(mfsize.values())
    manifests_other = [kiosk for kiosk in _manifestsall(mfl) if kiosk != manifestUSBFilename]
    if manifests_other:
        for w in manifests_other:
            try:
                data_w = _read_manifest(os.path.join(mfl, w))
            except _ManifestValidationException as mfe:
                logger.error("Manifest " + w + " is invalid.")
                logger.error(str(mfe))
                rht_rc = 7
                return False
            for f in data_w['curriculum']['artifacts']:
                if f['type'].startswith('content'):
                    thefile = os.path.join(rht_usbmount, f['target directory'], f['filename'])
                    if thefile in mfsize:
                        del mfsize[thefile]
    # Calculate and present the totals of space manipulation
    # Total size being removed
    mfsize_totgive = sum(mfsize.values())
    logger.info("Removing files giving back is " + _bytes2human(mfsize_totgive) + " out of " + _bytes2human(mfsize_totorig))
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("usbsizeremove partially completed.")
    else:
        logger.info("usbsizeremove completed.")

def usbremove(manifestUSBFilename):
    """Remove manifest from USB.

    Specify the manifest file found on the USB (use \"usblist\" to see
    what is available to remove from the USB).
    """
    global rht_usbmount
    global rht_rc
    global error_summary
    error_summary = ''
    manifestUSBFilename = os.path.basename(manifestUSBFilename)
    logger = logging.getLogger('vm-usb')
    rht_usbmount = _usbmount()
    if not rht_usbmount:
        return
    mfl = os.path.join(rht_usbmount, "manifests")
    if not os.path.isdir(mfl):
        # Missing manifests directory
        logger.error(rht_usbmount + " does not have manifests directory")
        rht_rc = 4
        return
    mfsource = os.path.join(mfl, manifestUSBFilename)
    logger.info("Removing from USB: " + manifestUSBFilename)
    logger.debug("Removing from USB: " + mfsource)
    try:
        data_x = _read_manifest(mfsource)
    except _ManifestValidationException as mfe:
        logger.error("Manifest " + mfsource + " is invalid.")
        logger.error(str(mfe))
        rht_rc = 7
        return False
    rht_course = data_x['curriculum']['name']
    # Define list of files and sizes in manifest
    mfsize = dict()
    for f in data_x['curriculum']['artifacts']:
        if f['type'].startswith('content'):
            thefile = os.path.join(rht_usbmount, f['target directory'], f['filename'])
            if os.path.isfile(thefile):
                mfsize[thefile] = os.path.getsize(thefile)
            else:
                logger.error("Manifest " + manifestUSBFilename + " corrupt on USB")
                logger.error("Artifact " + f['filename'] + " missing on USB")
                logger.error("USB is corrupt, you should probably start over.")
    mfsize[mfsource] = os.path.getsize(mfsource)
    mfsize_totorig = sum(mfsize.values())
    manifests_other = [kiosk for kiosk in _manifestsall(mfl) if kiosk != manifestUSBFilename]
    if manifests_other:
        for w in manifests_other:
            try:
                data_w = _read_manifest(os.path.join(mfl, w))
            except _ManifestValidationException as mfe:
                logger.error("Manifest " + w + " is invalid.")
                logger.error(str(mfe))
                rht_rc = 7
                return False
            for f in data_w['curriculum']['artifacts']:
                if f['type'].startswith('content'):
                    thefile = os.path.join(rht_usbmount, f['target directory'], f['filename'])
                    if thefile in mfsize:
                        del mfsize[thefile]
    # Calculate and present the totals of space manipulation
    # Total size being removed
    mfsize_totgive = sum(mfsize.values())
    logger.info("Removing files giving back is " + _bytes2human(mfsize_totgive) + " out of " + _bytes2human(mfsize_totorig))
    # Remove manifest files
    logger.info("Removing obsolete artifacts from " + manifestUSBFilename)
    logger.debug("List of artifacts being removed: " + str(mfsize))
    for artifact_x in data_x['curriculum']['artifacts']:
        if artifact_x['type'].startswith('content'):
            thefile = os.path.join(rht_usbmount, artifact_x['target directory'], artifact_x['filename'])
            if thefile in mfsize:
                logger.info("Deleting " + artifact_x['filename'])
                _delete(thefile)
                # Remove boot directory if appropriate
                if 'RHCIfoundation' in data_x['curriculum']['name'] and 'boot' in artifact_x['content type']:
                    bootdir = os.path.join(rht_usbmount, artifact_x['target directory'])
                    logger.info("Recursively removing " + bootdir)
                    try:
                        retcode = _subprocess_call("rm -rf " + bootdir, logger, shell=True)
                        if retcode == 0:
                            logger.debug(bootdir + ": remove OK")
                        else:
                            logger.error("Recursive removal of " + bootdir + ": retcode " + str(retcode))
                    except OSError as e:
                        logger.error("rm execution failed: " + str(e))
            else:
                logger.info("NOT deleting " + artifact_x['filename'])
    logger.info("Deleting manifest " + manifestUSBFilename)
    _delete(mfsource)
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("usbremove partially completed.")
        logger.error("NOT calling usbmkmenu.")
    else:
        logger.info("usbremove completed.")
        logger.info("Automatically calling usbmkmenu.")
        usbmkmenu()

def remove(manifestFilename):
    """Remove manifest from cache (and their unique artifacts).

    Specify the manifest file found in the cache (use \"list\" to see
    what is available to remove from the cache).

    Looks in the cache directory defined in $HOME/vm_repo_config.yml
    """
    global rht_rc
    global error_summary
    global alwaysyes
    error_summary = ''
    manifestFilename = os.path.basename(manifestFilename)
    logger = logging.getLogger('vm-usb')
    mfl = config['repository']
    logger.info("Removing from Cache Manifest: " + manifestFilename)
    logger.debug("Working from cache: " + mfl)
    if not os.path.isdir(mfl):
        logger.error(mfl + " as a cache, does not exist")
        rht_rc = 5
        return
    msg = "Confirm removal of manifest: " + manifestFilename
    confirm = True if alwaysyes or input("%s (y/N) " % msg).lower() == 'y' else False
    if not confirm:
        logger.warning("Removal aborted")
        return
    mfsource = os.path.join(mfl, manifestFilename)
    # Generate list of other manifest files in cache
    manifests_other = [kiosk for kiosk in _manifests(os.path.dirname(mfsource)) if kiosk != manifestFilename]
    # Remove manifest
    try:
        data = _read_manifest(mfsource)
    except _ManifestValidationException as mfe:
        logger.error("Manifest " + mfsource + " is invalid.")
        logger.error(str(mfe))
        rht_rc = 7
        return False
    for artifact in data['curriculum']['artifacts']:
        destination = os.path.join(mfl, artifact['filename'])
        # Verify that file is not in use in another manifest
        remove = True
        for x in manifests_other:
            try:
                data_x = _read_manifest(os.path.join(mfl, x))
            except _ManifestValidationException as mfe:
                logger.error("Manifest " + x + " is invalid.")
                logger.error(str(mfe))
                rht_rc = 7
                return False
            for artifact_x in data_x['curriculum']['artifacts']:
                if artifact['filename'] == artifact_x['filename']:
                    remove = False
        # Remove if singular
        if remove == True:
            _delete(destination)
        else:
            logger.debug("NOT removing " + destination)
    # Remove manifest
    _delete(mfsource)
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("remove partially completed.")
    else:
        logger.info("remove completed.")

def removeloop(manifestPartname):
    """Loop through manifests whose names start with and delete.

    Specify the beginning part of the manifest filename (no wildards)
    found in the cache (use \"list\" to see what is available to remove
    from the cache).

    Looks in the cache directory defined in $HOME/vm_repo_config.yml
    """
    global rht_rc
    global error_summary
    error_summary = ''
    manifestPartname = os.path.basename(manifestPartname)
    logger = logging.getLogger('vm-usb')
    mfl = config['repository']
    logger.info("Loop removing from cache manifest: " + manifestPartname + "*")
    logger.debug("Working from cache: " + mfl)
    if not os.path.isdir(mfl):
        logger.error(mfl + " as a cache, does not exist")
        rht_rc = 5
        return
    manifests_list = [kiosk for kiosk in _manifests(mfl) if kiosk.startswith(manifestPartname)]
    if manifests_list:
        for removeicmf in manifests_list:
            remove(removeicmf)
        logger.info("Loop removing completed of: " + manifestPartname + "*")
    else:
        logger.info("None found in loop removing: " + manifestPartname + "*")

def rmobsoletes():
    """Remove obsolete artifacts from cache.
    (those that are unreferenced which can be listed with \"lsartifacts\")

    Looks in the cache directory defined in $HOME/vm_repo_config.yml
    """
    global rht_rc
    global error_summary
    global alwaysyes
    error_summary = ''
    logger = logging.getLogger('vm-usb')
    mfl = config['repository']
    logger.info("Removing Obsolete Artifacts from Cache")
    logger.debug("Working from cache: " + mfl)
    if not os.path.isdir(mfl):
        logger.error(mfl + " as a cache, does not exist")
        rht_rc = 5
        return
    orphans = _artifacts(mfl)
    for mfn in _manifests(mfl):
        try:
            mf = _read_manifest(os.path.join(mfl,mfn))
        except _ManifestValidationException as mfe:
            logger.error("Manifest " + mfn + " is invalid.")
            logger.error(str(mfe))
            rht_rc = 7
            return False
        for f in mf['curriculum']['artifacts']:
            try:
                orphans.remove(f['filename'])
            except ValueError as e:
                pass
    removed = 0
    for orphan in orphans:
        destination = os.path.join(mfl, orphan)
        msg = "Remove apparent orphan " + orphan
        if alwaysyes or input("%s (y/N) " % msg).lower() == 'y':
            _delete(destination)
            removed = removed+1
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("rmobsoletes partially completed.")
    else:
        logger.info("rmobsoletes completed.")
        logger.info("Removed " + str(removed) + " files.")

def usbsizeadd(manifestFilename):
    """Display size test of add (or replace) manifest to USB.

    Specify the manifest file found in the cache directory (use \"list\"
    to see what is available to add to the USB)
    """
    global rht_usbmount
    global rht_rc
    global error_summary
    error_summary = ''
    manifestFilename = os.path.basename(manifestFilename)
    logger = logging.getLogger('vm-usb')
    rht_usbmount = _usbmount()
    if not rht_usbmount:
        return
    rht_cachedir = config['repository']
    mfsource = os.path.join(rht_cachedir, manifestFilename)
    mfl = os.path.join(rht_usbmount, "manifests")
    if not os.path.isdir(mfl):
        # Missing manifests directory
        logger.error(rht_usbmount + " does not have manifests directory")
        rht_rc = 4
        return
    logger.info("Size test adding to USB: " + manifestFilename)
    logger.debug("Size test copying from Cache Manifest: " + mfsource)
    logger.debug("Size test copying to USB Mountpoint: " + rht_usbmount)
    try:
        data = _read_manifest(mfsource)
    except _ManifestValidationException as mfe:
        logger.error("Manifest " + mfsource + " is invalid.")
        logger.error(str(mfe))
        rht_rc = 7
        return False
    # Abort if generation < 7
    rht_generation = data['curriculum']['generation']
    if rht_generation < 7:
        logger.error("Manifest is the wrong generation " + str(rht_generation))
        logger.error("This version of vm-usb only supports generation 7+")
        logger.error("Check the course documentation for proper USB creation")
        logger.error("Warning: This requires a separate USB stick")
        return
    # Abort if modality != ILT
    rht_modality = data['curriculum']['modality']
    if "ILT" not in rht_modality:
        logger.error("Manifest is the wrong modality " + str(rht_modality))
        logger.error("This version of vm-usb only supports modality of ILT")
        logger.error("Check the course documentation for proper USB creation")
        logger.error("Warning: Other modalities are used straight from cache")
        return
    rht_course = data['curriculum']['name']
    rht_technology = data['curriculum']['technology']
    # Define list of files and sizes in new
    try:
        mfnewsize = dict([ (os.path.join(rht_usbmount, f['target directory'], f['filename']), os.path.getsize(os.path.join(rht_cachedir, f['filename']))) for f in data['curriculum']['artifacts'] if f['type'].startswith('content') ])
    except:
        logger.error("Content artifacts missing from manifest " + manifestFilename)
        logger.error("Use verify to locate and download missing artifacts")
        rht_rc = 7
        return
    mfnewsize[manifestFilename] = os.path.getsize(mfsource)
    mfnewsize_totorig = sum(mfnewsize.values())
    # Find replaceable manifests (RHCIfoundation-* or name-technology-*)
    if 'RHCIfoundation' in rht_course:
        rht_old = rht_course
    else:
        rht_old = rht_course + '-' + rht_technology
    oldmanifests = [manifest for manifest in _manifestsall(mfl) if manifest.startswith(rht_old)]
    # Define list of files and sizes in old
    if oldmanifests:
        oldmanifest = oldmanifests[0]
        logger.info("Comparing to existing manifest " + oldmanifest)
        # Remove from mfnewsize if a filename is in manifest
        mfold = os.path.join(mfl, oldmanifest)
        try:
            data_x = _read_manifest(mfold)
        except _ManifestValidationException as mfe:
            logger.error("Manifest " + mfold + " is invalid.")
            logger.error(str(mfe))
            rht_rc = 7
            return False
        # Define list of files and sizes
        mfoldsize = dict()
        for f in data_x['curriculum']['artifacts']:
            if f['type'].startswith('content'):
                thefile = os.path.join(rht_usbmount, f['target directory'], f['filename'])
                if os.path.isfile(thefile):
                    mfoldsize[thefile] = os.path.getsize(thefile)
                else:
                    logger.error("Manifest " + oldmanifest + " corrupt on USB")
                    logger.error("Artifact " + f['filename'] + " missing on USB")
                    logger.error("USB is corrupt, you should probably start over.")
        mfoldsize[mfold] = os.path.getsize(mfold)
        mfoldsize_totorig = sum(mfoldsize.values())
        # Remove files from both manifests
        common_f = dict([ (x, mfnewsize[x]) for x in mfnewsize if x in mfoldsize ])
        for f in common_f:
            del mfnewsize[f]
            del mfoldsize[f]
    # Search other manifests for artifacts already there
    if oldmanifests:
        manifests_other = [kiosk for kiosk in _manifestsall(mfl) if kiosk != oldmanifest]
    else:
        manifests_other = [kiosk for kiosk in _manifestsall(mfl)]
    if manifests_other:
        for w in manifests_other:
            try:
                data_w = _read_manifest(os.path.join(mfl, w))
            except _ManifestValidationException as mfe:
                logger.error("Manifest " + w + " is invalid.")
                logger.error(str(mfe))
                rht_rc = 7
                return False
            for f in data_w['curriculum']['artifacts']:
                if f['type'].startswith('content'):
                    thefile = os.path.join(rht_usbmount, f['target directory'], f['filename'])
                    if thefile in mfnewsize:
                        del mfnewsize[thefile]
                    if oldmanifests:
                        if thefile in mfoldsize:
                            del mfoldsize[thefile]
    # Calculate and present the totals of space manipulation
    # Total size of needed space
    mfnewsize_totneed = sum(mfnewsize.values())
    logger.info("New files needed space is " + _bytes2human(mfnewsize_totneed) + " out of " + _bytes2human(mfnewsize_totorig))
    # Total size being removed
    if oldmanifests:
        mfoldsize_totgive = sum(mfoldsize.values())
        logger.info("Old files giving back is " + _bytes2human(mfoldsize_totgive) + " out of " + _bytes2human(mfoldsize_totorig))
        usb_spaceneeded = mfnewsize_totneed - mfoldsize_totgive
    else:
        usb_spaceneeded = mfnewsize_totneed
    logger.info("Calculation finds we need: " + str(usb_spaceneeded) + " bytes (" + _bytes2human(usb_spaceneeded) + ")")
    # Total size available
    usb_total, usb_used, usb_free = _usbspace()
    logger.info("USB space Total: " + _bytes2human(usb_total) + "  Used: " + _bytes2human(usb_used) + "  Free: " + _bytes2human(usb_free))
    if usb_spaceneeded > usb_free:
        logger.error("Insufficient free space on " + rht_usbmount)
        return
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("usbsizeadd partially completed.")
    else:
        logger.info("usbsizeadd completed.")

def usbadd(manifestFilename):
    """Add (or replace) manifest to USB.

    Specify the manifest file found in the cache directory (use \"list\"
    to see what is available to add to the USB)
    """
    global rht_usbmount
    global rht_usbparts
    global rht_rc
    global error_summary
    error_summary = ''
    manifestFilename = os.path.basename(manifestFilename)
    logger = logging.getLogger('vm-usb')
    rht_usbmount = _usbmount()
    if not rht_usbmount:
        return
    rht_cachedir = config['repository']
    mfsource = os.path.join(rht_cachedir, manifestFilename)
    mfl = os.path.join(rht_usbmount, "manifests")
    if not os.path.isdir(mfl):
        # Missing manifests directory
        logger.error(rht_usbmount + " does not have manifests directory")
        rht_rc = 4
        return
    logger.info("Adding to USB: " + manifestFilename)
    logger.debug("Copying from Cache Manifest: " + mfsource)
    logger.debug("Copying to USB Mountpoint: " + rht_usbmount)
    try:
        data = _read_manifest(mfsource)
    except _ManifestValidationException as mfe:
        logger.error("Manifest " + mfsource + " is invalid.")
        logger.error(str(mfe))
        rht_rc = 7
        return False
    # Abort if generation < 7
    rht_generation = data['curriculum']['generation']
    if rht_generation < 7:
        logger.error("Manifest is the wrong generation " + str(rht_generation))
        logger.error("This version of vm-usb only supports generation 7+")
        logger.error("Check the course documentation for proper USB creation")
        logger.error("Warning: This requires a separate USB stick")
        return
    # Abort if modality != ILT
    rht_modality = data['curriculum']['modality']
    if "ILT" not in rht_modality:
        logger.error("Manifest is the wrong modality " + str(rht_modality))
        logger.error("This version of vm-usb only supports modality of ILT")
        logger.error("Check the course documentation for proper USB creation")
        logger.error("Warning: Other modalities are used straight from cache")
        return
    rht_course = data['curriculum']['name']
    # Abort if generation > 7 and course = RHCIfoundation and USB is not GPT
    if rht_course == 'RHCIfoundation' and rht_generation > 7:
        _usbpartitions()
        goodorbad = True
        # Complain if unrecognized partitioning
        if rht_usbparts['partStyle'] == 'unrecognized':
            logger.error("Device partitioning is unrecognized")
            goodorbad = False
        # Complain if msdos partitioning
        elif rht_usbparts['partStyle'] == 'msdos':
            logger.error("Device has msdos partitions")
            goodorbad = False
        # Complain if gptUnknown partitioning
        elif rht_usbparts['partStyle'] == 'gptUnknown':
            logger.error("GPT partitioning is unknown (not by usbmkpart)")
            goodorbad = False
        # Declare happiness with gpthybrid
        elif rht_usbparts['partStyle'] == 'gpthybrid':
            logger.info("Device has three gpthybrid partitions")
            logger.info("gpthybrid is deprecated - please repartition")
        elif rht_usbparts['partStyle'] == 'gptoldefi':
            logger.info("Device has two gptoldefi partitions")
            logger.info("gptoldefi is deprecated - please repartition")
        elif rht_usbparts['partStyle'] == 'gptefi':
            logger.info("Device has two gptefi partitions")
        if not goodorbad:
            logger.error("RHCIfoundation manifest is generation " + str(rht_generation))
            logger.error("This generation requires the USB to be GPT partitioned")
            logger.error("This generation does not support Legacy BIOS booting")
            logger.error("Check the course documentation for proper USB creation")
            rht_rc = 8
            return
    rht_technology = data['curriculum']['technology']
    # Define list of files and sizes in new
    try:
        mfnewsize = dict([ (os.path.join(rht_usbmount, f['target directory'], f['filename']), os.path.getsize(os.path.join(rht_cachedir, f['filename']))) for f in data['curriculum']['artifacts'] if f['type'].startswith('content') ])
    except:
        logger.error("Content artifacts missing from manifest " + manifestFilename)
        logger.error("Use verify to locate and download missing artifacts")
        rht_rc = 7
        return
    mfnewsize[manifestFilename] = os.path.getsize(mfsource)
    mfnewsize_totorig = sum(mfnewsize.values())
    # Find replaceable manifests (RHCIfoundation-* or name-technology-*)
    if 'RHCIfoundation' in rht_course:
        rht_old = rht_course
    else:
        rht_old = rht_course + '-' + rht_technology
    oldmanifests = [manifest for manifest in _manifestsall(mfl) if manifest.startswith(rht_old)]
    # Define list of files and sizes in old
    if oldmanifests:
        oldmanifest = oldmanifests[0]
        logger.info("Comparing to existing manifest " + oldmanifest)
        # Remove from mfnewsize if a filename is in manifest
        mfold = os.path.join(mfl, oldmanifest)
        try:
            data_x = _read_manifest(mfold)
        except _ManifestValidationException as mfe:
            logger.error("Manifest " + mfold + " is invalid.")
            logger.error(str(mfe))
            rht_rc = 7
            return False
        # Define list of files and sizes
        mfoldsize = dict()
        for f in data_x['curriculum']['artifacts']:
            if f['type'].startswith('content'):
                thefile = os.path.join(rht_usbmount, f['target directory'], f['filename'])
                if os.path.isfile(thefile):
                    mfoldsize[thefile] = os.path.getsize(thefile)
                else:
                    logger.error("Manifest " + oldmanifest + " corrupt on USB")
                    logger.error("Artifact " + f['filename'] + " missing on USB")
                    logger.error("USB is corrupt, you should probably start over.")
        mfoldsize[mfold] = os.path.getsize(mfold)
        mfoldsize_totorig = sum(mfoldsize.values())
        # Remove files from both manifests
        common_f = dict([ (x, mfnewsize[x]) for x in mfnewsize if x in mfoldsize ])
        for f in common_f:
            del mfnewsize[f]
            del mfoldsize[f]
    # Search other manifests for artifacts already there
    if oldmanifests:
        manifests_other = [kiosk for kiosk in _manifestsall(mfl) if kiosk != oldmanifest]
    else:
        manifests_other = [kiosk for kiosk in _manifestsall(mfl)]
    if manifests_other:
        for w in manifests_other:
            try:
                data_w = _read_manifest(os.path.join(mfl, w))
            except _ManifestValidationException as mfe:
                logger.error("Manifest " + w + " is invalid.")
                logger.error(str(mfe))
                rht_rc = 7
                return False
            for f in data_w['curriculum']['artifacts']:
                if f['type'].startswith('content'):
                    thefile = os.path.join(rht_usbmount, f['target directory'], f['filename'])
                    if thefile in mfnewsize:
                        del mfnewsize[thefile]
                    if oldmanifests:
                        if thefile in mfoldsize:
                            del mfoldsize[thefile]
    # Calculate and present the totals of space manipulation
    # Total size of needed space
    mfnewsize_totneed = sum(mfnewsize.values())
    logger.info("New files needed space is " + _bytes2human(mfnewsize_totneed) + " out of " + _bytes2human(mfnewsize_totorig))
    # Total size being removed
    if oldmanifests:
        mfoldsize_totgive = sum(mfoldsize.values())
        logger.info("Old files giving back is " + _bytes2human(mfoldsize_totgive) + " out of " + _bytes2human(mfoldsize_totorig))
        usb_spaceneeded = mfnewsize_totneed - mfoldsize_totgive
    else:
        usb_spaceneeded = mfnewsize_totneed
    logger.info("Calculation finds we need: " + str(usb_spaceneeded) + " bytes (" + _bytes2human(usb_spaceneeded) + ")")
    # Total size available
    usb_total, usb_used, usb_free = _usbspace()
    logger.info("USB space Total: " + _bytes2human(usb_total) + "  Used: " + _bytes2human(usb_used) + "  Free: " + _bytes2human(usb_free))
    if usb_spaceneeded > usb_free:
        logger.error("Insufficient free space on " + rht_usbmount)
        rht_rc = 6
        return
    # Remove old manifest files
    if oldmanifests:
        logger.info("Removing obsolete artifacts from " + oldmanifest)
        logger.debug("List of artifacts being removed: " + str(mfoldsize))
        logger.debug("List of artifacts to be added: " + str(mfnewsize))
        for artifact_x in data_x['curriculum']['artifacts']:
            # only content
            if artifact_x['type'].startswith('content'):
                thefile = os.path.join(rht_usbmount, artifact_x['target directory'], artifact_x['filename'])
                #FIXME: Somehow check both mfoldsize and mfnewsize
                if thefile in mfoldsize:
                    #if thefile not in mfnewsize:
                    logger.info("Deleting " + artifact_x['filename'])
                    _delete(thefile)
                    # Remove boot directory if appropriate
                    if 'RHCIfoundation' in data_x['curriculum']['name'] and 'boot' in artifact_x['content type']:
                        bootdir = os.path.join(rht_usbmount, artifact_x['target directory'])
                        logger.info("Recursively removing " + bootdir)
                        try:
                            retcode = _subprocess_call("rm -rf " + bootdir, logger, shell=True)
                            if retcode == 0:
                                logger.debug(bootdir + ": remove OK")
                            else:
                                logger.error("Recursive removal of " + bootdir + ": retcode " + str(retcode))
                        except OSError as e:
                            logger.error("rm execution failed: " + str(e))
                else:
                    logger.info("NOT deleting " + artifact_x['filename'])
        logger.info("Deleting manifest " + oldmanifest)
        _delete(mfold)
    # Copy the manifest
    logger.info("Copying manifest file: " + manifestFilename)
    destination = os.path.join(mfl, manifestFilename)
    _rsync(mfsource, destination)
    # Copy each of the artifacts (of type content)
    logger.info("Starting copy of " + manifestFilename)
    for artifact in data['curriculum']['artifacts']:
        if artifact['type'].startswith('content'):
            logger.info("Copying artifact: " + artifact['filename'])
            source = os.path.join(rht_cachedir, artifact['filename'])
            destination = os.path.join(rht_usbmount, artifact['target directory'], artifact['filename'])
            _rsync(source, destination)
            if 'RHCIfoundation' in rht_course:
                if 'final name' in artifact:
                    if artifact['final name'].endswith('dvd') and artifact['final name'].startswith('rhel6'):
                        # If the DVD (RHEL6 only), export the images tree
                        logger.info("Extracting RHEL6 DVD images: " + artifact['filename'])
                        tmppoint = tempfile.mkdtemp()
                        _mountdvd(os.path.join(rht_cachedir, artifact['filename']), tmppoint)
                        _rsync(os.path.join(tmppoint, 'images'), os.path.join(rht_usbmount, artifact['target directory']))
                        _umount(tmppoint)
                        if os.path.isdir(tmppoint):
                            try:
                                os.rmdir(tmppoint)
                                logger.debug(tmppoint + ": rmdir OK")
                            except OSError as e:
                                logger.error("Directory removal failed of " + tmppoint)
                                logger.error("os.rmdir execution failed: " + str(e))
                if 'boot' in artifact['content type']:
                    logger.info("Extracting boot files: " + artifact['filename'])
                    tmppoint = tempfile.mkdtemp()
                    tmppointslash = tmppoint + "/"
                    boottarget = os.path.join(rht_usbmount, artifact['target directory'])
                    _mountdvd(os.path.join(rht_cachedir, artifact['filename']), tmppoint)
                    _rsync(tmppointslash, boottarget)
                    _chmod(boottarget)
                    _umount(tmppoint)
                    if os.path.isdir(tmppoint):
                        try:
                            os.rmdir(tmppoint)
                            logger.debug(tmppoint + ": rmdir OK")
                        except OSError as e:
                            logger.error("Directory removal failed of " + tmppoint)
                            logger.error("os.rmdir execution failed: " + str(e))
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("usbadd partially completed.")
        if 'RHCIfoundation' in rht_course:
            logger.error("NOT calling usbmkboot.")
        else:
            logger.error("NOT calling usbmkmenu.")
    else:
        logger.info("usbadd completed.")
        if 'RHCIfoundation' in rht_course:
            logger.info("Automatically calling usbmkboot.")
            usbmkboot()
        else:
            logger.info("Automatically calling usbmkmenu.")
            usbmkmenu()

def usbdiff():
    """Compare existence of manifests in cache and USB device.

    == on both, <U on USB only, C> in cache only
    """
    global rht_usbmount
    global rht_rc
    global error_summary
    error_summary = ''
    logger = logging.getLogger('vm-usb')
    rht_usbmount = _usbmount()
    if not rht_usbmount:
        return
    mfl = os.path.join(rht_usbmount, "manifests")
    rht_cachedir = config['repository']
    logger.info("Comparing USB Mountpoint: " + rht_usbmount)
    logger.info("        with Local Cache: " + rht_cachedir)
    if not os.path.isdir(rht_cachedir):
        logger.error(rht_cachedir + " as a cache, does not exist.")
        rht_rc = 5
        return
    if not os.path.isdir(mfl):
        logger.warning("USB improperly formatted - missing " + mfl)
        rht_rc = 4
        return
    cachemanifests = _manifests(rht_cachedir)
    usbmanifests = _manifests(mfl)
    combinedmanifests = _natsort(set().union(cachemanifests, usbmanifests))
    for mfn in combinedmanifests:
        if mfn in cachemanifests:
            location = "C> "
            if mfn in usbmanifests:
                location = "== "
        else:
            if mfn in usbmanifests:
                location = "<U "
            else:
                location = "?? "
        logger.info(location + mfn)
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("usbdiff partially completed.")
    else:
        logger.info("usbdiff completed.")

def usbupdate():
    """Update the USB device with the latest manifests from cache.

    For each manifest on USB is there a later one in cache?
    If so, usbadd that manifest
    """
    global rht_usbmount
    global rht_rc
    global error_summary
    global alwaysyes
    error_summary = ''
    logger = logging.getLogger('vm-usb')
    rht_usbmount = _usbmount()
    if not rht_usbmount:
        return
    mfl = os.path.join(rht_usbmount, "manifests")
    rht_cachedir = config['repository']
    logger.info("Updating USB Mountpoint: " + rht_usbmount)
    logger.info("       from Local Cache: " + rht_cachedir)
    if not os.path.isdir(rht_cachedir):
        logger.error(rht_cachedir + " as a cache, does not exist.")
        rht_rc = 5
        return
    if not os.path.isdir(mfl):
        logger.warning("USB improperly formatted - missing " + mfl)
        rht_rc = 4
        return
    newermanifests = []
    for mfn in _manifests(mfl):
        try:
            mf = _read_manifest(os.path.join(mfl,mfn))
        except _ManifestValidationException as mfe:
            logger.error("Manifest " + mfn + " is invalid.")
            logger.error(str(mfe))
            rht_rc = 10
            return False
        rht_course = mf['curriculum']['name']
        rht_technology = mf['curriculum']['technology']
        rht_release = mf['curriculum']['technology']
        # Find replaceable manifests (name-technology-*)
        # Restrict to modality ILT and generation 7
        # rht_old = rht_course + '-' + rht_technology + '-.*-.*ILT.*-7-.*\\.icmf'
        # Restrict to modality ILT
        rht_old = rht_course + '-' + rht_technology + '-.*-.*ILT.*\\.icmf'
        newmanifests = [manifest for manifest in _manifests(rht_cachedir) if re.match(rht_old, manifest)]
        if newmanifests:
            newmanifest = newmanifests[-1]
            manifestsorted = _natsort([ newmanifest, mfn ])
            if newmanifest == mfn:
                logger.info("Already latest: " + mfn)
            elif newmanifest == manifestsorted[-1]:
                logger.info("USB is older  : " + mfn)
                logger.info("     cache has: " + newmanifest)
                newermanifests.append(newmanifest)
            else:
                logger.info("USB is newer  : " + mfn)
                logger.info("     cache has: " + newmanifest)
        else:
            logger.info("Not in cache  : " + mfn)
    if newermanifests:
        msg = "Confirm updating USB as above"
        confirm = True if alwaysyes or input("%s (y/N) " % msg).lower() == 'y' else False
        if not confirm:
            logger.warning("Update aborted")
            return
        # for each manifest in set, call usbadd
        for mfn in newermanifests:
            usbadd(mfn)
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("usbupdate partially completed.")
    else:
        logger.info("usbupdate completed.")

def usbvalidate():
    """Validates the USB device as usable for an install.

    Find and mount USB
    Is there an RHCIfoundation manifest
    Has the RHCIfoundation manifest extraction happened
    Loop check all manifests found on USB
    """
    global rht_already
    global rht_usbmount
    global rht_usbparts
    global rht_rc
    global error_summary
    error_summary = ''
    logger = logging.getLogger('vm-usb')
    rht_already = set()
    rht_usbmount = _usbmount()
    if not rht_usbmount:
        return
    logger.info("Validating USB Mountpoint: " + rht_usbmount)
    # Retrieve partitioning information
    _usbpartitions()
    goodorbad = True
    # Complain if unrecognized partitioning
    if rht_usbparts['partStyle'] == 'unrecognized':
        logger.error("Device partitioning is unrecognized")
        goodorbad = False
    # Confirm that msdos partitioning appears to be mine
    elif rht_usbparts['partStyle'] == 'msdos':
        if len(glob.glob(rht_usbparts['diskName'] + '*')) == 2:
            logger.info("Device has one msdos partition")
        else:
            logger.error("Device has additional msdos partitions")
            goodorbad = False
    # Complain if gptUnknown partitioning
    elif rht_usbparts['partStyle'] == 'gptUnknown':
        logger.error("GPT partitioning is unknown (not by usbmkpart)")
        goodorbad = False
    # Declare happiness with gpthybrid
    elif rht_usbparts['partStyle'] == 'gpthybrid':
        logger.info("Device has three gpthybrid partitions")
        logger.info("gpthybrid is deprecated - please repartition")
    elif rht_usbparts['partStyle'] == 'gptoldefi':
        logger.info("Device has two gptoldefi partitions")
        logger.info("gptoldefi is deprecated - please repartition")
    elif rht_usbparts['partStyle'] == 'gptefi':
        logger.info("Device has two gptefi partitions")
    mfl = os.path.join(rht_usbmount, "manifests")
    if not os.path.isdir(mfl):
        # Missing manifests directory
        logger.error(rht_usbmount + " does not have any manifests")
        goodorbad = False
    else:
        # Check for RHCIfoundation manifest
        candidates = [ f for f in os.listdir(mfl) if f.startswith("RHCIfoundation-")]
        if not candidates:
            logger.error(rht_usbmount + " missing RHCIfoundation manifest")
            goodorbad = False
        else:
            logger.info("Does have a required RHCIfoundation manifest")
            # Need to check for /boot...ks/ files
            for mf in candidates:
                mfabs = os.path.join(mfl, mf)
                try:
                    data = _read_manifest(mfabs)
                except _ManifestValidationException as mfe:
                    logger.error("Manifest " + mfabs + " is invalid.")
                    logger.error(str(mfe))
                    return False
                for artifact in data['curriculum']['artifacts']:
                    if artifact['type'].startswith('content'):
                        if 'boot' in artifact['content type']:
                            target = os.path.join(rht_usbmount, artifact['target directory'], "ks")
                            if os.path.isdir(target):
                                logger.debug("Appears to have extracted directory")
                                target = os.path.join(rht_usbmount, artifact['target directory'], "extlinux/ldlinux.sys")
                                if os.path.isfile(target):
                                    logger.info("Appears to be bootable")
                                else:
                                    logger.info("Not configured to be bootable")
                            else:
                                logger.error("Missing extracted directory " + target)
                                logger.error("Retry usbadd RHCIfoundation manifest")
                                logger.error("Capture and report the output from usbadd if this continues")
                                goodorbad = False
                            # TEST: Check for number of RHEL isos
                            # Extract rhelver from artifact['filename']
                            installver = artifact['filename'].split('-')[2]
                            # Assume DIR is rhel<rhelver>/x86_64/isos/
                            installdir = 'rhel' + installver + '/x86_64/isos'
                            usbinstalldir = os.path.join(rht_usbmount, installdir)
                            # Count files in directory
                            installisos = [name for name in os.listdir(usbinstalldir) if os.path.isfile(os.path.join(usbinstalldir, name))]
                            # Error if -ne 1
                            if ( len(installisos) != 1 ):
                                logger.error("Appear to have multiple ISOs in " + installdir)
                                logger.error("Remove other manifests to reduce clutter")
                                logger.error("Perhaps you have both beta and GA manifests for RHEL?")
                                goodorbad = False
                            else:
                                logger.debug("Only one ISO in " + installdir)
            # Perform traditional check of manifests if passing so far
            if goodorbad:
                for mf in _manifests(mfl):
                    mfabs = os.path.join(mfl, mf)
                    if not _verify(mfabs, 1, 0):
                        goodorbad = False
    print()
    if goodorbad:
        logger.info("USBValidate SUCCEEDED")
    else:
        logger.warning("USBValidate FAILED - look above for ERROR")
        logger.warning("Summary of failures:")
        logger.warning(error_summary)
        rht_rc = 10

def f0validate():
    """Verify checksums of artifacts of all deployed manifests.

    Loop checks all manifests found in /content/manifests
    """
    global rht_already
    global rht_rc
    global error_summary
    error_summary = ""
    logger = logging.getLogger('vm-usb')
    rht_already = set()
    mfl = os.path.join(rht_kioskdir,"manifests")
    logger.info("Validating Manifests in " + mfl)
    goodorbad = True
    if not os.path.isdir(mfl):
        # Missing manifests directory
        logger.error(rht_kioskdir + " does not have any manifests")
        goodorbad = False
    else:
        # Perform traditional check of manifests
        for mf in _manifests(mfl):
            mfabs = os.path.join(mfl, mf)
            if not _verify(mfabs, 2, 0):
                goodorbad = False
        for mf in _manifestsquiesced(mfl):
            mfabs = os.path.join(mfl, mf)
            if not _verify(mfabs, 3, 0):
                goodorbad = False
    print()
    if goodorbad:
        logger.info("f0validate SUCCEEDED")
    else:
        logger.warning("f0validate FAILED - look above for ERROR")
        logger.warning("Summary of failures:")
        logger.warning(error_summary)
        rht_rc = 10

def f0vmsmd5sum():
    """Create new .md5sums file of active manifests.

    Loop checks all manifests found in /content/manifests
    """
    global rht_already
    global rht_rc
    global error_summary
    error_summary = ""
    logger = logging.getLogger('vm-usb')
    rht_already = set()
    mfl = os.path.join(rht_kioskdir,"manifests")
    logger.info("Generating md5sums for active manifests in " + mfl)
    goodorbad = True
    if not os.path.isdir(mfl):
        # Missing manifests directory
        logger.error(rht_kioskdir + " does not have any manifests")
        goodorbad = False
    else:
        # Remove existing .md5sum files in mfl
        logger.info("Removing existing md5sum files from " + mfl)
        try:
            retcode = _subprocess_call("rm -f " + mfl + "/*.md5sum", logger, shell=True)
            if retcode == 0:
                logger.debug(mfl + "/*.md5sum: remove OK")
            else:
                logger.error("Removal of " + mfl + "/*.md5sum: retcode " + str(retcode))
        except OSError as e:
            logger.error("rm execution failed: " + str(e))
        # Loop through active manifests
        for mfn in _manifests(mfl):
            try:
                mf = _read_manifest(os.path.join(mfl,mfn))
            except _ManifestValidationException as mfe:
                logger.error("Manifest " + mfn + " is invalid.")
                logger.error(str(mfe))
                rht_rc = 10
                return False
            rht_course = mf['curriculum']['name']
            md5sumfile = rht_course + '-vms.md5sum'
            logger.info("Generating " + md5sumfile + " from " + mfn)
            for a in mf['curriculum']['artifacts']:
                # if type=content, final name.contains=/vms/, final name.endswith=.qcow2
                if a['type'].startswith('content') and 'final name' in a:
                    if '/vms/' in a['final name'] and (a['final name'].endswith('.qcow2') or a['final name'].endswith('.iso')):
                        # md5line = checksum + ' ' + basename(final name)
                        md5line = a['checksum'] + ' ' + os.path.basename(a['final name'])
                        # append line to md5sumfile
                        logger.debug("Adding line to " + md5sumfile)
                        with open(os.path.join(mfl,md5sumfile), "a") as md5append:
                            md5append.write(md5line + "\n")
                        if 'hardlink names' in a:
                            for linkname in a['hardlink names']:
                                md5line = a['checksum'] + ' ' + os.path.basename(linkname)
                                # append line to md5sumfile
                                logger.debug("Adding line to " + md5sumfile)
                                with open(os.path.join(mfl,md5sumfile), "a") as md5append:
                                    md5append.write(md5line + "\n")
                # if type=content and content type=iso , target directory.endswith=/vms, filename.endswith=.iso
                if a['type'].startswith('content') and a['content type'].startswith('iso'):
                    if a['target directory'].endswith('/vms') and a['filename'].endswith('.iso'):
                        # md5line = checksum + ' ' + basename(final name)
                        md5line = a['checksum'] + ' ' + a['filename']
                        # append line to md5sumfile
                        logger.debug("Adding line to " + md5sumfile)
                        with open(os.path.join(mfl,md5sumfile), "a") as md5append:
                            md5append.write(md5line + "\n")
    print()
    if goodorbad:
        logger.info("f0vmsmd5sum SUCCEEDED")
    else:
        logger.warning("f0vmsmd5sum FAILED - look above for ERROR")
        logger.warning("Summary of failures:")
        logger.warning(error_summary)
        rht_rc = 10

def verifynewer(dateOrToday):
    """Confirm artifact checksums for newer manifests in cache.

       Accepts as an argument "YYYY-MM-DD", "today", or "yesterday".
       Will verify the icmf files whose modification date matches or is
       newer than the one specified."""
    global rht_already
    global rht_rc
    global error_summary
    error_summary = ""
    logger = logging.getLogger('vm-usb')
    rht_already = set()
    if not re.match('^(\\d{4}-\\d{2}-\\d{2}|yesterday|today)$', dateOrToday):
        logger.error(dateOrToday + " not a valid date: YYYY-MM-DD or today")
        rht_rc = 10
        return
    if dateOrToday == "today":
        compareDate = datetime.date.today()
    elif dateOrToday == "yesterday":
        compareDate = datetime.date.today() - datetime.timedelta(days = 1)
    else:
        year,month,day = (int(d) for d in dateOrToday.split('-'))
        try:
            compareDate = datetime.date(year, month, day)
        except:
            logger.error(dateOrToday + " not a valid date: YYYY-MM-DD or today")
            rht_rc = 10
            return
    mfl = config['repository']
    logger.info("Verifying Newer Cache Directory: " + mfl)
    goodorbad = True
    if not os.path.isdir(mfl):
        logger.error(mfl + " as a cache, does not exist")
        goodorbad = False
    else:
        for mf in _manifests(mfl):
            mfabs = os.path.join(mfl, mf)
            mfmodDate = datetime.date.fromtimestamp(os.path.getmtime(mfabs))
            if mfmodDate >= compareDate:
                if not _verify(mfabs, 0, 0):
                    goodorbad = False
    print()
    if goodorbad:
        logger.info("Newer Verification SUCCEEDED")
    else:
        logger.warning("Verification FAILED - look above for problem")
        logger.warning("Summary of failures:")
        logger.warning(error_summary)
        rht_rc = 10

def verifyquick(manifestFilenameOrAll):
    """Confirm artifact exists for the manifest in cache (no sum).

       Only checks that artifacts exist (no md5sums) in the cache.
       Use \"verify\" to fully check the artifacts in the cache.
       Accepts as an argument "all" or the full name of the .icmf file."""
    global rht_already
    global rht_rc
    global error_summary
    error_summary = ""
    manifestFilenameOrAll = os.path.basename(manifestFilenameOrAll)
    logger = logging.getLogger('vm-usb')
    rht_already = set()
    mfl = config['repository']
    logger.info("Quick Verifying Cache Directory: " + mfl)
    goodorbad = True
    if not os.path.isdir(mfl):
        logger.error(mfl + " as a cache, does not exist")
        goodorbad = False
    elif manifestFilenameOrAll == "all":
        for mf in _manifests(mfl):
            mfabs = os.path.join(mfl, mf)
            if not _verify(mfabs, 0, 1):
                goodorbad = False
    else:
        mfabs = os.path.join(mfl, manifestFilenameOrAll)
        goodorbad = _verify(mfabs, 0, 1)
    print()
    if goodorbad:
        logger.info("Quick Verification SUCCEEDED - BUT you should use verify")
    else:
        logger.warning("Verification FAILED - look above for problem")
        logger.warning("Summary of failures:")
        logger.warning(error_summary)
        rht_rc = 10

def size(manifestFilenameOrAll):
    """Display artifact size for the manifest in cache.

       Accepts as an argument "all" or the full name of the .icmf file."""
    global rht_already
    global rht_rc
    global error_summary
    error_summary = ""
    manifestFilenameOrAll = os.path.basename(manifestFilenameOrAll)
    logger = logging.getLogger('vm-usb')
    rht_already = set()
    mfl = config['repository']
    logger.info("Sizing Cache Directory: " + mfl)
    goodorbad = True
    if not os.path.isdir(mfl):
        logger.error(mfl + " as a cache, does not exist")
        goodorbad = False
    elif manifestFilenameOrAll == "all":
        for mf in _manifests(mfl):
            mfabs = os.path.join(mfl, mf)
            if not _verify(mfabs, 0, 2):
                goodorbad = False
    else:
        mfabs = os.path.join(mfl, manifestFilenameOrAll)
        goodorbad = _verify(mfabs, 0, 2)
    print()
    if goodorbad:
        logger.info("Sizing SUCCEEDED")
    else:
        logger.warning("Sizing FAILED - look above for problem")
        logger.warning("Summary of failures:")
        logger.warning(error_summary)
        rht_rc = 10

def usbverifynewer(dateOrToday):
    """Confirm artifact checksums for newer manifests on USB.

       Accepts as an argument "YYYY-MM-DD", "today", or "yesterday".
       Will verify the icmf files whose modification date matches or is
       newer than the one specified."""
    global rht_already
    global rht_usbmount
    global rht_rc
    global error_summary
    error_summary = ""
    logger = logging.getLogger('vm-usb')
    rht_already = set()
    if not re.match('^(\\d{4}-\\d{2}-\\d{2}|yesterday|today)$', dateOrToday):
        logger.error(dateOrToday + " not a valid date: YYYY-MM-DD or today")
        rht_rc = 10
        return
    if dateOrToday == "today":
        compareDate = datetime.date.today()
    elif dateOrToday == "yesterday":
        compareDate = datetime.date.today() - datetime.timedelta(days = 1)
    else:
        year,month,day = (int(d) for d in dateOrToday.split('-'))
        try:
            compareDate = datetime.date(year, month, day)
        except:
            logger.error(dateOrToday + " not a valid date: YYYY-MM-DD or today")
            rht_rc = 10
            return
    rht_usbmount = _usbmount()
    if not rht_usbmount:
        return
    mfl = os.path.join(rht_usbmount, "manifests")
    logger.info("Verifying USB Mountpoint: " + rht_usbmount)
    goodorbad = True
    if not os.path.isdir(mfl):
        # Missing manifests directory
        logger.error(rht_usbmount + " does not have any manifests")
        goodorbad = False
    else:
        for mf in _manifests(mfl):
            mfabs = os.path.join(mfl, mf)
            mfmodDate = datetime.date.fromtimestamp(os.path.getmtime(mfabs))
            if mfmodDate >= compareDate:
                if not _verify(mfabs, 1, 0):
                    goodorbad = False
    print()
    if goodorbad:
        logger.info("Newer Verification SUCCEEDED")
    else:
        logger.warning("Verification FAILED - look above for problem")
        logger.warning("Summary of failures:")
        logger.warning(error_summary)
        rht_rc = 10

def usbverify(manifestUSBFilenameOrAll):
    """Confirm artifact checksums for the manifest on USB.

       Accepts as an argument "all" or the full name of the .icmf file."""
    global rht_already
    global rht_usbmount
    global rht_rc
    global error_summary
    error_summary = ""
    manifestUSBFilenameOrAll = os.path.basename(manifestUSBFilenameOrAll)
    logger = logging.getLogger('vm-usb')
    rht_already = set()
    rht_usbmount = _usbmount()
    if not rht_usbmount:
        return
    mfl = os.path.join(rht_usbmount, "manifests")
    logger.info("Verifying USB Mountpoint: " + rht_usbmount)
    goodorbad = True
    if not os.path.isdir(mfl):
        # Missing manifests directory
        logger.error(rht_usbmount + " does not have any manifests")
        goodorbad = False
    elif manifestUSBFilenameOrAll == "all":
        for mf in _manifests(mfl):
            mfabs = os.path.join(mfl, mf)
            if not _verify(mfabs, 1, 0):
                goodorbad = False
    else:
        mfabs = os.path.join(mfl, manifestUSBFilenameOrAll)
        goodorbad = _verify(mfabs, 1, 0)
    print()
    if goodorbad:
        logger.info("Verification SUCCEEDED")
    else:
        logger.warning("Verification FAILED - look above for problem")
        logger.warning("Summary of failures:")
        logger.warning(error_summary)
        rht_rc = 10

def verify(manifestFilenameOrAll):
    """Confirm artifact checksums for the manifest in cache.

       Accepts as an argument "all" or the full name of the .icmf file."""
    global rht_already
    global rht_rc
    global error_summary
    error_summary = ""
    manifestFilenameOrAll = os.path.basename(manifestFilenameOrAll)
    logger = logging.getLogger('vm-usb')
    rht_already = set()
    mfl = config['repository']
    logger.info("Verifying Cache Directory: " + mfl)
    goodorbad = True
    if not os.path.isdir(mfl):
        logger.error(mfl + " as a cache, does not exist")
        goodorbad = False
    elif manifestFilenameOrAll == "all":
        for mf in _manifests(mfl):
            mfabs = os.path.join(mfl, mf)
            if not _verify(mfabs, 0, 0):
                goodorbad = False
    else:
        mfabs = os.path.join(mfl, manifestFilenameOrAll)
        goodorbad = _verify(mfabs, 0, 0)
    print()
    if goodorbad:
        logger.info("Verification SUCCEEDED")
    else:
        rht_rc = 10
        logger.warning("Verification FAILED - look above for problem")
        logger.warning("Summary of failures:")
        logger.warning(error_summary)

def usbmkpart(usbdevice, parttype):
    """Function to partition USB destination.

    Pass the currently unmounted device path as an argument followed
    by partition type of gpt, gptefi, or msdos (gpthybrid deprecated).
    i.e. /dev/sdd gptefi
    """
    global rht_rc
    global error_summary
    global alwaysyes
    error_summary = ""
    logger = logging.getLogger('vm-usb')
    logger.info("Partitioning USB Device: " + usbdevice)
    devname = os.path.basename(usbdevice)
    if not _cmd_exists("parted"):
        logger.error("parted executable missing from path")
        logger.error("Try installing parted package")
        rht_rc = 1
        return
    else:
        try:
            # Test version
            partedversion = subprocess.check_output("parted -v | grep -o '[0-9]\\.[0-9]'", shell=True).decode().replace("\n","")
        except OSError as e:
            logger.error("parted version check failes: " + str(e))
            rht_rc = 6
            return
        if float(partedversion) < 3.4:
            logger.error("parted version too old: " + partedversion)
            logger.error("parted must be 3.4+ available on RHEL 9+")
            rht_rc = 1
            return
    if not _cmd_exists("sgdisk"):
        logger.error("sgdisk executable missing from path")
        logger.error("Try installing gdisk package")
        rht_rc = 1
        return
    if not _cmd_exists("wipefs"):
        logger.error("wipefs executable missing from path")
        logger.error("Try installing util-linux package")
        rht_rc = 1
        return
    if parttype == 'gptefi' or parttype == 'gpthybrid' or parttype == 'gpt':
        partGPT = True
    elif parttype == 'msdos':
        partGPT = False
    else:
        logger.error(parttype + " not a valid partition type (gpt|gptefi|gpthybrid|msdos).")
        return
    if parttype == 'gpthybrid':
        logger.info("gpthybrid is deprecated - please repartition")
        msg = "Confirm DEPRECATED " + parttype + " partitioning " + usbdevice
        confirm = True if alwaysyes or input("%s (y/N) " % msg).lower() == 'y' else False
        if not confirm:
            logger.warning("Partitioning aborted")
            return
    if devname:
        blockdev = '/sys/block/' + devname
        if not os.path.exists(blockdev):
            # Device name is not a block device on system
            logger.error(blockdev + " does not exist as block device.")
            return
    else:
        # Device name unparseable
        logger.error(usbdevice + " not parseable.")
        return
    try:
        line = subprocess.check_output(['grep', usbdevice, '/etc/mtab']).decode()
        logger.error(usbdevice + " (or partition) currently mounted.")
        logger.error("Please unmount the device then try again.")
        return
    except:
        logger.debug(usbdevice + " not currently mounted")
    msg = "Confirm " + parttype + " partitioning " + usbdevice
    confirm = True if alwaysyes or input("%s (y/N) " % msg).lower() == 'y' else False
    if not confirm:
        logger.warning("Partitioning aborted")
        return
    try:
        retcode = subprocess.call("LANG=en_US.UTF-8 parted -s -f " + usbdevice + " print | grep  \'Partition Table: unknown\' &>/dev/null", shell=True)
        if retcode == 0:
            logger.info("No existing partition table")
        else:
            msg = "Wipe existing partitioning of " + usbdevice
            confirm = True if alwaysyes or input("%s (y/N) " % msg).lower() == 'y' else False
            if not confirm:
                logger.warning("Partitioning aborted")
                return
    except OSError as e:
        logger.error("Unable to test for partition table: " + str(e))
    try:
        # Wipe existing partitioning
        retcode = subprocess.call("wipefs --all " + usbdevice + " &>/dev/null", shell=True)
        if retcode == 0:
            logger.info(usbdevice + ": wipefs OK")
        else:
            logger.error("wipefs failed of " + usbdevice + " retcode: " + str(retcode))
            rht_rc = retcode
            return
    except OSError as e:
        logger.error("wipefs execution failed: " + str(e))
        rht_rc = 6
        return
    try:
        # Zap existing partitioning
        retcode = subprocess.call("sgdisk -Z " + usbdevice + " &>/dev/null", shell=True)
        if retcode == 0:
            logger.info(usbdevice + ": zap partitions OK")
        else:
            logger.error("Zap partitions failed of " + usbdevice + " retcode: " + str(retcode))
            rht_rc = retcode
            return
    except OSError as e:
        logger.error("sgdisk zap execution failed: " + str(e))
        rht_rc = 6
        return
    msg = "Exhaustive zeroing of " + usbdevice + " (recommended, not required)"
    confirm = True if alwaysyes or input("%s (y/N) " % msg).lower() == 'y' else False
    if confirm:
        try:
            # Zero out the device
            retcode = subprocess.call("dd if=/dev/zero of=" + usbdevice + " bs=1M &>/dev/null", shell=True)
        except OSError as e:
            logger.error("dd zero failed: " + str(e))
            rht_rc = 6
            return
    if partGPT:
        try:
            # Wipe existing partitioning and convert msdos to gpt
            retcode = subprocess.call("sgdisk -og " + usbdevice + " &>/dev/null", shell=True)
            if retcode == 0:
                logger.info(usbdevice + ": wipe partitions OK")
            else:
                logger.error("Wipe partitions failed of " + usbdevice + " retcode: " + str(retcode))
                rht_rc = retcode
                return
        except OSError as e:
            logger.error("sgdisk wipe execution failed: " + str(e))
            rht_rc = 6
            return
        # branch on parttype of gpt type
        if "gpthybrid" in parttype:
            # Create partitioning for gpthybrid
            try:
                # Create partitioning
                retcode = subprocess.call("ENDSECTOR=$(sgdisk -E " + usbdevice + "); sgdisk -n 1:2048:4095 -c 1:'BIOS Boot Partition' -t 1:ef02 -n 2:4096:413695 -c 2:'EFI System Partition' -t 2:ef00 -n 3:413696:$ENDSECTOR -c 3:'Linux RHTINST' -t 3:8300 " + usbdevice + " &>/dev/null", shell=True)
                if retcode == 0:
                    logger.info(usbdevice + ": partitioning OK")
                    partsearch = devname + ".*3"
                else:
                    logger.error("Partitioning failed of " + usbdevice + " retcode: " + str(retcode))
                    rht_rc = retcode
                    return
            except OSError as e:
                logger.error("sgdisk partitioning execution failed: " + str(e))
                rht_rc = 6
                return
        else:
            # Create partitioning for gptefi/gpt
            try:
                # Create partitioning
                #retcode = subprocess.call("ENDSECTOR=$(sgdisk -E " + usbdevice + "); ESPSECTOR=$(( $ENDSECTOR - 409600 )); RHTSECTOR=$(( $ESPSECTOR - 1 )); sgdisk -n 1:2048:$RHTSECTOR -c 1:'Linux RHTINST' -t 1:8300 -n 2:$ESPSECTOR:$ENDSECTOR -c 2:'EFI System Partition' -t 2:ef00 " + usbdevice + " &>/dev/null", shell=True)
                retcode = subprocess.call("ENDSECTOR=$(sgdisk -E " + usbdevice + "); sgdisk -n 1:2048:409599 -c 1:'EFI System Partition' -t 1:ef00 -n 2:409600:$ENDSECTOR -c 2:'Linux RHTINST' -t 2:8300 " + usbdevice + " &>/dev/null", shell=True)
                if retcode == 0:
                    logger.info(usbdevice + ": partitioning OK")
                    partsearch = devname + ".*2"
                else:
                    logger.error("Partitioning failed of " + usbdevice + " retcode: " + str(retcode))
                    rht_rc = retcode
                    return
            except OSError as e:
                logger.error("sgdisk partitioning execution failed: " + str(e))
                rht_rc = 6
                return
    else:
        # Create msdos partitioning
        try:
            # Create partitioning
            retcode = subprocess.call("parted -s -f " + usbdevice + " mklabel msdos &>/dev/null", shell=True)
            if retcode == 0:
                logger.info(usbdevice + ": partition initialization OK")
            else:
                logger.error("Partitioning failed of " + usbdevice + " retcode: " + str(retcode))
                rht_rc = retcode
                return
            retcode = subprocess.call("parted -s -f " + usbdevice + " mkpart primary ext4 1MiB 100% &>/dev/null", shell=True)
            if retcode == 0:
                logger.info(usbdevice + ": partitioning OK")
                partsearch = devname + ".*1"
            else:
                logger.error("Partitioning failed of " + usbdevice + " retcode: " + str(retcode))
                rht_rc = retcode
                return
        except OSError as e:
            logger.error("parted partitioning execution failed: " + str(e))
            rht_rc = 6
            return
    f = open("/proc/partitions").read()
    partname = next(iter(re.findall(partsearch, f, re.M) or []), "")
    if partname:
        logger.info("/dev/" + partname + ": apparent RHTINST partition")
        logger.info("Now run usbformat of /dev/" + partname)
    else:
        logger.error("Cannot locate partition on " + usbdevice)
        rht_rc = 6
        return
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("usbmkpart partially completed.")
    else:
        logger.info("Appear to have properly partitioned USB device.")
        logger.info("usbmkpart completed.")

def usbformat(usbpartition):
    """Function to format USB destination.

    Pass the currently unmounted partition path as an argument.
    i.e. /dev/sdd1 for msdos
         /dev/sdd2 for gptefi/gpt partitioning
         /dev/sdd3 for gpthybrid partitioning
    """
    global rht_rc
    global rht_usbmount
    global rht_usbparts
    global error_summary
    global alwaysyes
    error_summary = ""
    logger = logging.getLogger('vm-usb')
    logger.info("Formatting USB Partition: " + usbpartition)
    if os.path.exists(usbpartition):
        partname = os.path.basename(usbpartition)
        try:
            sysname = subprocess.check_output(['find', '/sys/devices', '-type', 'd', '-name', partname]).decode().replace("\n","")
            blockname = os.path.dirname(sysname)
            devname = os.path.basename(blockname)
            if devname == 'block':
                logger.error("Invalid partition name: " + usbpartition)
                rht_rc = 6
                return
        except:
            logger.error("Unable to find device: " + usbpartition)
            rht_rc = 6
            return
    else:
        logger.error("Device does not exist: " + usbpartition)
        rht_rc = 6
        return
    try:
        line = subprocess.check_output(['grep', usbpartition, '/etc/mtab']).decode()
        parts = line.split(' ')
        logger.error(usbpartition + " currently mounted.")
        logger.error("Please unmount the device then try again.")
        rht_rc = 6
        return
    except:
        logger.debug(usbpartition + " not currently mounted")
    # Test/confirm whether partition was created with usbmkpart - log
    _usbpartitions('/dev/' + devname)
    if rht_usbparts['partRHTINST'] in partname:
        logger.info(usbpartition + ' appears created by usbmkpart')
    else:
        logger.warning(usbpartition + ' NOT created by usbmkpart')
    msg = "Confirm reformatting " + usbpartition
    confirm = True if alwaysyes or input("%s (y/N) " % msg).lower() == 'y' else False
    if not confirm:
        logger.warning("Format aborted")
        return
    try:
        retcode = subprocess.call("grep -E \'64bit|64-bit\' /etc/mke2fs.conf &>/dev/null", shell=True)
        if retcode == 0:
            logger.info("mkfs.ext4 64-bit support")
            mkfsopt = "^has_journal,^64bit"
        else:
            logger.info("mkfs.ext4 no 64-bit support")
            mkfsopt = "^has_journal"
    except OSError as e:
        logger.error("Access of /etc/mke2fs.conf failed: " + str(e))
        rht_rc = 6
        return
    try:
        retcode = subprocess.call("grep -E \'metadata_csum\' /etc/mke2fs.conf &>/dev/null", shell=True)
        if retcode == 0:
            logger.info("mkfs.ext4 metadata_csum support")
            mkfsopt = mkfsopt + ",^metadata_csum"
        else:
            logger.info("mkfs.ext4 no metadata_csum support")
    except OSError as e:
        logger.error("Access of /etc/mke2fs.conf failed: " + str(e))
        rht_rc = 6
        return
    try:
        retcode = subprocess.call("mkfs -t ext4 -O " + mkfsopt + " -b 4096 -i 819200 -L " + rht_label + " \"" + usbpartition + "\" &>/dev/null", shell=True)
        if retcode == 0:
            logger.info(usbpartition + ": format OK")
        else:
            logger.error("Format failed of " + usbpartition + " retcode: " + str(retcode))
            rht_rc = retcode
            return
    except OSError as e:
        logger.error("mkfs execution failed: " + str(e))
        rht_rc = 6
        return
    rht_usbmount = _mountusb(usbpartition)
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("usbformat partially completed.")
    else:
        logger.info("Appear to have properly formatted USB device.")
        logger.info("usbformat completed.")
    return rht_usbmount

def usbmkboot():
    """Function to make the USB device bootable.

    This option takes no arguments, detects the USB device and does extreme
    things to the device after prompting for confirmation.
    It assumes that an RHTINST device is currently plugged in.
    """
    global rht_usbmount
    global rht_usbparts
    global rht_rc
    global error_summary
    global alwaysyes
    error_summary = ""
    logger = logging.getLogger('vm-usb')
    syslinux_dir = "/usr/share/syslinux"
    # Mount device
    rht_usbmount = _usbmount()
    if not rht_usbmount:
        return
    # Get partitioning information
    _usbpartitions()
    # Test for pre-requisite files existence
    # Test for mbr.bin file
    if 'gpt' in rht_usbparts['partStyle']:
        mbrfile = "/usr/share/syslinux/gptmbr.bin"
    else:
        mbrfile = os.path.join(rht_usbmount, "boot/extlinux/mbr.bin")
    if not os.path.isfile(mbrfile):
        logger.error("Device missing " + mbrfile)
        if 'gpt' in rht_usbparts['partStyle']:
            logger.error("Try installing syslinux-extlinux package")
        else:
            logger.error("Re-add RHCIfoundation manifest")
        rht_rc = 6
        return
    # Test for extlinux path
    extpath = os.path.join(rht_usbmount, "boot/extlinux")
    if not os.path.isfile(os.path.join(extpath, "extlinux.conf")):
        logger.error("extlinux.conf missing in " + extpath)
        logger.error("Re-add RHCIfoundation manifest")
        rht_rc = 6
        return
    # Test for needed executables
    if not _cmd_exists("extlinux"):
        logger.error("extlinux executable missing from path")
        logger.error("Try installing syslinux-extlinux package")
        rht_rc = 1
        return
    if not os.path.isfile(os.path.join(syslinux_dir, "vesamenu.c32")):
        logger.error("extlinux missing menu " + syslinux_dir + "/vesamenu.c32")
        logger.error("Try installing syslinux-extlinux package")
        rht_rc = 1
        return
    if not _cmd_exists("parted"):
        logger.error("parted executable missing from path")
        logger.error("Try installing parted package")
        rht_rc = 1
        return
    else:
        try:
            # Test version
            partedversion = subprocess.check_output("parted -v | grep -o '[0-9]\\.[0-9]'", shell=True).decode().replace("\n","")
        except OSError as e:
            logger.error("parted version check failed: " + str(e))
            rht_rc = 6
            return
        if float(partedversion) < 3.4:
            logger.error("parted version too old: " + partedversion)
            logger.error("parted must be 3.4+ available on RHEL 9+")
            rht_rc = 1
            return
    # Test gpt partition layout matches usbmkpart
    goodorbad = True
    # Complain if unrecognized partitioning
    if rht_usbparts['partStyle'] == 'unrecognized':
        logger.error("Device partitioning is unrecognized")
        goodorbad = False
    # Confirm that msdos partitioning appears to be mine
    elif rht_usbparts['partStyle'] == 'msdos':
        if len(glob.glob(rht_usbparts['diskName'] + '*')) == 2:
            logger.info("Device has one msdos partition")
            if not rht_usbparts['partRHTINST']:
                logger.error("Device has invalid partition")
                goodofbad = False
        else:
            logger.error("Device has additional msdos partitions")
            goodorbad = False
    # Complain if gptUnknown partitioning
    elif rht_usbparts['partStyle'] == 'gptUnknown':
        logger.error("GPT partitioning is unknown (not by usbmkpart)")
        goodorbad = False
    # Declare happiness with gpthybrid
    elif rht_usbparts['partStyle'] == 'gpthybrid':
        logger.info("Device has three gpthybrid partitions")
        logger.info("gpthybrid is deprecated - please repartition")
    # Declare happiness with gptoldefi
    elif rht_usbparts['partStyle'] == 'gptoldefi':
        logger.info("Device has two gptoldefi partitions")
        logger.info("gptoldefi is deprecated - please repartition")
    # Declare happiness with gptefi
    elif rht_usbparts['partStyle'] == 'gptefi':
        logger.info("Device has two gptefi partitions")
    if not goodorbad:
        rht_rc = 6
        return
    # Offer escape route
    dev = rht_usbparts['diskName']
    devp = '/dev/' + rht_usbparts['partRHTINST']
    part2 = '/dev/' + rht_usbparts['partESP']
    part3 = devp
    tmpdev = re.sub("\\d+$", "", devp)
    devn = devp.lstrip(tmpdev)
    print()
    print("WARNING - You get to keep all the pieces if system becomes unbootable")
    print("WARNING - We really mean it - do not cry to us if your system is destroyed")
    msg = "Confirm writing to " + devp + " mounted to " + rht_usbmount
    confirm = True if alwaysyes or input("%s (y/N) " % msg).lower() == 'y' else False
    if not confirm:
        logger.warning("usbmkboot aborted")
        return
    logger.info("Making bootable: " + rht_usbmount)
    # Reformat and populate EFI System Partition
    if 'gpt' in rht_usbparts['partStyle']:
        # Call to mkfs.vfat -n RHTESP part2
        logger.info("Formatting FAT and copying EFI/ files to " + part2)
        try:
            retcode = subprocess.call("mkfs -t vfat -n RHTESP \"" + part2 + "\" &>/dev/null", shell=True)
            if retcode == 0:
                logger.info(part2 + ": vfat format OK")
            else:
                logger.error("Format failed of " + part2 + " retcode: " + str(retcode))
                rht_rc = retcode
                return
        except OSError as e:
            logger.error("mkfs execution failed: " + str(e))
            rht_rc = 6
            return
        # Mount it
        ESPtarget = tempfile.mkdtemp()
        logger.debug("Mounting " + part2 + " to " + ESPtarget)
        _createdir(ESPtarget)
        try:
            #retcode = subprocess.call("mount -o sync \"" + part2 + "\" \"" + ESPtarget + "\" &>/dev/null", shell=True)
            retcode = _subprocess_call("mount \"" + part2 + "\" \"" + ESPtarget + "\"", logger, shell=True)
            if retcode == 0:
                logger.debug(part2 + ": mount OK")
            else:
                logger.error("ESP mount failed retcode: " + str(retcode))
                rht_rc = 6
                return
        except OSError as e:
            logger.error("mount execution failed: " + str(e))
            rht_rc = 6
            return
        # rsync (rht_usbmount/boot/EFI to mountpoint)
        _rsync(os.path.join(rht_usbmount, "boot/EFI"), ESPtarget)
        # Unmount part2
        logger.info("Looking to unmount EFI partition " + part2)
        _umount(ESPtarget)
        if os.path.isdir(ESPtarget):
            try:
                os.rmdir(ESPtarget)
                logger.debug(ESPtarget + ": rmdir OK")
            except OSError as e:
                logger.error("Directory removal failed of " + ESPtarget)
                logger.error("os.rmdir execution failed: " + str(e))
    # On both gpt/msdos copy extlinux support files
    # Copy needed files from client OS extlinux
    logger.info("Copying extlinux menu files to " + extpath)
    # Must copy vesamenu.c32
    _rsync(os.path.join(syslinux_dir, "vesamenu.c32"), extpath)
    # If exists, copy libutil.c32 and libcom32.c32
    srcfile = os.path.join(syslinux_dir, "libutil.c32")
    if os.path.isfile(srcfile):
        _rsync(srcfile, extpath)
    srcfile = os.path.join(syslinux_dir, "libcom32.c32")
    if os.path.isfile(srcfile):
        _rsync(srcfile, extpath)
    # Run extlinux to install in to the mountpoint
    logger.info("Using extlinux to install to " + extpath)
    try:
        retcode = subprocess.call("extlinux --install " + extpath + " &>/dev/null", shell=True)
        if retcode == 0:
            logger.info(extpath + ": extlinux OK")
        else:
            logger.error("extlinux failed of " + rht_usbmount + " retcode: " + str(retcode))
            rht_rc = retcode
            return
    except OSError as e:
        logger.error("extlinux execution failed: " + str(e))
        rht_rc = 6
        return
    # Unchattr the ldlinux.sys file
    logger.info("Using chattr to remove immutable of " + extpath + "/ldlinux.sys")
    try:
        retcode = subprocess.call("chattr -i " + extpath + "/ldlinux.sys &>/dev/null", shell=True)
        if retcode == 0:
            logger.info(extpath + ": chattr OK")
        else:
            logger.error("chattr failed of " + rht_usbmount + " retcode: " + str(retcode))
            rht_rc = retcode
            return
    except OSError as e:
        logger.error("chattr execution failed: " + str(e))
        rht_rc = 6
        return
    # Run dd to install mbr.bin
    if 'gpthybrid' in rht_usbparts['partStyle'] or 'msdos' in rht_usbparts['partStyle']:
        logger.info("Using dd to write " + mbrfile + " to " + dev)
        try:
            retcode = subprocess.call("dd conv=notrunc bs=440 count=1 if=" + mbrfile + " of=" + dev + " &>/dev/null", shell=True)
            if retcode == 0:
                logger.info(dev + ": dd of mbr.bin OK")
            else:
                logger.error("dd of mbr.bin failed to " + dev + " retcode: " + str(retcode))
                rht_rc = retcode
                return
        except OSError as e:
            logger.error("dd execution failed: " + str(e))
            rht_rc = 6
            return
    # Umount device to keep parted happy
    _usbumount()
    # Flag partition bootable
    if 'gpthybrid' in rht_usbparts['partStyle']:
        logger.info("Using sgdisk to tag bootable " + part3)
        try:
            retcode = subprocess.call("sgdisk " + dev + " --attributes=3:set:2 &>/dev/null", shell=True)
            if retcode == 0:
                logger.info(part3 + ": sgdisk set of Legacy BIOS bootable flag OK")
            else:
                logger.error("sgdisk set of boot flag failed to " + part3 + " retcode: " + str(retcode))
                rht_rc = retcode
                return
        except OSError as e:
            logger.error("sgdisk execution failed: " + str(e))
            rht_rc = 6
            return
    elif 'msdos' in rht_usbparts['partStyle']:
        logger.info("Using parted to tag bootable " + devp)
        try:
            retcode = subprocess.call("parted -s -f " + dev + " set " + devn + " boot on &>/dev/null", shell=True)
            if retcode == 0:
                logger.info(devp + ": parted set of boot flag OK")
            else:
                logger.error("parted set of boot flag failed to " + devp + " retcode: " + str(retcode))
                rht_rc = retcode
                return
        except OSError as e:
            logger.error("parted execution failed: " + str(e))
            rht_rc = 6
            return
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("usbmkboot partially completed.")
        logger.error("NOT calling usbmkmenu.")
    else:
        logger.info("Appear to have successfully made USB bootable.")
        logger.info("usbmkboot completed.")
        logger.info("Automatically calling usbmkmenu.")
        usbmkmenu()

def usbmkmenu():
    """Function to make the USB device bootmenu with icmf list.

    This option takes no arguments, detects the USB device and attempts
    to create an updated bootmenu.
    It assumes that an RHTINST device is currently plugged in.
    """
    global rht_usbmount
    global rht_rc
    global error_summary
    error_summary = ""
    logger = logging.getLogger('vm-usb')
    # Mount device
    time.sleep(5)
    rht_usbmount = _usbmount()
    if not rht_usbmount:
        return
    # Get device name (devp - RHTINST partition; dev - disk)
    #try:
    #    line = subprocess.check_output(['grep', rht_usbmount, '/etc/mtab']).decode()
    #    parts = line.split(' ')
    #    devp = parts[0]
    #except:
    #    logger.error("Device not currently mounted")
    #    return
    #dev = re.sub("\\d+$", "", devp)
    #dev = re.sub("p$", "", dev)
    #devn = devp.lstrip(dev)

    # outline of code here
    for menu in ['f0', 'standalone']:
        oldgrubname = os.path.join(rht_usbmount, "boot/EFI/BOOT/" + menu + "-mkmenu.cfg")
        newgrubname = "/tmp/new-" + menu + "-mkmenu.cfg"
        # Test read of oldgrubname
        if not(os.access(oldgrubname,os.R_OK)):
            logger.error("Existing grub f0-mkmenu.cfg not accessible")
            logger.debug(oldgrubname + "not accessible")
            rht_rc = 7
            return
        cfglines = []
        # Open newfile for write
        newgrubfile = open(newgrubname, 'w')
        # FIXME: Test write of newgrubname
        # Open existingfile for read /boot/EFI/BOOT/f0-mkmenu.cfg
        with open(oldgrubname, "r") as oldgrubfile:
        # loop:
            for cfgline in oldgrubfile:
        ##  readlineofexistingfile
                cfgline = cfgline.rstrip('\n')
        ##  addtolinelist
                cfglines.append(cfgline)
        ##  writelinetonewfile
                newgrubfile.write(cfgline + '\n')
        ##  if readline is '}'
                if cfgline == '}':
        ###   endloop
                    logger.debug('Found end of first entry')
                    break
        oldgrubfile.close()
        # writecommenttonewfile
        newgrubfile.write('# Course-Technology menu generated ' + datetime.date.today().strftime('%Y%m%d') + '\n')
        # getlistoficmf
        mfl=os.path.join(rht_usbmount, "manifests")
        if os.path.isdir(mfl):
        # loop through each icmf:
            for mf in _manifests(mfl):
        ##  parse icmffilename to first two words: course, technology
                mfparts = mf.split('-')
                mfcourse = mfparts[0]
                mftech = mfparts[1]
                if not mfcourse and not mftech:
                    logger.debug('Malformed manifest filename on USB: ' + mf)
                    continue
        ##  if course = RHCIfoundation:
                elif mfcourse == 'RHCIfoundation':
        ###   skip
                    continue
        ##  if course beginswith ex (skip exam manifests):
                elif mfcourse.upper().startswith('EX'):
        ###   skip
                    continue
        ##  elif course beginswith RHCI
                elif mfcourse.startswith('RHCI'):
        ###   argument=course.lstrip('RHCI')
                    grubarg = mfcourse.lstrip('RHCI')
        ##  else
                else:
        ###   argument=course-technology
                    grubarg = mfcourse + '-' + mftech
                logger.info("Adding to menu: " + grubarg)
        ##  loop linelist:
                for line in cfglines:
        ###   line.replace (.*) with argument
                    line = re.sub('\\(.*\\)', '(' + grubarg + ')', line)
        ###   if line.contains "linux" line.append argument
                    if 'vmlinuz' in line:
                        line = line + ' ' + grubarg
        ###   writelinetonewfile
                    newgrubfile.write(line + '\n')
        else:
            logger.warning("USB improperly formatted - missing " + mfl)
            rht_rc = 4
            return
        # closenewfile
        newgrubfile.close()
        # writenewfile over existingfile
        _rsync(newgrubname, oldgrubname)
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("usbmkmenu partially completed.")
    else:
        logger.info("Appear to have successfully made USB bootmenu.")
        logger.info("usbmkmenu completed.")

def lsicmfs(f):
    """List icmfs in cache that references passed artifact.

    Looks in the cache directory defined in $HOME/vm_repo_config.yml
    """
    global rht_rc
    global error_summary
    error_summary = ""
    logger = logging.getLogger('vm-usb')
    mfl = config['repository']
    counterm=0
    counterf=0
    logger.info("Listing icmfs referencing " + f)
    if not os.path.isdir(mfl):
        logger.error(mfl + " as a cache, does not exist.")
        rht_rc = 5
        return
    # Test for existence of f

    notfound = True
    for x in _manifests(mfl):
        try:
            data_x = _read_manifest(os.path.join(mfl, x))
        except _ManifestValidationException as mfe:
            logger.error("Manifest " + x + " is invalid.")
            logger.error(str(mfe))
            return False
        counterm=counterm+1
        for artifact_x in data_x['curriculum']['artifacts']:
            if f == artifact_x['filename']:
                notfound = False
                print("\033[92m  REFERENCED in\033[0m: ", x)
                counterf=counterf+1
    if notfound:
        print("\033[91mUNREFERENCED\033[0m: ", f, " not in any manifests")
    else:
        print("\033[92m  REFERENCED\033[0m: ", f, " in above manifests")
    logger.info("Totals in cache: " + str(counterm) + " manifests; " + str(counterf) + " references")
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("lsicmfs partially completed.")
    else:
        logger.info("lsicmfs completed.")

def lsartifacts():
    """List artifacts in cache (and whether they are referenced).

    Looks in the cache directory defined in $HOME/vm_repo_config.yml
    """
    global rht_rc
    global error_summary
    error_summary = ""
    logger = logging.getLogger('vm-usb')
    mfl = config['repository']
    counterm=0
    countera=0
    counterx=0
    logger.info("Listing Artifacts in Local Cache: " + mfl)
    if not os.path.isdir(mfl):
        logger.error(mfl + " as a cache, does not exist.")
        rht_rc = 5
        return
    for f in _natsort(os.listdir(mfl)):
        if f.lower().endswith(".icmf"):
            print("\033[92m    MANIFEST\033[0m: ", f)
            counterm=counterm+1
        else:
            remove = True
            for x in _manifests(mfl):
                try:
                    data_x = _read_manifest(os.path.join(mfl, x))
                except _ManifestValidationException as mfe:
                    logger.error("Manifest " + x + " is invalid.")
                    logger.error(str(mfe))
                    return False
                for artifact_x in data_x['curriculum']['artifacts']:
                    if f == artifact_x['filename']:
                        remove = False
            if remove:
                print("\033[91mUNREFERENCED\033[0m: ", f)
                counterx=counterx+1
            else:
                print("\033[92m  REFERENCED\033[0m: ", f)
                countera=countera+1
    logger.info("Totals in cache: " + str(counterm) + " manifests; " + str(countera) + " artifacts; " + str(counterx) + " orphans")
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("lsartifacts partially completed.")
    else:
        logger.info("lsartifacts completed.")

def list():
    """List manifests available in cache.

    Looks in the cache directory defined in $HOME/vm_repo_config.yml
    """
    global rht_rc
    global error_summary
    error_summary = ""
    logger = logging.getLogger('vm-usb')
    counter=1
    mfl = config['repository']
    logger.info("Listing Local Cache: " + mfl)
    if not os.path.isdir(mfl):
        logger.error(mfl + " as a cache, does not exist.")
        rht_rc = 5
        return
    for mf in _manifests(mfl):
        print("manifest: #%dm %s" % (counter,mf))
        counter=counter+1
    counter=counter-1
    logger.info("Found " + str(counter) + " manifests in cache.")
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("list partially completed.")
    else:
        logger.info("list completed.")

def usblist():
    """List manifests and space available on USB.

    Looks in the manifests/ directory on the USB device.
    Use \"usbvalidate\" to verify all the artifacts on the USB device.
    Assumes an RHTINST formatted device is plugged in.
    """
    global rht_usbmount
    global rht_rc
    global error_summary
    error_summary = ""
    logger = logging.getLogger('vm-usb')
    counter=1
    rht_usbmount=_usbmount()
    if not rht_usbmount:
        return
    mfl=os.path.join(rht_usbmount, "manifests")
    logger.info("Listing USB Mountpoint:" + rht_usbmount)
    if os.path.isdir(mfl):
        for mf in _manifests(mfl):
            print("manifest: #%dm %s" % (counter,mf))
            counter=counter+1
    else:
        logger.warning("USB improperly formatted - missing " + mfl)
        rht_rc = 4
        return
    counter=counter-1
    logger.info("Found " + str(counter) + " manifests on USB.")
    total, used, free = _usbspace()
    logger.info("USB space Total: " + _bytes2human(total) + "  Used: " + _bytes2human(used) + "  Free: " + _bytes2human(free))
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("usblist partially completed.")
    else:
        logger.info("usblist completed.")

def usborphans():
    """List files on USB that are not referenced as artifacts.

    Looks in the manifests/ directory on the USB device.
    """
    global rht_usbmount
    global rht_rc
    global error_summary
    error_summary = ""
    logger = logging.getLogger('vm-usb')
    rht_usbmount=_usbmount()
    if not rht_usbmount:
        return
    mfl=os.path.join(rht_usbmount, "manifests")
    logger.info("Listing Orphans on USB Mountpoint: " + rht_usbmount)
    if not os.path.isdir(mfl):
        logger.error("USB improperly formatted - missing " + mfl)
        rht_rc = 4
        return
    # Generate list of files
    mfsize = dict()
    for dirName, subdirList, fileList in os.walk(rht_usbmount):
        if not dirName.startswith(os.path.join(rht_usbmount, "boot")) and not dirName.startswith(os.path.join(rht_usbmount, "manifests")) and not dirName.startswith(os.path.join(rht_usbmount, "surveys")) and not dirName.startswith(os.path.join(rht_usbmount, "instructor")):
            for fname in fileList:
                f=os.path.join(dirName, fname)
                mfsize[f] = os.path.getsize(f)
    # Step through USB manifests
    usbmanifests = [manifest for manifest in _manifestsall(mfl)]
    if usbmanifests:
        for usbmanifest in usbmanifests:
            logger.debug("Comparing to " + usbmanifest)
            mf = os.path.join(mfl, usbmanifest)
            try:
                data_x = _read_manifest(mf)
            except _ManifestValidationException as mfe:
                logger.error("Manifest " + usbmanifest + " is invalid.")
                logger.error(str(mfe))
                return False
            for f in data_x['curriculum']['artifacts']:
                if f['type'].startswith('content'):
                    thefile = os.path.join(rht_usbmount, f['target directory'], f['filename'])
                    if thefile in mfsize:
                        del mfsize[thefile]
    # Print the orphans
    if mfsize:
        mfsize_totwasted = sum(mfsize.values())
        for f in mfsize:
            fname=f.replace(rht_usbmount + "/", "")
            print(fname + " (" + _bytes2human(mfsize[f]) + ")")
        logger.info("Orphaned total space is " + _bytes2human(mfsize_totwasted))
    else:
        logger.info("There are no orphaned artifacts on USB")
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("lsorphans partially completed.")
    else:
        logger.info("lsorphans completed.")

def usbparttest(destination=None):
    """Test for the USB device with the RHTINST.
    """
    global rht_usbmount
    global rht_usbparts
    global rht_rc
    global error_summary
    error_summary = ""
    logger = logging.getLogger('vm-usb')
    _usbpartitions(destination)
    logger.info("Device name     : " + rht_usbparts["diskName"])
    logger.info("Partition Style : " + rht_usbparts["partStyle"])
    logger.info("RHTINST partname: " + rht_usbparts["partRHTINST"])
    logger.info("ESP     partname: " + rht_usbparts["partESP"])
    logger.info("Boot    partname: " + rht_usbparts["partBoot"])
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("usbparttest partially completed.")
    else:
        logger.info("usbparttest completed.")

def f0list():
    """List manifests deployed on foundation0.

    Looks in the /content/manifests/ directory.
    """
    global rht_rc
    global error_summary
    error_summary = ""
    logger = logging.getLogger('vm-usb')
    counter=0
    mfl = os.path.join(rht_kioskdir,"manifests")
    logger.info("Listing deployed manifests: " + mfl)
    if not os.path.isdir(mfl):
        logger.error(mfl + " directory does not exist.")
        rht_rc = 3
        return
    for mf in _manifests(mfl):
        counter=counter+1
        if mf.startswith("RHCI"):
            print("Infrastructure : " + mf)
        else:
            print("Active course  : " + mf)
    for mf in _manifestsquiesced(mfl):
        counter=counter+1
        print("Quiesced course: " + mf)
    logger.info("Found " + str(counter) + " manifests deployed.")
    if error_summary:
        error_summary = "List of errors that may need help:" + error_summary
        logger.error(error_summary)
        logger.debug(error_summary)
        logger.error("f0list partially completed.")
    else:
        logger.info("f0list completed.")

def version():
    """Show the vm-usb version number."""
    logger = logging.getLogger('vm-usb')
    myversion="SUBRELEASESTRING"
    if "STRING" in myversion:
        myversion="9.0-1.rUNKNOWN"
    logger.info("vm-usb.py " + myversion)

def help(command=None):
    """Display help."""
    mymethods = _methods()
    if command in mymethods:
        print(command.upper())
        print(getattr(sys.modules[__name__],command).__doc__)
    else:
        print(sys.modules[__name__].__doc__)
        print("VERBS")
        _info(sys.modules[__name__])
        print("")
        print(" For detailed help on a verb, type \"help <verb>\"")

def exit():
    """Get out of the interactive shell."""
    global rht_rc
    # exit is a valid command with no error
    rht_rc = 0
    raise EOFError

def config_create():
    """Create the vm_repo_config.yml configuration file in the user's home directory."""
    global alwaysyes
    logger = logging.getLogger('vm-usb')
    # Hunt for home directory
    myuser = os.getenv("SUDO_USER")
    if not myuser:
        myuser = os.getenv("USER")
        if not myuser:
            myuser = "root"
    myhome = os.path.expanduser("~" + myuser)
    fn = os.path.join(myhome, "vm_repo_config.yml")
    logger.info("Creating configuration file: " + fn)
    
    # Check if config file already exists
    if os.path.exists(fn):
        logger.warning("Configuration file already exists: " + fn)
        msg = "Overwrite existing configuration file"
        confirm = True if alwaysyes or input("%s (y/N) " % msg).lower() == 'y' else False
        if not confirm:
            logger.info("Configuration creation cancelled")
            return False
    
    # Create default configuration
    config = { 'repository': os.path.join(myhome, "vm_repository") }
    
    # Create repository directory if it doesn't exist
    if not os.path.exists(config['repository']):
        try:
            os.makedirs(config['repository'])
            logger.info("Created repository directory: " + config['repository'])
        except OSError as e:
            logger.error("Failed to create repository directory: " + str(e))
            return False
    
    # Write configuration file
    try:
        with open(fn, 'w') as fp:
            yaml.dump(config, fp, default_flow_style=False, explicit_start=True)
        logger.info("Successfully created configuration file: " + fn)
        logger.info("Repository directory: " + config['repository'])
        return True
    except IOError as e:
        logger.error("Failed to create configuration file: " + str(e))
        return False

def load_manifest(manifestFilename):
    """Load artifacts from a YAML manifest file to their target directories.
    
    This function reads the specified .yml manifest file from the repository cache,
    creates the target directories if they don't exist, and copies all artifacts
    from the cache to their respective target directories.
    
    Specify the .yml manifest file found in the cache (use \"list\" to see
    what is available to load from the cache).
    """
    global rht_rc
    global config
    logger = logging.getLogger('vm-usb')
    
    # Get the repository cache directory
    rht_cachedir = config['repository']
    
    # Build the full path to the manifest file
    manifestPath = os.path.join(rht_cachedir, manifestFilename)
    
    logger.info("Loading manifest: " + manifestFilename)
    logger.debug("Manifest path: " + manifestPath)
    
    # Check if manifest file exists
    if not os.path.isfile(manifestPath):
        logger.error("Manifest file not found: " + manifestPath)
        rht_rc = 1
        return
    
    # Check if it's a .yml file
    if not manifestFilename.lower().endswith('.yml'):
        logger.error("Manifest file must have .yml extension: " + manifestFilename)
        rht_rc = 1
        return
    
    # Parse the YAML manifest file
    try:
        with open(manifestPath, 'r') as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)
    except yaml.YAMLError as e:
        logger.error("Error parsing YAML manifest: " + str(e))
        rht_rc = 2
        return
    except IOError as e:
        logger.error("Cannot read manifest file: " + str(e))
        rht_rc = 3
        return
    
    # Validate the manifest structure
    if not isinstance(data, dict) or 'name' not in data:
        logger.error("Invalid manifest format: missing 'name' field")
        rht_rc = 2
        return
    
    # Get the course name for logging
    course_name = data.get('name', 'Unknown')
    logger.info("Processing course: " + course_name)
    
    # Get the list of files from the 'files' key
    files_list = data.get('files', [])
    
    if not files_list:
        logger.error("No 'files' section found in manifest")
        rht_rc = 2
        return
    
    # Process each file
    artifacts_processed = 0
    artifacts_skipped = 0
    
    for file_entry in files_list:
        if not isinstance(file_entry, dict) or 'filename' not in file_entry:
            logger.debug("Skipping invalid file entry: " + str(file_entry))
            artifacts_skipped += 1
            continue
        
        filename = file_entry['filename']
        target_dir = file_entry.get('target_directory', '/content')
        
        # Use final_name if available, otherwise use original filename
        final_name = file_entry.get('final_name', filename)
        
        logger.info("Processing artifact: " + filename)
        logger.debug("Target directory: " + target_dir)
        if final_name != filename:
            logger.debug("Final name: " + final_name)
        
        # Build source and destination paths
        source_path = os.path.join(rht_cachedir, filename)
        
        # Create target directory if it doesn't exist
        _createdir(target_dir)
        
        # Build destination path using final_name
        destination_path = os.path.join(target_dir, final_name)
        
        # Check if source file exists
        if not os.path.isfile(source_path):
            logger.warning("Source file not found, skipping: " + source_path)
            artifacts_skipped += 1
            continue
        
        # Copy the file
        if final_name != filename:
            logger.info("Copying: " + filename + " -> " + target_dir + "/" + final_name)
        else:
            logger.info("Copying: " + filename + " -> " + target_dir)
        try:
            _rsync(source_path, destination_path)
            artifacts_processed += 1
            if final_name != filename:
                logger.debug("Successfully copied: " + filename + " as " + final_name)
            else:
                logger.debug("Successfully copied: " + filename)
        except Exception as e:
            logger.error("Failed to copy " + filename + ": " + str(e))
            artifacts_skipped += 1
    
    # Summary
    logger.info("Load manifest completed.")
    logger.info("Artifacts processed: " + str(artifacts_processed))
    if artifacts_skipped > 0:
        logger.warning("Artifacts skipped: " + str(artifacts_skipped))
    
    if artifacts_processed == 0:
        logger.error("No artifacts were successfully processed.")
        rht_rc = 4

def _read_config():
    """Read the configuration from the user's home directory."""
    logger = logging.getLogger('vm-usb')
    # Hunt for home directory
    myuser = os.getenv("SUDO_USER")
    if not myuser:
        myuser = os.getenv("USER")
        if not myuser:
            myuser = "root"
    myhome = os.path.expanduser("~" + myuser)
    fn = os.path.join(myhome, "vm_repo_config.yml")
    logger.info("Configuration file: " + fn)
    try:
        fp = open(fn)
    except IOError as e:
        en=e.errno
        if (en == errno.EACCES or en == errno.ENOENT):
            config={ 'repository': os.path.join(myhome, "vm_repository") }
            if not(os.access(config['repository'],os.R_OK)):
                os.makedirs(config['repository'])
            fp = open(fn,'w')
            yaml.dump(config, fp, default_flow_style=False, explicit_start=True)
            fp.close()
            return config
        else:
            raise
    else:
        with fp:
            config=yaml.load(fp, Loader=yaml.SafeLoader)
            fp.close()
            return config

def _info(object):
    """Print methods and doc strings.
    Takes module, class, list, dictionary, or string."""
    # http://www.diveintopython.net/power_of_introspection/index.html#apihelper.divein
    methodList = [method for method in dir(object) if isinstance(getattr(object, method), collectionsAbc.Callable)]
    print("\n".join(["  %-14s %s" %
                     (method,
                      str(getattr(object, method).__doc__).splitlines()[0])
                     for method in methodList if not method.startswith('_')]))

def _methods():
    """List the methods the user might invoke (i.e. those without leading _)"""
    me=sys.modules[__name__]
    return [method for method in dir(me) if isinstance(getattr(me,method), collectionsAbc.Callable) and
            not method.startswith('_')]

def _cltopy(argv):
    """Turn a command line-style instruction into a python method invocation."""
    if type(argv) == str:
        argv=shlex.split(argv)
    if len(argv) == 0:
        return ""
    # check for a valid verb
    try:
        _methods().index(argv[0])
    except ValueError as e:
        raise NotImplementedError

    # Escape backslashes and single quotes
    for x in range(1,len(argv)):
        argv[x]=argv[x].replace("\\","\\\\")
        argv[x]=argv[x].replace("'", "\\'")

    # Produce the command
    if len(argv) == 1:
        return argv[0] + "()"
    else:
        return argv[0]  + "(\'" + "\',\'".join(argv[1::]) + "\')"

def _complete_manifestFilenameOrAll(word,state):
    """tab-complete a partial manifest name, or \"all\"
    """
    if  "all".startswith(word):
        if state == 0:
            return "all"
        else:
            return _complete_manifestFilename(word,state-1)
    else:
        return _complete_manifestFilename(word,state)

def _complete_manifestFilename(word,state):
    """tab-complete a partial manifest name.
    This looks in the repository for manifests starting with the given text"""
    mfpart=word + "*"
    candidates=[f for f in glob.glob(os.path.join(config['repository'],mfpart))
                if f.endswith('.icmf')]
    if (len(candidates)>state):
        return os.path.basename(candidates[state])

def _complete_manifestUSBFilenameOrAll(word,state):
    """tab-complete a partial manifest name, or \"all\"
    """
    if  "all".startswith(word):
        if state == 0:
            return "all"
        else:
            return _complete_manifestUSBFilename(word,state-1)
    else:
        return _complete_manifestUSBFilename(word,state)

def _complete_manifestUSBFilename(word,state):
    """tab-complete a partial manifest name.
    This looks in the manifests directory of the mounted USB for
    manifests starting with the given text"""
    global rht_usbmount
    if not rht_usbmount:
        rht_usbmount = _usbmount()
    mfpart=word + "*"
    candidates=[f for f in glob.glob(os.path.join(rht_usbmount,"manifests",mfpart))
                if f.endswith('.icmf')]
    if (len(candidates)>state):
        return os.path.basename(candidates[state])

def _complete_manifestF0Filename(word,state):
    """tab-complete a partial manifest name.
    This looks in the f0 manifests for manifests starting with the given text"""
    mfpart=word + "*"
    candidates=[f for f in glob.glob(os.path.join(rht_kioskdir,"manifests",mfpart))
                if f.endswith('.icmf')]
    if (len(candidates)>state):
        return os.path.basename(candidates[state])

def _complete_manifestF0quiesced(word,state):
    """tab-complete a partial manifest name.
    This looks in the f0 manifests for manifests starting with the given text"""
    mfpart=word + "*"
    candidates=[f for f in glob.glob(os.path.join(rht_kioskdir,"manifests",mfpart))
                if f.endswith('.icmf_quiesced')]
    if (len(candidates)>state):
        return os.path.basename(candidates[state])

def _complete_manifestF0icmfs(word,state):
    """tab-complete a partial manifest name.
    This looks in the f0 manifests for manifests starting with the given text"""
    mfpart=word + "*"
    candidates=[f for f in glob.glob(os.path.join(rht_kioskdir,"manifests",mfpart))
                if f.endswith('.icmf') or f.endswith('.icmf_quiesced')]
    if (len(candidates)>state):
        return os.path.basename(candidates[state])

def _complete_command(word,state):
    """tab-complete a partial command"""
    possibilities=[method for method in _methods() if method.startswith(word)]
    if (len(possibilities)>state):
        return possibilities[state]

def _get_params(function):
    """Return the parameters taken by the given function."""
    p=[]
    for i in range(0,function.__code__.co_argcount):
        p.append(function.__code__.co_varnames[i])
    return p

def _tab_complete(text, state):
    """Figure out what the user means.

    This is the top-level function for resolving tab completion.  It delegates
    to other functions called _complete_${paramName}(word, state)  where word is
    the last word of the command to be completed, and state is 0,1,2... until
    the options have run out and a non-string is returned.  The function should
    return the completed word.

    If more of the command is needed, it cam be found from
    readline.get_line_buffer()
    """
    lbuffer=readline.get_line_buffer()
    argv=shlex.split(lbuffer)
    if lbuffer.count(' ') == 0:
        return _complete_command(text,state)
    else:
        # see if there's a custom function for completing this part
        me=sys.modules[__name__]
        params=_get_params(getattr(me,argv[0]))
        nextPart=[method for method in dir(me) if isinstance(getattr(me,method), collectionsAbc.Callable) and
            method.startswith('_complete_' + params[lbuffer.count(' ')-1])]
        if len(nextPart) > 0:
            return getattr(me,nextPart[0])(text,state)
        else:
            return _complete__manifest(text,state)

def _noisy_tab_complete(text,state):
    """Tab completion for debugging - showing exceptions"""
    try:
        return _tab_complete(text,state)
    except Exception as e:
        print(str(e))
        raise e

def _exec(cmd):
    """Run the given command, catching errors."""
    try:
        exec(_cltopy(cmd))
    except KeyboardInterrupt as i:
        print("Interrupted.")
    except NotImplementedError as ni:
        print("Command not found.")
        help()
    except IOError as ioe:
        print(str(ioe))
    except TypeError as te:
        if "() takes" in str(te):
            print(te)
            print("Wrong arguments. Check help for the command.")
        elif "() missing" in str(te):
            print(te)
            print("Missing arguments. Check below help for the command.")
            if type(cmd) == str:
                help(cmd.split()[0])
            else:
                help(cmd[0])
        else: 
            raise

def _interact():
    # http://stackoverflow.com/questions/5597836/how-can-i-embedcreate-an-interactive-python-shell-in-my-python-program
    # http://stackoverflow.com/questions/2046050/tab-completion-in-python-command-line-interface-how-to-catch-tab-events#2046054
    logger = logging.getLogger('vm-usb')
    vars = globals().copy()
    vars.update(locals())
    readline.parse_and_bind("tab: complete")
    readline.set_completer_delims(" ")
    readline.set_completer(_tab_complete)
    print("VM Management USB Tool")
    print("  Type \"help\" for help.")
    keepGoing=True
    while keepGoing:
        try:
            todo = input('vm-usb> ')
            logger.debug("COMMAND: " + str(todo))
            _exec(todo)
        except KeyboardInterrupt as e:
            print("\nBye!")
            keepGoing=False
        except EOFError as e:
            print("\nBye!")
            keepGoing=False

def _main(argv):
    """Run vm-usb in interactive mode or single command mode, as requested"""
    global config
    global verbose
    global alwaysyes
    global rht_rc
    os.umask(0o002)
    if '--verbose' in argv:
        verbose=True
        argv.remove('--verbose')
    if '-v' in argv:
        verbose=True
        argv.remove('-v')
    if '--yes' in argv:
        alwaysyes=True
        argv.remove('--yes')
    if '-y' in argv:
        alwaysyes=True
        argv.remove('-y')
    logger = _configure_logging()
    # Confirm we are running this with root privileges
    _checkroot()
    # Read in configuration
    config=_read_config()
    if len(argv) == 1:
        _interact()
    else:
        logger.debug("COMMAND: " + str(sys.argv[1::]))
        _exec(sys.argv[1::])
    # Only attempt to unmount if we did a USB related command
    if rht_usbmount:
        _usbumount()
    # Shutdown logger
    logging.shutdown()
    sys.exit(rht_rc)

if __name__ == "__main__":
   _main(sys.argv)

