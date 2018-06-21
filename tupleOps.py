# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 10:08:39 2018

@author: ic_admin
"""
import math as m

def tsum(a, b):
    return tuple(a[i]+b[i] for i in range(len(a)))

def tdiff(a, b):
    return tuple(a[i]-b[i] for i in range(len(a)))

def tmult(a, b, tint=False):
    if tint: return tuple(int(a[i]*b) for i in range(len(a)))
    else: return tuple(a[i]*b for i in range(len(a)))

def tdist(a, b=[]):
    if b: return m.sqrt(sum(tuple((a[i]-b[i])**2 for i in range(len(a)))))
    else: return m.sqrt(sum(tuple((a[i])**2 for i in range(len(a)))))

def tdir(a, b=[], tint=False):
    if b:
        if tint: return tuple(int(tmult(tdiff(b,a),1/tdist(a,b))))
        else: return tuple(tmult(tdiff(b,a),1/tdist(a,b)))
    else:
        if tint: return tuple(int(tmult(a,1/tdist(a))))
        else: return tuple(tmult(a,1/tdist(a)))

def tint(a):
    return tuple(int(a[i]) for i in range(len(a)))

def sign(x):
    return (x > 0) - (x < 0)