# Windows兼容检查

2026-10-27，候选0.7.10。当前没有Windows版星露谷的游戏内启动、音画或保存实测证据。

已确认运行模块为.NET 6、IL-only AnyCPU，未引用macOS专用系统接口。玩家包只包含本模组自有DLL；游戏、SMAPI和MonoGame等程序集由玩家安装的对应Windows版本提供，不随模组分发。本机`.app`和`.command`是macOS启动便利工具，Windows玩家不使用它们，直接把两个模组目录放进SMAPI的Mods目录。

`tests/validate_windows_package.py`检查：Windows文件名、大小写冲突、路径长度、ZIP完整性、两个模组根目录、版本一致、程序集CPU/CLR标志、内容补丁资源和52张TMX图片引用。`.github/workflows/windows-package.yml`还会在真正的Windows runner解压候选ZIP，并读取CLR程序集标识；结果尚待该流程执行。

这些结果属于安装包与程序集兼容性检查，不能据此称Windows游戏运行已经通过。发布说明应继续明确：Windows游戏启动、绘制、音频、输入和存档尚未实机验收；多人模式也未获支持认证。若Windows检查失败，应先修复再公开候选包。
