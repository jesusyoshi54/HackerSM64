import struct
import functools
import TE_defs as t
import sys
import importlib as IL
from pathlib import Path

a = lambda s: functools.partial(pack_pass,s)

def pack_pass(s,b):
	if type(b) == str:
		return b
	else:
		return struct.pack(s,b)

Types = "bBhHlLf"
for c in Types:
	globals()[c] = a(">%s"%c)
def p(x):
	global Place
	global Ptrs
	Ptrs.append(str(x))
	return H(Place)+H(len(Ptrs)-1)
def z(args):
	res=b''
	for a in args:
		res+=p(a)
	return res
def Pack(MSB,VAR):
	b = bytes()
	s = ''
	L = 0 #length of bytes
	for v in VAR:
		if type(v) == str:
			L += 1
			if b:
				s += SF(b.hex()) + f",{v}"
				b = bytes()
			else:
				s += v
		else:
			b += v
			L += len(v)
	return (f"{SF(MSB.hex())}{','*(len(s)>0 or len(b)>0)}{s}{','*(len(s)>0 and len(b)>0)}{SF(b.hex())}",len(MSB)+L)
def Ret(Funcs,MSB,*args):
	if type(MSB)==int:
		return Pack(bytes([MSB]),[l(b) for l,b in zip(Funcs,args)])
	else:
		return Pack(bytes(MSB),[l(b) for l,b in zip(Funcs,args)])
def Make(MSB,*Funcs):
	return functools.partial(Ret,[*Funcs],MSB)
def SF(s):
	a = ['0x'+(s[i:i+2]) for i in range(0, len(s), 2)]
	return ','.join(a)
Funcs = {
	'SetSpd':(0x40,h),
	'SetSfx':(0x41,H),
	'SetEnv':(0x42,B,B,B,B),
	'UsrStr':(0x43,B),
	'SetScissor':(0x44,H,H,H,H),
	'SetRainbow':(0x46,H),
	'SetOrigin':(0x47,H,H),
	'Jump':(0x48,p),
	'TransOffs':(0x49,h,h),
	'TransAbs':(0x4A,h,h),
	#needs editing
	'PopTransform':(0x4B,),
	'FFSpd':(0x4c,h),
	'NoFFSpd':(0x4D,),
	'ResetKeyboard':(0x4E,),
	'StartKeyboard':(0x4F,B),
	'AutoNextBox':(0x70,),
	'AbtnNextBox':(0x71,),
	'Blank':(0x72,H),
	'BtnBranchOpen':(0x73,H),
	'Pause':(0x74,H),
	'BtnBranchClose':(0x75,),
	'EnBlip':(0x76,),
	'DisBlip':(0x77,),
	'PersistMusic':(0x78,),
	'PlayMusic':(0x79,B),
	'ClearBuffer':(0x7A,),
	'AbtnEndStr':(0x7B,),
	'TimeEndStr':(0x7C,H),
	'MosaicBGBox':(0x7D,H,H,H,H,p,B,B),
	#needs editing
	'PrintDL':([0x7E,255,255],B,p,z),
	'ShadedBGBox':(0x7F,H,H,H,H,B,B,B,B),
	'TexBGBox':(0x80,H,H,H,H,p),
	#needs editing
	'PushTransform':([0x81,255,255],z),
	'SetCutscene':(0x82,B),
	'Pad':(0x83,),
	'ScaleText':(0x84,f,f),
	'DialogOptions':(0x85,B),
	'DialogResponse':(0x86,B),
	'GenericText':(0x87,),
	'ScreenShake':(0x88,B),
	#Camera Cmds
	'TriggerWarp':(0x8F,H,B),
	'StartGenBracket':(0x93,B),
	'EndGenBracket':(0x94,B),
	'StartDialogBracket':(0x95,B),
	'EndDialogBracket':(0x96,B),
	'SetRtrn':(0x97,B),
	'GotoRtrn':(0x98,B),
	'ShadowText':(0x99,B),
	'WobbleText':(0x9A,B),
	'EndTransition':(0x9B,B,B,B,B),
	'StartTransition':(0x9C,B,B,B,B),
	'CallOnce':(0xA0,B,p,B,z),
	'CallLoop':(0xA1,B,p,B,z),
	'MatchRtrn':(0xA2,B,l),
	'MarioAction':(0xA6,p),
	'BoxTransition':(0xAA,h,h,h,h),
	'JumpLink':(0xAC,p),
	'Pop':(0xAD,),
	'ShakeText':(0xAE,B),
	'WordWrap':(0xB0,H),
	'PrintGlyph':(0xAF,p),
}
def FindEnd(string):
	cnt=0
	x=0
	start=0
	if '[' not in string:
		return None
	for c in string:
		if '[' in c:
			cnt+=1
			start=1
		if ']' in c:
			cnt-=1
		if cnt==0 and start:
			break
		x+=1
	return x

