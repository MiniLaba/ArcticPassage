const {chromium}=require('../../FrosthavnPromo/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--use-angle=metal','--enable-webgl','--ignore-gpu-blocklist']});
 const page=await browser.newPage({viewport:{width:1600,height:900}});
 await page.goto('http://127.0.0.1:4183/',{waitUntil:'domcontentloaded'});
 await page.setContent('<style>body{margin:0}#host{position:fixed;inset:0}canvas{display:block}</style><div id="host"></div>');
 const stats=await page.evaluate(async()=>{
  const {createWorld}=await import('/src/worldBundle.mjs');
  window.posterWorld=await createWorld(document.getElementById('host'),{reducedMotion:true});
  return window.posterWorld.getState();
 });
 await page.screenshot({path:'/private/tmp/frosthavn-world-poster.png'});
 const summer=await page.evaluate(()=>{window.posterWorld.setSeason('summer');window.posterWorld.setNight(true);return window.posterWorld.getState();});
 if(summer.night!==0)throw new Error('Summer midnight sun must remain above the horizon');
 await page.waitForTimeout(100);await page.screenshot({path:'/private/tmp/frosthavn-world-midnight-sun.png'});
 const winter=await page.evaluate(()=>{window.posterWorld.setSeason('winter');window.posterWorld.setNight(true);return window.posterWorld.getState();});
 if(winter.night!==1)throw new Error('Winter long night must be available');
 console.log(JSON.stringify(stats));
 await page.evaluate(()=>window.posterWorld.dispose());await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
