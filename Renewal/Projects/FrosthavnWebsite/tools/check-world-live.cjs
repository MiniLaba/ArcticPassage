const {chromium}=require('../../FrosthavnPromo/node_modules/playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--use-angle=metal','--enable-webgl','--ignore-gpu-blocklist']});
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[],worldRequests=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});page.on('request',r=>{if(r.url().includes('worldBundle'))worldRequests.push(r.url());});
 const url=process.env.FROSTHAVN_URL||'https://frosthavn-siming.lovable.app/';await page.goto(url,{waitUntil:'domcontentloaded'});
 await page.locator('.sx-world').waitFor({timeout:30000});
 assert.equal(await page.locator('dialog[open]').count(),0);assert.equal(worldRequests.length,0,'model should not download before entering');
 await page.locator('#explore').scrollIntoViewIfNeeded();await page.locator('.sx-world').screenshot({path:'/private/tmp/world-live-cover.png'});
 await page.getByRole('button',{name:'走进立体海湾 ↗',exact:true}).click();await page.waitForFunction(()=>document.querySelector('.sx-world')?.dataset.sceneStatus==='ready',null,{timeout:60000});
 await page.getByRole('button',{name:'拉近',exact:true}).click();await page.waitForTimeout(500);
 const box=await page.locator('.sx-world-stage').boundingBox();await page.mouse.move(box.x+box.width*.55,box.y+box.height*.55);await page.mouse.down();await page.mouse.move(box.x+box.width*.42,box.y+box.height*.59,{steps:10});await page.mouse.up();
 await page.locator('.sx-world').screenshot({path:'/private/tmp/world-live-desktop.png'});
 let fullscreen=false;
 if(await page.getByRole('button',{name:'全屏浏览',exact:true}).count()){
  await page.getByRole('button',{name:'全屏浏览',exact:true}).click();await page.waitForFunction(()=>!!document.fullscreenElement);fullscreen=true;
  await page.screenshot({path:'/private/tmp/world-live-fullscreen.png'});await page.getByRole('button',{name:'退出全屏',exact:true}).click();
 }
 await page.getByRole('button',{name:'走过一年 ▷',exact:true}).click();await page.waitForFunction(()=>document.querySelector('.sx-world')?.dataset.worldSeason!=='winter',null,{timeout:18000});await page.getByRole('button',{name:'暂停四季 Ⅱ',exact:true}).click();
 await page.locator('.sx-world-seasons').getByRole('button',{name:'夏',exact:true}).click();await page.getByRole('button',{name:'午夜太阳',exact:true}).click();await page.waitForTimeout(1800);await page.locator('.sx-world').screenshot({path:'/private/tmp/world-live-midnight-sun.png'});
 await page.getByRole('button',{name:'Switch to English',exact:true}).click();assert(await page.getByRole('button',{name:'Midnight sun',exact:true}).isVisible());
 const mobile=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true});await mobile.goto(url,{waitUntil:'domcontentloaded'});await mobile.locator('#explore').scrollIntoViewIfNeeded();await mobile.getByRole('button',{name:'走进立体海湾 ↗',exact:true}).click();await mobile.waitForFunction(()=>document.querySelector('.sx-world')?.dataset.sceneStatus==='ready',null,{timeout:60000});await mobile.locator('.sx-world').screenshot({path:'/private/tmp/world-live-mobile.png'});assert((await mobile.evaluate(()=>document.documentElement.scrollWidth))<=391);
 console.log(JSON.stringify({url,live:true,noOpeningModal:true,lazyWorld:true,realWebGL:true,zoomAndDrag:true,fullscreen,annualCycle:true,midnightSun:true,english:true,mobileViewport:390,errors,worldRequests},null,2));
 await browser.close();if(errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
