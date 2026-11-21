import { useState } from 'react';
import { DOWNLOAD, GUIDE, type Lang } from './content';

const paths = {
  windows: 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\Stardew Valley\\Mods',
  mac: '~/Library/Application Support/Steam/steamapps/common/Stardew Valley/Contents/MacOS/Mods',
  linux: '~/.local/share/Steam/steamapps/common/Stardew Valley/Mods',
};

export default function InstallGuide({ lang }: { lang: Lang }) {
  const en = lang === 'en', t = (zh: string, english: string) => en ? english : zh;
  const [os, setOs] = useState<keyof typeof paths>('windows');
  const [copied, setCopied] = useState(false);
  const [checked, setChecked] = useState<number[]>([]);
  const steps = [
    [t('准备游戏与备份', 'Your game & a backup'), t('需要电脑端《星露谷物语》1.6.15 或以上版本，单人游玩。退出游戏，先复制一份存档备份。手机和主机版不适用。', 'You need desktop Stardew Valley 1.6.15 or newer, in single player. Exit the game and back up your save. Mobile and consoles are not supported.')],
    [t('安装两项前置', 'Install two prerequisites'), t('安装与游戏版本兼容的 SMAPI，再把 ContentPatcher 文件夹放入 Mods。', 'Install a game-compatible SMAPI, then place the ContentPatcher folder in Mods.')],
    [t('放入两个模组文件夹', 'Place both mod folders'), t('下载 install.zip 玩家包，解压后，把 ArcticPassage 与 ArcticPassage.Runtime 一起放进 Mods。', 'Download the install.zip player package. Extract ArcticPassage and ArcticPassage.Runtime into Mods together. ')],
    [t('通过 SMAPI 启动', 'Launch through SMAPI'), t('使用 SMAPI 配置好的游戏入口。加载列表应出现霜灯港内容包和 Harbor Services 运行模块，没有缺失前置的红色错误。', 'Use your SMAPI-configured game launcher. Look for the Frosthavn content pack and Harbor Services runtime in the loaded mods, without missing-dependency errors.')],
    [t('收信，然后登机', 'A letter, then a flight'), t('进入存档，阅读月月鸟邀请信并领取机票。到山谷巴士站按 B，再按 Enter 出发。抵达后沿机场南侧步道进镇，按 K 查看行程。', 'Load a save, read Moonbird’s invitation and take the enclosed ticket. At the Valley bus stop press B, then Enter. Walk south from the airstrip into town. K opens your route book.')],
  ];
  async function copyPath() {
    try { await navigator.clipboard.writeText(paths[os]); setCopied(true); } catch { setCopied(false); }
  }
  return <div className="ig-guide">
    <div className="ig-intro"><span className="fh-eyebrow">MOONBIRD AIR / DEPARTURES</span><h2 id="fh-dialog-title">{t('从安装，到抵达。', 'From installation to arrival.')}</h2><p>{t('把这页当作你的登机指南。每一步都可以展开查看。', 'Your boarding guide, one step at a time. Open each step for details.')}</p></div>
    <div className="ig-platform" role="group" aria-label={t('选择电脑系统', 'Choose your computer system')}>
      {(['windows', 'mac', 'linux'] as const).map(value => <button key={value} type="button" aria-pressed={os === value} onClick={() => { setOs(value); setCopied(false); }}>{value === 'mac' ? 'macOS' : value === 'linux' ? 'Linux' : 'Windows'}</button>)}
    </div>
    <p className="ig-small ig-compat" role="note">{os==='mac'?t('已实测：macOS · 星露谷 1.6.15 · SMAPI 4.5.2。','Tested: macOS · Stardew Valley 1.6.15 · SMAPI 4.5.2.'):os==='windows'?t('提供通用安装包。Windows 游戏运行尚未实测，建议先在独立存档中启程。','A portable package is provided. Windows gameplay has not been verified; begin with a separate save.'):t('提供通用安装包。Linux 游戏运行尚未实测，建议先在独立存档中启程。','A portable package is provided. Linux gameplay has not been verified; begin with a separate save.')}</p>
    <div className="ig-path"><span>{t('常见 Steam 安装位置', 'Typical Steam location')}</span><code>{paths[os]}</code><button type="button" onClick={() => void copyPath()}>{copied ? t('已复制', 'Copied') : t('复制路径', 'Copy path')}</button></div>
    <p className="ig-small">{t('如果游戏装在其他位置：Steam 游戏库 → 右键游戏 → 管理 → 浏览本地文件。macOS 继续进入 Contents / MacOS。', 'For a custom location: Steam Library → right-click the game → Manage → Browse local files. On macOS continue into Contents / MacOS.')}</p>
    <div className="ig-progress"><span>{t('行前自查', 'Your checklist')}</span><span aria-live="polite">{checked.length} / 5 {t('已检查', 'checked')}</span></div>
    <div className="ig-steps">{steps.map(([title, body], i) => <details className="ig-step" key={title} open={i === 0 ? true : undefined}>
      <summary><span className="ig-step-number">0{i + 1}</span><strong>{title}</strong><span className="ig-expand">+</span></summary>
      <div className="ig-step-body"><p>{body}</p>
        {i === 0 && <a className="fh-text-link" target="_blank" rel="noreferrer" href="https://stardewvalleywiki.com/Saves">{t('存档位置与备份说明 ↗', 'Save locations & backups ↗')}</a>}
        {i === 1 && <div className="ig-links"><a target="_blank" rel="noreferrer" href="https://smapi.io/">SMAPI ↗</a><a target="_blank" rel="noreferrer" href="https://www.nexusmods.com/stardewvalley/mods/1915">Content Patcher ↗</a></div>}
        {i === 2 && <><a className="fh-button" href={DOWNLOAD}>{t('领取旅行安装包 ↗', 'Get the travel package ↗')}</a><pre className="ig-tree">{'Stardew Valley/\n└─ Mods/\n   ├─ ContentPatcher/\n   │  └─ manifest.json\n   ├─ ArcticPassage/\n   │  ├─ manifest.json\n   │  └─ content.json\n   └─ ArcticPassage.Runtime/\n      ├─ manifest.json\n      └─ ArcticPassage.Runtime.dll'}</pre><p className="ig-small">{t('三个 manifest.json 都应直接位于对应文件夹内。不要把 ZIP 或多套一层的外壳目录放进去；两个霜灯港文件夹必须同版。', 'Each manifest.json belongs directly inside its mod folder. Do not install the ZIP or an extra wrapper folder. Both Frosthavn folders must be the same version.')}</p></>}
        {i === 4 && <div className="ig-captures">{['letter', 'checkin', 'arrival'].map((image, n) => <figure key={image}><img src={'/assets/guide-' + image + '.webp'} alt={t(['游戏中的月月鸟邀请信与机票', '巴士站登机界面', '实际雪跑道抵达画面'][n]!, ['In-game invitation and ticket', 'Bus stop check-in', 'Actual airstrip arrival'][n]!)} loading="lazy" /><figcaption>{['01 / LETTER', '02 / CHECK-IN', '03 / ARRIVAL'][n]}</figcaption></figure>)}<p className="ig-small">{t('收好机票，在巴士站出发，沿雪跑道南侧的小路进镇。', 'Keep your ticket. Depart at the bus stop, then follow the southern airstrip path into town.')}</p></div>}
        <label className="ig-check"><input type="checkbox" checked={checked.includes(i)} onChange={e => setChecked(previous => e.target.checked ? [...previous, i] : previous.filter(n => n !== i))} />{t('这一步我已检查', 'I have checked this step')}</label>
      </div>
    </details>)}</div>
    <div className="ig-trouble"><h3>{t('遇到问题？先看这里。', 'Trouble getting started?')}</h3>
      {[
        [t('没有收到邀请信', 'No invitation letter'), t('先确认通过 SMAPI 启动、两个模组均已加载，然后正常睡一晚再查邮箱。领票后再到巴士站按 B。', 'Check that SMAPI loaded both mods, sleep normally, then check the mailbox again. Take the ticket before pressing B at the bus stop.')],
        [t('提示缺失前置或重复模组', 'Missing dependency or duplicate mod'), t('核对 Content Patcher 和运行模块，确保两个霜灯港目录同版、没有套层、Mods 中没有新旧两份。', 'Check Content Patcher and the runtime. Install matching Frosthavn versions, remove extra folder nesting and keep old backups outside Mods.')],
        [t('更新与卸载', 'Updating & uninstalling'), t('退出游戏、备份存档后，同时替换两个模组目录。卸载前先回山谷；建议先使用备份或单独存档开始旅程。', 'Exit, back up and replace both mod folders together. Return to the Valley before uninstalling. Begin with a backup or a separate save.')],
      ].map(([q, a]) => <details key={q}><summary>{q}<span>+</span></summary><p>{a}</p></details>)}
    </div>

    <a className="fh-text-link" href={GUIDE} target="_blank" rel="noreferrer">{t('完整文字安装说明 ↗', 'Full written installation guide ↗')}</a>
  </div>;
}
