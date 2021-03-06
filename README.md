# 二次开发

## 项目准备

* Fork [官方仓库](https://github.com/LLK/scratch-flash) 并配置本地代码

  ```shell
  git clone https://github.com/LLK/scratch-flash.git
  cd scratch-flash
  git remote -v  # 查看本地所有远程 URL 配置
  git remote add upstream https://github.com/LLK/scratch-flash.git  # 添加官方远程 upstream
  git fetch upstream  # 更新代码到官方 upstream 最新版本
  git checkout develop  # 切换到本地默认分支
  git merge upstream/develop  # 将本地 develop 分支与官方（upstream) develop 合并
  git push origin develop  # 推送到自己的 github 仓库
  ```

* 使用 gradle 编译项目(**未配置包含库文件到编译结果中,暂时不建议使用**)
  * 从 [一个逗比](https://www.adobe.com/support/flashplayer/debug_downloads.html)
   下载 `playerglobal_10.2.swc` 和 `playerglobal_11.6.swc` 并放在 `libs/` 下 [附:版本列表](https://helpx.adobe.com/flash-player/kb/archived-flash-player-versions.html)
  * [可选配置] 修改 `build.properties` 中的 `FLEX_HOME` 值为 FlexSDK 安装路径
  * 修改 `scratch.gradle` 文件

    ```gradle
    dependencies {
      flexSDK group: 'org.apache', name: 'apache-flex-sdk', version: '4.15.0', ext: 'zip'
      //external group: 'macromedia.com', name: 'playerglobal', version: playerVersion.replace('.', '_'), ext: 'swc'
      merged files(
        "${commonDir}/libs/playerglobal_${playerVersion}.swc",
        "${commonDir}/libs/as3corelib.swc",
        "${commonDir}/libs/blooddy_crypto.swc",
        "${commonDir}/libs/grabcut.swc"
      )
    }
    ```
    **提示:** 因为逗比收购 Macromedia 后将原网址设置重定向导致无法下载文件,只好通过制定本地文件方式编译.
  * 命令行输入 `./gradlew build` (前提是已安装 `gradle` ,自行百度)

* 使用 Flash Builder 4.7 新建 Flex 并编译项目
  * 项目位置: `项目位置`为原始 scratch-flash 目录; `项目类型`为 web
  * 服务器设置: 无
  * 构建路径: `框架链接`:合并到代码中; 验证 RSL 摘要(建议在生产环境中使用)
  * 新建项目后,会有一个 layout 错误,删掉即可
    ```mxml
    <?xml version="1.0" encoding="utf-8"?>
    <s:Application xmlns:fx="http://ns.adobe.com/mxml/2009"
                   xmlns:s="library://ns.adobe.com/flex/spark"
                   xmlns:mx="library://ns.adobe.com/flex/mx">
    </s:Application>
    ```
  * 修改项目属性: 修改 `项目属性` -> `Flex 编译器` 中的 `编辑器选项`,只需要 `生成可访问的 SWF 文件` 和 `启用严格类型检查`,同时在 `附加的编辑器参数` 中添加编译参数 `-locale zh_CN -swf-version=19 -default-size=1024,768 -define+=SCRATCH::allow3d,false -define+=SCRATCH::revision,'20180101'`
  * 检查构建路径: 确保 `项目属性` -> `Flex 构建路径` -> `框架链接` 设置为 `合并到代码中`,确认输入输出目录.
  * 指定项目构建模块: `src/Scratch.as` 上右键 -> `设置为默认应用程序`

  **提示:** 可取消 `FB 顶部菜单 -> 项目 -> 自动构建` 的勾选状态,加快 FB 响应速度.

* 配置 Flash Builder 4.7 调试

  * [可选] 卸载已安装的 `Flash Player` (非 Debugger 版) [官方教程 Win](https://helpx.adobe.com/flash-player/kb/uninstall-flash-player-windows.html) | [Mac](https://helpx.adobe.com/flash-player/kb/uninstall-flash-player-mac-os.html)
  * 下载 `Flash Player Debugger` 独立版 `flashplayer_29_sa_debug`
  * 解压文件,修改 `FB 首选项` -> `Flash Builder` -> `调试` -> `独立 Adobe Flash Player(调试版本)` 的值指向解压后文件: `/Applications/Flash Player.app`
  * 设置断点,启动调试模式

  **提示 1:** `Error 2060: 安全沙箱冲突:ExternalInterface 调用者 ... 不能访问 ...`  需要设置访问信任: `$HOME/Library/Preferences/Macromedia/Flash\ Player/\#Security/FlashPlayerTrust` 中添加 App 路径 `path_to_bin_bebug/Scratch.swf`

  **提示 2:** `Error: Calling JSeditorReady() failed` 是因为 2.0 使用此方法作为 before_action .可以简单将 `function JSeditorReady() { return true; }` 添加在 `html-template/index.template.html` 中,或者添加其他逻辑.如果要跨域访问,还需要设置 `allowScriptAccess` 为 `always` (原值为 "sameDomain").

## 离线模式

### 舞台大小

修改 `src/Scratch.as` 文件:

```actionscript
  public function presentationModeWasChanged(enterPresentation:Boolean):void {
    ...
    if (isOffline) {
      stage.displayState = enterPresentation ? StageDisplayState.FULL_SCREEN_INTERACTIVE : StageDisplayState.NORMAL;
    }
    ...
  }
```

### 窗口标题

修改 `src/scratch/ScratchStage.as` 文件:

```actionscript
public function updateInfo():void {
  ...
  // 离线模式 ? 舞台全屏 : 正常(小舞台)
  if (Scratch.app.isOffline) {
    info.userAgent = 'Scratch 2.0 Offline Editor'; // 这个不是 swf 范围内,无法动态修改
  }
  ...
}
```

### 工具位置

修改 `src/ui/parts/TopBarPart.as` 文件(最好是根据全局大小计算 x 轴位置):

```actionscript
protected function fixLayout():void {
  ...
  // cursor tool buttons
  var space:int = 3;
  copyTool.x = app.isOffline ? 493 : 427; // 设置工具图标按钮的 x 坐标
  cutTool.x = copyTool.right() + space;
  growTool.x = cutTool.right() + space;
  shrinkTool.x = growTool.right() + space;
  helpTool.x = shrinkTool.right() + space;
  copyTool.y = cutTool.y = shrinkTool.y = growTool.y = helpTool.y = buttonY - 3;
  ...
}
```

### 语言选择

编译结果无 `locale` 目录,需要手动复制.不需要那么多, `zh-cn.po` 和 `lang_list.txt` 就够了.同时还要修改 `lang_list.txt` 中的可用语言列表.

* 设置默认中文 `src/translation/Translator.as`

  ```actionscript
  public static var currentLang:String = 'en'; // 改为 'zh-cn'
  ```

* 设置默认字体大小 `src/translation/Translator.as`

  ```actionscript
  Block.setFonts(10, 9, true, 0); // default font settings
  ```

* 设置首选中文字体 `src/svgeditor/DrawProperties.as`

  ```actionscript
  private static function setFontsFor(lang:String):void {
    ...
    public var fontName:String = 'Helvetica';
    ...
  }
  ```

## 顶部菜单

### 修改颜色

修改 `src/CSS.as`

```actionscript
public static const topBarColor_default:int = 0x9C9EA2;
```

**提示:** 颜色转换规则 `#000000` => `0x000000`, 且必须六位写全.

### 添加菜单项目

### 修改默认格式 *.sb2

* 修改加载项目的文件 `src/scratch/ScratchRuntime.as`

  ```actionscript
  public function selectProjectFile():void {
    ...
      var filter:FileFilter;
      // 选择文件时,过滤文件类型
      if (Scratch.app.isExtensionDevMode) {
        filter = new FileFilter('ScratchX Project', '*.sbx;*.sb;*.sb2');
      } else {
        filter = new FileFilter('Scratch Project', '*.sb2;*.sb');
      }
      Scratch.loadSingleFile(fileLoadHandler, filter);
    }
    ...
  }
  ```

* 修改保存项目的文件 `src/Scratch.as`

  ```actionscript
  public function exportProjectToFile(fromJS:Boolean = false, saveCallback:Function = null):void {
    ...
  }
  ```

## 资源相关

编译结果中未包含 `media/*`, 需要手动复制添加.该目录包含各种图片声音资源和 `README.md`. 可执行 `python download-sprite-media.py` 下载角色和多媒体资源; 执行 `python media/libs/generate-costume-library.py` 下载自定义库.

### 资源加载

官方默认配置使用 CDN 加载资源,导致无法加载.提供两种方案:

* 加载本地资源: 修改 `src/util/Server.as` 中获取资源的三个方法

  ```actionscript
  // 加载图片资源
  public function getAsset(md5:String, whenDone:Function):URLLoader {
    // var url:String = URLs.assetCdnPrefix + URLs.internalAPI + 'asset/' + md5 + '/get/';
    var url:String = 'media/' + md5;
    return serverGet(url, whenDone);
  }
  // 加载声音资源
  public function getMediaLibrary(libraryType:String, whenDone:Function):URLLoader {
    // var url:String = getCdnStaticSiteURL() + 'medialibraries/' + libraryType + 'Library.json';
    var url:String = 'media/libs' + libraryType + 'Library.json';
    return serverGet(url, whenDone);
  }
  // 加载其他资源
  public function getThumbnail(idAndExt:String, w:int, h:int, whenDone:Function):URLLoader {
    // var url:String = getCdnStaticSiteURL() + 'medialibrarythumbnails/' + idAndExt;
    var url:String = 'media/' + idAndExt;
    return downloadThumbnail(url, w, h, whenDone);
  }
  ```

  **注意:** 因为离线版问题,这里并不能马上看到效果.需要将编译结果 Scratch.swf 复制覆盖官方离线版目录中,再从官方图标点开.

* 加载自定义 CDN 资源: 修改 `src/util/Server.as` 中设置 CDN 方法

  ```actionscript
  public function Server() {
    setDefaultURLs(); // 设置默认 URL

    // 接受来自 flash 变量的 URL 重写
    try {
      var urlOverrides:String = Scratch.app.loaderInfo.parameters['urlOverrides'];
      if (urlOverrides) overrideURLs(by.blooddy.crypto.serialization.JSON.decode(urlOverrides));
    } catch (e:*) {
    }
  }

  /**
   * No default URLs
   **/
  protected function setDefaultURLs():void {}

  /**
   * 重写 URL 地址
   **/
  public function overrideURLs(overrides:Object):void {
    var forceProtocol:String;
    var swfURL:String = Scratch.app.loaderInfo.url;
    if (swfURL && URLUtil.isHttpURL(swfURL)) { // "isHttpURL" is true if the protocol is either HTTP or HTTPS
      forceProtocol = URLUtil.getProtocol(swfURL);
    }
    for (var name:String in overrides) {
      if (overrides.hasOwnProperty(name)) {
        var url:String = overrides[name];

        if (forceProtocol && URLUtil.isHttpURL(url)) {
          url = URLUtil.replaceProtocol(url, forceProtocol);
        }

        URLs[name] = url;
      }
    }
  }

  /**
   * 获取 CDN 静态资源 URL
   **/
  protected function getCdnStaticSiteURL():String {
    return URLs.siteCdnPrefix + URLs.staticFiles;
  }
  ```

* 默认角色(官方保留的小猫商标)

  * 利用 Linux 的 grep 命令查找小猫图片所在文件

  ```shell
  $ cd /Applications/Scratch\ 2.app/Contents/Resources/media/libs
  $ grep f88bf1935daea28f8ca098462a31dbb0 *
  > costumeLibrary.json:        "md5": "f88bf1935daea28f8ca098462a31dbb0.svg",
  ```

  * 修改 `src/scratch/ScratchRuntime.as`

    ```actionscript
    public function installEmptyProject():void {
      app.saveForRevert(null, true);
      app.oldWebsiteURL = '';
      installProject(new ScratchStage());
      // 调用 `src/util/ProjectIO.as` 的 `fetchSprite` 方法读取 json 文件加载资源,具体参数参考方法定义;也可以调用 `fetchImage` 方法
      var io:ProjectIO = new ProjectIO(app);
      io.fetchSprite('project.json', addSprite);
    }
    /**
     * 添加角色回调方法
     **/
    private function addSprite(costumeOrSprite:*):void {
      var spr:ScratchSprite;
      var c:ScratchCostume = costumeOrSprite as ScratchCostume;
      // 可使用 "Hello" instanceof String 判断
      if (c) {
        spr = new ScratchSprite(c.costumeName);
        spr.setInitialCostume(c);
        app.addNewSprite(spr);
        return;
      }
      spr = costumeOrSprite as ScratchSprite;
      if (spr) {
        app.addNewSprite(spr);
        return;
      }
      // 添加 sprite 的其他造型
      var list:Array = costumeOrSprite as Array;
      if (list) {
        var sprName:String = list[0].costumeName;
        if (sprName.length > 3) sprName = sprName.slice(0, sprName.length - 2);
        spr = new ScratchSprite(sprName);
        for each (c in list) spr.costumes.push(c);
        if (spr.costumes.length > 1) spr.costumes.shift(); // remove default costume
        spr.showCostumeNamed(list[0].costumeName);
        app.addNewSprite(spr);
      }
    }
    ```

### 添加资源类别

* 将自定义类别添加到 `src/ui/media/MediaLibrary.as` 中

  ```actionscript
  // 角色库 - 分类
  private static const costumeCategories:Array = ['All', 'Animals', 'Fantasy', 'Letters', 'People', 'Things', 'Transportation'];
  // 扩展库 - 分类
  private static const extensionCategories:Array = ['All', 'Hardware'];
  // 声音库 - 分类
  private static const soundCategories:Array = [
    'All', 'Animal', 'Effects', 'Electronic', 'Human', 'Instruments',
    'Music Loops', 'Musical Notes', 'Percussion', 'Vocals'];
  // 背景库 - 分类
  private static const backdropCategories:Array = ['All', 'Indoors', 'Outdoors', 'Other'];
  // 背景库 - 主题
  private static const backdropThemes:Array = ['Castle', 'City', 'Flying', 'Holiday', 'Music and Dance', 'Nature', 'Space', 'Sports', 'Underwater'];
  // 角色库 - 主题
  private static const costumeThemes:Array = ['Castle', 'City', 'Dance', 'Dress-Up', 'Flying', 'Holiday', 'Music', 'Space', 'Sports', 'Underwater', 'Walking'];
  // 角色库 - 类型
  private static const imageTypes:Array = ['All', 'Bitmap', 'Vector'];
  ```

* 可修改资源类型有`sprite`,`sound`,`backdrop`三种,可添加栏目有如下几种:
  * `costumeCategories`   对应:  `角色库 / 分类`
  * `costumeThemes`       对应:  `角色库 / 主题`
  * `imageTypes`          对应:  `角色库 / 类型`
  * `backdropCategories`  对应:  `背景库 / 分类`
  * `backdropThemes`      对应:  `背景库 / 主题`
  * `soundCategories`     对应:  `声音库 / 分类`
  * `extensionCategories` 对应:  `扩展库 / 分类`

* 操作步骤:
  * [可选] 添加栏目
  * 添加资源文件(图片,声音)
  * 资源配置文件中 `media/libs/{sprite,sound,backdrop}Library.json` 中添加自定义资源条目

    ```json
    [{
      "name": "Z-Story",
      "md5": "4a0f2901c77f3b9ef44b61b5e8fc3e68.json",
      "type": "sprite",
      "tags": ["letters", "drawing", "vector"],
      "info": [0, 3, 1]
    }]
    ```

  * 添加资源配置文件 `media/4a0f2901c77f3b9ef44b61b5e8fc3e68.json`

  **提示:** JSON 格式模板为 `{ "name": ResourceDisplayName, "md5": ResourceFileName,   "type": ResourceCategory,  "tags": MountPoint, "info": Array }`.角色 info 使用 `md5.json` 中的 `objName` 值.

  * name 界面显示名称 string
  * md5 真实资源文件名称 md5.json
  * type 资源所属类型 [sprite, sound, backdrop]
  * tags 资源所属栏目 [All, Other]
  * info 资源编号数组

### 添加字体

* 将字体文件复制到 `src/assets/fonts/` 目录中

* 注册字体 `src/assets/Resources.as`

  ```actionscript
  [Embed(source='fonts/WawaSC-Regular.otf', fontName='Wawa', embedAsCFF = 'false', advancedAntiAliasing = 'true')] private static const Font7:Class;
  ```

* 使用字体 `src/svgeditor/DrawPropertyUI.as`

  ```actionscript
  private function makeFontUI():void {
    ...
      m.addItem('Marker');
      m.addItem('Mystery');
      m.addItem('Scratch');
      m.addItem('Wawa'); // 必须是注册的 fontName
      m.showOnStage(Scratch.app.stage);
    }
    ...
  }
  ```

### 添加 / 修改汉化

* 编辑 `locale/zh-cn.po` 文件, 按以下格式添加或修改即可:

  ```yml
  msgid "%b and %b"
  msgstr "%b 与 %b"
  ```

  **提示:** 第一行为程序中需要国际化的字符串(即被替换掉的原字符串,`需要与程序中的字符串完全一致`),第二行为国际化后的字符串(即界面显示字符串).

## 自定义 Block

* 自定义块类型 `src/Specs.as`

  ```actionscript
  public static const categories:Array = [
    // [id, category_name, color]
    [0,  "undefined",   0xD42828],
    [1,  "Motion",      0x4a6cd4],
    [2,  "Looks",       0x8a55d7],
    [3,  "Sound",       0xbb42c3],
    [4,  "Pen",         0x0e9a6c], // Scratch 1.4: 0x009870
    [5,  "Events",      0xc88330],
    [6,  "Control",     0xe1a91a],
    [7,  "Sensing",     0x2ca5e2],
    [8,  "Operators",   0x5cb712],
    [9,  "Data",        variableColor],
    [10, "More Blocks", procedureColor],
    [11, "Parameter",   parameterColor],
    [12, "List",        listColor],
    [20, "Extension",   extensionsColor],
  ];
  ...
  public static var commands:Array = [
    // ["specification", "type", "catalog", "callback", "default(optional)"]
    // type: " " 空字符串表示输入框; "r" 表示文本显示框
    // catalog: 对应父类 ID,即上述数组第一列
    // callback: 回调方法,需要在 Primitives.as 中注册
    // default: 默认值,可选
    ["link to %s", " ", 8, "href", "http://www.baidu.com"],
  ]
  ```

* 添加 / 修改块类型显示 `src/ui/PaletteSelector.as`

  ```actionscript
  private static const categories:Array = [
    'Motion', 'Looks', 'Sound', 'Pen', 'Data', // column 1
    'Events', 'Control', 'Sensing', 'Operators', 'More Blocks']; // column 2
  ...
  private function initCategories():void {
    // (类型)总行数
    const numberOfRows:int = 5;
    ...
  }
  ```

  运动 | 事件

  外观 | 控制

  声音 | 侦测

  画笔 | 运算

  数据 | 更多

* 添加 / 修改 Block 回调事件 `src/primitives/Primitives.as`

  ```actionscript
  import flash.net.URLRequest;
  import flash.net.navigateToURL;
  import mx.utils.URLUtil;
  ...
  public function addPrimsTo(primTable:Dictionary):void {
    ...
    primTable["href"] = function(b:*):* {
      var url:String = interp.arg(b, 0); // 获取 Block 输入参数
      // 也可使用正则表达式判断并添加逻辑
      // var pattern:RegExp = /^w*:\/\//i;
      // var result:Object = pattern.exec(url);
      if (URLUtil.isHttpURL(url)) {
        navigateToURL(new URLRequest(url), "_blank")
      }
    };
    ...
    addOtherPrims(primTable);
  }
  ```

  **注意:** 此处数组 `primTable["href"]` 中的 `"href"` 必须与 `src/Specs.as` 注册时的 `callback` 对应,否则无法调用.[Flex 官方文档 - flash.net.navigateToURL](https://help.adobe.com/en_US/FlashPlatform/reference/actionscript/3/flash/net/package.html#navigateToURL())

## 版本发布

* 导出发行版: `FB 顶部菜单` -> `项目` -> `导出发行版...` -> `确定`

* 覆盖旧文件: `cp $HOME/Workspace/scratch/scratch-flash-develop/bin-release/Scratch.swf /Applications/Scratch\ 2.app/Contents/Resources/`

---

loadSingleGithubURL
默认角色 f88bf1935daea28f8ca098462a31dbb0.svg

## Scratch 2.0 editor and player [![Build Status](https://api.travis-ci.org/LLK/scratch-flash.svg?branch=master)](https://travis-ci.org/LLK/scratch-flash)

### Note: Scratch 2.0 is now in maintenance mode while the team focuses efforts on [Scratch 3.0](https://scratch.mit.edu/developers). While critical issues will be addressed please note that any feature requests or minor issues will not be reviewed until the next major release.

---

This is the open source version of Scratch 2.0 and the core code for the official version found on http://scratch.mit.edu. This code has been released under the GPL version 2 license. Forks can be released under the GPL v2 or any later version of the GPL.

If you're interested in contributing to Scratch, please take a look at the issues on this repository. Two great ways of helping Scratch are by identifying bugs and documenting them as issues, or fixing issues and creating pull requests. When submitting pull requests please be patient -- the Scratch Team is very busy and it can take a while to find time to review them. The organization and class structures can't be radically changed without significant coordination and collaboration from the Scratch Team, so these types of changes should be avoided.

It's been said that the Scratch Team spends about one hour of design discussion for every pixel in Scratch, but some think that estimate is a little low. While we welcome suggestions for new features in our <a href="http://scratch.mit.edu/discuss/1/">suggestions forum</a> (especially ones that come with mockups), we are unlikely to accept PRs with new features that we haven't deeply thought through. Why? Because we have a strong belief in the value of keeping things simple for new users. To learn more about our design philosophy, see this <a href="http://scratch.mit.edu/discuss/post/1576/">forum post<a>, or <a href="http://web.media.mit.edu/~jmaloney/papers/ScratchLangAndEnvironment.pdf">this paper</a>.

### Building

The Scratch 2.0 build process now uses [Gradle](http://gradle.org/) to simplify the process of acquiring dependencies: the necessary Flex SDKs will automatically be downloaded and cached for you. The [Gradle wrapper](https://docs.gradle.org/current/userguide/gradle_wrapper.html) is included in this repository, but you will need a Java Runtime Environment or Java Development Kit in order to run Gradle; you can download either from Oracle's [Java download page](http://www.oracle.com/technetwork/java/javase/downloads/index.html). That page also contains guidance on whether to download the JRE or JDK.

There are two versions of the Scratch 2.0 editor that can be built from this repository. See the following table to determine the appropriate command for each version. When building on Windows, replace `./gradlew` with `.\gradlew`.

Required Flash version | Features | Command
--- | --- | ---
11.6 or above | 3D-accelerated rendering | `./gradlew build -Ptarget=11.6`
10.2 - 11.5 | Compatibility with older Flash (Linux, older OS X, etc.) | `./gradlew build -Ptarget=10.2`

A successful build should look something like this (SDK download information omitted):

```sh
$ ./gradlew build -Ptarget=11.6
Defining custom 'build' task when using the standard Gradle lifecycle plugins has been deprecated and is scheduled to be removed in Gradle 3.0
Target is: 11.6
Commit ID for scratch-flash is: e6df4f4
:copyresources
:compileFlex
WARNING: The -library-path option is being used internally by GradleFx. Alternative: specify the library as a 'merged' Gradle dependendency
:copytestresources
:test
Skipping tests since no tests exist
:build

BUILD SUCCESSFUL

Total time: 13.293 secs
```

Upon completion, you should find your new SWF in the `build` subdirectory.

```sh
$ ls -R build
build:
10.2  11.6

build/10.2:
ScratchFor10.2.swf

build/11.6:
Scratch.swf
```

Please note that the Scratch trademarks (including the Scratch name, logo, Scratch Cat, and Gobo) are property of MIT. For use of these Marks, please see the [Scratch Trademark Policy](http://wiki.scratch.mit.edu/wiki/Scratch_1.4_Source_Code#Scratch_Trademark_Policy).

### Debugging

Here are a few integrated development environments available with Flash debugging support:

* [Intellij IDEA](http://www.jetbrains.com/idea/features/flex_ide.html)
* [Adobe Flash Builder](http://www.adobe.com/products/flash-builder.html)
* [FlashDevelop](http://www.flashdevelop.org/)
* [FDT for Eclipse](http://fdt.powerflasher.com/)

It may be difficult to configure your IDE to use Gradle's cached version of the Flex SDK. To debug the Scratch 2.0 SWF with your own copy of the SDK you will need the [Flex SDK](http://flex.apache.org/) version 4.10+, and [playerglobal.swc files](http://helpx.adobe.com/flash-player/kb/archived-flash-player-versions.html#playerglobal) for Flash Player versions 10.2 and 11.4 added to the Flex SDK.

After downloading ``playerglobal11_4.swc`` and ``playerglobal10_2.swc``, move them to ``<path to flex>/frameworks/libs/player/<version>/playerglobal.swc``. E.g., ``playerglobal11_4.swc`` should be located at ``<path to flex>/frameworks/libs/player/11.4/playerglobal.swc``.

Consult your IDE's documentation to configure it for your newly-constructed copy of the Flex SDK.

If the source is building but the resulting .swf is producing runtime errors, your first course of action should be to download version 4.11 of the Flex SDK and try targeting that. The Apache foundation maintains an [installer](http://flex.apache.org/installer.html) that lets you select a variety of versions.
