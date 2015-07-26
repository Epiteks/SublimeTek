#SublimeTek

SublimeText plugin for Epitech students

##Install

Add [this repo](https://github.com/hug33k/SublimeTek) in Package Control :
__ctrl+shift+p__ > _Package Control: Add repository_

Then install it :
__ctrl+shift+p__ > _Package Control: Install package_ > "SublimeTek"

##Usage

###Method 1 : Command Palette

__ctrl+shift+p__ > "SublimeTek" > Your choice

###Method 2 : Keybinding

Press __ctrl+alt+space__ (Windows / Linux) or __cmd+alt+space__ (OSX) to use Sublime Tek.
(Temporarily, it launch only the "Norme" checker)

##Configuration

You need to configure SublimeTek if you want to use all the features.
The settings file is available by menu : _Preferences_ > _Package Settings_ > _SublimeTek_

Here is an example of configuration :
````json
{
    "login": "YOUR LOGIN",
    "full_name": "YOUR NAME",
    "unix_password": "YOUR UNIX PASSWORD IN SHA512",
    "BLIH":
    {
        "server": "git.epitech.eu",
        "auto_clone": false,
        "rendu_folder": "/home/login_x/rendu",
        "base_location": "/home/login_x",
        "ask_for_folder_at_clone": false,
    }
}
````

##Features

* Norme Checker
    * Header
    * Includes
    * Columns number
    * Lines number
    * Functions number
    * Spaces around keywords
    * Superfluous \n

* BLIH Integration
    * Create repositories
    * Remove repositories
    * Clone repositories
    * ACLs

##TODO

* Norme
    * Header
        * Filename
        * Login
    * Groups
        * Lists of logins (cf BLIH)
    * Lines
        * Spaces at end of lines
        * Indentation Emacs-LIKE

* BLIH
    * Sublime-project configuration file with .gitignore
    * List of logins for project

* Epitech Header

You can ask for features, I'll check feasibility.
