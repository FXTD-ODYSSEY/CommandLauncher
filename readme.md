
<h1 style="text-align:center">
Maya CommandLauncher 
</h1>

[中文文档](./readme_zh_CN.md)

This Plugin is inspire by two plugins below 
+ [CommandSearch](http://technicaldirector.nl/projects/command_search/)
+ [quicklauncher](https://github.com/csaez/quicklauncher)

Most of the code structure modified from the commandSearch source code.    
And I also thanks for the Listary5.0 software , some good feature also borrow from it.   

## Install

Install Method also using the module installer method, you could check my other plugin [mpdb](https://github.com/FXTD-ODYSSEY/mpdb) for more detail

1. download the release version of the plugin. (you also can clone the release branch)
2. unzip the folder to any location in your computer.(skip this step if you clone the branch)
3. drag the mpdb.mel to your running Maya viewport.

![alt](img/01.gif)

![alt](img/02.gif)

## How to use

> &emsp;&emsp;When install complete, you can find a search icon on the Maya status line.     
> &emsp;&emsp;After that,you can press Tab Key on the viewport, the search bar will popup.     

### Status Icon

![alt](img/03.png)

> &emsp;&emsp;press the status Icon you can disable the CommandLauncher and Open the setting or Help.     

![alt](img/04.png)

> &emsp;&emsp;When you press the OFF button, the CommandLauncher will delete completely.     
> &emsp;&emsp;And It will log the setting into the json file so that next Maya launch would not enable the CommandLauncher automatically.      

![alt](img/05.png)

> &emsp;&emsp;press the setting button will popup the SettingWindow     

### Search 

> &emsp;&emsp;By Default, when you press the Tab key on the viewport, will launch the search bar.     
> &emsp;&emsp;Then,you can type your keyword to search the command in Maya.     

> &emsp;&emsp;You can use Keyboard to browse the search results.     
> + Use the` Up and Down Arrow` for scrolling.
> + Use the `Left and Right Arrow `for switch to Pin and Option Button.
> + Press `Alt + Num` you can jump to the specific item quickly.
> + Press `Ctrl + Num` you can trigger the specific item quickly.

![alt](img/06.gif)

### Filter Results

![alt](img/11.gif)

> &emsp;&emsp;Press `Ctrl + Q W E R T` Key can switch the filter mode.     

### Pins Sets

> &emsp;&emsp;The search icon on the left can open the menu when you click it.     

![alt](img/07.png)

> &emsp;&emsp;Press the Add Item will popup a input dialog for the sets name you want to add.     
> &emsp;&emsp;Press the Clear Item will clear current active pins sets.     
> &emsp;&emsp;Press the Delete Item will popup a input dialog to select the delete set name.     

![alt](img/08.png)

> &emsp;&emsp;After Pin Set create , when you pin the result item will add to the active Pin Set automatically.     

![alt](img/09.png)

> &emsp;&emsp;By Default, if you active the pin set but nothing input will popup up the pin set result below.     

![alt](img/10.gif)

> + Press `Ctrl + alt + + Num` can switch the top nine Pin Sets swiftly.

### Setting

![alt](img/05.png)

> + Language Mode - switch current plugin text Language
> + Tab Key Enabled - disable or enable the Tab HotKey register
> + scroll start line - Define the line number that the `Up and Down Arrow` Key will scroll the Scroll Bar
> + scroll lock line - Define the line number that the quick shortcut num will display
> + shortcut number - Support How many quick shortcut num
> + item display num - Define How many item will display, if the number is too large, will slow down the search time.

---

> &emsp;&emsp;Here is the code path search setting, which add  `documents / maya / version / scripts` directory by default.         
> &emsp;&emsp;After adding the directory, click Refresh to search the code files under the directory for execution. (both Python and Mel are available).       
> &emsp;&emsp;The first button is used to add a new directory.      
> &emsp;&emsp;The second button is used to refresh the load of the current directory.      
> &emsp;&emsp;The third button is to open the folder where the settings are stored for manual modification.     
