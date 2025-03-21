import matlablib.engine
eng = matlab.engine.start_matlab()
eng.cd(r'myFolder', nargout=0)
eng.myFnc()