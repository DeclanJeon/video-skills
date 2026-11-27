# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///
import os,resource,sys
resource.setrlimit(resource.RLIMIT_CPU,(60,62))
resource.setrlimit(resource.RLIMIT_AS,(8589934592,8589934592))
resource.setrlimit(resource.RLIMIT_FSIZE,(536870912,536870912))
os.execv(sys.argv[1],sys.argv[1:])