def Write(out,header,Test,name):
	global Place
	global Ptrs
	E='char %s[] = {\n'%name
	Z = 'u32 *%s[] = {\n'%(name+'_ptrlist')
	cmt = "/* %s interpreted string\n"%name
	header.write('extern char %s[];\n'%name)
	for cmd in Test:
		iter=0
		while(iter<len(cmd)):
			if '[' in cmd[iter]:
				c=FindEnd(cmd[iter:])+iter
				if c>0:
					try:
						q = cmd[iter+1:c]
						Ecmd,chars=eval(q)
						cmt+=' '+q
						Place+=chars
						E+=(Ecmd+',')
						iter+=len(q)+2
					except:
						q = cmd[iter:c+1]
						Q=t.Ascii.get(q)
						if Q:
							cmt+= cmd[iter+1:c]
							Q+=','
							E+=Q
							Place+=1
						iter+=len(q)
				else:
					Q=t.Ascii.get(cmd[iter],'0x9e')+','
					cmt+=cmd[iter]
					E+=Q
					Place+=1
					iter+=1
			else:
				Q=t.Ascii.get(cmd[iter],'0x9e')
				if Q:
					Q+=','
					cmt+=cmd[iter]
					E+=Q
					Place+=1
				iter+=1
	if E[-1] == ',':
		E = E[:-1]+"\n};\n"
	if Ptrs:
		Z+= ','.join(Ptrs)
		o.write(Z + '\n};\n')
		o.write("u32 *%s = &%s;\n"%(name+'_ptrptr',name+'_ptrlist'))
	o.write(E)
	o.write(cmt+'*/\n')

if __name__ == "__main__":
	global Place
	global Ptrs
	Ptrs = []
	Place = 0
	f = sys.argv[1:-1]
	o = sys.argv[-1]
	z=''
	for file in f:
		q = 'build/us_n64' / Path(file)
		if q==Path(o):
			z = file
		else:
			#try ido build path (need to potentially edit to support other platforms??)
			q = 'build/us_ido' / Path(file)
			if q==Path(o):
				z = file
	if not z:
		print(z,f,"bad")
		raise 'no output'
	else:
		f = z
		q = Path(f).stem
		r = Path(sys.path[0]).parent / Path(f).parent
		sys.path.append(str(r))
		f = IL.import_module(q)
		h = o.replace('.py','.h')
		head = '#include "%s"\n'%h
		h = open(h,'w')
		o = open(o,'w')
		o.write(head)
		for k,v in Funcs.items():
			globals()[k] = Make(*v)
		s = [a for a in f.__dict__ if type(a) == str and '__' not in a]
		s = [[f.__dict__.get(a),a] for a in s]
		h.write('#include "src/game/text_engine.h"\n')
		for a in s:
			if a[1]=='externs':
				[h.write(b+'\n') for b in a[0]]
			elif a[1]=='headers':
				[o.write(b+'\n') for b in a[0]]
			elif type(a[0])==list or type(a[0])==tuple and a[0]:
				Place = 0
				Ptrs = []
				Write(o,h,*a)