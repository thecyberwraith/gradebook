# Gradebook

This program is a collection of Python 3 scripts that operate together to
manage grading information shared by Virginia Tech's Hokie Spa, Cengage's
WebAssign, and the Canvas systems.

## Installation

The entry script is currently 'gradebook.py', and it has a Bash header line. To
utilize this script efficiently, add a symbolic link to 'gradebook.py' to your
bin directory. In the example folder is a 'config.ini' file. Make a copy of
this file and place it where you wish. Then, either create an environment
variable 'GRADEBOOK_CONFIG_FILE' or execute the program locally to your
'config.ini' file. As long as your 'config.ini' has a base directory pointed
correctly, then the program should work! To begin, execute

'gradebook init'

to create the necessary files.
