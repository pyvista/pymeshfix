rem @echo off

REM For Python 2.7, 3.5, 3.6
call:build_wheel "C:\Python27\python.exe"
call:build_wheel "C:\Program Files\Python35\python.exe"
call:build_wheel python

goto:eof

::--------------------------------------------------------
::-- Build and test a python wheel
::--------------------------------------------------------
:build_wheel

"%~1" -m pip install pip --upgrade pip --user -q
"%~1" -m pip install wheel --user -q
"%~1" -m pip install setuptools --user --upgrade -q
"%~1" -m pip install numpy --user -q
"%~1" -m pip install vtk --user -q

"%~1" %~dp0setup.py -q bdist_wheel

rem for testing
"%~1" -m pip uninstall pymeshfix
"%~1" %~dp0setup.py -q install --user
"%~1" %~dp0pymeshfix\examples\fix.py
goto:eof
