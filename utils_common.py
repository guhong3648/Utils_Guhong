import os
import glob
import natsort
import numpy as np

def make_dir(path, exist_ok=True):
    if not os.path.exists(path): 
        os.makedirs(path, exist_ok=exist_ok)
        os.chmod(path, 0o777)
        
def globsort(path):
    return natsort.natsorted(glob.glob(path))

def listdir(path):
    return natsort.natsorted(os.listdir(path))

def minMax_scaling(x, lb=0, m=None, M=None):
    if m==None: m = x.min()
    if M==None: M = x.max()
    if lb==0:
        return (x-m)/(M-m)
    if lb==-1:
        return (2*x-(M+m))/(M-m)
