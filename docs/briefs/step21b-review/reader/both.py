#!/usr/bin/env python3
"""The independent review of step 21b: one program under perl 5.42 and under
the compiler, each in a directory of its own, made fresh, that holds the
same files; stdout, stderr, the exit status and every file left behind are
compared. Both get at most 256 open files, 30 seconds of processor and
8 MB a file written (T131). `drive.py` runs a file of cases through this.

    python3 docs/briefs/step21b-review/reader/both.py < programs

reads programs from stdin, `====` on a line of its own between two (each
the body, `use v5.42;` put before it), and shows what each side did.
`CURLY_ROOT` names another tree's compiler (the one before a mend)."""
import os, sys, subprocess, shutil, hashlib
HERE=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..','..'))
ROOT=os.environ.get('CURLY_ROOT',HERE); PERL=os.environ.get('CURLY_PERL','/opt/perl-5.42/bin/perl')
S=os.path.join(HERE,'build','review21b'); os.makedirs(S,exist_ok=True)
import threading
LOCK=threading.Lock(); COUNT=0
FILES={'in.txt': b'a\nb\nc\n', 'nonl.txt': b'x\ny', 'empty.txt': b'', 'zero.txt': b'1\n0'}
def limits():
    import resource
    resource.setrlimit(resource.RLIMIT_NOFILE,(256,256))
    resource.setrlimit(resource.RLIMIT_FSIZE,(8<<20,8<<20))
    resource.setrlimit(resource.RLIMIT_CPU,(30,30))
def tree(d):
    out={}
    for r,ds,fs in os.walk(d):
        for f in fs:
            p=os.path.join(r,f); out[os.path.relpath(p,d)]=open(p,'rb').read()
    return out
def both(body, stdin=b'', files=None, env=None, pre='use v5.42;\n', stress=True):
    src=pre+body+('\n' if not body.endswith('\n') else '')
    h=hashlib.sha1(src.encode()).hexdigest()[:12]
    with LOCK:
        global COUNT; COUNT += 1; h += '-%d-%d' % (os.getpid(), COUNT)
    w=os.path.join(S,'w',h); shutil.rmtree(w,ignore_errors=True); os.makedirs(w)
    pl=os.path.join(w,'p.pl'); open(pl,'w').write(src)
    fl=dict(FILES); fl.update(files or {})
    res={}
    ce=dict(os.environ); ce['CURLY_RT_OBJ']=os.path.join(S,'rt-old.o' if 'CURLY_ROOT' in os.environ else 'rt.o')
    c=subprocess.run(['node',ROOT+'/bin/curlyc.ts','-o',os.path.join(w,'bin'),pl],capture_output=True,env=ce)
    for who in ('perl','ours'):
        d=os.path.join(w,who); os.makedirs(d)
        for f,data in fl.items():
            p=os.path.join(d,f); os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'wb').write(data)
        e={'PATH':'/usr/bin:/bin'}
        if stress: e.update(CURLY_GC_STRESS='1',CURLY_GC_POISON='1')
        e.update(env or {})
        if who=='ours' and c.returncode!=0:
            res[who]=('refused' if c.returncode==1 else 'COMPILER', c.stderr); continue
        cmd=[PERL,pl] if who=='perl' else [os.path.join(w,'bin')]
        try:
            # (stdout and stderr to files with a limit on their size and on the processor's time: T131.)
            so=os.path.join(w,who+'.out'); se=os.path.join(w,who+'.err')
            with open(so,'wb') as fo, open(se,'wb') as fe:
                r=subprocess.run(cmd,input=stdin,stdout=fo,stderr=fe,env=e,cwd=d,timeout=120,preexec_fn=limits)
            if r.returncode in (-25,-24,-9): res[who]=('TIMEOUT',)
            else: res[who]=(r.returncode,open(so,'rb').read(),open(se,'rb').read(),tree(d))
        except subprocess.TimeoutExpired:
            res[who]=('TIMEOUT',)
    P,C=res['perl'],res['ours']
    if C[0] in ('refused','COMPILER'): v=C[0]
    elif C[0]==1 and b'fault: ' in C[2]: v='fault'
    elif P==C: v='same'
    else: v='WRONG'
    shutil.rmtree(w,ignore_errors=True)
    return v,P,C,src
if __name__=='__main__':
    progs=sys.stdin.read().split('\n====\n')
    for body in progs:
        v,P,C,src=both(body)
        print('###',v); print(body.strip())
        if v in('refused','COMPILER'): print('  perl:',P[:3]); print('  ours:',C[1].decode()[-300:])
        elif v=='fault': print('  perl:',P[:3]); print('  ours:',C[:3])
        elif v=='WRONG':
            print('  perl:',P); print('  ours:',C)
        else: print('  both:',P[:3])
