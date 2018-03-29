# 笔记

**修改 `Scratch.as` 中的 isOffline = false 会只显示 stage 舞台。**

## 二次开发

---

### 项目准备

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

* 使用 gradle 编译项目(**未配置包含库文件到编译结果中,暂时不建议使用**)
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
  * 指定项目构建模块: 修改 `项目属性` -> `Flex 模块` -> `添加`, 修改 `源代码` 指向 `src/Scratch.as`, 输出大小选择 `不优化` 即可(非 AS 开发者,未掌握优化配置).

  **提示:** 可取消 `FB 顶部菜单 -> 项目 -> 自动构建` 的勾选状态,加快 FB 响应速度.

---

### 修改顶部菜单

#### 修改颜色

```actionscript
// 修改 src/CSS.as 中的 topBarColor 默认值即可改变颜色
public static const topBarColor_default:int = 0x9C9EA2;
```

**提示:** 颜色转换规则 `#000000` => `0x000000`, 且必须六位写全.

### 资源加载

官方默认配置使用 CDN 加载资源,导致无法加载.提供两种方案:

* 加载本地资源: 修改 `src/util/Server.as` 中获取资源的三个方法

  ```actionscript
  // 加载图片资源
  public function getAsset(md5:String, whenDone:Function):URLLoader {
    var url:String = URLs.assetCdnPrefix + URLs.internalAPI + 'asset/' + md5 + '/get/';
    return serverGet(url, whenDone);
  }
  // 加载声音资源
  public function getMediaLibrary(libraryType:String, whenDone:Function):URLLoader {
    var url:String = getCdnStaticSiteURL() + 'medialibraries/' + libraryType + 'Library.json';
    return serverGet(url, whenDone);
  }
  // 加载其他资源
  public function getThumbnail(idAndExt:String, w:int, h:int, whenDone:Function):URLLoader {
    var url:String = getCdnStaticSiteURL() + 'medialibrarythumbnails/' + idAndExt;
    return downloadThumbnail(url, w, h, whenDone);
  }
  ```

* 加载自定义 CDN 资源: 修改 `src/util/Server.as` 中设置 CDN 方法

  ```actionscript
  protected function getCdnStaticSiteURL():String {
    return URLs.siteCdnPrefix + URLs.staticFiles;
  }
  ```

### 发布版本

`FB 顶部菜单` -> `项目` -> `导出发行版...` -> `确定` 即可导出自己的 scratch.swf



---

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
