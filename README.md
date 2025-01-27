# philosopher.koplugin

## English 
This is a plugin for KOReader that displays random text from a json file on mobile devices.

It works similarly to hitokoto (一言), randomly showing sentences and their sources. The data is sourced from hitokoto as well. However, this plugin is specifically designed for KOReader.

If you want to customize the displayed sentences, you can modify the contents of the data.json file.

The default directory of this plugin is suitable for Kobo devices, but you can modify it to fit your own device.

Tip: https://github.com/hitokoto-osc/sentences-bundle/

Above is the hitokoto library, from which you can download the latest sentences. Copy the merge_json.py file into the sentences folder you downloaded, then run merge_json.py on your PC. Follow the prompts and place the final generated file in the plugin folder (it's just merging files). You can choose a few categories you like and delete the rest before running the script (I can't add category selection, so it's done this way). If the data.json file is too large, it may cause lag.

## 中文
这是一个针对 KOReader 的插件，实现在移动设备上随机显示来自 json 文件的文本。

其效果类似于 hitokoto（一言），随机显示句子和来源。其数据也来自 hitokoto。不过，这个插件专为 KOReader 设计。

*如果你想自定义输出的句子，可以修改 data.json 文件的内容。

*重要：这个插件的默认目录适用于 kobo 设备，你可以自行修改以适配你的设备。

提示： https://github.com/hitokoto-osc/sentences-bundle/ 

以上是一言库，你可以从中下载最新一言。将 merge_json.py 复制到你下载的 sentences 文件夹中，然后在PC上运行 merge_json.py ，根据提示，把最终生成的文件放到插件文件夹中：（其实就只是合并一下），你可以选择你喜欢的几个类别，把余下的删除再运行这个脚本（太菜了做不出类别选择只能这样），如果 data.json 过大可能会导致卡顿。

## Supported formats

|   formats    |    date   |
|:------------:|:---------:|
|&#x2611; json  | 2025/01/26 |

## License
GPL v3