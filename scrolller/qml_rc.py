# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 6.2.0
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore

qt_resource_data = b"\
\x00\x00\x01\xea\
i\
mport QtQuick 2.\
11\x0aimport QtQuic\
k.Controls 2.4\x0ai\
mport QtQuick.La\
youts 1.11\x0aimpor\
t QtQml 2.15\x0a\x0a\x0aA\
pplicationWindow\
 {\x0a    id: appli\
cation\x0a    width\
: 820\x0a    height\
: 450\x0a\x0a    maxim\
umHeight: height\
\x0a    maximumWidt\
h: width\x0a\x0a    mi\
nimumHeight: hei\
ght\x0a    minimumW\
idth: width\x0a\x0a   \
 color: \x22transpa\
rent\x22\x0a    visibl\
e: true\x0a\x0a    Com\
ponent.onComplet\
ed: {\x0a        Ba\
ckend.exampleSig\
nal.connect(onEx\
ampleSignal)\x0a   \
 }\x0a\x0a    function\
 onExampleSignal\
() {\x0a        con\
sole.log('Exampl\
e signal fired!'\
)\x0a    }\x0a}\
"

qt_resource_name = b"\
\x00\x07\
\x0e\xbcX\xfc\
\x00g\
\x00u\x00i\x00.\x00q\x00m\x00l\
"

qt_resource_struct = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
\x00\x00\x01|gm\x1dh\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
