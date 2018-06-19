@echo off

REM For Python 2.7, 3.5, 3.6
call:build_wheel "C:\Python27\python.exe"
call:build_wheel "C:\Program Files\Python35\python.exe"
call:build_wheel python


::--------------------------------------------------------
::-- Build and test a python wheel
::--------------------------------------------------------
:build_wheel

pip=%~1 -m pip
%pip% install pip --upgrade pip --user
%pip% install wheel --user
%pip% install setuptools --user --upgrade
%pip% install numpy --user
%pip% install vtk --user

%~1 %~dp0setup.py bdist_wheel

rem for testing
%pip% uninstall pymeshfix
%~1 %~dp0setup.py install --user
%~1 %~dp0pymeshfix\examples\fix.py
goto:eof
