# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 6.2.0
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore

qt_resource_data = b"\
\x00\x00\x01\xff\
i\
mport QtQuick 2.\
11\x0aimport QtQuic\
k.Controls 2.4\x0ai\
mport QtQuick.La\
youts 1.11\x0aimpor\
t QtQml 2.15\x0a\x0aim\
port \x22qrc:/objec\
ts\x22\x0a\x0aApplication\
Window {\x0a    id:\
 application\x0a   \
 width: 820\x0a    \
height: 450\x0a\x0a   \
 maximumHeight: \
height\x0a    maxim\
umWidth: width\x0a\x0a\
    minimumHeigh\
t: height\x0a    mi\
nimumWidth: widt\
h\x0a\x0a    color: St\
yle.slate3\x0a    v\
isible: true\x0a\x0a  \
  Component.onCo\
mpleted: {\x0a     \
   Backend.examp\
leSignal.connect\
(onExampleSignal\
)\x0a    }\x0a\x0a    fun\
ction onExampleS\
ignal() {\x0a      \
  console.log('E\
xample signal fi\
red!')\x0a    }\x0a}\
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
\x00\x00\x01|g\x0aj\x1d\
"

def qInitResources():
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
