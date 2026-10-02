# 星界战士 BD 选择 Mod

**1.0.0-beta.1 · Steam Windows PC · 游戏版本 2.6.4**

## 下载 / Download

**[下载完整安装包 / Download Mod ZIP（62.4 MB）](https://github.com/boyl/astral-ascent-bd-mod/releases/download/v1.0.0-beta.1/AstralAscent-BD-Mod-v1.0.0-beta.1.zip)**

[发布说明与校验文件 / Release notes and checksums](https://github.com/boyl/astral-ascent-bd-mod/releases/tag/v1.0.0-beta.1)。当前为预发布版；请下载上述安装包，GitHub 的 `Source code` 压缩包不能直接安装。

[English instructions](README.en.md)

支持立即装配构筑、光环自选、保存光环方案、手柄操作及中英文切换。一个安装包包含两种语言，光环名称与效果取自游戏对应语言的数据。

## 安装和使用

1. 需要 [PowerShell 7](https://learn.microsoft.com/zh-cn/powershell/scripting/install/installing-powershell-on-windows)。包内已带 Python 和 Frida，无需另装 Python。
2. 退出游戏，完整解压发布 ZIP，在 `astral-bd` 内运行 `INSTALL.cmd`。
3. 以后从 Steam、快捷方式或游戏 EXE 正常启动即可自动加载。
4. 按 **F8** 或手柄 **Back＋Start** 打开。顶部 **Language / 语言** 切换中英文，选择会保留；BD 或方案页手柄 **Y** 切语言。

| 页面 | 操作 |
|---|---|
| BD 构筑 | 选择成型或成长模式并立即装配；选择保留为之后新局的默认配方 |
| 光环自选 | 按品质和元素筛选 355 项光环，查看效果，指定五槽之一立即装备或清空；允许重复 |
| 光环方案 | 保存当前五槽（含空槽），在列表中选择后立即应用；保留当前法术与符文 |

成型模式替换一号玩家五个光环、四个法术及配方符文。多数配方只开放首槽；3D 猎人四个法术各有完整四槽配套符文。成长模式立即装备法术，之后按房间推进分四次领取核心符文、两件光环、三件光环、剩余核心符文；未领补给保留，需要足够空光环槽。

手柄：LB/RB 切三页，上下或左摇杆选择，LT/RT 跳八项，A 应用，B 收起。BD 页 X 领补给；光环页 X 切元素、Y 清槽、右摇杆按下切品质、左摇杆按下重置筛选；方案页 X 保存。方案名称留空自动命名，同名另存。

12 套配方包含导弹冰剑、雪花冰碎片、雷云、低费连放、**3D 猎人（标记冰剑）**等。社区来源见 `recipes.json`；本版不将社区 T0 评价当作全配方强度实测结论。

## 存档与卸载

装备写入沿用原版检查点；大厅和起始平台装备即时刷新，进入有检查点的房间后保存。续局使用原版“保存进度并退出”，不重新覆盖装备。

用户配置放在 `%LOCALAPPDATA%\AstralAscentBD`。`aura-plans.json` 保存光环方案，`profile.json` 保存默认构筑和成长进度，`ui-settings.json` 保存语言。更新与卸载保留这些文件及原版存档。

更新时退出游戏，再运行新版 `INSTALL.cmd`。卸载时退出游戏，运行 `UNINSTALL.cmd`。“关闭 Mod”停止后续自动发放，原生装备保留。

## 支持范围

仅支持已核对指纹的 Steam Windows x64 2.6.4；其他版本清晰报错。目标为一号玩家，双人、全部角色与解锁组合、Proton 和其他平台尚未完整认证。本版使用原生挂钩和 D3D11，不属于 A2M2 外观替换包；**创意工坊订阅不能自动安装原生加载器，仍需手动安装**。

游戏 EXE、存档和个人方案不包含在公开包内。安装检测到其他来源的 `version.dll` 会停止覆盖。第三方依赖保留各自许可证；游戏名称与效果文案归原权利人。

本次新增验证包括中英文目录 ID 一致、两种语言 D3D 界面和手柄操作。界面自动测试与真实游戏装备验证分开记录。
